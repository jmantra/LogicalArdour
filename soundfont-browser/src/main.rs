mod gm;
mod sf2;

use std::io::Write;
use std::path::PathBuf;
use std::sync::mpsc::{self, Receiver};
use std::sync::{Arc, Mutex};

use eframe::egui;
use sf2::Preset;

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([460.0, 760.0]),
        persist_window: false,
        ..Default::default()
    };
    eframe::run_native(
        "Soundfont Browser",
        options,
        Box::new(|cc| Ok(Box::new(BrowserApp::new(cc)))),
    )?;
    // The window closed without a choice. Lua treats empty output as cancel.
    std::process::exit(1);
}

struct ScanUpdate {
    presets: Vec<Preset>,
    scanned: usize,
    total: usize,
    failed: usize,
    done: bool,
}

struct BrowserApp {
    query: String,
    font_dir: String,
    status: String,
    presets: Arc<Mutex<Vec<Preset>>>,
    highlight: Option<(PathBuf, u16, u16)>,
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
            status: "Scanning soundfonts…".to_string(),
            presets: Arc::new(Mutex::new(Vec::new())),
            highlight: None,
            scan_rx: None,
            scanning: false,
            settings_focused: false,
            collapse_categories: true,
        };
        if let Some(storage) = cc.storage {
            if let Some(value) = storage.get_string("font_dir") {
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
        self.status = "Scanning soundfonts…".to_string();
        if let Ok(mut presets) = self.presets.lock() {
            presets.clear();
        }
        std::thread::spawn(move || scan_directory(directory, tx));
    }

    fn take_scan_updates(&mut self) {
        let Some(rx) = &self.scan_rx else {
            return;
        };
        while let Ok(update) = rx.try_recv() {
            if let Ok(mut presets) = self.presets.lock() {
                *presets = update.presets;
            }
            if update.done {
                self.scanning = false;
                self.status = format!(
                    "{} presets from {} soundfonts{}",
                    self.presets.lock().map(|list| list.len()).unwrap_or(0),
                    update.total.saturating_sub(update.failed),
                    if update.failed == 0 {
                        String::new()
                    } else {
                        format!(" ({} unreadable)", update.failed)
                    }
                );
            } else {
                self.status = format!("Scanning {} / {}", update.scanned, update.total);
            }
        }
    }

    fn visible_presets(&self) -> Vec<Preset> {
        let presets = self.presets.lock().ok();
        let Some(presets) = presets else {
            return Vec::new();
        };
        let query = self.query.trim().to_lowercase();
        let mut visible: Vec<Preset> = presets
            .iter()
            .filter(|preset| matches_query(preset, &query))
            .cloned()
            .collect();
        visible.sort_by(|a, b| {
            gm::category_order(a.category)
                .cmp(&gm::category_order(b.category))
                .then(a.name.to_lowercase().cmp(&b.name.to_lowercase()))
                .then(a.font_name.to_lowercase().cmp(&b.font_name.to_lowercase()))
                .then(a.bank.cmp(&b.bank))
                .then(a.program.cmp(&b.program))
        });
        visible
    }

    fn choose(&mut self, preset: &Preset) {
        let absolute = preset
            .path
            .canonicalize()
            .unwrap_or_else(|_| preset.path.clone());
        let name = preset.name.replace(['\n', '\r'], " ");
        println!("{}\n{name}", absolute.display());
        let _ = std::io::stdout().flush();
        std::process::exit(0);
    }
}

impl eframe::App for BrowserApp {
    fn save(&mut self, storage: &mut dyn eframe::Storage) {
        storage.set_string("font_dir", self.font_dir.clone());
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
                        .hint_text("Preset, family, or soundfont")
                        .desired_width(f32::INFINITY),
                );
                if field.changed() {
                    self.highlight = None;
                }
            });
            ui.add_space(6.0);
        });

        let visible = self.visible_presets();
        if let Some(id) = &self.highlight {
            if !visible
                .iter()
                .any(|preset| preset.path == id.0 && preset.bank == id.1 && preset.program == id.2)
            {
                self.highlight = visible
                    .first()
                    .map(|preset| (preset.path.clone(), preset.bank, preset.program));
            }
        } else if let Some(preset) = visible.first() {
            self.highlight = Some((preset.path.clone(), preset.bank, preset.program));
        }

        if !self.settings_focused {
            if ctx.input(|input| input.key_pressed(egui::Key::ArrowDown)) {
                move_highlight(&mut self.highlight, &visible, 1);
            }
            if ctx.input(|input| input.key_pressed(egui::Key::ArrowUp)) {
                move_highlight(&mut self.highlight, &visible, -1);
            }
            if ctx.input(|input| input.key_pressed(egui::Key::Enter)) {
                if let Some(preset) = highlighted_preset(&self.highlight, &visible).cloned() {
                    self.choose(&preset);
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
                    "Reading preset headers…"
                } else {
                    "No presets match."
                });
                return;
            }

            egui::ScrollArea::vertical().show(ui, |ui| {
                let mut index = 0;
                while index < visible.len() {
                    let category = visible[index].category;
                    let end = visible[index..]
                        .iter()
                        .position(|preset| preset.category != category)
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
                        for preset in &visible[index..end] {
                            let selected = self.highlight.as_ref().is_some_and(|id| {
                                preset.path == id.0 && preset.bank == id.1 && preset.program == id.2
                            });
                            ui.horizontal(|ui| {
                                if ui.selectable_label(selected, &preset.name).clicked() {
                                    self.choose(preset);
                                }
                                if preset.font_name != preset.name {
                                    ui.label(egui::RichText::new(&preset.font_name).weak().small());
                                }
                            });
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

fn move_highlight(highlight: &mut Option<(PathBuf, u16, u16)>, visible: &[Preset], delta: isize) {
    if visible.is_empty() {
        return;
    }
    let current = highlight
        .as_ref()
        .and_then(|id| {
            visible.iter().position(|preset| {
                preset.path == id.0 && preset.bank == id.1 && preset.program == id.2
            })
        })
        .unwrap_or(0);
    let next = (current as isize + delta).clamp(0, visible.len() as isize - 1) as usize;
    let preset = &visible[next];
    *highlight = Some((preset.path.clone(), preset.bank, preset.program));
}

fn highlighted_preset<'a>(
    highlight: &Option<(PathBuf, u16, u16)>,
    visible: &'a [Preset],
) -> Option<&'a Preset> {
    highlight.as_ref().and_then(|id| {
        visible
            .iter()
            .find(|preset| preset.path == id.0 && preset.bank == id.1 && preset.program == id.2)
    })
}

fn matches_query(preset: &Preset, query: &str) -> bool {
    if query.is_empty() {
        return true;
    }
    preset.name.to_lowercase().contains(query)
        || preset.category.to_lowercase().contains(query)
        || preset.font_name.to_lowercase().contains(query)
}

fn default_font_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../soundfonts")
}

fn scan_directory(directory: PathBuf, tx: std::sync::mpsc::Sender<ScanUpdate>) {
    let mut files = Vec::new();
    if let Ok(entries) = std::fs::read_dir(&directory) {
        for entry in entries.flatten() {
            let path = entry.path();
            let is_font = path
                .extension()
                .and_then(|ext| ext.to_str())
                .is_some_and(|ext| {
                    ext.eq_ignore_ascii_case("sf2") || ext.eq_ignore_ascii_case("sf3")
                });
            if path.is_file() && is_font {
                files.push(path);
            }
        }
    }
    files.sort();
    let total = files.len();
    let mut presets = Vec::new();
    let mut failed = 0usize;
    let _ = tx.send(ScanUpdate {
        presets: presets.clone(),
        scanned: 0,
        total,
        failed,
        done: false,
    });
    for (index, path) in files.iter().enumerate() {
        match sf2::read_presets(path) {
            Ok(found) => presets.extend(found),
            Err(_) => failed += 1,
        }
        if index % 8 == 7 || index + 1 == total {
            let _ = tx.send(ScanUpdate {
                presets: presets.clone(),
                scanned: index + 1,
                total,
                failed,
                done: false,
            });
        }
    }
    let _ = tx.send(ScanUpdate {
        presets,
        scanned: total,
        total,
        failed,
        done: true,
    });
}
