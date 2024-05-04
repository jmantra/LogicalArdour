import argparse
import librosa

def analyze_audio(audio_file):
    # Load audio file
    y, sr = librosa.load(audio_file)

    # Calculate tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    print( tempo)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Tempo Analysis Tool")
    parser.add_argument("audio_file", help="Path to the input audio file")
    args = parser.parse_args()

    analyze_audio(args.audio_file)

