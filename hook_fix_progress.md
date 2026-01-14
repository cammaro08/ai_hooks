# Hook Fix

## Problem
Hooks were not running. Two issues identified:
1. Sandbox was blocking writes to `~/.claude/logs/`
2. Hooks were not configured in `~/.claude/settings.json`

## Fixes Applied

### Fix 1: Sandbox Permissions
Updated `.claude/settings.local.json` to allow writes to:
- `/Users/talha.sheikh/.claude/logs`
- `/Users/talha.sheikh/.claude/data`

### Fix 2: Hooks Configuration
Added hooks to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "~/.claude/hooks/before_shell.py"}]}],
    "PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "~/.claude/hooks/after_shell.py"}]}],
    "UserPromptSubmit": [{"matcher": "", "hooks": [{"type": "command", "command": "~/.claude/hooks/before_submit.py"}]}],
    "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "~/.claude/hooks/stop.py"}]}]
  }
}
```

## Next Steps
1. Restart Claude Code
2. Start new conversation
3. Run: `echo "test"` - check if `~/.claude/logs/before_shell.json` exists
4. Run: `rm -rf /tmp/test` - should be blocked

## Expected Behavior
- Dangerous commands blocked by `before_shell.py`
- Logs created in `~/.claude/logs/`
- Session data in `~/.claude/data/sessions/`

## Status
- [x] Sandbox permissions configured
- [x] Hooks added to settings.json
- [x] Claude Code restarted and hooks activated
- [x] All hooks tested and working

## Test Results (2026-01-14 17:30)

### ✅ Hooks Working
1. **before_shell.py (PreToolUse:Bash)**
   - Dangerous command blocking: ✅ Working
   - Test: `rm -rf /tmp/test` was blocked successfully
   - Logging: Commands logged to `~/.claude/logs/before_shell.json`

2. **after_shell.py (PostToolUse:Bash)**
   - Logging: Command outputs logged to `~/.claude/logs/after_shell.json`
   - Timestamps show active logging (17:29)

3. **before_submit.py (UserPromptSubmit)**
   - Logging: User prompts logged to `~/.claude/logs/before_submit.json`
   - Chat naming dialog: Works for NEW conversations only
   - Current conversation already named "haha", so dialog skips

4. **stop.py (Stop)**
   - Logging: Stop events logged to `~/.claude/logs/stop.json`
   - Audio notifications: ⚠️ Required fix

### 🔧 Audio Notification Fix
**Problem**: Audio notifications weren't playing when Claude finished processing

**Root Cause**: The `stop.py` hook requires `--notify` flag to enable TTS

**Fix Applied**: Updated `~/.claude/settings.json`:
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

**TTS Setup**:
- Script: `~/.claude/hooks/utils/tts/pyttsx3_tts.py`
- Uses local TTS (no API keys needed)
- Auto-installs pyttsx3 via uv inline dependencies
- Announcement format: "Chat {name}, {completion_message}"

**Next Step**: Restart Claude Code to activate audio notifications

## Final Status
- [x] All hooks configured and tested
- [x] Dangerous command blocking working
- [x] All logging working
- [x] Chat naming working (for new conversations)
- [x] Audio notification flag added
- [ ] Restart Claude Code to enable audio
