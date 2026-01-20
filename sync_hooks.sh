#!/bin/bash
# Sync hooks from ~/.claude/hooks/ to this repo

SRC="$HOME/.claude/hooks"
DEST="$(dirname "$0")"

echo "Syncing hooks from $SRC to $DEST"

# Copy updated hook files
cp "$SRC/stop.py" "$DEST/stop.py"
echo "  Copied stop.py"

cp "$SRC/before_submit.py" "$DEST/before_submit.py"
echo "  Copied before_submit.py"

cp "$SRC/utils/llm/oai.py" "$DEST/utils/llm/oai.py"
echo "  Copied utils/llm/oai.py"

echo ""
echo "Done! Run 'git diff' to see changes."
