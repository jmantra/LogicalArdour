use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::mpsc::{self, Receiver};
use std::sync::{Arc, Mutex};

use eframe::egui;

const ACOUSTIC: &str = "Acoustic Kits";
const ELECTRONIC: &str = "Electronic Kits";
const AVL: &str = "AVL Drumkits";

#[derive(Clone, Debug, PartialEq, Eq)]
struct Kit {
    path: PathBuf,
    /// Name shown in the list and used as the Ardour track name.
    name: String,
    category: &'static str,
    /// Set for AVL kits. The Lua script loads this LV2 plugin instead of the .sf2.
    plugin: Option<String>,
}

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([460.0, 760.0]),
        persist_window: false,
        ..Default::default()
    };
    eframe::run_native(
        "Drum Soundfont Browser",
        options,
        Box::new(|cc| Ok(Box::new(BrowserApp::new(cc)))),
    )?;
    // The window closed without a choice. Lua treats empty output as cancel.
    std::process::exit(1);
}

struct ScanUpdate {
    kits: Vec<Kit>,
    scanned: usize,
    total: usize,
    done: bool,
}

struct BrowserApp {
    query: String,
    font_dir: String,
    status: String,
    kits: Arc<Mutex<Vec<Kit>>>,
    highlight: Option<PathBuf>,
    scan_rx: Option<Receiver<ScanUpdate>>,
    scanning: bool,
    settings_focused: bool,
    collapse_categories: bool,
}

impl BrowserApp {
    fn new(cc: &eframe::CreationContext<'_>) -> Self {
        let mut app = Self {
            query: String::new(),
            font_dir: default_font_dir().display().to_string(),
            status: "Scanning drum soundfonts…".to_string(),
            kits: Arc::new(Mutex::new(Vec::new())),
            highlight: None,
            scan_rx: None,
            scanning: false,
            settings_focused: false,
            collapse_categories: true,
        };
        if let Some(storage) = cc.storage {
            if let Some(value) = storage.get_string("drum_font_dir") {
                app.font_dir = value;
            }
        }
        app.start_scan();
        app
    }

    fn start_scan(&mut self) {
        let directory = PathBuf::from(&self.font_dir);
        let (tx, rx) = mpsc::channel();
        self.scan_rx = Some(rx);
        self.scanning = true;
        self.status = "Scanning drum soundfonts…".to_string();
        if let Ok(mut kits) = self.kits.lock() {
            kits.clear();
        }
        std::thread::spawn(move || scan_directory(directory, tx));
    }

    fn take_scan_updates(&mut self) {
        let Some(rx) = &self.scan_rx else {
            return;
        };
        while let Ok(update) = rx.try_recv() {
            if let Ok(mut kits) = self.kits.lock() {
                *kits = update.kits;
            }
            if update.done {
                self.scanning = false;
                let count = self.kits.lock().map(|list| list.len()).unwrap_or(0);
                self.status = format!("{count} drum kits");
            } else {
                self.status = format!("Scanning {} / {}", update.scanned, update.total);
            }
        }
    }

    fn visible_kits(&self) -> Vec<Kit> {
        let kits = self.kits.lock().ok();
        let Some(kits) = kits else {
            return Vec::new();
        };
        let query = self.query.trim().to_lowercase();
        let mut visible: Vec<Kit> = kits
            .iter()
            .filter(|kit| matches_query(kit, &query))
            .cloned()
            .collect();
        visible.sort_by(|a, b| {
            category_order(a.category)
                .cmp(&category_order(b.category))
                .then(a.name.to_lowercase().cmp(&b.name.to_lowercase()))
                .then(a.path.cmp(&b.path))
        });
        visible
    }

    fn choose(&mut self, kit: &Kit) {
        let absolute = kit.path.canonicalize().unwrap_or_else(|_| kit.path.clone());
        let name = kit.name.replace(['\n', '\r'], " ");
        if let Some(plugin) = &kit.plugin {
            let plugin = plugin.replace(['\n', '\r'], " ");
            println!("{}\n{name}\navl\n{plugin}", absolute.display());
        } else {
            println!("{}\n{name}\nsf2\n", absolute.display());
        }
        let _ = std::io::stdout().flush();
        std::process::exit(0);
    }
}

impl eframe::App for BrowserApp {
    fn save(&mut self, storage: &mut dyn eframe::Storage) {
        storage.set_string("drum_font_dir", self.font_dir.clone());
    }

    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.take_scan_updates();
        if self.scanning {
            ctx.request_repaint();
        }

        egui::TopBottomPanel::top("search").show(ctx, |ui| {
            ui.add_space(6.0);
            ui.horizontal(|ui| {
                ui.label("Search");
                let field = ui.add(
                    egui::TextEdit::singleline(&mut self.query)
                        .hint_text("Kit name")
                        .desired_width(f32::INFINITY),
                );
                if field.changed() {
                    self.highlight = None;
                }
            });
            ui.add_space(6.0);
        });

        let visible = self.visible_kits();
        if let Some(path) = &self.highlight {
            if !visible.iter().any(|kit| kit.path == *path) {
                self.highlight = visible.first().map(|kit| kit.path.clone());
            }
        } else if let Some(kit) = visible.first() {
            self.highlight = Some(kit.path.clone());
        }

        if !self.settings_focused {
            if ctx.input(|input| input.key_pressed(egui::Key::ArrowDown)) {
                move_highlight(&mut self.highlight, &visible, 1);
            }
            if ctx.input(|input| input.key_pressed(egui::Key::ArrowUp)) {
                move_highlight(&mut self.highlight, &visible, -1);
            }
            if ctx.input(|input| input.key_pressed(egui::Key::Enter)) {
                if let Some(kit) = highlighted_kit(&self.highlight, &visible).cloned() {
                    self.choose(&kit);
                }
            }
        }

        let mut settings_focused = false;
        egui::TopBottomPanel::bottom("status").show(ctx, |ui| {
            ui.add_space(4.0);
            ui.label(&self.status);
            ui.horizontal(|ui| {
                ui.label("Soundfonts");
                let folder = ui.add(
                    egui::TextEdit::singleline(&mut self.font_dir)
                        .desired_width(ui.available_width() - 80.0),
                );
                settings_focused |= folder.has_focus();
                if ui.button("Rescan").clicked() {
                    self.highlight = None;
                    self.start_scan();
                }
            });
            ui.add_space(4.0);
        });
        self.settings_focused = settings_focused;

        egui::CentralPanel::default().show(ctx, |ui| {
            if visible.is_empty() {
                ui.label(if self.scanning {
                    "Reading drum soundfonts…"
                } else {
                    "No drum kits match."
                });
                return;
            }

            egui::ScrollArea::vertical().show(ui, |ui| {
                let mut index = 0;
                while index < visible.len() {
                    let category = visible[index].category;
                    let end = visible[index..]
                        .iter()
                        .position(|kit| kit.category != category)
                        .map(|offset| index + offset)
                        .unwrap_or(visible.len());
                    let mut header =
                        egui::CollapsingHeader::new(format!("{category} ({})", end - index))
                            .id_salt(category)
                            .default_open(false);
                    if self.collapse_categories {
                        header = header.open(Some(false));
                    }
                    header.show(ui, |ui| {
                        for kit in &visible[index..end] {
                            let selected = self
                                .highlight
                                .as_ref()
                                .is_some_and(|path| kit.path == *path);
                            if ui.selectable_label(selected, &kit.name).clicked() {
                                self.choose(kit);
                            }
                        }
                    });
                    index = end;
                }
            });
        });
        if self.collapse_categories && !self.scanning && !visible.is_empty() {
            self.collapse_categories = false;
        }
    }
}

fn move_highlight(highlight: &mut Option<PathBuf>, visible: &[Kit], delta: isize) {
    if visible.is_empty() {
        return;
    }
    let current = highlight
        .as_ref()
        .and_then(|path| visible.iter().position(|kit| kit.path == *path))
        .unwrap_or(0);
    let next = (current as isize + delta).clamp(0, visible.len() as isize - 1) as usize;
    *highlight = Some(visible[next].path.clone());
}

fn highlighted_kit<'a>(highlight: &Option<PathBuf>, visible: &'a [Kit]) -> Option<&'a Kit> {
    highlight
        .as_ref()
        .and_then(|path| visible.iter().find(|kit| kit.path == *path))
}

fn matches_query(kit: &Kit, query: &str) -> bool {
    if query.is_empty() {
        return true;
    }
    kit.name.to_lowercase().contains(query) || kit.category.to_lowercase().contains(query)
}

fn default_font_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../Drum Soundfonts")
}

fn category_order(category: &str) -> usize {
    match category {
        ACOUSTIC => 0,
        ELECTRONIC => 1,
        AVL => 2,
        _ => 3,
    }
}

fn scan_directory(directory: PathBuf, tx: std::sync::mpsc::Sender<ScanUpdate>) {
    let mut files = Vec::new();
    if let Ok(entries) = std::fs::read_dir(&directory) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() && is_soundfont(&path) {
                files.push(path);
            }
        }
    }
    files.sort();
    let total = files.len();
    let mut kits = Vec::new();
    let _ = tx.send(ScanUpdate {
        kits: kits.clone(),
        scanned: 0,
        total,
        done: false,
    });
    for (index, path) in files.iter().enumerate() {
        if let Some(kit) = kit_from_path(path) {
            kits.push(kit);
        }
        if index % 8 == 7 || index + 1 == total {
            let _ = tx.send(ScanUpdate {
                kits: kits.clone(),
                scanned: index + 1,
                total,
                done: false,
            });
        }
    }
    let _ = tx.send(ScanUpdate {
        kits,
        scanned: total,
        total,
        done: true,
    });
}

fn is_soundfont(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| ext.eq_ignore_ascii_case("sf2") || ext.eq_ignore_ascii_case("sf3"))
}

fn kit_from_path(path: &Path) -> Option<Kit> {
    let stem = path.file_stem()?.to_str()?;
    let (category, plugin) = classify(stem)?;
    let name = plugin.clone().unwrap_or_else(|| clean_name(stem));
    Some(Kit {
        path: path.to_path_buf(),
        name,
        category,
        plugin,
    })
}

/// `None` means the file is excluded from the browser.
fn classify(stem: &str) -> Option<(&'static str, Option<String>)> {
    let lower = stem.to_lowercase();
    if lower == "test" || lower == "muljordd" {
        return None;
    }
    if lower.contains("avl") {
        return Some((AVL, Some(avl_plugin(&lower))));
    }
    if is_electronic(&lower) {
        return Some((ELECTRONIC, None));
    }
    Some((ACOUSTIC, None))
}

fn is_electronic(lower: &str) -> bool {
    const NEEDLES: [&str; 12] = [
        "808",
        "809",
        "analog",
        "analong",
        "electronic",
        "dance",
        "house",
        "hiphop",
        "hip-hop",
        "hip hop",
        "alesis",
        "nin",
    ];
    NEEDLES.iter().any(|needle| lower.contains(needle)) || lower.contains("sonineko")
}

fn avl_plugin(lower: &str) -> String {
    if lower.contains("hotrod") || lower.contains("hot rod") || lower.contains("hot-rod") {
        "Blonde Bop HotRod Drumkit".to_string()
    } else if lower.contains("blonde") {
        "Blonde Bop Drumkit".to_string()
    } else if lower.contains("zeppelin") {
        "Red Zeppelin Drumkit".to_string()
    } else if lower.contains("pearl") {
        "Black Pearl Drumkit".to_string()
    } else if lower.contains("busk") || lower.contains("holiday") {
        "Buskman's Holiday Percussion".to_string()
    } else {
        clean_name(lower)
    }
}

fn clean_name(stem: &str) -> String {
    let mut name = String::new();
    let mut pending_space = false;
    for ch in stem.chars() {
        if ch == '_' || ch == '-' {
            pending_space = !name.is_empty();
            continue;
        }
        if ch.is_whitespace() {
            pending_space = !name.is_empty();
            continue;
        }
        if pending_space {
            name.push(' ');
            pending_space = false;
        }
        name.push(ch);
    }
    name
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skips_test_and_duplicate_muljord() {
        assert!(classify("test").is_none());
        assert!(classify("Test").is_none());
        assert!(classify("muljordd").is_none());
        assert!(classify("Muljordd").is_none());
        assert_eq!(classify("muljord").unwrap().0, ACOUSTIC);
    }

    #[test]
    fn groups_known_kits() {
        assert_eq!(classify("808").unwrap().0, ELECTRONIC);
        assert_eq!(classify("analongt8kit").unwrap().0, ELECTRONIC);
        assert_eq!(classify("analogt9kit").unwrap().0, ELECTRONIC);
        assert_eq!(classify("HipHop-2").unwrap().0, ELECTRONIC);
        assert_eq!(classify("HouseKit").unwrap().0, ELECTRONIC);
        assert_eq!(classify("SoniNeko_Drum_Soundfont").unwrap().0, ELECTRONIC);
        assert_eq!(classify("NIN_Drumkit").unwrap().0, ELECTRONIC);
        assert_eq!(classify("Alesis_D4_Drum_Module").unwrap().0, ELECTRONIC);
        assert_eq!(classify("Dance Drums").unwrap().0, ELECTRONIC);
        assert_eq!(classify("Electronic Drums").unwrap().0, ELECTRONIC);

        assert_eq!(classify("Standard 2").unwrap().0, ACOUSTIC);
        assert_eq!(classify("PowerKit2").unwrap().0, ACOUSTIC);
        assert_eq!(classify("Jazz Drums").unwrap().0, ACOUSTIC);
        assert_eq!(classify("Travis_Barker").unwrap().0, ACOUSTIC);
        assert_eq!(classify("sfx").unwrap().0, ACOUSTIC);
        assert_eq!(classify("orch").unwrap().0, ACOUSTIC);
    }

    #[test]
    fn maps_avl_plugins() {
        let cases = [
            ("AVL_Red_Zeppelin", "Red Zeppelin Drumkit"),
            ("AVL Black Pearl", "Black Pearl Drumkit"),
            ("AVL_Blonde_Bop", "Blonde Bop Drumkit"),
            ("AVL Blonde Bop HotRod", "Blonde Bop HotRod Drumkit"),
            ("AVL Buskmans_Holiday", "Buskman's Holiday Percussion"),
        ];
        for (stem, plugin) in cases {
            let (category, found) = classify(stem).unwrap();
            assert_eq!(category, AVL);
            assert_eq!(found.as_deref(), Some(plugin));
        }
    }

    #[test]
    fn folder_matches_plan() {
        let dir = default_font_dir();
        if !dir.is_dir() {
            return;
        }
        let mut names = Vec::new();
        for entry in std::fs::read_dir(&dir).unwrap().flatten() {
            let path = entry.path();
            if !is_soundfont(&path) {
                continue;
            }
            let stem = path.file_stem().unwrap().to_string_lossy().to_string();
            let listed = kit_from_path(&path);
            if stem.eq_ignore_ascii_case("test") || stem.eq_ignore_ascii_case("muljordd") {
                assert!(listed.is_none(), "{stem} should be excluded");
            } else {
                assert!(listed.is_some(), "{stem} should be listed");
                names.push(stem);
            }
        }
        assert!(names
            .iter()
            .any(|name| name.eq_ignore_ascii_case("muljord")));
        assert!(!names.iter().any(|name| name.eq_ignore_ascii_case("test")));
        assert!(!names
            .iter()
            .any(|name| name.eq_ignore_ascii_case("muljordd")));
    }
}
