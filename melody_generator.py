#!/usr/bin/env python3
"""
Melody Generator - Writes an MMA groove for a key, scale, and genre.
Exports one MIDI file for an Ardour synth track.
"""

import argparse
import json
import random
import os
import subprocess
import sys
import tempfile
from typing import List, Tuple


def resource_directories() -> List[str]:
    """resources/ next to this script, then the script directory, then a frozen binary."""
    root = os.path.dirname(os.path.abspath(__file__))
    directories = [os.path.join(root, "resources"), root]
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        directories.extend([os.path.join(exe_dir, "resources"), exe_dir])
    return directories


def resource_file(filename: str) -> str:
    """Find a data file shipped beside this script or the installed binary."""
    directories = resource_directories()
    for directory in directories:
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            return path
    looked = ", ".join(directories) if directories else "(none)"
    raise FileNotFoundError(f"Could not find {filename}. Looked in: {looked}")


def genres_json_path() -> str:
    """genres.json sits in resources/, beside the script, or beside the installed binary."""
    return resource_file("genres.json")


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


# MMA KeySig names. A few menu spellings are not in MMA's tables, so those
# point at the enharmonic name MMA accepts. The integer is the signature
# (positive sharps, negative flats) and chooses chord spelling.
MAJOR_KEYSIG = {
    "C": ("C", 0), "C#": ("C#", 7), "Db": ("Db", -5), "D": ("D", 2),
    "D#": ("Eb", -3), "Eb": ("Eb", -3), "E": ("E", 4), "F": ("F", -1),
    "F#": ("F#", 6), "Gb": ("Gb", -6), "G": ("G", 1), "G#": ("Ab", -4),
    "Ab": ("Ab", -4), "A": ("A", 3), "A#": ("Bb", -2), "Bb": ("Bb", -2),
    "B": ("B", 5),
}
MINOR_KEYSIG = {
    "A": ("A", 0), "A#": ("A#", 7), "Bb": ("Bb", -5), "B": ("B", 2),
    "C": ("C", -3), "C#": ("C#", 4), "Db": ("C#", 4), "D": ("D", -1),
    "D#": ("D#", 6), "Eb": ("Eb", -6), "E": ("E", 1), "F": ("F", -4),
    "F#": ("F#", 3), "Gb": ("F#", 3), "G": ("G", -2), "G#": ("G#", 5),
    "Ab": ("Ab", -7),
}
PITCH_CLASS = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10,
    "B": 11,
}
SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
# Triad intervals from newchord.py. Each run picks one loop.
MAJOR_PROGRESSIONS = (
    ([0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]),  # I V vi IV
    ([0, 4, 7], [9, 12, 16], [5, 9, 12], [7, 11, 14]),  # I vi IV V
    ([0, 4, 7], [5, 9, 12], [7, 11, 14], [0, 4, 7]),  # I IV V I
    ([9, 12, 16], [5, 9, 12], [0, 4, 7], [7, 11, 14]),  # vi IV I V
)
MINOR_PROGRESSIONS = (
    ([0, 3, 7], [8, 12, 15], [3, 7, 10], [10, 14, 17]),  # i VI III VII
    ([0, 3, 7], [5, 8, 12], [7, 10, 14], [0, 3, 7]),  # i iv v i
    ([0, 3, 7], [8, 12, 15], [5, 8, 12], [7, 10, 14]),  # i VI iv v
    ([0, 3, 7], [10, 14, 17], [8, 12, 15], [10, 14, 17]),  # i VII VI VII
)
MELODY_CENTER = 72
MELODY_LOW = 60
MELODY_HIGH = 84


def load_mma_genre(name: str) -> Tuple[dict, dict]:
    """Profile from genres.json plus its MMA groove entry."""
    profile = load_genre(name)
    path = resource_file("mma_genres.json")
    with open(path, "r", encoding="utf-8") as handle:
        mapping = json.load(handle)
    entry = mapping.get(profile.get("id"))
    if not isinstance(entry, dict) or not entry.get("groove"):
        raise ValueError(f"No MMA groove for genre: {profile.get('id')}")
    return profile, entry


def mma_script_path() -> str:
    """mma.py next to this repo, or under MMA_HOME, or beside a frozen binary."""
    root = os.path.dirname(os.path.abspath(__file__))
    candidates = [os.path.join(root, "mma", "mma.py")]
    home = os.environ.get("MMA_HOME")
    if home:
        candidates.append(os.path.join(home, "mma.py"))
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        candidates.append(os.path.join(exe_dir, "mma", "mma.py"))
    for path in candidates:
        if os.path.isfile(path):
            return path
    looked = ", ".join(candidates)
    raise FileNotFoundError(f"Could not find mma.py. Looked in: {looked}")


def mma_key_signature(key: str, scale: str) -> Tuple[str, str, int]:
    """Return the KeySig line, the spelled tonic, and the signature count."""
    scale_name = (scale or "").lower()
    table = MINOR_KEYSIG if scale_name == "minor" else MAJOR_KEYSIG
    chosen = table.get(key.strip())
    if not chosen:
        kind = "minor" if scale_name == "minor" else "major"
        raise ValueError(f"Invalid {kind} key for MMA: {key}")
    tonic, signature = chosen
    if scale_name == "minor":
        return f"KeySig {tonic} minor", tonic, signature
    return f"KeySig {tonic}", tonic, signature


def chord_symbol(tonic_pc: int, intervals: List[int], use_flats: bool) -> str:
    """Spell one triad. A minor third becomes an MMA 'm' suffix."""
    root = (tonic_pc + intervals[0]) % 12
    third = (tonic_pc + intervals[1]) % 12
    if use_flats and root == 11:
        name = "Cb"
    else:
        name = (FLAT_NAMES if use_flats else SHARP_NAMES)[root]
    if (third - root) % 12 == 3:
        name += "m"
    return name


def chord_loop(key: str, scale: str, bars: int) -> Tuple[str, List[str]]:
    """One chord per bar, tiled from a diatonic loop chosen for this run."""
    keysig, tonic, signature = mma_key_signature(key, scale)
    progressions = MINOR_PROGRESSIONS if (scale or "").lower() == "minor" else MAJOR_PROGRESSIONS
    progression = random.choice(progressions)
    tonic_pc = PITCH_CLASS[tonic]
    use_flats = signature < 0
    chords = [
        chord_symbol(tonic_pc, progression[index % len(progression)], use_flats)
        for index in range(bars)
    ]
    return keysig, chords


def write_mma_chart(path: str, tempo: int, key: str, scale: str, groove: str, bars: int) -> str:
    """Write a groove-and-chords chart. Returns the KeySig line."""
    keysig, chords = chord_loop(key, scale, bars)
    lines = [f"Tempo {int(tempo)}", keysig, f"Groove {groove}", ""]
    lines.extend(f"{index} {chord}" for index, chord in enumerate(chords, start=1))
    lines.append("")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return keysig


def mma_python() -> str:
    """The interpreter that runs mma.py. A frozen binary is not a Python interpreter."""
    if getattr(sys, "frozen", False):
        return "python3"
    return sys.executable


def run_mma(chart_path: str, output_path: str) -> None:
    """One MMA process per chart. The program keeps global state, so it is not re-entered."""
    completed = subprocess.run(
        [mma_python(), mma_script_path(), "-f", output_path, chart_path],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not os.path.isfile(output_path):
        detail = (completed.stderr or completed.stdout or "").strip()
        raise OSError(detail or f"MMA exited {completed.returncode}")


def _read_varlen(data: bytes, pos: int) -> Tuple[int, int]:
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos


def _write_varlen(value: int) -> bytes:
    chunks = [value & 0x7F]
    value >>= 7
    while value:
        chunks.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(chunks))


def _fold_into_melody_range(pitch: int) -> int:
    """Move a pitch by octaves until it sits between C4 and C6."""
    while pitch > MELODY_HIGH:
        pitch -= 12
    while pitch < MELODY_LOW:
        pitch += 12
    return pitch


def _octave_shift_toward_center(pitches: List[int]) -> int:
    """Whole octaves that bring the median pitch closest to C5."""
    if not pitches:
        return 0
    ordered = sorted(pitches)
    median = ordered[len(ordered) // 2]
    return int(round((MELODY_CENTER - median) / 12.0))


def _parse_imported_tracks(data: bytes, path: str):
    """Read MMA's file, dropping key signatures, program changes, and bank selects."""
    if data[:4] != b"MThd" or len(data) < 14:
        raise OSError(f"MMA did not write a MIDI header: {path}")
    header_len = int.from_bytes(data[4:8], "big")
    track_count = int.from_bytes(data[10:12], "big")
    pos = 8 + header_len
    tracks = []
    for _ in range(track_count):
        if data[pos:pos + 4] != b"MTrk":
            raise OSError(f"Missing MIDI track in {path}")
        length = int.from_bytes(data[pos + 4:pos + 8], "big")
        pos += 8
        end = pos + length
        running = None
        pending = 0
        name = ""
        events = []
        while pos < end:
            delta, pos = _read_varlen(data, pos)
            pending += delta
            status = data[pos]
            if status & 0x80:
                running = status
                pos += 1
            else:
                status = running
            if status == 0xFF:
                meta_type = data[pos]
                pos += 1
                size, pos = _read_varlen(data, pos)
                payload = data[pos:pos + size]
                pos += size
                if meta_type == 0x03:
                    name = payload.decode("latin1", errors="replace")
                if meta_type == 0x59:
                    continue
                events.append(("meta", pending, meta_type, payload))
            elif status in (0xF0, 0xF7):
                size, pos = _read_varlen(data, pos)
                payload = data[pos:pos + size]
                pos += size
                events.append(("sysex", pending, status, payload))
            elif (status & 0xF0) in (0xC0, 0xD0):
                data1 = data[pos]
                pos += 1
                if (status & 0xF0) == 0xC0:
                    continue
                events.append(("short", pending, status & 0xF0, data1))
            else:
                data1 = data[pos]
                data2 = data[pos + 1]
                pos += 2
                kind = status & 0xF0
                if kind == 0xB0 and data1 in (0, 32):
                    continue
                events.append(("voice", pending, kind if kind in (0x80, 0x90) else status, data1, data2))
            pending = 0
        tracks.append((name, events))
    return header_len, tracks


def _place_note(pitch: int, shift: int, open_notes: dict, sounding: bool) -> int:
    """Pair a note-off with the pitch chosen for its note-on, then stay inside C4-C6."""
    stack = open_notes.get(pitch)
    if not sounding and stack:
        return stack.pop(0)
    placed = _fold_into_melody_range(pitch + shift * 12 + random.choice((-12, 0, 12)))
    if sounding:
        open_notes.setdefault(pitch, []).append(placed)
    return placed


def _note_stats(events):
    """Note count, median pitch, and how often the track stacks notes into a chord."""
    tick = 0
    pitches = []
    onset_counts = {}
    for event in events:
        tick += event[1]
        if event[0] != "voice" or event[2] != 0x90 or event[4] == 0:
            continue
        pitches.append(event[3])
        onset_counts[tick] = onset_counts.get(tick, 0) + 1
    if not pitches:
        return None
    ordered = sorted(pitches)
    chord_onsets = sum(1 for count in onset_counts.values() if count >= 3)
    return {
        "notes": len(pitches),
        "median": ordered[len(ordered) // 2],
        "max_simultaneous": max(onset_counts.values()),
        "chord_ratio": chord_onsets / len(onset_counts),
    }


def _is_drum_track(name: str) -> bool:
    label = name.strip().lower()
    return label == "drum" or label.startswith("drum")


def _is_low_bass(name: str, stats: dict) -> bool:
    """A bass line sitting below the melody register."""
    return name.strip().lower().startswith("bass") and stats["median"] < 50


def _is_chord_bed(stats: dict) -> bool:
    """Block chords, as opposed to a single-note riff that MMA named Chord."""
    return stats["max_simultaneous"] >= 3 and stats["chord_ratio"] >= 0.5


def _select_melody_tracks(tracks):
    """The line Ardour should import. Chord beds and low bass stay out of this file."""
    musical = []
    for name, events in tracks:
        if _is_drum_track(name):
            continue
        stats = _note_stats(events)
        if not stats:
            continue
        musical.append((name, events, stats))
    melody = [
        (name, events)
        for name, events, stats in musical
        if not _is_low_bass(name, stats) and not _is_chord_bed(stats)
    ]
    if melody:
        return melody
    lines = [
        item for item in musical
        if item[2]["max_simultaneous"] == 1 and not _is_low_bass(item[0], item[2])
    ]
    if len(lines) > 1:
        lowest = min(item[2]["median"] for item in lines)
        lines = [item for item in lines if item[2]["median"] != lowest]
    if lines:
        return [(name, events) for name, events, _ in lines]
    riffs = [item for item in musical if not _is_low_bass(item[0], item[2])]
    pool = riffs or musical
    if not pool:
        return []
    name, events, _ = max(pool, key=lambda item: item[2]["notes"])
    return [(name, events)]


def _timed_meta(events, meta_types):
    tick = 0
    found = []
    for event in events:
        tick += event[1]
        if event[0] == "meta" and event[2] in meta_types:
            found.append((tick, event[2], event[3]))
    return found


def _placed_melody_notes(events, shift: int):
    """Absolute-time notes, with each note-off following the pitch chosen for its note-on."""
    tick = 0
    open_notes = {}
    placed = []
    for event in events:
        tick += event[1]
        if event[0] != "voice":
            continue
        kind = event[2] & 0xF0
        if kind not in (0x80, 0x90):
            continue
        sounding = kind == 0x90 and event[4] > 0
        pitch = _place_note(event[3], shift, open_notes, sounding)
        placed.append((tick, 1 if sounding else 0, kind, pitch, event[4] if sounding else 0))
    return placed


def _write_single_track(header: bytearray, messages) -> bytes:
    """One MIDI track. A one-track file cannot be split into chord and bass tracks."""
    if len(header) >= 14:
        header[10:12] = (1).to_bytes(2, "big")
    body = bytearray()
    last = 0
    for tick, message in messages:
        body.extend(_write_varlen(max(0, tick - last)))
        last = tick
        body.extend(message)
    return bytes(header) + b"MTrk" + len(body).to_bytes(4, "big") + bytes(body)


def normalize_imported_midi(path: str) -> None:
    """Keep the melody line, lift it into C4-C6, and write it as one channel-1 track.

    MMA's groove is a drum part, a chord bed, and one or more bass lines, each
    in its own MIDI track. Ardour keeps those tracks inside the imported
    region and creates a new track for the next one when the region is dragged.
    The chord bed and the low bass are left out, so this import is only the melody.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    header_len, tracks = _parse_imported_tracks(data, path)
    melody_tracks = _select_melody_tracks(tracks)
    pitches = [
        event[3]
        for _, events in melody_tracks
        for event in events
        if event[0] == "voice" and event[2] == 0x90 and event[4] > 0
    ]
    shift = _octave_shift_toward_center(pitches)
    messages = [(0, b"\xFF\x03" + _write_varlen(6) + b"Melody")]
    for _, events in tracks:
        for tick, meta_type, payload in _timed_meta(events, (0x51, 0x58)):
            messages.append((tick, b"\xFF" + bytes([meta_type]) + _write_varlen(len(payload)) + payload))
    for _, events in melody_tracks:
        for tick, order, kind, pitch, velocity in _placed_melody_notes(events, shift):
            messages.append((tick, bytes([kind, pitch, velocity]), order))
    # Note-offs share a tick with the next note-on and must be written first.
    timed = []
    for item in messages:
        if len(item) == 3:
            tick, message, order = item
        else:
            tick, message = item
            order = -1
        timed.append((tick, order, message))
    timed.sort(key=lambda item: (item[0], item[1]))
    end_tick = timed[-1][0] if timed else 0
    timed.append((end_tick, 2, b"\xFF\x2F\x00"))
    header = bytearray(data[:8 + header_len])
    with open(path, "wb") as handle:
        handle.write(_write_single_track(header, [(tick, message) for tick, _, message in timed]))


def generate_mma_accompaniment(
    key: str,
    scale: str,
    groove: str,
    bars: int,
    tempo: int,
    output_file: str,
) -> str:
    """Write a chart, run MMA, and return the major or minor scale name."""
    chart_scale = "minor" if (scale or "").lower() == "minor" else "major"
    handle = tempfile.NamedTemporaryFile(prefix="la-mma-", suffix=".mma", delete=False)
    chart_path = handle.name
    handle.close()
    try:
        write_mma_chart(chart_path, tempo, key, chart_scale, groove, bars)
        run_mma(chart_path, output_file)
        normalize_imported_midi(output_file)
    finally:
        try:
            os.remove(chart_path)
        except OSError:
            pass
    return chart_scale


def main():
    parser = argparse.ArgumentParser(
        description="Write an MMA groove for a key, major or minor scale, and genre.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python melody_generator.py --key E --scale minor --genre pop --bars 4 --tempo 140
  python melody_generator.py --key Bb --scale major --genre jazz --bars 8 --tempo 120 --seed 7
        """,
    )
    parser.add_argument(
        "--key", "-k",
        required=True,
        help="Key signature (C, C#, Db, D, Eb, F#, Bb, and the other menu spellings).",
    )
    parser.add_argument(
        "--scale", "-s",
        required=True,
        choices=["major", "minor"],
        help="major or minor.",
    )
    parser.add_argument(
        "--genre", "-g",
        required=True,
        help="Genre id or display name from genres.json.",
    )
    parser.add_argument(
        "--tempo", "-t",
        type=int,
        required=True,
        help="Tempo in BPM.",
    )
    parser.add_argument(
        "--bars", "-b",
        type=int,
        default=4,
        help="Number of bars (default: 4).",
    )
    parser.add_argument(
        "--output", "-o",
        default="melody.mid",
        help="Output MIDI filename (default: melody.mid).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for a repeatable chord loop and octave scatter.",
    )
    args = parser.parse_args()
    if args.bars < 1:
        parser.error("--bars must be at least 1")
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    print(f"Generating melody for {args.bars} bars...")
    try:
        profile, groove_entry = load_mma_genre(args.genre)
        scale_name = generate_mma_accompaniment(
            args.key,
            args.scale,
            groove_entry["groove"],
            args.bars,
            args.tempo,
            args.output,
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Genre: {profile.get('displayName')} ({profile.get('id')})")
    print(f"Resolved scale: {scale_name}")
    print(f"Melody saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
