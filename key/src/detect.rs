use realfft::RealFftPlanner;

/// Essentia Key names. Index 0 is A, matching the bgate profiles.
const KEYS: [&str; 12] = [
    "A", "Bb", "B", "C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab",
];

/// bgate major and minor profiles from Faraldo, Jordà, and Herrera.
/// Polyphony is off in KeyExtractor, so these are used directly.
const BGATE_MAJOR: [f32; 12] = [
    1.00, 0.00, 0.42, 0.00, 0.53, 0.37, 0.00, 0.77, 0.00, 0.38, 0.21, 0.30,
];
const BGATE_MINOR: [f32; 12] = [
    1.00, 0.00, 0.36, 0.39, 0.00, 0.38, 0.00, 0.74, 0.27, 0.00, 0.42, 0.23,
];

const SAMPLE_RATE: f32 = 44100.0;
const FRAME_SIZE: usize = 4096;
const HOP_SIZE: usize = 4096;
const MIN_FREQUENCY: f32 = 25.0;
const MAX_FREQUENCY: f32 = 3500.0;
const PEAK_THRESHOLD: f32 = 0.0001;
const MAX_PEAKS: usize = 60;
const HPCP_SIZE: usize = 12;
const HPCP_HARMONICS: i32 = 4;
const TUNING_FREQUENCY: f32 = 440.0;
const HPCP_WINDOW: f32 = 1.0;
const PCP_THRESHOLD: f32 = 0.2;
const SILENCE_CUTOFF: f32 = 1e-10;
const DB_SILENCE_CUTOFF: f32 = -100.0;

struct HarmonicPeak {
    semitone: f32,
    strength: f32,
}

struct Peak {
    frequency: f32,
    magnitude: f32,
}

/// Estimate key and scale with Essentia KeyExtractor defaults.
pub fn detect_key(audio: &[f32]) -> Result<(String, String), String> {
    if audio.is_empty() {
        return Err("empty input signal".to_string());
    }

    let window = hann_window(FRAME_SIZE);
    let harmonics = harmonic_peaks(HPCP_HARMONICS);
    let mut planner = RealFftPlanner::<f32>::new();
    let fft = planner.plan_fft_forward(FRAME_SIZE);
    let mut fft_in = fft.make_input_vec();
    let mut fft_out = fft.make_output_vec();
    let mut spectrum = vec![0.0f32; FRAME_SIZE / 2 + 1];

    let mut hpcp_sum = [0.0f32; HPCP_SIZE];
    let mut frame_count = 0usize;

    for frame in frames(audio, FRAME_SIZE, HOP_SIZE) {
        for (index, sample) in frame.iter().enumerate() {
            fft_in[index] = sample * window[index];
        }
        fft.process(&mut fft_in, &mut fft_out)
            .map_err(|err| format!("fft failed: {err}"))?;
        for (mag, bin) in spectrum.iter_mut().zip(fft_out.iter()) {
            *mag = bin.norm();
        }

        let peaks = spectral_peaks(&spectrum);
        let whitened = spectral_whitening(&spectrum, &peaks);
        let hpcp = hpcp(&peaks, &whitened, &harmonics);
        for (sum, value) in hpcp_sum.iter_mut().zip(hpcp) {
            *sum += value;
        }
        frame_count += 1;
    }

    if frame_count == 0 {
        return Err("no audio frames to analyse".to_string());
    }

    let mut average = hpcp_sum;
    for value in &mut average {
        *value /= frame_count as f32;
    }
    normalize_peak(&mut average);
    for value in &mut average {
        if *value < PCP_THRESHOLD {
            *value = 0.0;
        }
    }

    estimate(&average)
}

fn hann_window(size: usize) -> Vec<f32> {
    let mut window = Vec::with_capacity(size);
    let denom = (size - 1) as f32;
    for i in 0..size {
        let value = 0.5 - 0.5 * ((2.0 * std::f32::consts::PI * i as f32) / denom).cos();
        window.push(value);
    }
    let sum: f32 = window.iter().map(|value| value.abs()).sum();
    if sum != 0.0 {
        let scale = 2.0 / sum;
        for value in &mut window {
            *value *= scale;
        }
    }
    window
}

/// FrameCutter with startFromZero = false: the first frame is centered on
/// sample 0 and incomplete edges are zero-padded.
fn frames(audio: &[f32], frame_size: usize, hop_size: usize) -> Vec<Vec<f32>> {
    let mut out = Vec::new();
    let mut start = -((frame_size as isize + 1) / 2);
    let length = audio.len() as isize;
    let mut last = false;

    while !last {
        if start >= length {
            break;
        }
        let mut frame = vec![0.0f32; frame_size];
        let mut idx = 0isize;

        if start < 0 {
            idx = (-start).min(frame_size as isize);
        }

        let copy_from = start + idx;
        let available = if copy_from < length {
            length - copy_from
        } else {
            0
        };
        let howmuch = (frame_size as isize - idx).min(available).max(0);
        if howmuch > 0 {
            let src = copy_from as usize;
            let dst = idx as usize;
            let n = howmuch as usize;
            frame[dst..dst + n].copy_from_slice(&audio[src..src + n]);
        }
        idx += howmuch;

        if idx < frame_size as isize {
            if start + (frame_size as isize) / 2 >= length {
                last = true;
            }
        }

        out.push(frame);
        start += hop_size as isize;
    }
    out
}

fn spectral_peaks(spectrum: &[f32]) -> Vec<Peak> {
    let size = spectrum.len();
    let nyquist = SAMPLE_RATE / 2.0;
    let scale = nyquist / (size - 1) as f32;
    let mut peaks = Vec::new();
    let mut i = ((MIN_FREQUENCY / scale).ceil() as isize).max(0) as usize;

    if i + 1 < size && spectrum[i] > spectrum[i + 1] && spectrum[i] > PEAK_THRESHOLD {
        peaks.push(Peak {
            frequency: i as f32 * scale,
            magnitude: spectrum[i],
        });
    }

    loop {
        while i + 1 < size - 1 && spectrum[i] >= spectrum[i + 1] {
            i += 1;
        }
        while i + 1 < size - 1 && spectrum[i] < spectrum[i + 1] {
            i += 1;
        }
        let mut j = i;
        while j + 1 < size - 1 && spectrum[j] == spectrum[j + 1] {
            j += 1;
        }

        if j + 1 < size - 1 && spectrum[j + 1] < spectrum[j] && spectrum[j] > PEAK_THRESHOLD {
            let (bin, magnitude) = if j != i {
                ((i + j) as f32 * 0.5, spectrum[i])
            } else {
                interpolate(spectrum[j - 1], spectrum[j], spectrum[j + 1], j)
            };
            let frequency = bin * scale;
            if frequency > MAX_FREQUENCY {
                break;
            }
            peaks.push(Peak {
                frequency,
                magnitude,
            });
        }

        i = j;
        if i + 1 >= size - 1 {
            if i == size - 2
                && spectrum[i - 1] < spectrum[i]
                && spectrum[i + 1] < spectrum[i]
                && spectrum[i] > PEAK_THRESHOLD
            {
                let (bin, magnitude) =
                    interpolate(spectrum[i - 1], spectrum[i], spectrum[i + 1], i);
                peaks.push(Peak {
                    frequency: bin * scale,
                    magnitude,
                });
            }
            break;
        }
    }

    let pos = MAX_FREQUENCY / scale;
    if (size as f32 - 2.0) < pos
        && pos <= (size as f32 - 1.0)
        && spectrum[size - 1] > spectrum[size - 2]
        && spectrum[size - 1] > PEAK_THRESHOLD
    {
        peaks.push(Peak {
            frequency: (size - 1) as f32 * scale,
            magnitude: spectrum[size - 1],
        });
    }

    peaks.sort_by(|a, b| {
        b.magnitude
            .partial_cmp(&a.magnitude)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| {
                a.frequency
                    .partial_cmp(&b.frequency)
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
    });
    peaks.truncate(MAX_PEAKS);
    peaks
}

fn interpolate(left: f32, middle: f32, right: f32, bin: usize) -> (f32, f32) {
    let denom = left - 2.0 * middle + right;
    if denom == 0.0 {
        return (bin as f32, middle);
    }
    let delta = 0.5 * ((left - right) / denom);
    let result_bin = bin as f32 + delta;
    let result_val = middle - 0.25 * (left - right) * delta;
    (result_bin, result_val)
}

fn spectral_whitening(spectrum: &[f32], peaks: &[Peak]) -> Vec<f32> {
    if peaks.is_empty() {
        return Vec::new();
    }

    let max_freq = MAX_FREQUENCY * 1.2;
    let spectral_range = SAMPLE_RATE / 2.0;
    let resolution = 100.0f32;
    let spec_size = spectrum.len();

    let mut magnitudes_db = Vec::with_capacity(peaks.len());
    let mut max_amp = f32::NEG_INFINITY;
    for peak in peaks {
        let db = 2.0 * lin2db(peak.magnitude);
        if peak.frequency <= max_freq {
            max_amp = max_amp.max(db);
        }
        magnitudes_db.push(db);
    }

    let mut x_points = Vec::new();
    let mut y_points = Vec::new();
    let mut freq = 0.0f32;
    while freq <= max_freq && freq <= spectral_range {
        let begin = freq - 50.0f32.max(freq * 0.34);
        let end = freq + 50.0f32.max(freq * 0.58);
        let mut b = (begin / spectral_range * (spec_size as f32 - 1.0) + 0.5) as i32;
        let mut e = (end / spectral_range * (spec_size as f32 - 1.0) + 0.5) as i32;
        b = b.clamp(0, spec_size as i32 - 1);
        e = e.max(b + 1).min(spec_size as i32);
        let center = b as f32 / 2.0 + e as f32 / 2.0;
        let half = e as f32 - center;

        let mut weight_sum = 0.0f32;
        let mut weighted = 0.0f32;
        for bin in b..e {
            let mut weight = 1.0 - (bin as f32 - center).abs() / half;
            weight *= weight;
            weight *= weight;
            let energy = spectrum[bin as usize] * spectrum[bin as usize];
            weight *= energy;
            weighted += energy * weight;
            weight_sum += weight;
        }
        if weight_sum != 0.0 {
            weighted /= weight_sum;
        }
        x_points.push(freq);
        y_points.push(weighted);
        freq += resolution;
    }

    if y_points.len() >= 2 {
        let last = y_points.len() - 1;
        y_points[last] = y_points[last - 1];
    }
    for value in &mut y_points {
        *value = 2.0 * lin2db(value.sqrt());
    }

    let mut white = vec![0.0f32; peaks.len()];
    for (index, peak) in peaks.iter().enumerate() {
        let amp = magnitudes_db[index];
        if peak.frequency > max_freq - resolution {
            white[index] = amp;
            continue;
        }
        let envelope = break_point(&x_points, &y_points, peak.frequency);
        if amp < max_amp - 40.0 {
            white[index] = (max_amp - 40.0 - amp) / 2.0;
        }
        if amp > envelope {
            white[index] = 0.0;
        } else if amp > envelope - 30.0 {
            white[index] = amp - envelope;
        } else {
            white[index] = -200.0;
        }
        white[index] -= 20.0 * peak.frequency / 4000.0;
    }

    for value in &mut white {
        *value = db2lin(*value / 2.0);
    }
    white
}

fn break_point(x_points: &[f32], y_points: &[f32], x: f32) -> f32 {
    if x_points.len() < 2 {
        return y_points.first().copied().unwrap_or(DB_SILENCE_CUTOFF);
    }
    if x <= x_points[0] {
        return y_points[0];
    }
    if x >= *x_points.last().unwrap() {
        return *y_points.last().unwrap();
    }
    let mut j = 0;
    while x > x_points[j + 1] {
        j += 1;
    }
    let slope = (y_points[j + 1] - y_points[j]) / (x_points[j + 1] - x_points[j]);
    (x - x_points[j]) * slope + y_points[j]
}

fn lin2db(value: f32) -> f32 {
    if value < SILENCE_CUTOFF {
        DB_SILENCE_CUTOFF
    } else {
        10.0 * value.log10()
    }
}

fn db2lin(value: f32) -> f32 {
    10.0f32.powf(value / 10.0)
}

fn harmonic_peaks(n_harmonics: i32) -> Vec<HarmonicPeak> {
    let mut peaks: Vec<HarmonicPeak> = Vec::new();
    for i in 0..=n_harmonics {
        let mut semitone = 12.0 * ((i + 1) as f64).log2();
        let octweight = 1.0f64.max((semitone / 12.0) * 0.5);
        while semitone >= 12.0 - 0.00001 {
            semitone -= 12.0;
        }
        let semitone = semitone as f32;
        let weight = (1.0 / octweight) as f32;
        if let Some(existing) = peaks
            .iter_mut()
            .find(|peak| peak.semitone > semitone - 0.00001 && peak.semitone < semitone + 0.00001)
        {
            existing.strength += weight;
        } else {
            peaks.push(HarmonicPeak {
                semitone,
                strength: weight,
            });
        }
    }
    peaks
}

fn hpcp(peaks: &[Peak], magnitudes: &[f32], harmonics: &[HarmonicPeak]) -> [f32; HPCP_SIZE] {
    let mut hpcp = [0.0f32; HPCP_SIZE];
    for (peak, magnitude) in peaks.iter().zip(magnitudes) {
        if peak.frequency < MIN_FREQUENCY || peak.frequency > MAX_FREQUENCY {
            continue;
        }
        for harmonic in harmonics {
            let fundamental = peak.frequency * 2.0f32.powf(-harmonic.semitone / 12.0);
            add_weighted(fundamental, *magnitude, harmonic.strength, &mut hpcp);
        }
    }
    hpcp
}

fn add_weighted(freq: f32, magnitude: f32, harmonic_weight: f32, hpcp: &mut [f32; HPCP_SIZE]) {
    if freq <= 0.0 {
        return;
    }
    let size = HPCP_SIZE as f32;
    let resolution = size / 12.0;
    let bin = (freq / TUNING_FREQUENCY).log2() * size;
    let left = (bin - resolution * HPCP_WINDOW / 2.0).ceil() as i32;
    let right = (bin + resolution * HPCP_WINDOW / 2.0).floor() as i32;
    let harmonic = harmonic_weight * harmonic_weight;
    let power = magnitude * magnitude;
    for index in left..=right {
        let distance = (bin - index as f32).abs() / resolution;
        let weight = (std::f32::consts::PI * distance / HPCP_WINDOW).cos();
        let mut wrapped = index % HPCP_SIZE as i32;
        if wrapped < 0 {
            wrapped += HPCP_SIZE as i32;
        }
        hpcp[wrapped as usize] += weight * power * harmonic;
    }
}

fn normalize_peak(values: &mut [f32]) {
    let max = values.iter().copied().fold(0.0f32, f32::max);
    if max != 0.0 {
        for value in values {
            *value /= max;
        }
    }
}

fn estimate(pcp: &[f32; HPCP_SIZE]) -> Result<(String, String), String> {
    let (mean_major, std_major) = profile_stats(&BGATE_MAJOR);
    let (mean_minor, std_minor) = profile_stats(&BGATE_MINOR);
    let mean_pcp = pcp.iter().sum::<f32>() / HPCP_SIZE as f32;
    let std_pcp = pcp
        .iter()
        .map(|value| (value - mean_pcp) * (value - mean_pcp))
        .sum::<f32>()
        .sqrt();

    let mut best_major = -1.0f32;
    let mut major_index = -1i32;
    let mut best_minor = -1.0f32;
    let mut minor_index = -1i32;

    for shift in 0..HPCP_SIZE {
        let corr_major = correlation(
            pcp,
            mean_pcp,
            std_pcp,
            &BGATE_MAJOR,
            mean_major,
            std_major,
            shift,
        );
        if corr_major > best_major {
            best_major = corr_major;
            major_index = shift as i32;
        }
        let corr_minor = correlation(
            pcp,
            mean_pcp,
            std_pcp,
            &BGATE_MINOR,
            mean_minor,
            std_minor,
            shift,
        );
        if corr_minor > best_minor {
            best_minor = corr_minor;
            minor_index = shift as i32;
        }
    }

    let (index, scale) = if best_major > best_minor {
        (major_index, "major")
    } else if best_minor >= best_major {
        (minor_index, "minor")
    } else {
        return Err("could not estimate a key".to_string());
    };

    if index < 0 {
        return Err("could not estimate a key".to_string());
    }
    Ok((KEYS[index as usize].to_string(), scale.to_string()))
}

fn profile_stats(profile: &[f32; 12]) -> (f32, f32) {
    let mean = profile.iter().sum::<f32>() / 12.0;
    let std = profile
        .iter()
        .map(|value| (value - mean) * (value - mean))
        .sum::<f32>()
        .sqrt();
    (mean, std)
}

fn correlation(
    pcp: &[f32; HPCP_SIZE],
    mean_pcp: f32,
    std_pcp: f32,
    profile: &[f32; 12],
    mean_profile: f32,
    std_profile: f32,
    shift: usize,
) -> f32 {
    if std_pcp == 0.0 || std_profile == 0.0 {
        return 0.0;
    }
    let mut sum = 0.0f32;
    for i in 0..HPCP_SIZE {
        let mut index = i as i32 - shift as i32;
        if index < 0 {
            index += HPCP_SIZE as i32;
        }
        sum += (pcp[i] - mean_pcp) * (profile[index as usize] - mean_profile);
    }
    sum / (std_pcp * std_profile)
}
