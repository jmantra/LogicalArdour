import essentia
import essentia.standard as es

def detect_key(file_path):
    # Create the required algorithms
    loader = es.MonoLoader(filename=file_path)
    key_detector = es.KeyExtractor()

    # Load the audio file
    audio = loader()

    # Detect the key
    key, scale, strength = key_detector(audio)

    return key, scale, strength

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python detect_key.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    key, scale, strength = detect_key(audio_file)

    print(f"The key of the song is {key} {scale}")
