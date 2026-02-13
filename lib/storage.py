"""JSONL read/write for daily observation logs."""

import json
from datetime import date
from pathlib import Path

from lib.config import LOG_DIR


def _log_path(day=None):
  """Return the JSONL log path for a given date (default: today)."""
  if day is None:
    day = date.today()
  return LOG_DIR / f"{day.isoformat()}.jsonl"


def append(record, day=None):
  """Append a single JSON record to today's log file."""
  path = _log_path(day)
  with open(path, "a") as f:
    f.write(json.dumps(record) + "\n")


def read(day=None):
  """Read all records from a day's log file. Returns list of dicts."""
  path = _log_path(day)
  if not path.exists():
    return []
  records = []
  with open(path) as f:
    for line in f:
      line = line.strip()
      if line:
        records.append(json.loads(line))
  return records
