#!/usr/bin/env python3
import os
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.traceback import install
from youtube_transcriber.transcriber import download_youtube_audio, transcribe_audio
from youtube_transcriber.summarizer import generate_summary
import json
from dotenv import load_dotenv

# Install rich traceback handler
install()

# Initialize Rich console
console = Console()

def save_summary(summary: str, output_file: str = "summary.txt"):
    """Save summary to a text file."""
    output_path = Path.cwd() / output_file
    with open(output_path, "w") as f:
        f.write(summary)
    return output_path

def cleanup_files(audio_path: Path, json_path: Path):
    """Clean up temporary files."""
    try:
        if audio_path.exists():
            audio_path.unlink()
            console.print(f"[green]Cleaned up audio file: {audio_path.name}[/green]")
        if json_path.exists():
            json_path.unlink()
            console.print(f"[green]Cleaned up JSON file: {json_path.name}[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not delete some temporary files: {e}[/yellow]")

@click.command()
@click.argument("url")
@click.option("--no-save", is_flag=True, help="Don't save the summary to a file")
@click.option("--cleanup", is_flag=True, help="Delete audio and JSON files after processing")
@click.option("--output", "-o", default="summary.txt", help="Output file for the summary")
def main(url: str, no_save: bool, cleanup: bool, output: str):
    """
    Generate a summary of a YouTube video from its URL.
    
    Example: youtube-summary https://www.youtube.com/watch?v=...
    """
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    hf_token = os.getenv("HF_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not hf_token or not openai_key:
        console.print("[red]Error: Missing required environment variables[/red]")
        console.print("Please ensure you have set:")
        console.print("  - HF_TOKEN (Hugging Face API token)")
        console.print("  - OPENAI_API_KEY (OpenAI API key)")
        return
    
    # Create output directory in current working directory
    output_dir = Path.cwd() / "downloads"
    output_dir.mkdir(exist_ok=True)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            # Download audio
            download_task = progress.add_task(description="[blue]Downloading YouTube audio...[/blue]", total=None)
            audio_path = download_youtube_audio(url, output_dir)
            progress.update(download_task, description="[green]✓ Audio downloaded[/green]")
            
            # Transcribe audio
            transcribe_task = progress.add_task(description="[blue]Transcribing audio...[/blue]", total=None)
            transcription = transcribe_audio(audio_path, hf_token)
            progress.update(transcribe_task, description="[green]✓ Transcription complete[/green]")
            
            # Generate summary
            summary_task = progress.add_task(description="[blue]Generating summary...[/blue]", total=None)
            summary = generate_summary(transcription)
            if not summary:
                raise ValueError("Summary generation failed. The model returned an empty response.")
            progress.update(summary_task, description="[green]✓ Summary generated[/green]")
            
            # Save or display summary
            if not no_save:
                output_path = save_summary(summary, output)
                console.print(f"\n[green]Summary saved to: {output_path}[/green]")
            
            # Display summary in terminal
            console.print("\n", Panel(
                summary,
                title="[bold blue]Summary[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            ))
            
            # Cleanup if requested
            if cleanup:
                cleanup_task = progress.add_task(description="[blue]Cleaning up temporary files...[/blue]", total=None)
                json_path = Path.cwd() / "output.json"
                cleanup_files(audio_path, json_path)
                progress.update(cleanup_task, description="[green]✓ Cleanup complete[/green]")
    
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise click.Abort()

if __name__ == "__main__":
    main() 