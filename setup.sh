#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.apptracker"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "=== apptracker setup ==="

# Create directories
mkdir -p "$INSTALL_DIR/logs" "$INSTALL_DIR/lib"
mkdir -p "$LAUNCH_AGENTS"

# Copy source files
cp "$REPO_DIR/tracker.py" "$INSTALL_DIR/"
cp "$REPO_DIR/report.py" "$INSTALL_DIR/"
cp "$REPO_DIR/lib/"*.py "$INSTALL_DIR/lib/"

echo "Copied source files to $INSTALL_DIR"

# Config
if [ ! -f "$INSTALL_DIR/config.ini" ]; then
  read -rp "Enter your Slack webhook URL: " webhook_url
  sed "s|https://hooks.slack.com/services/YOUR/WEBHOOK/URL|$webhook_url|" \
    "$REPO_DIR/config.ini.example" > "$INSTALL_DIR/config.ini"
  chmod 600 "$INSTALL_DIR/config.ini"
  echo "Created config.ini (chmod 600)"
else
  echo "config.ini already exists, skipping"
fi

# Unload existing services (ignore errors if not loaded)
launchctl bootout "gui/$(id -u)/com.hosaypeng.apptracker" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/com.hosaypeng.apptracker-report" 2>/dev/null || true

# Install launchd plists
cp "$REPO_DIR/launchd/com.hosaypeng.apptracker.plist" "$LAUNCH_AGENTS/"
cp "$REPO_DIR/launchd/com.hosaypeng.apptracker-report.plist" "$LAUNCH_AGENTS/"

# Load services
launchctl bootstrap "gui/$(id -u)" "$LAUNCH_AGENTS/com.hosaypeng.apptracker.plist"
launchctl bootstrap "gui/$(id -u)" "$LAUNCH_AGENTS/com.hosaypeng.apptracker-report.plist"

echo ""
echo "=== Setup complete ==="
echo "Tracker daemon: running (KeepAlive)"
echo "Daily report:   fires at 22:00"
echo "Logs:           $INSTALL_DIR/logs/"
echo ""
echo "Verify with: launchctl list | grep apptracker"
