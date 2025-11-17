#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "openai",
#     "python-dotenv",
# ]
# ///

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from dotenv import load_dotenv


def main():
    """
    OpenAI TTS Script

    Uses OpenAI's latest TTS model for high-quality text-to-speech.
    Accepts optional text prompt as command-line argument.

    Usage:
    - ./openai_tts.py                    # Uses default text
    - ./openai_tts.py "Your custom text" # Uses provided text

    Features:
    - OpenAI gpt-4o-mini-tts model (latest)
    - Nova voice (engaging and warm)
    - Saves to temp file and plays with afplay (macOS)
    """

    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables", file=sys.stderr)
        print("Please add your OpenAI API key to .env file:", file=sys.stderr)
        print("OPENAI_API_KEY=your_api_key_here", file=sys.stderr)
        sys.exit(1)

    try:
        from openai import OpenAI

        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Get text from command line argument or use default
        if len(sys.argv) > 1:
            text = " ".join(sys.argv[1:])  # Join all arguments as text
        else:
            text = "Today is a wonderful day to build something people love!"

        # Generate audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

            try:
                # Generate audio
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=text,
                )

                # Save to file
                response.write_to_file(temp_path)

                # Play with afplay (macOS built-in audio player)
                result = subprocess.run(["afplay", temp_path], check=True, capture_output=True, text=True)
                if result.stderr:
                    print(f"⚠️  afplay stderr: {result.stderr}", file=sys.stderr)

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass

    except ImportError as e:
        print(f"❌ Error: Required package not installed: {e}", file=sys.stderr)
        print("This script uses UV to auto-install dependencies.", file=sys.stderr)
        print("Make sure UV is installed: https://docs.astral.sh/uv/", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
