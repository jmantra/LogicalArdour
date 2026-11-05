use std::fs::File;
use std::path::Path;

use rubato::{
    Resampler, SincFixedIn, SincInterpolationParameters, SincInterpolationType, WindowFunction,
};
use symphonia::core::audio::SampleBuffer;
use symphonia::core::codecs::DecoderOptions;
use symphonia::core::errors::Error as SymphoniaError;
use symphonia::core::formats::FormatOptions;
use symphonia::core::io::MediaSourceStream;
use symphonia::core::meta::MetadataOptions;
use symphonia::core::probe::Hint;

const TARGET_RATE: u32 = 44100;

/// Load an audio file the way Essentia MonoLoader does: first audio stream,
/// channels averaged to mono, resampled to 44100 Hz.
pub fn load_mono_44100(path: &str) -> Result<Vec<f32>, String> {
    let (samples, sample_rate) = decode_mono(Path::new(path))?;
    if samples.is_empty() {
        return Err(format!("no audio samples in {path}"));
    }
    resample(&samples, sample_rate, TARGET_RATE)
}

fn decode_mono(path: &Path) -> Result<(Vec<f32>, u32), String> {
    let file =
        File::open(path).map_err(|err| format!("could not open {}: {err}", path.display()))?;
    let source = MediaSourceStream::new(Box::new(file), Default::default());

    let mut hint = Hint::new();
    if let Some(ext) = path.extension().and_then(|ext| ext.to_str()) {
        hint.with_extension(ext);
    }

    let probed = symphonia::default::get_probe()
        .format(
            &hint,
            source,
            &FormatOptions::default(),
            &MetadataOptions::default(),
        )
        .map_err(|err| format!("could not read {}: {err}", path.display()))?;

    let mut format = probed.format;
    let track = format
        .tracks()
        .iter()
        .find(|track| track.codec_params.sample_rate.is_some())
        .ok_or_else(|| format!("no audio track in {}", path.display()))?;
    let track_id = track.id;
    let sample_rate = track
        .codec_params
        .sample_rate
        .ok_or_else(|| format!("unknown sample rate in {}", path.display()))?;

    let mut decoder = symphonia::default::get_codecs()
        .make(&track.codec_params, &DecoderOptions::default())
        .map_err(|err| format!("could not decode {}: {err}", path.display()))?;

    let mut mono = Vec::new();
    loop {
        let packet = match format.next_packet() {
            Ok(packet) => packet,
            Err(SymphoniaError::IoError(err))
                if err.kind() == std::io::ErrorKind::UnexpectedEof =>
            {
                break;
            }
            Err(SymphoniaError::ResetRequired) => {
                decoder.reset();
                continue;
            }
            Err(err) => return Err(format!("could not decode {}: {err}", path.display())),
        };
        if packet.track_id() != track_id {
            continue;
        }

        let decoded = match decoder.decode(&packet) {
            Ok(decoded) => decoded,
            Err(SymphoniaError::DecodeError(_)) => continue,
            Err(err) => return Err(format!("could not decode {}: {err}", path.display())),
        };

        let spec = *decoded.spec();
        let mut buffer = SampleBuffer::<f32>::new(decoded.capacity() as u64, spec);
        buffer.copy_interleaved_ref(decoded);
        let channels = spec.channels.count();
        if channels == 0 {
            continue;
        }
        if channels == 1 {
            mono.extend_from_slice(buffer.samples());
        } else {
            for frame in buffer.samples().chunks_exact(channels) {
                let sum: f32 = frame.iter().copied().sum();
                mono.push(sum / channels as f32);
            }
        }
    }

    Ok((mono, sample_rate))
}

fn resample(input: &[f32], from: u32, to: u32) -> Result<Vec<f32>, String> {
    if from == to {
        return Ok(input.to_vec());
    }
    if from == 0 {
        return Err("audio sample rate is 0".to_string());
    }

    let params = SincInterpolationParameters {
        sinc_len: 256,
        f_cutoff: 0.95,
        interpolation: SincInterpolationType::Linear,
        oversampling_factor: 256,
        window: WindowFunction::BlackmanHarris2,
    };
    let chunk = 1024.min(input.len()).max(1);
    let mut resampler = SincFixedIn::<f32>::new(to as f64 / from as f64, 2.0, params, chunk, 1)
        .map_err(|err| format!("could not resample audio: {err}"))?;

    let mut output = Vec::new();
    let mut offset = 0;
    while offset + chunk <= input.len() {
        let block = input[offset..offset + chunk].to_vec();
        let processed = resampler
            .process(&[block], None)
            .map_err(|err| format!("could not resample audio: {err}"))?;
        output.extend_from_slice(&processed[0]);
        offset += chunk;
    }
    if offset < input.len() {
        let rest = input[offset..].to_vec();
        let processed = resampler
            .process_partial(Some(&[rest]), None)
            .map_err(|err| format!("could not resample audio: {err}"))?;
        output.extend_from_slice(&processed[0]);
    }
    Ok(output)
}
