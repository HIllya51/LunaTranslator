#!/bin/bash
# LunaTranslator Decky Plugin Uninstaller

PLUGIN_NAME="LunaTranslator Overlay"
PLUGIN_DIR="$HOME/homebrew/plugins/$PLUGIN_NAME"

echo "=========================================="
echo "  LunaTranslator Decky Plugin Uninstaller"
echo "=========================================="
echo ""

if [ -d "$PLUGIN_DIR" ]; then
    echo "Removing plugin directory..."
    rm -rf "$PLUGIN_DIR"
    echo "Plugin removed successfully!"
    echo ""
    echo "Please restart Steam or reboot to complete uninstallation."
else
    echo "Plugin not found at: $PLUGIN_DIR"
    echo "Nothing to uninstall."
fi
