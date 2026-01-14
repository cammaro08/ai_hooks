#!/usr/bin/env python3
# Claude Hook: beforeShellExecution
# Adapted from Claude's pre_tool_use.py

import json
import sys
import re
from pathlib import Path


def is_dangerous_rm_command(command):
    """
    Comprehensive detection of dangerous rm commands.
    Matches various forms of rm -rf and similar destructive patterns.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = ' '.join(command.lower().split())

    # Pattern 1: Standard rm -rf variations
    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf, rm -fr, rm -Rf, etc.
        r'\brm\s+.*-[a-z]*f[a-z]*r',  # rm -fr variations
        r'\brm\s+--recursive\s+--force',  # rm --recursive --force
        r'\brm\s+--force\s+--recursive',  # rm --force --recursive
        r'\brm\s+-r\s+.*-f',  # rm -r ... -f
        r'\brm\s+-f\s+.*-r',  # rm -f ... -r
    ]

    # Check for dangerous patterns
    for pattern in patterns:
        if re.search(pattern, normalized):
            return True

    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    dangerous_paths = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~',           # Home directory
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards in general rm -rf context
        r'\.',          # Current directory
        r'\.\s*$',      # Current directory at end of command
    ]

    if re.search(r'\brm\s+.*-[a-z]*r', normalized):  # If rm has recursive flag
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True

    return False


def is_env_file_access(command):
    """
    Check if the command is trying to access .env files containing sensitive data.
    """
    # Pattern to detect .env file access (but allow .env.sample)
    env_patterns = [
        r'\b\.env\b(?!\.sample)',  # .env but not .env.sample
        r'cat\s+.*\.env\b(?!\.sample)',  # cat .env
        r'echo\s+.*>\s*\.env\b(?!\.sample)',  # echo > .env
        r'touch\s+.*\.env\b(?!\.sample)',  # touch .env
        r'cp\s+.*\.env\b(?!\.sample)',  # cp .env
        r'mv\s+.*\.env\b(?!\.sample)',  # mv .env
    ]

    for pattern in env_patterns:
        if re.search(pattern, command):
            return True

    return False


def main():
    try:
        # Read JSON input from stdin (Claude format)
        input_data = json.load(sys.stdin)

        # Claude provides: conversation_id, generation_id, hook_event_name, workspace_roots, command, working_directory
        command = input_data.get('command', '')

        # Check for .env file access (blocks access to sensitive environment files)
        if is_env_file_access(command):
            result = {
                "permission": "deny",
                "user_message": "Access to .env files containing sensitive data is prohibited. Use .env.sample for template files instead.",
                "agent_message": "BLOCKED: Access to .env files containing sensitive data is prohibited"
            }
            print(json.dumps(result))
            sys.exit(3)  # Exit code 3 blocks tool call in Claude

        # Check for dangerous rm -rf commands
        if is_dangerous_rm_command(command):
            result = {
                "permission": "deny",
                "user_message": "Dangerous rm command detected and prevented for safety.",
                "agent_message": "BLOCKED: Dangerous rm command detected and prevented"
            }
            print(json.dumps(result))
            sys.exit(3)  # Exit code 3 blocks tool call in Claude

        # Ensure log directory exists
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'before_shell.json'

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

        # Allow the command to proceed
        result = {"permission": "allow"}
        print(json.dumps(result))
        sys.exit(0)

    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors - allow by default
        result = {"permission": "allow"}
        print(json.dumps(result))
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully - allow by default
        result = {"permission": "allow"}
        print(json.dumps(result))
        sys.exit(0)


if __name__ == '__main__':
    main()
