#!/usr/bin/env python3
"""
Melody Generator - Creates random melodies based on key, scale, and tempo.
Exports quantized MIDI files compatible with Ardour.
"""

import argparse
import json
import math
import random
import re
import os
import sys
from typing import List, Dict, Tuple

try:
    import mido
    from mido import Message, MidiFile, MidiTrack
except ImportError:
    print("Error: mido library is required. Install it with: pip install mido")
    exit(1)


# Scale intervals (semitones from root)
SCALES: Dict[str, List[int]] = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'locrian': [0, 1, 3, 5, 6, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
}

# Note mapping: flats to sharps
NOTE_MAPPING: Dict[str, str] = {
    'Cb': 'B',
    'Db': 'C#',
    'Eb': 'D#',
    'Fb': 'E',
    'Gb': 'F#',
    'Ab': 'G#',
    'Bb': 'A#',
    'C': 'C',
    'D': 'D',
    'E': 'E',
    'F': 'F',
    'G': 'G',
    'A': 'A',
    'B': 'B',
}

# MIDI note numbers for C0-B0 (all sharps, no flats)
MIDI_NOTES: Dict[str, int] = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
}


def normalize_note(note: str) -> str:
    """
    Convert flat notes to their sharp equivalents.
    Examples: Bb -> A#, Eb -> D#, Ab -> G#
    """
    note = note.capitalize()
    if note in NOTE_MAPPING:
        return NOTE_MAPPING[note]
    return note


def parse_note_with_octave(note_str: str) -> int:
    """
    Parse a note string with octave (e.g., "C3", "A#2", "Bb4") and convert to MIDI note number.
    
    Args:
        note_str: Note string in format like "C3", "A#2", "Bb4", etc.
    
    Returns:
        MIDI note number (0-127)
    
    Raises:
        ValueError: If note format is invalid
    """
    note_str = note_str.strip()
    if not note_str:
        raise ValueError(f"Empty note string")
    
    # Match note name (with optional sharp/flat) and octave number
    # Pattern: (note name)(optional # or b)(octave number)
    match = re.match(r'^([A-G])([#b]?)(-?\d+)$', note_str, re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid note format: {note_str}. Expected format: C3, A#2, Bb4, etc.")
    
    note_name = match.group(1).upper()
    accidental = match.group(2)
    octave = int(match.group(3))
    
    # Combine note name and accidental
    if accidental:
        full_note = note_name + accidental.upper()
    else:
        full_note = note_name
    
    # Normalize to sharps
    normalized = normalize_note(full_note)
    
    if normalized not in MIDI_NOTES:
        raise ValueError(f"Invalid note: {full_note} (normalized to {normalized})")
    
    # Calculate MIDI note number
    # MIDI note = (octave + 1) * 12 + note_offset
    # C0 = 12, C1 = 24, C2 = 36, C3 = 48, C4 = 60, etc.
    note_offset = MIDI_NOTES[normalized]
    midi_note = (octave + 1) * 12 + note_offset
    
    if not (0 <= midi_note <= 127):
        raise ValueError(f"MIDI note {midi_note} out of range (0-127) for {note_str}")
    
    return midi_note


def load_notes_from_file(filepath: str) -> List[int]:
    """
    Load MIDI note numbers from a text file.
    Each line should contain a note in format like "C3", "A#2", "Bb4", etc.
    Empty lines are ignored.
    
    Args:
        filepath: Path to the notes file
    
    Returns:
        List of MIDI note numbers
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If any note format is invalid
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Notes file not found: {filepath}")
    
    notes = []
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            try:
                midi_note = parse_note_with_octave(line)
                notes.append(midi_note)
            except ValueError as e:
                raise ValueError(f"Error on line {line_num} of {filepath}: {e}")
    
    if not notes:
        raise ValueError(f"No valid notes found in {filepath}")
    
    return notes


def get_scale_notes(key: str, scale_name: str) -> List[int]:
    """
    Get MIDI note numbers for all notes in the specified key and scale.
    Returns notes in a 2-octave range (C4 to C6 typically).
    """
    # Normalize key (flats to sharps)
    normalized_key = normalize_note(key)
    
    if normalized_key not in MIDI_NOTES:
        raise ValueError(f"Invalid key: {key} (normalized to {normalized_key})")
    
    if scale_name.lower() not in SCALES:
        raise ValueError(f"Invalid scale: {scale_name}. Available scales: {', '.join(SCALES.keys())}")
    
    # Get root MIDI note (C4 = 60)
    root_midi = MIDI_NOTES[normalized_key] + 60
    
    # Get scale intervals
    intervals = SCALES[scale_name.lower()]
    
    # Generate notes for 2 octaves
    scale_notes = []
    for octave in range(2):  # 2 octaves
        for interval in intervals:
            note_midi = root_midi + interval + (octave * 12)
            if 0 <= note_midi <= 127:  # Valid MIDI range
                scale_notes.append(note_midi)
    
    return sorted(scale_notes)


def generate_melody(
    scale_notes: List[int],
    num_notes: int = 16,
    note_lengths: List[int] = None,
    rhythm_pattern: str = 'mixed',
    ticks_per_beat: int = 480
) -> List[Tuple[int, int]]:
    """
    Generate a random melody from scale notes.
    Returns list of (note, duration_in_ticks) tuples.
    
    Args:
        scale_notes: List of MIDI note numbers in the scale
        num_notes: Number of notes in the melody
        note_lengths: List of durations in ticks
        rhythm_pattern: 'even', 'mixed', or 'varied'
        ticks_per_beat: Ticks per beat for quantization (default: 480)
    """
    if note_lengths is None:
        # Calculate note lengths based on ticks_per_beat
        # 16th note = ticks_per_beat / 4
        # 8th note = ticks_per_beat / 2
        # Quarter note = ticks_per_beat
        # Dotted quarter = ticks_per_beat * 1.5
        # Half note = ticks_per_beat * 2
        sixteenth = ticks_per_beat // 4
        eighth = ticks_per_beat // 2
        quarter = ticks_per_beat
        dotted_quarter = int(ticks_per_beat * 1.5)
        half = ticks_per_beat * 2
        dotted_eighth = int(ticks_per_beat * 0.75)
        
        if rhythm_pattern == 'even':
            note_lengths = [quarter]  # Quarter notes only
        elif rhythm_pattern == 'mixed':
            note_lengths = [eighth, quarter, dotted_quarter]  # 8th, quarter, dotted quarter
        else:  # varied
            note_lengths = [sixteenth, eighth, dotted_eighth, quarter, dotted_quarter, half]
    
    melody = []
    for _ in range(num_notes):
        note = random.choice(scale_notes)
        duration = random.choice(note_lengths)
        melody.append((note, duration))
    
    return melody


# Sixteenth, eighth, quarter, half, whole.
DURATION_SIXTEENTHS = (1, 2, 4, 8, 16)
MAJOR_FAMILY = {"major", "mixolydian"}


def genres_json_path() -> str:
    """genres.json sits beside the installed binary, or beside this script."""
    directories = []
    if getattr(sys, "frozen", False):
        directories.append(os.path.dirname(os.path.abspath(sys.executable)))
    directories.append(os.path.dirname(os.path.abspath(__file__)))
    for directory in directories:
        path = os.path.join(directory, "genres.json")
        if os.path.isfile(path):
            return path
    looked = ", ".join(directories) if directories else "(none)"
    raise FileNotFoundError(f"Could not find genres.json. Looked in: {looked}")


def load_genre(name: str) -> dict:
    """Find a profile by id or display name."""
    path = genres_json_path()
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    wanted = name.strip().lower()
    profiles = data.get("profiles", [])
    for profile in profiles:
        profile_id = str(profile.get("id", "")).lower()
        display = str(profile.get("displayName", "")).lower()
        if wanted == profile_id or wanted == display:
            return profile
    known = ", ".join(str(profile.get("id", "")) for profile in profiles)
    raise ValueError(f"Unknown genre: {name}. Known ids: {known}")


def resolve_scale(key_scale: str, suggested: str) -> str:
    """Honor the scale that came with the key.

    A minor key stays natural minor. A genre may still color a major key
    with mixolydian. Any other requested scale is kept as given.
    """
    key_scale = (key_scale or "").lower()
    suggested = (suggested or "").lower()
    if key_scale == "minor":
        return "minor"
    if key_scale == "major" and suggested in MAJOR_FAMILY and suggested in SCALES:
        return suggested
    if key_scale in SCALES:
        return key_scale
    if suggested in SCALES:
        return suggested
    return key_scale


def scale_notes_for_range(key: str, scale_name: str, octave_spread: int) -> List[int]:
    """Scale tones spanning octave_spread octaves, centered on octave 4."""
    normalized_key = normalize_note(key)
    if normalized_key not in MIDI_NOTES:
        raise ValueError(f"Invalid key: {key} (normalized to {normalized_key})")
    if scale_name.lower() not in SCALES:
        raise ValueError(f"Invalid scale: {scale_name}. Available scales: {', '.join(SCALES.keys())}")

    root_midi = MIDI_NOTES[normalized_key] + 60
    spread = max(1, int(octave_spread))
    start = -int((spread - 1) / 2)
    intervals = SCALES[scale_name.lower()]
    notes = []
    for octave in range(start, start + spread):
        for interval in intervals:
            note_midi = root_midi + interval + (octave * 12)
            if 0 <= note_midi <= 127:
                notes.append(note_midi)
    return sorted(set(notes))


def weighted_index(weights: List[float]) -> int:
    total = sum(max(weight, 0.0) for weight in weights)
    if total <= 0:
        return random.randrange(len(weights))
    pick = random.random() * total
    running = 0.0
    for index, weight in enumerate(weights):
        running += max(weight, 0.0)
        if pick <= running:
            return index
    return len(weights) - 1


def generate_genre_melody(
    key: str,
    key_scale: str,
    profile: dict,
    num_notes: int = 16,
    num_bars: int = None,
    ticks_per_beat: int = 480,
) -> Tuple[str, List[Tuple[int, int, int, int]]]:
    """
    Build a melody from a genre profile.

    With num_bars, the melody fills that many 4/4 bars and notes are clipped
    to the final bar line. Otherwise it stops after num_notes notes.

    Returns the resolved scale name and events of
    (start_tick, note, duration_ticks, velocity).
    """
    scale_name = resolve_scale(key_scale, str(profile.get("suggestedScaleId", key_scale)))
    spread = int(profile.get("defaultOctaveSpread") or 2)
    scale_notes = scale_notes_for_range(key, scale_name, spread)
    if not scale_notes:
        raise ValueError(f"No MIDI notes for {key} {scale_name}")

    pitch_dist = list(profile.get("pitchClassDistribution") or [])
    onset = list(profile.get("onsetProb") or [])
    durations = list(profile.get("durationDist") or [])
    accents = list(profile.get("beatAccent") or [])
    if len(pitch_dist) != 12:
        raise ValueError("pitchClassDistribution must have 12 values")
    if len(onset) != 16:
        raise ValueError("onsetProb must have 16 values")
    if len(durations) != 5:
        raise ValueError("durationDist must have 5 values")
    if len(accents) != 4:
        raise ValueError("beatAccent must have 4 values")

    stepwise = float(profile.get("stepwiseBias") or 0.0)
    contour_amp = float(profile.get("contourAmp") or 0.0)
    contour_rate = float(profile.get("contourRate") or 0.0)
    rest_prob = min(1.0, max(0.0, float(profile.get("restProb") or 0.0)))
    swing = float(profile.get("swing") or 0.0)
    velocity_base = float(profile.get("velocityBase") or 0.7)
    accent_mean = sum(accents) / len(accents) or 1.0

    sixteenth = ticks_per_beat // 4
    eighth = ticks_per_beat // 2
    root = MIDI_NOTES[normalize_note(key)] + 60
    center = root + ((spread - 1) / 2.0) * 12
    events: List[Tuple[int, int, int, int]] = []
    previous_index = None
    pos = 0
    limit = max(num_notes * 64, 64)
    note_index = 0
    total_slots = num_bars * 16 if num_bars else None

    def place(at_pos: int, room: int = None) -> int:
        nonlocal previous_index, note_index
        preferred = center + contour_amp * 12.0 * math.sin(
            2.0 * math.pi * contour_rate * note_index
        )
        if previous_index is not None and random.random() < stepwise:
            choices = []
            if previous_index > 0:
                choices.append(previous_index - 1)
            if previous_index + 1 < len(scale_notes):
                choices.append(previous_index + 1)
            if not choices:
                choices = [previous_index]
            nearest = min(abs(scale_notes[index] - preferred) for index in choices)
            chosen = random.choice([
                index for index in choices
                if abs(scale_notes[index] - preferred) == nearest
            ])
        else:
            weights = []
            for note in scale_notes:
                distance = abs(note - preferred)
                weights.append(max(pitch_dist[note % 12], 0.0) * math.exp(-distance / 6.0))
            chosen = weighted_index(weights)
        previous_index = chosen
        note = scale_notes[chosen]
        beat = (at_pos // 4) % 4
        velocity = int(round(127.0 * velocity_base * (accents[beat] / accent_mean)))
        velocity = max(1, min(127, velocity))
        dur_steps = DURATION_SIXTEENTHS[weighted_index(durations)]
        if room is not None:
            dur_steps = min(dur_steps, room)
        if dur_steps < 1:
            return 0
        delay = int(round(swing * eighth)) if at_pos % 4 == 2 else 0
        start = at_pos * sixteenth + delay
        duration_ticks = dur_steps * sixteenth
        if room is not None:
            bar_end = (at_pos + room) * sixteenth
            if start >= bar_end:
                return 0
            duration_ticks = min(duration_ticks, bar_end - start)
        if duration_ticks < 1:
            return 0
        events.append((start, note, duration_ticks, velocity))
        note_index += 1
        return dur_steps

    if total_slots is not None:
        while pos < total_slots:
            if random.random() < float(onset[pos % 16]):
                if random.random() < rest_prob:
                    pos += 1
                    continue
                placed = place(pos, total_slots - pos)
                pos += placed if placed > 0 else 1
            else:
                pos += 1
    else:
        while note_index < num_notes and pos < limit:
            if random.random() < float(onset[pos % 16]):
                if random.random() < rest_prob:
                    pos += 1
                    continue
                pos += place(pos)
            else:
                pos += 1

        while note_index < num_notes:
            pos += place(pos)

    return scale_name, events


def write_timed_midi(
    events: List[Tuple[int, int, int, int]],
    tempo: int,
    output_file: str,
    time_signature: Tuple[int, int] = (4, 4),
    end_tick: int = None,
) -> None:
    """Write notes placed on an absolute tick grid, including rests and swing."""
    ticks_per_beat = 480
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo), time=0))
    track.append(mido.MetaMessage(
        "time_signature",
        numerator=time_signature[0],
        denominator=time_signature[1],
        clocks_per_click=24,
        notated_32nd_notes_per_beat=8,
        time=0,
    ))
    track.append(mido.MetaMessage("key_signature", key="C", time=0))

    timed = []
    for start, note, duration, velocity in events:
        timed.append((start, 1, Message("note_on", channel=0, note=note, velocity=velocity, time=0)))
        timed.append((start + duration, 0, Message("note_off", channel=0, note=note, velocity=0, time=0)))
    timed.sort(key=lambda item: (item[0], item[1]))

    last = 0
    for tick, _, message in timed:
        message.time = max(0, tick - last)
        last = tick
        track.append(message)

    if end_tick is not None and end_tick > last:
        track.append(mido.MetaMessage("end_of_track", time=end_tick - last))

    mid.save(output_file)
    print(f"Melody saved to {output_file}")


def create_quantized_midi(
    melody: List[Tuple[int, int]],
    tempo: int,
    output_file: str,
    time_signature: Tuple[int, int] = (4, 4)
) -> None:
    """
    Create a quantized MIDI file from the melody.
    All notes are aligned to a grid for perfect quantization.
    
    Args:
        melody: List of (note, duration_in_ticks) tuples
        tempo: Tempo in BPM
        output_file: Output MIDI filename
        time_signature: (numerator, denominator)
    """
    # Calculate ticks per beat (quantization grid)
    # Using 480 ticks per quarter note for standard quantization
    ticks_per_beat = 480
    
    # Create MIDI file
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    tempo_msg = mido.bpm2tempo(tempo)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo_msg))
    
    # Set time signature
    track.append(mido.MetaMessage('time_signature', 
                                   numerator=time_signature[0],
                                   denominator=time_signature[1],
                                   clocks_per_click=24,
                                   notated_32nd_notes_per_beat=8))
    
    # Set key signature (will be overridden per key in melody)
    track.append(mido.MetaMessage('key_signature', key='C'))
    
    # Quantization grid: smallest division is 16th note
    sixteenth_note = ticks_per_beat // 4
    
    for note, duration in melody:
        # Quantize duration to nearest 16th note grid
        # Ensure duration is a multiple of the smallest grid
        quantized_duration = round(duration / sixteenth_note) * sixteenth_note
        
        # Ensure minimum duration of 16th note
        if quantized_duration < sixteenth_note:
            quantized_duration = sixteenth_note
        
        # Note on (quantized to grid)
        # For first note: time=0 (start immediately)
        # For subsequent notes: time=0 (start immediately after previous note_off)
        track.append(Message('note_on', channel=0, note=note, velocity=80, time=0))
        
        # Note off after quantized duration
        # Time is ticks since the last message (note_on)
        track.append(Message('note_off', channel=0, note=note, velocity=0, time=quantized_duration))
    
    # Save MIDI file
    mid.save(output_file)
    print(f"Melody saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate random melodies from a key/scale or from a notes file. '
                    'Outputs quantized MIDI files compatible with Ardour.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using key and scale:
  python melody_generator.py --key C --scale major --tempo 120
  python melody_generator.py --key Bb --scale minor --tempo 90 --notes 32
  python melody_generator.py --key Eb --scale pentatonic --tempo 140 --output my_melody.mid
  
  # Using notes file:
  python melody_generator.py --notes-file midi_notes.txt --tempo 120
  python melody_generator.py --file midi_notes.txt --tempo 90 --notes 32
        """
    )
    
    # Create mutually exclusive group for key/scale vs notes file
    note_source_group = parser.add_mutually_exclusive_group(required=True)
    
    note_source_group.add_argument(
        '--key', '-k',
        type=str,
        help='Key signature (e.g., C, D, Eb, F#, Bb). Flats will be converted to sharps. '
             'Required if not using --notes-file.'
    )
    
    note_source_group.add_argument(
        '--notes-file', '--file', '-f',
        type=str,
        dest='notes_file',
        help='Path to a text file containing notes (one per line, e.g., "C3", "A#2", "Bb4"). '
             'Required if not using --key and --scale.'
    )
    
    parser.add_argument(
        '--scale', '-s',
        type=str,
        help='Scale type (major, minor, dorian, mixolydian, lydian, phrygian, '
             'locrian, pentatonic, pentatonic_minor, blues, harmonic_minor, melodic_minor). '
             'Required if using --key.'
    )
    
    parser.add_argument(
        '--tempo', '-t',
        type=int,
        required=True,
        help='Tempo in BPM (beats per minute)'
    )
    
    parser.add_argument(
        '--genre', '-g',
        type=str,
        default=None,
        help='Genre id or display name from genres.json. The genre shapes rhythm, '
             'pitch choice, range, and velocity. A minor key stays natural minor. '
             'A major key uses mixolydian when the genre suggests it.'
    )

    parser.add_argument(
        '--bars', '-b',
        type=int,
        default=None,
        help='Length of a genre melody in 4/4 bars. Notes are placed on the '
             '16th-note grid and clipped to the final bar line.'
    )

    parser.add_argument(
        '--notes', '-n',
        type=int,
        default=16,
        help='Number of notes in the melody (default: 16). Ignored for a genre '
             'melody when --bars is set.'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='melody.mid',
        help='Output MIDI filename (default: melody.mid)'
    )
    
    parser.add_argument(
        '--rhythm',
        type=str,
        choices=['even', 'mixed', 'varied'],
        default='mixed',
        help='Rhythm pattern: even (only quarter notes), mixed (8th/quarter/dotted), '
             'varied (more rhythmic variety) (default: mixed)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducible melodies'
    )
    
    args = parser.parse_args()
    
    # Validate arguments: if key is provided, scale must also be provided
    if args.key and not args.scale:
        parser.error("--scale is required when using --key")
    if args.scale and not args.key:
        parser.error("--key is required when using --scale")
    if args.genre and args.notes_file:
        parser.error("--genre is used with --key and --scale, not --notes-file")
    if args.bars is not None and args.bars < 1:
        parser.error("--bars must be at least 1")
    if args.notes < 1:
        parser.error("--notes must be at least 1")
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Get notes from either key/scale or notes file
    try:
        if args.notes_file:
            # Load notes from file
            scale_notes = load_notes_from_file(args.notes_file)
            print(f"Loaded {len(scale_notes)} notes from {args.notes_file}")
        else:
            # Get notes from key and scale
            normalized_key = normalize_note(args.key)
            if normalized_key != args.key:
                print(f"Note: Key {args.key} normalized to {normalized_key} (flats converted to sharps)")

            if not args.genre:
                scale_notes = get_scale_notes(args.key, args.scale)
                print(f"Generated scale: {normalized_key} {args.scale}")
                print(f"Scale contains {len(scale_notes)} notes")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        return 1
    
    # Generate melody (using 480 ticks per beat for quantization)
    ticks_per_beat = 480
    if args.genre:
        if args.bars:
            print(f"Generating melody for {args.bars} bars...")
        else:
            print(f"Generating melody with {args.notes} notes...")
        try:
            profile = load_genre(args.genre)
            scale_name, timed = generate_genre_melody(
                args.key,
                args.scale,
                profile,
                num_notes=args.notes,
                num_bars=args.bars,
                ticks_per_beat=ticks_per_beat,
            )
        except (ValueError, FileNotFoundError, OSError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Genre: {profile.get('displayName')} ({profile.get('id')})")
        print(f"Resolved scale: {scale_name}")
        end_tick = args.bars * 4 * ticks_per_beat if args.bars else None
        write_timed_midi(timed, args.tempo, args.output, end_tick=end_tick)
    else:
        print(f"Generating melody with {args.notes} notes...")
        melody = generate_melody(
            scale_notes,
            num_notes=args.notes,
            rhythm_pattern=args.rhythm,
            ticks_per_beat=ticks_per_beat
        )
        create_quantized_midi(melody, args.tempo, args.output)
    
    #print("\nMelody generation complete!")
    #print(f"You can now import '{args.output}' into Ardour.")
    #print("All notes are quantized to a 16th note grid.")
    
    return 0

if __name__ == '__main__':
    main()


