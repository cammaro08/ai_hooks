# Cursor AI Hooks

Custom hooks for Cursor IDE to enhance the AI agent experience.

## Features

- **Interactive Chat Naming**: Get prompted to name new chats (e.g., "10.12.3") for easy tracking
- **TTS Completion Announcements**: Hear when your chat finishes with the chat name included
- **Prompt Logging**: Track all prompts in JSON format
- **Session Management**: Store prompts per conversation with auto-generated agent names

## Hooks

### `beforeSubmitPrompt` (before_submit.py)
- Shows macOS dialog for custom chat naming on new conversations
- Auto-generates names from first 5 words if skipped
- Logs prompts to `~/.cursor/logs/before_submit.json`
- Manages session data in `~/.cursor/data/sessions/`

### `stop` (stop.py)
- Announces completion with chat name via TTS
- Supports multiple TTS services: ElevenLabs > OpenAI > pyttsx3
- Generates completion messages via LLM or random fallback
- Logs stop events to `~/.cursor/logs/stop.json`

### `beforeShellExecution` (before_shell.py)
- Validates shell commands before execution
- Can block dangerous commands

### `afterShellExecution` (after_shell.py)
- Logs shell command results
- Post-execution auditing

## Setup

1. Clone this repository:
   ```bash
   git clone git@github.com:cammaro08/ai_hooks.git ~/.cursor/hooks
   ```

2. Create `.env` file with your API keys:
   ```bash
   cd ~/.cursor/hooks
   cp .env.sample .env
   # Edit .env with your API keys
   ```

3. Install dependencies (via uv):
   ```bash
   # The hooks use uv to run Python scripts
   # Ensure uv is installed at ~/.local/bin/uv
   ```

4. Configure hooks in `~/.cursor/hooks.json`:
   ```json
   {
     "version": 1,
     "hooks": {
       "beforeShellExecution": [{ "command": "~/.cursor/hooks/before_shell.py" }],
       "afterShellExecution": [{ "command": "~/.cursor/hooks/after_shell.py" }],
       "beforeSubmitPrompt": [{ "command": "~/.cursor/hooks/before_submit.py --log-only --store-last-prompt --name-agent" }],
       "stop": [{ "command": "~/.cursor/hooks/stop.py --notify" }]
     }
   }
   ```

## Environment Variables

Create a `.env` file (not committed to git):
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
```

## Data Storage

- `~/.cursor/logs/conversation_names.json` - Maps conversation IDs to friendly names
- `~/.cursor/logs/before_submit.json` - Log of all submitted prompts
- `~/.cursor/logs/stop.json` - Log of all stop events
- `~/.cursor/data/sessions/*.json` - Per-conversation prompt history

## Utils

The `utils/` directory contains helper scripts:
- `utils/tts/` - Text-to-speech scripts (ElevenLabs, OpenAI, pyttsx3)
- `utils/llm/` - LLM clients for generating messages (OpenAI, Anthropic, Ollama)

## License

MIT
