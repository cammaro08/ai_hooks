# Claude Code Setup - Complete Configuration

This folder contains a complete, portable setup for Claude Code with custom status line and hooks. Simply copy these files to a new machine and follow the setup instructions below.

## What This Includes

### Status Line Features
- **Apple emoji icon** (🍎) at the start
- **Current directory** with `~` for home directory
- **Model name** in blue (e.g., `[sonnet-4.5]`)
- **Git branch** with status indicators in purple:
  - Branch name in green
  - `*` in red for unstaged changes
  - `+` in yellow for staged changes
- **Context window usage** in cyan (e.g., `[42k/200k (21%)]`)

### Hook Features
- **PreToolUse (Bash)**: Validates and blocks dangerous shell commands
- **PostToolUse (Bash)**: Logs shell command execution
- **UserPromptSubmit**: Names conversations and logs prompts
- **Stop**: Announces completion via TTS with LLM-generated messages

### Utility Scripts
- **LLM utilities**: OpenAI, Anthropic, and Ollama clients for generating completion messages
- **TTS utilities**: ElevenLabs, OpenAI, and pyttsx3 for text-to-speech announcements

---

## Installation Instructions

### Prerequisites

1. **Claude Code CLI** must be installed
2. **uv** (Python package manager) must be installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **jq** (for status line JSON parsing):
   ```bash
   brew install jq  # macOS
   # or
   apt-get install jq  # Linux
   ```

### Step 1: Copy Hook Files

Copy all hook files to the Claude hooks directory:

```bash
# Navigate to where you downloaded/extracted this folder
cd /path/to/claude_settings

# Create hooks directory if it doesn't exist
mkdir -p ~/.claude/hooks

# Copy all hook scripts
cp -r hooks/* ~/.claude/hooks/

# Make hook scripts executable
chmod +x ~/.claude/hooks/*.py
chmod +x ~/.claude/hooks/utils/llm/*.py
chmod +x ~/.claude/hooks/utils/tts/*.py
```

### Step 2: Configure Settings

Copy the settings.json file to your Claude configuration:

```bash
# Backup existing settings (if any)
[ -f ~/.claude/settings.json ] && cp ~/.claude/settings.json ~/.claude/settings.json.backup

# Copy new settings
cp settings.json ~/.claude/settings.json
```

### Step 3: Set Up Environment Variables (Optional)

The hooks support various API services for enhanced functionality. These are **optional** but enable features like:
- TTS announcements when tasks complete
- LLM-generated completion messages
- Agent naming

```bash
# Copy the .env.sample to the hooks directory
cp .env.sample ~/.claude/hooks/.env

# Edit the .env file with your API keys
nano ~/.claude/hooks/.env  # or use your preferred editor
```

Example `.env` file:
```bash
# OpenAI API key (for TTS and LLM completion messages)
OPENAI_API_KEY=sk-your-key-here

# Anthropic API key (for LLM completion messages)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ElevenLabs API key (for premium TTS)
ELEVENLABS_API_KEY=sk_your-key-here

# Optional: Your name for personalized messages
ENGINEER_NAME=YourName

# Optional: Override Ollama model (default: gpt-oss:20b)
OLLAMA_MODEL=gpt-oss:20b
```

**Note**: If you don't provide API keys, the hooks will still work but with fallback functionality (no TTS, random completion messages).

### Step 4: Verify Installation

1. **Check status line**:
   ```bash
   # Open a new Claude Code session
   claude

   # You should see a status line like:
   # 🍎 ~/projects/myproject/ [sonnet-4.5] [main*] [42k/200k (21%)]
   ```

2. **Test hooks**:
   ```bash
   # In Claude Code, try running a safe shell command
   # You should see it execute normally

   # Try a dangerous command (it should be blocked):
   # rm -rf /
   # You should see: "BLOCKED: Dangerous rm command detected"
   ```

3. **Check logs** (to verify hooks are working):
   ```bash
   # Logs are stored in ~/.claude/logs/
   ls -la ~/.claude/logs/

   # You should see:
   # - before_submit.json
   # - before_shell.json
   # - after_shell.json
   # - stop.json
   # - conversation_names.json
   ```

---

## Status Line Breakdown

The status line command is a single bash script that displays contextual information. Here's what each part shows:

```
🍎 ~/projects/myapp/ [sonnet-4.5] [main*+] [42k/200k (21%)]
│  │                  │            │       │
│  │                  │            │       └─ Context usage (tokens used/total %)
│  │                  │            └─────── Git branch with status (* = unstaged, + = staged)
│  │                  └──────────────────── Model name (shortened)
│  └─────────────────────────────────────── Current directory (~ for home)
└────────────────────────────────────────── Apple icon
```

**Color coding**:
- Apple icon: Purple (magenta)
- Model name: Blue
- Git branch: Purple brackets, green branch name, red `*`, yellow `+`
- Context info: Cyan

---

## Hook Descriptions

### PreToolUse (before_shell.py)
Runs before every Bash command execution. Validates commands and blocks dangerous operations:
- Blocks `rm -rf` on dangerous paths (/, ~, etc.)
- Blocks access to `.env` files (protects secrets)
- Logs all commands to `~/.claude/logs/before_shell.json`

### PostToolUse (after_shell.py)
Runs after Bash command execution. Logs command results:
- Captures command output
- Stores execution history
- Logs to `~/.claude/logs/after_shell.json`

### UserPromptSubmit (before_submit.py)
Runs when you submit a prompt to Claude. Features:
- Shows macOS dialog to name new conversations
- Auto-generates conversation names from first words of prompt
- Logs prompts to `~/.claude/logs/before_submit.json`
- Stores session data in `~/.claude/data/sessions/`
- Can generate unique agent names for sessions

### Stop (stop.py)
Runs when Claude stops generating. Features:
- Announces completion via TTS (if `--notify` flag enabled)
- Generates completion messages using LLM or fallback
- Includes conversation name in announcement
- Logs to `~/.claude/logs/stop.json`

---

## Customization

### Changing the Status Line Icon

Edit `~/.claude/settings.json` and find the `printf` command at the end of the status line. Change `🍎` to any emoji or text:

```json
"printf '\\033[35m⚡\\033[0m %s/ %s%s%s' \"$dir\" \"$model_info\" \"$git_info\" \"$context_info\""
```

### Disabling Hooks

Remove or comment out hooks in `~/.claude/settings.json`:

```json
{
  "hooks": {
    // Comment out hooks you don't want:
    // "PreToolUse": [...],
    "UserPromptSubmit": [...]
  }
}
```

### Enabling TTS Announcements

By default, TTS is disabled. To enable it, edit the Stop hook in `~/.claude/settings.json`:

```json
"Stop": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "~/.claude/hooks/stop.py --notify"
      }
    ]
  }
]
```

Make sure you have API keys configured in `~/.claude/hooks/.env`.

### Changing TTS Voice

Edit the TTS script you're using:
- **ElevenLabs**: Change `voice_id` in `utils/tts/elevenlabs_tts.py`
- **OpenAI**: Change `voice` parameter in `utils/tts/openai_tts.py` (options: alloy, echo, fable, onyx, nova, shimmer)
- **pyttsx3**: Adjust `rate` and `volume` in `utils/tts/pyttsx3_tts.py`

---

## Troubleshooting

### Status Line Not Showing

1. Check if `jq` is installed:
   ```bash
   which jq
   ```

2. Verify settings.json syntax:
   ```bash
   jq . ~/.claude/settings.json
   ```

3. Check Claude logs:
   ```bash
   tail -f ~/.claude/debug/*.log
   ```

### Hooks Not Running

1. Verify hook scripts are executable:
   ```bash
   ls -la ~/.claude/hooks/*.py
   # Should show -rwxr-xr-x
   ```

2. Check if uv is installed and in PATH:
   ```bash
   which uv
   # Should show: /Users/yourusername/.local/bin/uv
   ```

3. Test hook manually:
   ```bash
   echo '{"command":"ls -la"}' | ~/.claude/hooks/before_shell.py
   # Should output: {"permission":"allow"}
   ```

### TTS Not Working

1. Check API keys in `.env`:
   ```bash
   cat ~/.claude/hooks/.env
   ```

2. Test TTS script manually:
   ```bash
   ~/.claude/hooks/utils/tts/pyttsx3_tts.py "test message"
   ```

3. Check logs:
   ```bash
   cat ~/.claude/logs/stop.json | jq '.[-1]'
   ```

### Python Dependencies Not Installing

The hooks use `uv` with inline script dependencies, which auto-install packages. If this fails:

1. Check uv version:
   ```bash
   uv --version
   ```

2. Try running a utility script directly:
   ```bash
   uv run ~/.claude/hooks/utils/llm/anth.py --completion
   ```

---

## File Structure

```
claude_settings/
├── README.md                          # This file
├── settings.json                      # Claude settings (status line + hooks)
├── .env.sample                        # Template for API keys
└── hooks/                             # Hook scripts
    ├── before_shell.py                # PreToolUse hook
    ├── after_shell.py                 # PostToolUse hook
    ├── before_submit.py               # UserPromptSubmit hook
    ├── stop.py                        # Stop hook
    └── utils/                         # Utility scripts
        ├── llm/                       # LLM clients
        │   ├── anth.py                # Anthropic client
        │   ├── oai.py                 # OpenAI client
        │   └── ollama.py              # Ollama client
        └── tts/                       # TTS clients
            ├── elevenlabs_tts.py      # ElevenLabs TTS
            ├── openai_tts.py          # OpenAI TTS
            └── pyttsx3_tts.py         # Offline TTS
```

---

## Data Storage Locations

All Claude data is stored in `~/.claude/`:

- **Settings**: `~/.claude/settings.json`
- **Logs**: `~/.claude/logs/`
  - `before_submit.json` - All user prompts
  - `before_shell.json` - All shell commands (pre-execution)
  - `after_shell.json` - All shell command results
  - `stop.json` - All stop events
  - `conversation_names.json` - Map of conversation IDs to friendly names
- **Session Data**: `~/.claude/data/sessions/`
  - One JSON file per conversation
  - Contains prompts and optional agent name

---

## Updating

To update your setup:

1. Backup current configuration:
   ```bash
   cp ~/.claude/settings.json ~/.claude/settings.json.backup
   tar -czf ~/.claude/hooks_backup.tar.gz ~/.claude/hooks/
   ```

2. Copy new files over:
   ```bash
   cp -r hooks/* ~/.claude/hooks/
   cp settings.json ~/.claude/settings.json
   ```

3. Preserve your `.env` file (don't overwrite it):
   ```bash
   # Your API keys are safe in ~/.claude/hooks/.env
   ```

---

## Uninstallation

To remove this setup:

```bash
# Remove settings (restores default Claude behavior)
rm ~/.claude/settings.json

# Remove hooks
rm -rf ~/.claude/hooks/

# Optionally, remove logs and data
rm -rf ~/.claude/logs/
rm -rf ~/.claude/data/
```

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Claude Code documentation: https://docs.claude.ai/
3. Check uv documentation: https://docs.astral.sh/uv/

---

## License

MIT License - Feel free to modify and share!
