import random
import mido
from mido import MidiFile, MidiTrack, Message
import argparse

# Notes in the chromatic scale (sharps only for simplicity)
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Map flat notes to their sharp equivalents for consistent handling
FLAT_TO_SHARP = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}

# Scale mappings
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

# Generate a MIDI bassline
def generate_bassline(key, scale_type, length, filename):
    # Convert flat notes to sharps if necessary
    key = FLAT_TO_SHARP.get(key, key)  # Convert flats to sharps

    if key not in NOTES:
        raise ValueError(f"Invalid key: {key}. Please provide a valid key (e.g., C, D#, F#, Bb).")

    root_index = NOTES.index(key)  # Find index in unified NOTES list
    scale = MAJOR_SCALE if scale_type == "major" else MINOR_SCALE

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo (default: 120 BPM)
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))

    # Generate bassline
    time_per_measure = 1920  # ticks (4 beats per measure at 480 ticks/beat)
    bassline = []
    for _ in range(length):
        measure = []
        beat_time = time_per_measure // 4
        for _ in range(4):  # 4 beats per measure
            if random.random() < 0.8:  # 80% chance of a note
                note_interval = random.choice(scale)
                octave = random.choice([2, 3])  # Choose between lower octaves
                note = (root_index + note_interval + octave * 12) % 128
                duration = random.choice([beat_time // 2, beat_time])  # 8th or quarter note
                measure.append((note, duration))
            else:
                measure.append((None, beat_time))  # Rest
        bassline.extend(measure)

    # Write the bassline to the MIDI track
    for note, duration in bassline:
        if note is not None:
            track.append(Message('note_on', note=note, velocity=80, time=0))
            track.append(Message('note_off', note=note, velocity=80, time=duration))
        else:
            # Add a rest by waiting for the duration
            track.append(Message('note_on', note=0, velocity=0, time=duration))

    mid.save(filename)
    print(f"Bassline generated in {key} {scale_type} scale. MIDI file saved as {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a random MIDI bassline.")
    parser.add_argument("key", type=str, help="The key of the bassline (e.g., C, D#, F#, Bb).")
    parser.add_argument("scale_type", type=str, choices=["major", "minor"], help="Scale type (major or minor).")
    parser.add_argument("length", type=int, help="Number of measures in the bassline.")
    parser.add_argument("--output", type=str, default="bassline.mid", help="Output MIDI file name.")

    args = parser.parse_args()

    generate_bassline(args.key, args.scale_type, args.length, args.output)
