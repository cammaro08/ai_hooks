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
import base64
import subprocess
import tempfile
from dotenv import load_dotenv


def generate_audio(text, voice="alloy"):
    """
    Generate audio using OpenAI's audio model and play it.

    Args:
        text (str): The text to speak
        voice (str): Voice to use (alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        bool: True if successful, False otherwise
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        completion = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "wav"},
            messages=[
                {
                    "role": "user",
                    "content": f"Say exactly this and nothing else: {text}"
                }
            ]
        )

        # Decode and play the audio
        if completion.choices[0].message.audio:
            wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav_bytes)
                temp_path = f.name

            # Play audio using afplay (macOS)
            subprocess.run(["afplay", temp_path], capture_output=True)

            # Clean up
            os.unlink(temp_path)
            return True

        return False

    except Exception as e:
        print(f"Audio error: {e}", file=sys.stderr)
        return False


def generate_completion_audio(chat_name="", reason="completed"):
    """
    Generate a completion message and speak it using OpenAI audio.

    Args:
        chat_name (str): Optional chat name to include in message
        reason (str): Why Claude stopped - "completed" or "permission"

    Returns:
        bool: True if successful, False otherwise
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        engineer_name = os.getenv("ENGINEER_NAME", "").strip()

        # Build the chat name part
        if chat_name:
            chat_part = f"Start by saying 'Chat {chat_name}' then the message."
        else:
            chat_part = ""

        if engineer_name:
            name_part = f"The engineer's name is {engineer_name}. Sometimes mention their name."
        else:
            name_part = ""

        # Different prompts based on reason
        if reason == "permission":
            prompt = f"""You are a friendly AI assistant announcing that you need permission to continue.
{chat_part}
{name_part}

Generate and speak a short message (under 10 words) asking for permission.
Examples: "Need your approval to continue", "Waiting for permission", "Please approve to proceed"

Say it naturally and politely."""
        else:
            prompt = f"""You are a friendly AI assistant announcing task completion.
{chat_part}
{name_part}

Generate and speak a short, friendly completion message (under 10 words).
Examples: "All done!", "Task complete!", "Ready for your review!", "Finished!"

Say the completion message naturally and cheerfully."""

        completion = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "nova", "format": "wav"},
            messages=[{"role": "user", "content": prompt}]
        )

        # Decode and play the audio
        if completion.choices[0].message.audio:
            wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav_bytes)
                temp_path = f.name

            # Play audio using afplay (macOS)
            subprocess.run(["afplay", temp_path], capture_output=True)

            # Clean up
            os.unlink(temp_path)
            return True

        return False

    except Exception as e:
        print(f"Audio error: {e}", file=sys.stderr)
        return False


def prompt_llm(prompt_text):
    """
    Base OpenAI LLM prompting method using fastest model.

    Args:
        prompt_text (str): The prompt to send to the model

    Returns:
        str: The model's response text, or None if error
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-5-nano",  # Fastest OpenAI model
            messages=[{"role": "user", "content": prompt_text}],
            max_completion_tokens=100,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return None


def generate_completion_message():
    """
    Generate a completion message using OpenAI LLM.

    Returns:
        str: A natural language completion message, or None if error
    """
    engineer_name = os.getenv("ENGINEER_NAME", "").strip()

    if engineer_name:
        name_instruction = f"Sometimes (about 30% of the time) include the engineer's name '{engineer_name}' in a natural way."
        examples = f"""Examples of the style: 
- Standard: "Work complete!", "All done!", "Task finished!", "Ready for your next move!"
- Personalized: "{engineer_name}, all set!", "Ready for you, {engineer_name}!", "Complete, {engineer_name}!", "{engineer_name}, we're done!" """
    else:
        name_instruction = ""
        examples = """Examples of the style: "Work complete!", "All done!", "Task finished!", "Ready for your next move!" """

    prompt = f"""Generate a short, friendly completion message for when an AI coding assistant finishes a task. 

Requirements:
- Keep it under 10 words
- Make it positive and future focused
- Use natural, conversational language
- Focus on completion/readiness
- Do NOT include quotes, formatting, or explanations
- Return ONLY the completion message text
{name_instruction}

{examples}

Generate ONE completion message:"""

    response = prompt_llm(prompt)

    # Clean up response - remove quotes and extra formatting
    if response:
        response = response.strip().strip('"').strip("'").strip()
        # Take first line if multiple lines
        response = response.split("\n")[0].strip()

    return response


def generate_agent_name():
    """
    Generate a one-word agent name using OpenAI.
    
    Returns:
        str: A single-word agent name, or fallback name if error
    """
    import random
    
    # Example names to guide generation
    example_names = [
        "Phoenix", "Sage", "Nova", "Echo", "Atlas", "Cipher", "Nexus", 
        "Oracle", "Quantum", "Zenith", "Aurora", "Vortex", "Nebula",
        "Catalyst", "Prism", "Axiom", "Helix", "Flux", "Synth", "Vertex"
    ]
    
    # If no API key, return random fallback
    if not os.getenv("OPENAI_API_KEY"):
        return random.choice(example_names)
    
    # Create examples string
    examples_str = ", ".join(example_names[:10])  # Use first 10 as examples
    
    prompt_text = f"""Generate exactly ONE unique agent/assistant name.

Requirements:
- Single word only (no spaces, hyphens, or punctuation)
- Abstract and memorable
- Professional sounding
- Easy to pronounce
- Similar style to these examples: {examples_str}

Generate a NEW name (not from the examples). Respond with ONLY the name, nothing else.

Name:"""
    
    try:
        # Use faster model with lower tokens for name generation
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key")
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast, cost-effective model
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=20,
            temperature=0.7,
        )
        
        # Extract and clean the name
        name = response.choices[0].message.content.strip()
        # Ensure it's a single word
        name = name.split()[0] if name else "Agent"
        # Remove any punctuation
        name = ''.join(c for c in name if c.isalnum())
        # Capitalize first letter
        name = name.capitalize() if name else "Agent"
        
        # Validate it's not empty and reasonable length
        if name and 3 <= len(name) <= 20:
            return name
        else:
            raise Exception("Invalid name generated")
        
    except Exception:
        # Return random fallback name
        return random.choice(example_names)


def main():
    """Command line interface for testing."""
    import json

    if len(sys.argv) > 1:
        if sys.argv[1] == "--completion":
            message = generate_completion_message()
            if message:
                print(message)
            else:
                print("Error generating completion message")
        elif sys.argv[1] == "--completion-audio":
            # Generate and speak completion message
            # Usage: --completion-audio [chat_name] [reason]
            chat_name = sys.argv[2] if len(sys.argv) > 2 else ""
            reason = sys.argv[3] if len(sys.argv) > 3 else "completed"
            success = generate_completion_audio(chat_name, reason)
            if not success:
                print("Error generating audio", file=sys.stderr)
                sys.exit(1)
        elif sys.argv[1] == "--audio":
            # Speak provided text
            if len(sys.argv) > 2:
                text = " ".join(sys.argv[2:])
                success = generate_audio(text)
                if not success:
                    print("Error generating audio", file=sys.stderr)
                    sys.exit(1)
            else:
                print("Usage: ./oai.py --audio 'text to speak'")
                sys.exit(1)
        elif sys.argv[1] == "--agent-name":
            # Generate agent name (no input needed)
            name = generate_agent_name()
            print(name)
        else:
            prompt_text = " ".join(sys.argv[1:])
            response = prompt_llm(prompt_text)
            if response:
                print(response)
            else:
                print("Error calling OpenAI API")
    else:
        print("Usage: ./oai.py 'your prompt here' or ./oai.py --completion or ./oai.py --completion-audio [chat_name] or ./oai.py --audio 'text' or ./oai.py --agent-name")


if __name__ == "__main__":
    main()
