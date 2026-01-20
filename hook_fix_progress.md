# Hook Fix Progress

## Configuration

### Hooks in `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "~/.claude/hooks/before_shell.py"}]}],
    "PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "~/.claude/hooks/after_shell.py"}]}],
    "UserPromptSubmit": [{"matcher": "", "hooks": [{"type": "command", "command": "~/.claude/hooks/before_submit.py"}]}],
    "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "~/.claude/hooks/stop.py --notify"}]}]
  }
}
```

### Sandbox Permissions in `.claude/settings.local.json`:
- `/Users/talha.sheikh/.claude/logs`
- `/Users/talha.sheikh/.claude/data`

## Hooks

| Hook | File | Function |
|------|------|----------|
| PreToolUse:Bash | `before_shell.py` | Blocks dangerous commands, logs to `before_shell.json` |
| PostToolUse:Bash | `after_shell.py` | Logs command outputs to `after_shell.json` |
| UserPromptSubmit | `before_submit.py` | Chat naming dialog, logs to `before_submit.json` |
| Stop | `stop.py --notify` | Audio notifications, logs to `stop.json` |

## Audio Notifications

Uses OpenAI's `gpt-4o-audio-preview` model for direct audio generation.

**Features:**
- Announces chat name: "Chat {name}, all done!"
- Different messages for completion vs permission requests
- Voice: nova

**Script:** `~/.claude/hooks/utils/llm/oai.py --completion-audio [chat_name] [reason]`

## Fixes Applied (2026-01-14)

1. **Field name fix**: Scripts use `session_id` (not `conversation_id`)
2. **Audio model**: Changed from pyttsx3 to OpenAI `gpt-4o-audio-preview`
3. **Parameter fix**: Use `max_completion_tokens` for newer OpenAI models

## Status

- [x] All hooks configured and working
- [x] Dangerous command blocking
- [x] All logging working
- [x] Chat naming dialog (new conversations)
- [x] Audio notifications with chat name

---

## Repo Sync Progress

### Done
- [x] `claude_settings/settings.json` - copied from `~/.claude/settings.json`

### To Do - Copy from `~/.claude/hooks/` to repo root:
- [ ] `stop.py` - updated with session_id fix + OpenAI audio
- [ ] `before_submit.py` - updated with session_id fix
- [ ] `utils/llm/oai.py` - updated with audio generation functions

### Files in sync (no changes needed):
- `before_shell.py`
- `after_shell.py`
- `utils/llm/anth.py`
- `utils/llm/ollama.py`
- `utils/tts/*.py`
