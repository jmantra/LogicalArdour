mod audio;
mod detect;

use std::env;
use std::process::ExitCode;

fn main() -> ExitCode {
    let mut args = env::args();
    let _program = args.next();
    let Some(path) = args.next() else {
        println!("Usage: python detect_key.py <audio_file>");
        return ExitCode::from(1);
    };
    if args.next().is_some() {
        println!("Usage: python detect_key.py <audio_file>");
        return ExitCode::from(1);
    }

    let audio = match audio::load_mono_44100(&path) {
        Ok(audio) => audio,
        Err(err) => {
            eprintln!("key: {err}");
            return ExitCode::from(1);
        }
    };

    match detect::detect_key(&audio) {
        Ok((key, scale)) => {
            println!("The key of the song is {key} {scale}");
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("key: {err}");
            ExitCode::from(1)
        }
    }
}
