#!/usr/bin/env python3
"""Background daemon: polls frontmost app every 5s and logs to JSONL."""

import signal
import sys
import time
from datetime import datetime, timezone

from lib.app_monitor import get_frontmost_app, get_idle_seconds
from lib.config import ensure_dirs, load_config
from lib.sleep_detector import SleepDetector
from lib.storage import append

running = True


def handle_signal(signum, frame):
  global running
  running = False


def main():
  signal.signal(signal.SIGTERM, handle_signal)
  signal.signal(signal.SIGINT, handle_signal)

  cfg = load_config()
  poll_interval = int(cfg["tracker"]["poll_interval"])
  idle_threshold = int(cfg["tracker"]["idle_threshold"])
  idle_check_interval = int(cfg["tracker"]["idle_check_interval"])
  sleep_drift_threshold = int(cfg["tracker"]["sleep_drift_threshold"])
  debounce_seconds = int(cfg["tracker"]["debounce_seconds"])

  ensure_dirs()

  sleep_detector = SleepDetector(drift_threshold=sleep_drift_threshold)
  last_app = None
  last_app_time = 0.0
  last_idle_check = 0.0
  is_idle = False
  polls_since_idle_check = 0

  print(f"apptracker started (poll={poll_interval}s, idle_threshold={idle_threshold}s)",
        flush=True)

  while running:
    loop_start = time.monotonic()

    # Check for sleep gap
    sleep_gap = sleep_detector.check()
    if sleep_gap > 0:
      ts = datetime.now(timezone.utc).isoformat()
      append({"ts": ts, "event": "wake", "sleep_seconds": int(sleep_gap)})
      print(f"wake detected after {int(sleep_gap)}s sleep", flush=True)
      # Reset idle state after wake
      is_idle = False
      last_idle_check = 0.0

    # Get frontmost app
    app = get_frontmost_app()
    if app is None:
      time.sleep(poll_interval)
      continue

    now = time.monotonic()

    # Debounce: ignore app if it changed less than debounce_seconds ago
    if app != last_app:
      if last_app is not None and (now - last_app_time) < debounce_seconds:
        # Flicker — keep previous app
        app = last_app
      else:
        last_app = app
        last_app_time = now

    # Check idle periodically (every idle_check_interval seconds)
    polls_since_idle_check += 1
    if polls_since_idle_check * poll_interval >= idle_check_interval:
      polls_since_idle_check = 0
      idle_secs = get_idle_seconds()
      if idle_secs is not None:
        is_idle = idle_secs >= idle_threshold

    # Write observation
    ts = datetime.now(timezone.utc).isoformat()
    append({"ts": ts, "app": app, "idle": is_idle})

    # Sleep until next poll
    elapsed = time.monotonic() - loop_start
    sleep_time = max(0, poll_interval - elapsed)
    time.sleep(sleep_time)

  print("apptracker stopped", flush=True)


if __name__ == "__main__":
  sys.exit(main() or 0)
