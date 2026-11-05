use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

use eframe::egui;

const SAVED: &str = "Saved";

#[derive(Clone, Debug, PartialEq, Eq)]
struct GxPreset {
    path: PathBuf,
    /// Filename without .vstpreset. This is the Ardour preset label.
    label: String,
    /// Shown in the list and used as the Ardour track name.
    name: String,
    bank: String,
}

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([460.0, 760.0]),
        persist_window: false,
        ..Default::default()
    };
    eframe::run_native(
        "Guitarix Preset Browser",
        options,
        Box::new(|cc| Ok(Box::new(BrowserApp::new(cc)))),
    )?;
    // The window closed without a choice. Lua treats empty output as cancel.
    std::process::exit(1);
}

struct BrowserApp {
    query: String,
    preset_dir: String,
    status: String,
    presets: Arc<Mutex<Vec<GxPreset>>>,
    highlight: Option<PathBuf>,
    settings_focused: bool,
    collapse_categories: bool,
}

impl BrowserApp {
    fn new(cc: &eframe::CreationContext<'_>) -> Self {
        let mut app = Self {
            query: String::new(),
            preset_dir: default_preset_dir().display().to_string(),
            status: String::new(),
            presets: Arc::new(Mutex::new(Vec::new())),
            highlight: None,
            settings_focused: false,
            collapse_categories: true,
        };
        if let Some(storage) = cc.storage {
            if let Some(value) = storage.get_string("guitarix_preset_dir") {
                app.preset_dir = value;
            }
        }
        app.start_scan();
        app
    }

    fn start_scan(&mut self) {
        let found = scan_directory(PathBuf::from(&self.preset_dir));
        let count = found.len();
        let banks = found
            .iter()
            .map(|preset| preset.bank.as_str())
            .collect::<std::collections::BTreeSet<_>>()
            .len();
        self.status = format!("{count} presets in {banks} banks");
        if let Ok(mut presets) = self.presets.lock() {
            *presets = found;
        }
    }

    fn visible_presets(&self) -> Vec<GxPreset> {
        let presets = self.presets.lock().ok();
        let Some(presets) = presets else {
            return Vec::new();
        };
        let query = self.query.trim().to_lowercase();
        let mut visible: Vec<GxPreset> = presets
            .iter()
            .filter(|preset| matches_query(preset, &query))
            .cloned()
            .collect();
        visible.sort_by(|a, b| {
            bank_rank(&a.bank)
                .cmp(&bank_rank(&b.bank))
                .then(a.bank.to_lowercase().cmp(&b.bank.to_lowercase()))
                .then(a.name.to_lowercase().cmp(&b.name.to_lowercase()))
                .then(a.label.to_lowercase().cmp(&b.label.to_lowercase()))
        });
        visible
    }

    fn choose(&mut self, preset: &GxPreset) {
        let label = preset.label.replace(['\n', '\r'], " ");
        let name = preset.name.replace(['\n', '\r'], " ");
        println!("{label}\n{name}");
        let _ = std::io::stdout().flush();
        std::process::exit(0);
    }
}

impl eframe::App for BrowserApp {
    fn save(&mut self, storage: &mut dyn eframe::Storage) {
        storage.set_string("guitarix_preset_dir", self.preset_dir.clone());
    }

    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("search").show(ctx, |ui| {
            ui.add_space(6.0);
            ui.horizontal(|ui| {
                ui.label("Search");
                let field = ui.add(
                    egui::TextEdit::singleline(&mut self.query)
                        .hint_text("Preset or bank")
                        .desired_width(f32::INFINITY),
                );
                if field.changed() {
                    self.highlight = None;
                }
            });
            ui.add_space(6.0);
        });

        let visible = self.visible_presets();
        if let Some(path) = &self.highlight {
            if !visible.iter().any(|preset| preset.path == *path) {
                self.highlight = visible.first().map(|preset| preset.path.clone());
            }
        } else if let Some(preset) = visible.first() {
            self.highlight = Some(preset.path.clone());
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
                ui.label("Presets");
                let folder = ui.add(
                    egui::TextEdit::singleline(&mut self.preset_dir)
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

        let searching = !self.query.trim().is_empty();
        egui::CentralPanel::default().show(ctx, |ui| {
            if visible.is_empty() {
                ui.label("No presets match.");
                return;
            }

            egui::ScrollArea::vertical().show(ui, |ui| {
                let mut index = 0;
                while index < visible.len() {
                    let bank = visible[index].bank.clone();
                    let end = visible[index..]
                        .iter()
                        .position(|preset| preset.bank != bank)
                        .map(|offset| index + offset)
                        .unwrap_or(visible.len());
                    let mut header =
                        egui::CollapsingHeader::new(format!("{bank} ({})", end - index))
                            .id_salt(&bank)
                            .default_open(false);
                    if searching {
                        header = header.open(Some(true));
                    } else if self.collapse_categories {
                        header = header.open(Some(false));
                    }
                    header.show(ui, |ui| {
                        for preset in &visible[index..end] {
                            let selected = self
                                .highlight
                                .as_ref()
                                .is_some_and(|path| preset.path == *path);
                            if ui.selectable_label(selected, &preset.name).clicked() {
                                self.choose(preset);
                            }
                        }
                    });
                    index = end;
                }
            });
        });
        if self.collapse_categories && !visible.is_empty() {
            self.collapse_categories = false;
        }
    }
}

fn move_highlight(highlight: &mut Option<PathBuf>, visible: &[GxPreset], delta: isize) {
    if visible.is_empty() {
        return;
    }
    let current = highlight
        .as_ref()
        .and_then(|path| visible.iter().position(|preset| preset.path == *path))
        .unwrap_or(0);
    let next = (current as isize + delta).clamp(0, visible.len() as isize - 1) as usize;
    *highlight = Some(visible[next].path.clone());
}

fn highlighted_preset<'a>(
    highlight: &Option<PathBuf>,
    visible: &'a [GxPreset],
) -> Option<&'a GxPreset> {
    highlight
        .as_ref()
        .and_then(|path| visible.iter().find(|preset| preset.path == *path))
}

fn matches_query(preset: &GxPreset, query: &str) -> bool {
    if query.is_empty() {
        return true;
    }
    preset.name.to_lowercase().contains(query) || preset.bank.to_lowercase().contains(query)
}

fn bank_rank(bank: &str) -> u8 {
    if bank == SAVED {
        0
    } else {
        1
    }
}

fn default_preset_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".vst3/presets/brummer/Guitarix")
}

fn scan_directory(directory: PathBuf) -> Vec<GxPreset> {
    let mut presets = Vec::new();
    let Ok(entries) = std::fs::read_dir(&directory) else {
        return presets;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_file() && is_vstpreset(&path) {
            if let Some(preset) = preset_from_path(path) {
                presets.push(preset);
            }
        }
    }
    presets
}

fn is_vstpreset(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| ext.eq_ignore_ascii_case("vstpreset"))
}

fn preset_from_path(path: PathBuf) -> Option<GxPreset> {
    let stem = path.file_stem()?.to_str()?.to_string();
    let (bank, name) = stem
        .split_once(" - ")
        .filter(|(bank, name)| !bank.is_empty() && !name.is_empty())
        .map(|(bank, name)| (bank.to_string(), name.to_string()))
        .unwrap_or_else(|| (SAVED.to_string(), stem.clone()));
    Some(GxPreset {
        path,
        label: stem,
        name,
        bank,
    })
}
