#!/usr/bin/env python3
# Cursor Hook: afterShellExecution
# Adapted from Claude's post_tool_use.py

import json
import sys
from pathlib import Path


def main():
    try:
        # Read JSON input from stdin (Cursor format)
        # Cursor provides: conversation_id, generation_id, hook_event_name, workspace_roots, command, output
        input_data = json.load(sys.stdin)

        # Ensure log directory exists
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'after_shell.json'

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

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Exit cleanly on any other error
        sys.exit(0)


if __name__ == '__main__':
    main()
