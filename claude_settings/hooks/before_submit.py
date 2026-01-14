#!/usr/bin/env python3
# Cursor Hook: beforeSubmitPrompt
# Adapted from Claude's user_prompt_submit.py

import argparse
import json
import os
import sys
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


def get_conversation_names_file():
    """Get path to conversation names mapping file."""
    log_dir = Path.home() / '.claude' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / 'conversation_names.json'


def load_conversation_names():
    """Load conversation names from JSON file."""
    names_file = get_conversation_names_file()
    if names_file.exists():
        try:
            with open(names_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def save_conversation_names(names):
    """Save conversation names to JSON file."""
    names_file = get_conversation_names_file()
    with open(names_file, 'w') as f:
        json.dump(names, f, indent=2)


def ask_for_chat_name_dialog():
    """
    Show macOS dialog to ask user for chat name.
    Returns the name entered, or None if cancelled/timed out.
    """
    try:
        script = '''
        display dialog "Enter chat name (e.g., 10.12.3):" default answer "" with title "New Cursor Chat" giving up after 30
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=35
        )

        if result.returncode == 0:
            # Parse output: "button returned:OK, text returned:10.12.3, gave up:false"
            output = result.stdout.strip()
            # Extract text returned value
            if "text returned:" in output:
                parts = output.split(", ")
                for part in parts:
                    if part.startswith("text returned:"):
                        name = part.replace("text returned:", "").strip()
                        if name:  # Only return if not empty
                            return name
        return None
    except Exception:
        return None


def auto_generate_chat_name(prompt):
    """
    Auto-generate a chat name from the first few words of the prompt.
    """
    # Clean the prompt and take first 5 words
    words = prompt.strip().split()[:5]
    if words:
        name = " ".join(words)
        # Truncate to 50 chars max
        if len(name) > 50:
            name = name[:47] + "..."
        return name
    return "Unnamed Chat"


def handle_conversation_naming(conversation_id, prompt):
    """
    Handle naming for new conversations.
    Shows dialog for new conversations, skips for existing ones.
    """
    names = load_conversation_names()

    # Check if conversation already has a name
    if conversation_id in names:
        # Already named, skip
        return

    # New conversation - ask for name
    user_name = ask_for_chat_name_dialog()

    if user_name:
        names[conversation_id] = user_name
    else:
        # Auto-generate from prompt
        names[conversation_id] = auto_generate_chat_name(prompt)

    save_conversation_names(names)


def log_user_prompt(conversation_id, input_data):
    """Log user prompt to logs directory."""
    # Ensure logs directory exists
    log_dir = Path.home() / '.claude' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'before_submit.json'

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Append the entire input data
    log_data.append(input_data)

    # Write back to file with formatting
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def manage_session_data(conversation_id, prompt, name_agent=False):
    """Manage session data in JSON structure."""
    # Ensure sessions directory exists
    sessions_dir = Path.home() / '.claude' / 'data' / 'sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Load or create session file
    session_file = sessions_dir / f"{conversation_id}.json"

    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            session_data = {"conversation_id": conversation_id, "prompts": []}
    else:
        session_data = {"conversation_id": conversation_id, "prompts": []}

    # Add the new prompt
    session_data["prompts"].append(prompt)

    # Generate agent name if requested and not already present
    if name_agent and "agent_name" not in session_data:
        uv_path = get_uv_path()
        hooks_dir = Path.home() / '.claude' / 'hooks'

        # Try Ollama first (preferred)
        try:
            result = subprocess.run(
                [uv_path, "run", str(hooks_dir / "utils" / "llm" / "ollama.py"), "--agent-name"],
                capture_output=True,
                text=True,
                timeout=5  # Shorter timeout for local Ollama
            )

            if result.returncode == 0 and result.stdout.strip():
                agent_name = result.stdout.strip()
                # Check if it's a valid name (not an error message)
                if len(agent_name.split()) == 1 and agent_name.isalnum():
                    session_data["agent_name"] = agent_name
                else:
                    raise Exception("Invalid name from Ollama")
        except Exception:
            # Fall back to Anthropic if Ollama fails
            try:
                result = subprocess.run(
                    [uv_path, "run", str(hooks_dir / "utils" / "llm" / "anth.py"), "--agent-name"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout.strip():
                    agent_name = result.stdout.strip()
                    # Validate the name
                    if len(agent_name.split()) == 1 and agent_name.isalnum():
                        session_data["agent_name"] = agent_name
            except Exception:
                # If both fail, don't block the prompt
                pass

    # Save the updated session data
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except Exception:
        # Silently fail if we can't write the file
        pass


def validate_prompt(prompt):
    """
    Validate the user prompt for security or policy violations.
    Returns tuple (is_valid, reason).
    """
    # Example validation rules (customize as needed)
    blocked_patterns = [
        # Add any patterns you want to block
        # Example: ('rm -rf /', 'Dangerous command detected'),
    ]

    prompt_lower = prompt.lower()

    for pattern, reason in blocked_patterns:
        if pattern.lower() in prompt_lower:
            return False, reason

    return True, None


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--validate', action='store_true',
                          help='Enable prompt validation')
        parser.add_argument('--log-only', action='store_true',
                          help='Only log prompts, no validation or blocking')
        parser.add_argument('--store-last-prompt', action='store_true',
                          help='Store the last prompt for status line display')
        parser.add_argument('--name-agent', action='store_true',
                          help='Generate an agent name for the session')
        args = parser.parse_args()

        # Read JSON input from stdin (Cursor format)
        # Cursor provides: conversation_id, generation_id, hook_event_name, workspace_roots, prompt, attachments
        input_data = json.loads(sys.stdin.read())

        # Extract conversation_id and prompt (Cursor uses conversation_id instead of session_id)
        conversation_id = input_data.get('conversation_id', 'unknown')
        prompt = input_data.get('prompt', '')

        # Log the user prompt
        log_user_prompt(conversation_id, input_data)

        # Handle conversation naming (shows dialog for new conversations)
        handle_conversation_naming(conversation_id, prompt)

        # Manage session data with JSON structure
        if args.store_last_prompt or args.name_agent:
            manage_session_data(conversation_id, prompt, name_agent=args.name_agent)

        # Validate prompt if requested and not in log-only mode
        if args.validate and not args.log_only:
            is_valid, reason = validate_prompt(prompt)
            if not is_valid:
                # Return continue: false to block the prompt
                result = {"continue": False}
                print(json.dumps(result))
                sys.exit(0)

        # Success - prompt will be processed
        # Return continue: true to allow the prompt
        result = {"continue": True}
        print(json.dumps(result))
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully - allow by default
        result = {"continue": True}
        print(json.dumps(result))
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully - allow by default
        result = {"continue": True}
        print(json.dumps(result))
        sys.exit(0)


if __name__ == '__main__':
    main()
