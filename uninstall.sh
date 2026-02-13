#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.apptracker"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "=== apptracker uninstall ==="

# Unload launchd services
launchctl bootout "gui/$(id -u)/com.hosaypeng.apptracker" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/com.hosaypeng.apptracker-report" 2>/dev/null || true
echo "Unloaded launchd services"

# Remove plist files
rm -f "$LAUNCH_AGENTS/com.hosaypeng.apptracker.plist"
rm -f "$LAUNCH_AGENTS/com.hosaypeng.apptracker-report.plist"
echo "Removed plist files"

# Ask about data
read -rp "Remove logs and config at $INSTALL_DIR? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  rm -rf "$INSTALL_DIR"
  echo "Removed $INSTALL_DIR"
else
  echo "Kept $INSTALL_DIR (logs and config preserved)"
fi

echo ""
echo "=== Uninstall complete ==="
