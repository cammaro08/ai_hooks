#!/bin/bash
# Claude Code Setup - Test Script
# Verifies that the installation is working correctly

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Claude Code Setup - Test Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PASS=0
FAIL=0

# Helper functions
pass() {
    echo "✅ $1"
    ((PASS++))
}

fail() {
    echo "❌ $1"
    ((FAIL++))
}

warn() {
    echo "⚠️  $1"
}

# Test 1: Check jq
echo "Test 1: Checking jq installation..."
if command -v jq &> /dev/null; then
    pass "jq is installed"
else
    fail "jq is not installed (required for status line)"
fi
echo ""

# Test 2: Check uv
echo "Test 2: Checking uv installation..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    pass "uv is installed ($UV_VERSION)"
else
    fail "uv is not installed (required for hooks)"
fi
echo ""

# Test 3: Check settings.json
echo "Test 3: Checking settings.json..."
if [ -f ~/.claude/settings.json ]; then
    if jq empty ~/.claude/settings.json 2>/dev/null; then
        pass "settings.json exists and is valid JSON"
    else
        fail "settings.json exists but is invalid JSON"
    fi
else
    fail "settings.json not found at ~/.claude/settings.json"
fi
echo ""

# Test 4: Check hooks directory
echo "Test 4: Checking hooks directory..."
if [ -d ~/.claude/hooks ]; then
    pass "Hooks directory exists"

    # Check for hook files
    HOOKS=("before_shell.py" "after_shell.py" "before_submit.py" "stop.py")
    for hook in "${HOOKS[@]}"; do
        if [ -f ~/.claude/hooks/$hook ]; then
            if [ -x ~/.claude/hooks/$hook ]; then
                pass "  $hook exists and is executable"
            else
                fail "  $hook exists but is not executable"
            fi
        else
            fail "  $hook not found"
        fi
    done
else
    fail "Hooks directory not found at ~/.claude/hooks"
fi
echo ""

# Test 5: Check utility scripts
echo "Test 5: Checking utility scripts..."
if [ -d ~/.claude/hooks/utils/llm ]; then
    LLM_SCRIPTS=("anth.py" "oai.py" "ollama.py")
    for script in "${LLM_SCRIPTS[@]}"; do
        if [ -f ~/.claude/hooks/utils/llm/$script ]; then
            pass "  LLM script $script exists"
        else
            fail "  LLM script $script not found"
        fi
    done
else
    fail "LLM utils directory not found"
fi

if [ -d ~/.claude/hooks/utils/tts ]; then
    TTS_SCRIPTS=("elevenlabs_tts.py" "openai_tts.py" "pyttsx3_tts.py")
    for script in "${TTS_SCRIPTS[@]}"; do
        if [ -f ~/.claude/hooks/utils/tts/$script ]; then
            pass "  TTS script $script exists"
        else
            fail "  TTS script $script not found"
        fi
    done
else
    fail "TTS utils directory not found"
fi
echo ""

# Test 6: Test hook execution
echo "Test 6: Testing hook execution..."
if [ -x ~/.claude/hooks/before_shell.py ]; then
    TEST_INPUT='{"command":"echo test"}'
    RESULT=$(echo "$TEST_INPUT" | ~/.claude/hooks/before_shell.py 2>/dev/null)
    if echo "$RESULT" | jq -e '.permission == "allow"' &>/dev/null; then
        pass "before_shell.py executes correctly"
    else
        fail "before_shell.py did not return expected output"
    fi
else
    fail "Cannot test before_shell.py (not executable)"
fi
echo ""

# Test 7: Check .env file
echo "Test 7: Checking .env configuration..."
if [ -f ~/.claude/hooks/.env ]; then
    pass ".env file exists"

    # Check for API keys (without revealing them)
    if grep -q "OPENAI_API_KEY=sk-" ~/.claude/hooks/.env 2>/dev/null; then
        pass "  OpenAI API key is configured"
    else
        warn "  OpenAI API key not configured (optional)"
    fi

    if grep -q "ANTHROPIC_API_KEY=sk-ant-" ~/.claude/hooks/.env 2>/dev/null; then
        pass "  Anthropic API key is configured"
    else
        warn "  Anthropic API key not configured (optional)"
    fi

    if grep -q "ELEVENLABS_API_KEY=sk_" ~/.claude/hooks/.env 2>/dev/null; then
        pass "  ElevenLabs API key is configured"
    else
        warn "  ElevenLabs API key not configured (optional)"
    fi
else
    warn ".env file not found (optional features won't work)"
fi
echo ""

# Test 8: Check log directories
echo "Test 8: Checking log directories..."
if [ -d ~/.claude/logs ]; then
    pass "Logs directory exists"
else
    warn "Logs directory not found (will be created on first use)"
fi

if [ -d ~/.claude/data/sessions ]; then
    pass "Sessions directory exists"
else
    warn "Sessions directory not found (will be created on first use)"
fi
echo ""

# Test 9: Test status line command
echo "Test 9: Testing status line..."
STATUS_CMD=$(jq -r '.statusLine.command' ~/.claude/settings.json 2>/dev/null)
if [ -n "$STATUS_CMD" ]; then
    pass "Status line command found in settings.json"

    # Test with sample data
    SAMPLE_INPUT='{"model":{"display_name":"Claude 4.5 Sonnet"},"context_window":{"total_input_tokens":1000,"total_output_tokens":500,"context_window_size":200000,"used_percentage":0.75}}'
    STATUS_OUTPUT=$(echo "$SAMPLE_INPUT" | bash -c "$STATUS_CMD" 2>/dev/null)

    if [ -n "$STATUS_OUTPUT" ]; then
        pass "Status line command executes successfully"
        echo "     Output: $STATUS_OUTPUT"
    else
        fail "Status line command failed to execute"
    fi
else
    fail "Status line command not found in settings.json"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Test Results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All tests passed! Your installation is ready."
    echo ""
    echo "Start Claude Code with: claude"
else
    echo "⚠️  Some tests failed. Please review the output above."
    echo ""
    echo "Common fixes:"
    echo "  - Install jq: brew install jq"
    echo "  - Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  - Run install script: ./install.sh"
fi
echo ""
