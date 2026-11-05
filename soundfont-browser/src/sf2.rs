use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

use crate::gm;

const PRESET_HEADER_SIZE: u64 = 38;

#[derive(Clone, Debug)]
pub struct Preset {
    pub name: String,
    pub category: &'static str,
    pub bank: u16,
    pub program: u16,
    pub path: std::path::PathBuf,
    pub font_name: String,
}

pub fn read_presets(path: &Path) -> Result<Vec<Preset>, String> {
    let mut file = File::open(path).map_err(|err| err.to_string())?;
    let riff = read_fourcc(&mut file)?;
    let riff_size = read_u32(&mut file)?;
    let form = read_fourcc(&mut file)?;
    if &riff != b"RIFF" || &form != b"sfbk" {
        return Err("not a SoundFont".into());
    }

    let file_end = u64::from(riff_size) + 8;
    let font_name = path
        .file_stem()
        .and_then(|stem| stem.to_str())
        .unwrap_or("SoundFont")
        .to_string();
    let mut presets = Vec::new();

    while file.stream_position().map_err(|err| err.to_string())? + 8 <= file_end {
        let id = read_fourcc(&mut file)?;
        let size = read_u32(&mut file)?;
        let start = file.stream_position().map_err(|err| err.to_string())?;
        let chunk_end = start + padded(size);
        if chunk_end > file_end.saturating_add(1) {
            break;
        }

        if &id == b"LIST" {
            let list_type = read_fourcc(&mut file)?;
            if &list_type == b"pdta" {
                presets = read_phdr(&mut file, chunk_end, path, &font_name)?;
            }
        }

        file.seek(SeekFrom::Start(chunk_end))
            .map_err(|err| err.to_string())?;
    }

    if presets.is_empty() {
        return Err("no presets".into());
    }
    presets.sort_by(|a, b| (a.bank, a.program).cmp(&(b.bank, b.program)));
    Ok(presets)
}

fn read_phdr(
    file: &mut File,
    list_end: u64,
    path: &Path,
    font_name: &str,
) -> Result<Vec<Preset>, String> {
    let mut presets = Vec::new();
    while file.stream_position().map_err(|err| err.to_string())? + 8 <= list_end {
        let id = read_fourcc(file)?;
        let size = read_u32(file)?;
        let start = file.stream_position().map_err(|err| err.to_string())?;
        let chunk_end = start + padded(size);
        if &id == b"phdr" {
            if size < PRESET_HEADER_SIZE as u32 || size % PRESET_HEADER_SIZE as u32 != 0 {
                return Err("invalid preset header chunk".into());
            }
            let count = u64::from(size) / PRESET_HEADER_SIZE;
            if count < 2 {
                return Err("preset list has no records".into());
            }
            for _ in 0..count - 1 {
                let mut record = [0u8; PRESET_HEADER_SIZE as usize];
                file.read_exact(&mut record)
                    .map_err(|err| err.to_string())?;
                let mut name = fixed_string(&record[..20]);
                let program = u16::from_le_bytes([record[20], record[21]]);
                let bank = u16::from_le_bytes([record[22], record[23]]);
                if name.is_empty() {
                    name = gm::program_name(program).to_string();
                }
                presets.push(Preset {
                    name,
                    category: gm::category(bank, program),
                    bank,
                    program,
                    path: path.to_path_buf(),
                    font_name: font_name.to_string(),
                });
            }
            return Ok(presets);
        }
        file.seek(SeekFrom::Start(chunk_end.min(list_end)))
            .map_err(|err| err.to_string())?;
    }
    Err("preset headers were not found".into())
}

fn padded(size: u32) -> u64 {
    u64::from(size) + u64::from(size % 2)
}

fn read_fourcc(file: &mut File) -> Result<[u8; 4], String> {
    let mut bytes = [0u8; 4];
    file.read_exact(&mut bytes).map_err(|err| err.to_string())?;
    Ok(bytes)
}

fn read_u32(file: &mut File) -> Result<u32, String> {
    let mut bytes = [0u8; 4];
    file.read_exact(&mut bytes).map_err(|err| err.to_string())?;
    Ok(u32::from_le_bytes(bytes))
}

fn fixed_string(bytes: &[u8]) -> String {
    let end = bytes
        .iter()
        .position(|byte| *byte == 0)
        .unwrap_or(bytes.len());
    String::from_utf8_lossy(&bytes[..end])
        .trim_end_matches([' ', '\t'])
        .to_string()
}

#[cfg(test)]
mod tests {
    use super::read_presets;
    use std::path::Path;

    #[test]
    fn reads_stereo_grand_presets() {
        let path =
            Path::new(env!("CARGO_MANIFEST_DIR")).join("../soundfonts/Stereo Grand Piano.sf2");
        let presets = read_presets(&path).expect("Stereo Grand Piano should parse");
        assert!(!presets.is_empty());
        assert!(presets.iter().all(|preset| !preset.name.is_empty()));
        assert!(presets
            .iter()
            .all(|preset| preset.bank != 128 || preset.category == "Drum Kits"));
        assert!(presets.iter().any(|preset| preset.category == "Piano"));
        let drums = Path::new(env!("CARGO_MANIFEST_DIR")).join("../soundfonts/808_909.sf2");
        let kits = read_presets(&drums).expect("drum font should parse");
        assert!(kits.iter().any(|preset| preset.category == "Drum Kits"));
    }

    #[test]
    fn library_uses_bank_and_program_categories() {
        let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("../soundfonts");
        let mut presets = 0;
        let mut drums = 0;
        for entry in std::fs::read_dir(&dir).unwrap() {
            let path = entry.unwrap().path();
            let is_sf2 = path
                .extension()
                .and_then(|ext| ext.to_str())
                .is_some_and(|ext| ext.eq_ignore_ascii_case("sf2"));
            if !is_sf2 {
                continue;
            }
            let found =
                read_presets(&path).unwrap_or_else(|err| panic!("{}: {err}", path.display()));
            for preset in &found {
                assert!(!preset.name.is_empty(), "{}", path.display());
                if preset.bank == 128 || preset.bank == 120 {
                    assert_eq!(preset.category, "Drum Kits");
                    drums += 1;
                } else {
                    assert_ne!(preset.category, "Drum Kits");
                }
            }
            presets += found.len();
        }
        assert_eq!(presets, 269);
        assert_eq!(drums, 22);
    }
}
