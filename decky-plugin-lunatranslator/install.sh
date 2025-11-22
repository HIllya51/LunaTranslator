#!/bin/bash
# LunaTranslator Decky Plugin Installer
# Run this on your Steam Deck

set -e

PLUGIN_NAME="LunaTranslator Overlay"
PLUGIN_DIR="$HOME/homebrew/plugins/$PLUGIN_NAME"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  LunaTranslator Decky Plugin Installer"
echo "=========================================="
echo ""

# Check if Decky is installed
if [ ! -d "$HOME/homebrew" ]; then
    echo "ERROR: Decky Loader not found!"
    echo "Please install Decky Loader first:"
    echo "  https://decky.xyz/"
    exit 1
fi

echo "[1/5] Creating plugin directory..."
mkdir -p "$PLUGIN_DIR"

echo "[2/5] Copying plugin files..."
cp -r "$REPO_DIR/dist" "$PLUGIN_DIR/" 2>/dev/null || echo "  (dist not found, will need to build)"
cp "$REPO_DIR/main.py" "$PLUGIN_DIR/"
cp "$REPO_DIR/plugin.json" "$PLUGIN_DIR/"
cp "$REPO_DIR/package.json" "$PLUGIN_DIR/"
mkdir -p "$PLUGIN_DIR/defaults"
cp "$REPO_DIR/defaults/defaults.json" "$PLUGIN_DIR/defaults/"

echo "[3/5] Installing Python dependencies..."
pip install --user websockets

echo "[4/5] Setting permissions..."
chmod +x "$PLUGIN_DIR/main.py"

echo "[5/5] Done!"
echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Restart Steam or reboot your Steam Deck"
echo "  2. Open the Quick Access menu (... button)"
echo "  3. Find 'LunaTranslator' in Decky plugins"
echo ""
echo "Make sure LunaTranslator is running in Wine with"
echo "network service enabled on port 8080 (or configured port)"
echo ""
echo "For troubleshooting, check:"
echo "  $HOME/homebrew/logs/LunaTranslator Overlay/"
echo ""
