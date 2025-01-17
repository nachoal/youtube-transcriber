import os
import subprocess
import re
from pathlib import Path
import yt_dlp
from dotenv import load_dotenv
import sys
import json

# Load environment variables from .env file
load_dotenv()

def sanitize_title(title: str) -> str:
    """Replace characters that might cause issues with subprocess calls."""
    # Replace characters that might cause issues, keep only alphanumeric, spaces, hyphens, and underscores
    sanitized = re.sub(r'[^A-Za-z0-9_\- ]', '', title)
    # Replace multiple spaces with single space and strip
    return re.sub(r'\s+', ' ', sanitized).strip()

def download_youtube_audio(url: str, output_path: Path) -> Path:
    """Download audio from a YouTube video using yt-dlp."""
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        # Use more restrictive filename template
        "outtmpl": str(output_path / "%(title).100B.%(ext)s"),
        "restrictfilenames": True,  # Use safe filenames
        "windowsfilenames": True,   # Use Windows-compatible filenames
        "ignoreerrors": True,       # Skip on errors
        "nooverwrites": True,       # Don't overwrite files
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise RuntimeError("Failed to extract video info")
                
            # Get the downloaded filename from yt-dlp
            if 'requested_downloads' in info:
                # For playlist items
                filename = info['requested_downloads'][0]['filepath']
            else:
                # For single videos
                filename = ydl.prepare_filename(info)
                if filename.endswith('.webm'):  # Replace extension for the post-processed file
                    filename = filename.rsplit('.', 1)[0] + '.wav'
                    
            audio_path = Path(filename)
            if not audio_path.exists():
                raise FileNotFoundError(f"Downloaded file not found: {audio_path}")
                
            return audio_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to download audio: {str(e)}")

def transcribe_audio(audio_path: Path, hf_token: str) -> str:
    """Transcribe audio using insanely-fast-whisper CLI tool."""
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    cmd = [
        "insanely-fast-whisper",
        "--file-name", str(audio_path.absolute()),
        "--device-id", "mps",
        "--hf-token", hf_token
    ]
    
    # Just run the command and show its output
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("Transcription failed")
    
    # Read the transcription from the file the command created
    with open("output.json") as f:
        data = json.loads(f.read())
        return data.get("text", "")

def main():
    # Get configuration from environment variables
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is not set. Please check your .env file.")

    # YouTube URL can be provided as an environment variable or as a command line argument
    youtube_url = os.getenv("YOUTUBE_URL", "https://www.youtube.com/watch?v=wazHMMaiDEA")
    
    # Create output directory in current working directory
    output_dir = Path.cwd() / "downloads"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Download audio
        print("Downloading YouTube audio...")
        audio_path = download_youtube_audio(youtube_url, output_dir)
        print(f"Audio downloaded to: {audio_path}")
        
        # Transcribe audio
        print("Transcribing audio...")
        transcription = transcribe_audio(audio_path, hf_token)
        
        if not transcription:
            print("Warning: Transcription is empty!")
        else:
            print("\nTranscription:")
            print(transcription)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 