# apptracker

## Overview

macOS background daemon that tracks which app is in the foreground throughout the day and sends a daily usage summary to Slack at 10 PM. Zero external dependencies -- uses only Python stdlib and macOS system commands (`osascript`, `ioreg`).

## File Structure

- `tracker.py` -- Background daemon. Polls frontmost app every 5s, detects idle time and sleep/wake, logs observations as JSONL
- `report.py` -- Daily aggregator. Reads JSONL log, computes per-app durations, posts formatted summary to Slack
- `lib/app_monitor.py` -- `osascript` (frontmost app) and `ioreg` (idle time) wrappers
- `lib/sleep_detector.py` -- Clock drift detection (monotonic vs wall clock) to identify macOS sleep/wake
- `lib/storage.py` -- JSONL read/write for daily logs at `~/.apptracker/logs/YYYY-MM-DD.jsonl`
- `lib/slack_formatter.py` -- Slack message builder (mrkdwn format)
- `lib/config.py` -- Config loader with defaults, reads `~/.apptracker/config.ini`
- `launchd/` -- macOS launchd plist files for tracker daemon and daily report
- `setup.sh` -- Install script: copies files to `~/.apptracker/`, prompts for Slack webhook, loads launchd services
- `uninstall.sh` -- Clean removal: unloads services, optionally removes data
- `config.ini.example` -- Template config with all available settings

## Related Repos

- **Obsidian vault** (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`) -- Personal knowledge base. No direct data dependency.
- **peng-ai** (`~/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/peng-ai/`) -- Slack bot for habit tracking. Shares the same Slack workspace but operates independently.

## Environment

- Python 3 (`/opt/homebrew/bin/python3`)
- Zero pip dependencies -- stdlib only (`configparser`, `json`, `subprocess`, `urllib.request`)
- macOS Accessibility permission required for `osascript` (System Settings > Privacy & Security > Accessibility)
- Runtime data at `~/.apptracker/` (logs, config)

## Conventions

- 2-space indentation
- Snake_case filenames
- Zero external dependencies (stdlib `urllib` for HTTP, `osascript`/`ioreg` for system queries)
- All scripts run from `~/.apptracker/` working directory (not the repo)

## Verification

- `launchctl list | grep apptracker` -- Check both services are loaded
- `cat ~/.apptracker/logs/$(date +%Y-%m-%d).jsonl | tail -5` -- Verify tracker is logging
- `python3 report.py` -- Run report manually (posts to Slack if webhook configured)
- Check `~/.apptracker/logs/tracker.stderr.log` for daemon errors
- Check `~/.apptracker/logs/report.stderr.log` for report errors

## Rules

- Never commit `config.ini` or expose webhook URLs in logs/output
- Never push without explicit permission
- launchd plists reference hardcoded paths (`/Users/hsp/.apptracker/`) -- update if username changes

## Lessons

