import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_transcription(file_path: str = "output.json") -> str:
    """Load transcription from JSON file."""
    with open(file_path, "r") as f:
        data = json.load(f)
        return data["text"]

def generate_summary(text: str) -> str:
    """Generate summary using OpenAI's API."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""Please provide a comprehensive summary of the following transcription. 
    Focus on the main points and key takeaways. The summary should be well-structured 
    and easy to read:

    {text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates clear and concise summaries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def main():
    try:
        # Load transcription
        print("Loading transcription...")
        transcription = load_transcription()
        
        # Generate summary
        print("\nGenerating summary...")
        summary = generate_summary(transcription)
        
        print("\nSummary:")
        print("-" * 80)
        print(summary)
        print("-" * 80)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 