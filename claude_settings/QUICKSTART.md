# Quick Start Guide

This is a portable Claude Code configuration package. Copy this folder to any machine and follow the steps below.

## TL;DR Installation

```bash
# 1. Copy this folder to your new machine

# 2. Run the installation script
cd claude_settings
./install.sh

# 3. (Optional) Add your API keys
nano ~/.claude/hooks/.env

# 4. Start Claude Code
claude
```

## What You Get

### Custom Status Line
```
🍎 ~/projects/myapp/ [sonnet-4.5] [main*+] [42k/200k (21%)]
```

Shows:
- 🍎 Apple icon
- Current directory (with ~ for home)
- Model name (sonnet-4.5, Opus-4, etc.)
- Git branch with status (* = unstaged, + = staged)
- Context usage (tokens used/available)

### Hooks
- **Safety**: Blocks dangerous commands (rm -rf, .env access)
- **Logging**: Tracks all commands and prompts
- **Conversation naming**: Auto-names chats for easy reference
- **TTS announcements** (optional): Announces when tasks complete

## Manual Installation

If you prefer to install manually:

```bash
# Install hooks
mkdir -p ~/.claude/hooks
cp -r hooks/* ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py
chmod +x ~/.claude/hooks/utils/llm/*.py
chmod +x ~/.claude/hooks/utils/tts/*.py

# Install settings
cp settings.json ~/.claude/settings.json

# (Optional) Set up API keys
cp .env.sample ~/.claude/hooks/.env
nano ~/.claude/hooks/.env
```

## Requirements

- **jq**: For JSON parsing in status line
  - macOS: `brew install jq`
  - Linux: `apt-get install jq`

- **uv**: For Python script dependencies (optional but recommended)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Optional Features

### Enable TTS Announcements

Edit `~/.claude/settings.json` and change:
```json
"command": "~/.claude/hooks/stop.py"
```
to:
```json
"command": "~/.claude/hooks/stop.py --notify"
```

Then add API keys to `~/.claude/hooks/.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
# or
ANTHROPIC_API_KEY=sk-ant-your-key-here
# or
ELEVENLABS_API_KEY=sk_your-key-here
```

## Verification

After installation, verify it works:

1. **Status line**: Open Claude Code and check the status line
2. **Hooks**: Try running a command in Claude Code
3. **Logs**: Check `ls ~/.claude/logs/` for log files

## Troubleshooting

- **Status line not showing**: Make sure `jq` is installed
- **Hooks not working**: Make sure `uv` is installed and scripts are executable
- **TTS not working**: Check API keys in `~/.claude/hooks/.env`

See [README.md](README.md) for detailed documentation.
