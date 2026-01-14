#!/bin/bash
# Claude Code Setup - Installation Script
# This script installs the custom status line and hooks for Claude Code

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Claude Code Setup - Installation Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is not installed"
    echo "   Install it with: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
fi
echo "✅ jq is installed"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "⚠️  Warning: uv is not installed"
    echo "   Some hook features will not work without uv"
    echo "   Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ uv is installed"
fi

# Create backup if settings exist
if [ -f ~/.claude/settings.json ]; then
    BACKUP_FILE=~/.claude/settings.json.backup.$(date +%Y%m%d_%H%M%S)
    echo ""
    echo "📦 Backing up existing settings to:"
    echo "   $BACKUP_FILE"
    cp ~/.claude/settings.json "$BACKUP_FILE"
fi

# Create hooks directory
echo ""
echo "📁 Creating hooks directory..."
mkdir -p ~/.claude/hooks

# Copy hook files
echo "📝 Copying hook scripts..."
cp -r "$SCRIPT_DIR/hooks/"* ~/.claude/hooks/

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x ~/.claude/hooks/*.py
chmod +x ~/.claude/hooks/utils/llm/*.py
chmod +x ~/.claude/hooks/utils/tts/*.py

# Copy settings.json
echo "⚙️  Installing settings.json..."
cp "$SCRIPT_DIR/settings.json" ~/.claude/settings.json

# Copy .env.sample if .env doesn't exist
if [ ! -f ~/.claude/hooks/.env ]; then
    echo "📄 Creating .env template..."
    cp "$SCRIPT_DIR/.env.sample" ~/.claude/hooks/.env
    echo "⚠️  Note: Edit ~/.claude/hooks/.env to add your API keys"
else
    echo "✅ Existing .env file preserved"
fi

# Create log and data directories
echo "📊 Creating log directories..."
mkdir -p ~/.claude/logs
mkdir -p ~/.claude/data/sessions

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Next steps:"
echo ""
echo "1. (Optional) Edit your API keys:"
echo "   nano ~/.claude/hooks/.env"
echo ""
echo "2. Start a new Claude Code session:"
echo "   claude"
echo ""
echo "3. You should see a custom status line like:"
echo "   🍎 ~/projects/myapp/ [sonnet-4.5] [main*] [42k/200k (21%)]"
echo ""
echo "📚 For more info, see: $SCRIPT_DIR/README.md"
echo ""
