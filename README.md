# YouTube Video Summarizer

A CLI tool that downloads YouTube videos, transcribes them, and generates concise summaries.

## Requirements

- Python 3.12 or higher
- Hugging Face API token
- OpenAI API key

## Installation

1. Clone this repository
2. Install the package in development mode:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

## Usage

```bash
# Basic usage - saves summary to summary.txt by default
youtube-summary https://www.youtube.com/watch?v=your-video-id

# Don't save to file, only display in terminal
youtube-summary --no-save https://www.youtube.com/watch?v=your-video-id

# Save to custom file and cleanup temporary files
youtube-summary --output custom_summary.txt --cleanup https://www.youtube.com/watch?v=your-video-id
```

## Options

- `--no-save`: Don't save the summary to a file
- `--cleanup`: Delete audio and JSON files after processing
- `--output, -o`: Specify custom output file (default: summary.txt)

## Environment Variables

Create a `.env` file with:

```
HF_TOKEN=your-huggingface-token
OPENAI_API_KEY=your-openai-key
```
