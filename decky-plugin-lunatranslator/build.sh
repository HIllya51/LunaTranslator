#!/bin/bash
# Build script for LunaTranslator Decky Plugin

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Building LunaTranslator Decky Plugin"
echo "=========================================="
echo ""

# Check for pnpm
if ! command -v pnpm &> /dev/null; then
    echo "pnpm not found. Trying npm..."
    if ! command -v npm &> /dev/null; then
        echo "ERROR: Neither pnpm nor npm found!"
        echo "Please install Node.js and pnpm first."
        exit 1
    fi
    PKG_MANAGER="npm"
else
    PKG_MANAGER="pnpm"
fi

echo "[1/3] Installing dependencies..."
$PKG_MANAGER install

echo "[2/3] Building frontend..."
$PKG_MANAGER run build

echo "[3/3] Build complete!"
echo ""
echo "Files created:"
ls -la dist/

echo ""
echo "=========================================="
echo "  Build Successful!"
echo "=========================================="
echo ""
echo "To install on Steam Deck, run:"
echo "  ./install.sh"
echo ""
