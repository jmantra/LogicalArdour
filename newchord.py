import random
import mido
from mido import MidiFile, MidiTrack, Message
import argparse

# Major and Minor scale chord mappings
MAJOR_CHORDS = {
    "I": [0, 4, 7],
    "ii": [2, 5, 9],
    "iii": [4, 7, 11],
    "IV": [5, 9, 12],
    "V": [7, 11, 14],
    "vi": [9, 12, 16],
    "vii°": [11, 14, 17]
}

MINOR_CHORDS = {
    "i": [0, 3, 7],
    "ii°": [2, 5, 8],
    "III": [3, 7, 10],
    "iv": [5, 8, 12],
    "v": [7, 10, 14],
    "VI": [8, 12, 15],
    "VII": [10, 14, 17]
}

# Notes in the chromatic scale, including flat equivalents
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NOTES = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}


def generate_midi_chord_progression(key, scale_type, length, filename):
    # Convert flat notes to sharp equivalents if needed
    if key in FLAT_NOTES:
        key = FLAT_NOTES[key]

    # Validate the key
    if key not in NOTES:
        raise ValueError(f"Invalid key: {key}. Please provide a valid key (e.g., C, D#, F#, or Bb).")

    # Determine the root note index
    root_index = NOTES.index(key)

    # Select chord mapping based on the scale type
    chord_choices = MAJOR_CHORDS if scale_type == "major" else MINOR_CHORDS

    # Create a new MIDI file and track
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo (default: 120 BPM)
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))

    # Generate chord progression
    progression = []
    time_per_chord = 780  # Time in ticks for each chord

    for _ in range(length):
        chord = random.choice(list(chord_choices.keys()))
        chord_intervals = chord_choices[chord]
        chord_notes = [(root_index + interval) % 12 for interval in chord_intervals]

        for note in chord_notes:
            midi_note = 60 + note  # Middle C (MIDI note 60) as reference
            track.append(Message('note_on', note=midi_note, velocity=64, time=0))
            track.append(Message('note_off', note=midi_note, velocity=64, time=time_per_chord))

        chord_name = NOTES[chord_notes[0]]
        progression.append(f"{chord_name} {chord}")

    # Save the MIDI file
    mid.save(filename)
    print(f"Generated Chord Progression: {' - '.join(progression)}")
    print(f"MIDI file saved as {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a MIDI chord progression.")
    parser.add_argument("key", type=str, help="The key of the progression (e.g., C, D#, F#, or Bb).")
    parser.add_argument("scale_type", type=str, choices=["major", "minor"], help="Scale type (major or minor).")
    parser.add_argument("length", type=int, help="Length of the chord progression.")
    parser.add_argument("--output", type=str, default="chord_progression.mid", help="Output MIDI file name.")

    args = parser.parse_args()

    try:
        generate_midi_chord_progression(args.key, args.scale_type, args.length, args.output)
    except ValueError as e:
        print(e)
