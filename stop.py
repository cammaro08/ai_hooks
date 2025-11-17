#!/usr/bin/env python3
# Cursor Hook: stop
# Adapted from Claude's stop.py

import argparse
import json
import os
import sys
import random
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def get_uv_path():
    """Get the full path to uv executable."""
    # First, try to find uv in system PATH
    uv_in_path = shutil.which('uv')
    if uv_in_path:
        return uv_in_path
    
    # Fall back to the default location
    home_dir = Path.home()
    return str(home_dir / ".local" / "bin" / "uv")


def get_conversation_name(conversation_id):
    """
    Look up the friendly name for a conversation.
    Returns the name if found, or a truncated conversation_id as fallback.
    """
    names_file = Path.home() / '.cursor' / 'logs' / 'conversation_names.json'

    if names_file.exists():
        try:
            with open(names_file, 'r') as f:
                names = json.load(f)
                if conversation_id in names:
                    return names[conversation_id]
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: use truncated conversation_id
    if len(conversation_id) > 12:
        return f"...{conversation_id[-8:]}"
    return conversation_id


def get_completion_messages():
    """Return list of friendly completion messages."""
    return [
        "work complete",
        "all done",
        "task finished",
        "ready for review",
        "finished successfully"
    ]


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get hooks directory
    tts_dir = Path.home() / '.cursor' / 'hooks' / 'utils' / 'tts'

    # Check for ElevenLabs API key (highest priority)
    if os.getenv('ELEVENLABS_API_KEY'):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv('OPENAI_API_KEY'):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None


def get_llm_completion_message():
    """
    Generate completion message using available LLM services.
    Priority order: OpenAI > Anthropic > Ollama > fallback to random message

    Returns:
        str: Generated or fallback completion message
    """
    # Get hooks directory
    llm_dir = Path.home() / '.cursor' / 'hooks' / 'utils' / 'llm'

    uv_path = get_uv_path()

    # Try OpenAI first (highest priority)
    if os.getenv('OPENAI_API_KEY'):
        oai_script = llm_dir / "oai.py"
        if oai_script.exists():
            try:
                result = subprocess.run([
                    uv_path, "run", str(oai_script), "--completion"
                ],
                capture_output=True,
                text=True,
                timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Anthropic second
    if os.getenv('ANTHROPIC_API_KEY'):
        anth_script = llm_dir / "anth.py"
        if anth_script.exists():
            try:
                result = subprocess.run([
                    uv_path, "run", str(anth_script), "--completion"
                ],
                capture_output=True,
                text=True,
                timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Ollama third (local LLM)
    ollama_script = llm_dir / "ollama.py"
    if ollama_script.exists():
        try:
            result = subprocess.run([
                uv_path, "run", str(ollama_script), "--completion"
            ],
            capture_output=True,
            text=True,
            timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    # Fallback to random predefined message
    messages = get_completion_messages()
    return random.choice(messages)


def announce_completion(conversation_id=""):
    """Announce completion using the best available TTS service."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            print("No TTS script found", file=sys.stderr)
            return  # No TTS scripts available

        # Get chat name for this conversation
        chat_name = get_conversation_name(conversation_id) if conversation_id else "Unknown"

        # Get completion message (LLM-generated or fallback)
        completion_message = get_llm_completion_message()

        # Combine chat name with completion message into a natural, flowing announcement
        full_message = f"Chat {chat_name}, {completion_message}"
        print(f"Announcing: {full_message}", file=sys.stderr)

        # Call the TTS script with the completion message
        uv_path = get_uv_path()
        result = subprocess.run([
            uv_path, "run", tts_script, full_message
        ],
        capture_output=True,  # Suppress output
        text=True,
        timeout=10  # 10-second timeout
        )

        if result.returncode != 0:
            print(f"TTS failed with return code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"   stderr: {result.stderr}", file=sys.stderr)
        else:
            print("TTS completed successfully", file=sys.stderr)

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"TTS error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--notify', action='store_true', help='Enable TTS completion announcement')
        parser.add_argument('--followup', type=str, default=None, help='Optional followup message to auto-submit')
        args = parser.parse_args()

        # Read JSON input from stdin (Cursor format)
        # Cursor provides: conversation_id, generation_id, hook_event_name, workspace_roots, status, loop_count
        input_data = json.load(sys.stdin)

        # Extract fields
        conversation_id = input_data.get("conversation_id", "")
        status = input_data.get("status", "")
        loop_count = input_data.get("loop_count", 0)

        # Ensure log directory exists
        log_dir = Path.home() / '.cursor' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "stop.json"

        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        # Announce completion via TTS (only if --notify flag is set)
        if args.notify:
            announce_completion(conversation_id)

        # Return optional followup message (Cursor can auto-submit this)
        result = {}
        if args.followup:
            result["followup_message"] = args.followup

        if result:
            print(json.dumps(result))

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
