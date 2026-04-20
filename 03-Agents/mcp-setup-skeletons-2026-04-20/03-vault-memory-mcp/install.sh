#!/bin/bash
# Install vault-memory-mcp as a Python venv-based MCP server
set -euo pipefail

TARGET_DIR="${1:-$HOME/.claude/mcp-servers/vault-memory-mcp}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing vault-memory-mcp to: $TARGET_DIR"

mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/server.py" "$TARGET_DIR/server.py"
cp "$SCRIPT_DIR/pyproject.toml" "$TARGET_DIR/pyproject.toml"

cd "$TARGET_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet mcp

echo ""
echo "Installation complete."
echo ""
echo "Test with:"
echo "  cd $TARGET_DIR"
echo "  source .venv/bin/activate"
echo "  VAULT_MEMORY_WORKSPACE=/home/piet/.openclaw/workspace python server.py"
echo ""
echo "Or register in .claude/settings.local.json (see 02-settings.local.json template)."
