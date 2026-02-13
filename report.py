#!/usr/bin/env python3
"""Daily report: reads today's JSONL log, aggregates, posts to Slack."""

import json
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import date

from lib.config import load_config
from lib.slack_formatter import format_report
from lib.storage import read


def aggregate(records, poll_interval=5):
  """Compute per-app durations, idle time, and top context-switch pair.

  Each non-idle observation counts as poll_interval seconds of usage.
  """
  app_durations = defaultdict(float)
  idle_seconds = 0.0
  switch_counts = Counter()
  prev_app = None

  for rec in records:
    # Skip non-observation records (e.g. wake events)
    if "app" not in rec:
      continue

    app = rec["app"]
    is_idle = rec.get("idle", False)

    if is_idle:
      idle_seconds += poll_interval
    else:
      app_durations[app] += poll_interval

    # Track context switches (only between different active apps)
    if not is_idle and prev_app and app != prev_app:
      pair = tuple(sorted([prev_app, app]))
      switch_counts[pair] += 1

    if not is_idle:
      prev_app = app

  total_seconds = sum(app_durations.values())

  top_switch_pair = None
  top_switch_count = 0
  if switch_counts:
    top_pair, top_count = switch_counts.most_common(1)[0]
    top_switch_pair = top_pair
    top_switch_count = top_count

  return dict(app_durations), total_seconds, idle_seconds, top_switch_pair, top_switch_count


def post_to_slack(webhook_url, text):
  """Post a message to Slack via incoming webhook."""
  payload = json.dumps({"text": text}).encode("utf-8")
  req = urllib.request.Request(
    webhook_url,
    data=payload,
    headers={"Content-Type": "application/json"},
  )
  with urllib.request.urlopen(req, timeout=15) as resp:
    return resp.status


def main():
  cfg = load_config()
  webhook_url = cfg["slack"]["webhook_url"]
  poll_interval = int(cfg["tracker"]["poll_interval"])
  top_n = int(cfg["report"]["top_n"])

  today = date.today()
  records = read(today)

  if not records:
    print(f"No records for {today.isoformat()}, skipping report.", flush=True)
    return 0

  app_durations, total_seconds, idle_seconds, top_switch_pair, top_switch_count = \
    aggregate(records, poll_interval)

  if total_seconds == 0:
    print(f"All observations idle for {today.isoformat()}, skipping report.", flush=True)
    return 0

  message = format_report(
    app_durations, total_seconds, idle_seconds,
    top_switch_pair, top_switch_count,
    top_n=top_n, day=today,
  )

  print(message, flush=True)

  if not webhook_url or "YOUR" in webhook_url:
    print("\nWebhook URL not configured — printed report only.", flush=True)
    return 0

  status = post_to_slack(webhook_url, message)
  print(f"Slack response: {status}", flush=True)
  return 0


if __name__ == "__main__":
  sys.exit(main() or 0)
