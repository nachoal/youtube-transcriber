import os
import subprocess
from pathlib import Path
import yt_dlp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def download_youtube_audio(url: str, output_path: Path) -> Path:
    """Download audio from a YouTube video using yt-dlp."""
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = Path(output_path / f"{info['title']}.wav")
        return audio_path

def transcribe_audio(audio_path: Path, hf_token: str) -> str:
    """Transcribe audio using insanely-fast-whisper CLI tool."""
    cmd = [
        "insanely-fast-whisper",
        "--file-name", str(audio_path),
        "--device-id", "mps",
        "--hf-token", hf_token
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def main():
    # Get configuration from environment variables
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is not set. Please check your .env file.")

    # YouTube URL can be provided as an environment variable or as a command line argument
    youtube_url = os.getenv("YOUTUBE_URL", "https://www.youtube.com/watch?v=wazHMMaiDEA")
    
    # Create output directory in the current working directory
    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Download audio
        print("Downloading YouTube audio...")
        audio_path = download_youtube_audio(youtube_url, output_dir)
        
        # Transcribe audio
        print("Transcribing audio...")
        transcription = transcribe_audio(audio_path, hf_token)
        
        print("\nTranscription:")
        print(transcription)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 