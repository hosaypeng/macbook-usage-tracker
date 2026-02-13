# macbook-usage-tracker

Tracks which app is in the foreground on macOS throughout the day and sends a daily summary to Slack at 10 PM. Zero external dependencies — uses only Python stdlib and macOS system commands (`osascript`, `ioreg`).

## How It Works

- **Tracker daemon** polls the frontmost app every 5 seconds via `osascript`
- Detects idle time (no keyboard/mouse input for 5+ minutes) via `ioreg`
- Detects sleep/wake via monotonic vs wall clock drift
- Logs observations as JSONL to `~/.apptracker/logs/YYYY-MM-DD.jsonl`
- **Daily report** fires at 10 PM, aggregates usage, and posts to Slack

## Slack Message

```
📊 App Usage Summary for 2026-02-13 (Thursday)

Total tracked time: 6h 42m

  Arc          2h 31m  (37.6%)
  VS Code      1h 48m  (26.9%)
  Slack        0h 52m  (12.9%)
  Mail         0h 34m  (8.5%)
  Finder       0h 22m  (5.5%)
  Other (4 apps)  0h 35m  (8.6%)

Top switch: Arc <-> VS Code (47 times)
Idle time excluded: 1h 18m
```

## Setup

### Prerequisites

- macOS with Python 3 (`/opt/homebrew/bin/python3`)
- [Slack incoming webhook URL](https://api.slack.com/messaging/webhooks)
- Accessibility permission for your terminal app (System Settings → Privacy & Security → Accessibility)

### Install

```bash
git clone https://github.com/hosaypeng/macbook-usage-tracker.git
cd macbook-usage-tracker
bash setup.sh
```

The setup script copies files to `~/.apptracker/`, prompts for your Slack webhook URL, and loads two launchd services:

| Service | Schedule |
|---------|----------|
| `com.hosaypeng.apptracker` | Always running (KeepAlive) |
| `com.hosaypeng.apptracker-report` | Daily at 22:00 |

### Verify

```bash
launchctl list | grep apptracker
```

### Uninstall

```bash
bash uninstall.sh
```

## Configuration

Edit `~/.apptracker/config.ini`:

```ini
[slack]
webhook_url = https://hooks.slack.com/services/...

[tracker]
poll_interval = 5          # seconds between polls
idle_threshold = 300       # seconds of no input before marking idle
idle_check_interval = 30   # seconds between idle checks
sleep_drift_threshold = 30 # clock drift to detect sleep
debounce_seconds = 2       # ignore app switches shorter than this

[report]
top_n = 5                  # number of apps to show individually
```

## Project Structure

```
├── tracker.py             # Background daemon
├── report.py              # Daily aggregator + Slack poster
├── lib/
│   ├── app_monitor.py     # osascript + ioreg wrappers
│   ├── sleep_detector.py  # Clock drift detection
│   ├── storage.py         # JSONL read/write
│   ├── slack_formatter.py # Slack message builder
│   └── config.py          # Config loader
├── launchd/               # launchd plist files
├── setup.sh               # Install script
└── uninstall.sh           # Clean removal
```
