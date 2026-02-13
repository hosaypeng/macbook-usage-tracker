"""Load configuration from ~/.apptracker/config.ini."""

import configparser
import os
from pathlib import Path

BASE_DIR = Path.home() / ".apptracker"
CONFIG_PATH = BASE_DIR / "config.ini"
LOG_DIR = BASE_DIR / "logs"

DEFAULTS = {
  "slack": {
    "webhook_url": "",
  },
  "tracker": {
    "poll_interval": "5",
    "idle_threshold": "300",
    "idle_check_interval": "30",
    "sleep_drift_threshold": "30",
    "debounce_seconds": "2",
  },
  "report": {
    "top_n": "5",
  },
}


def load_config():
  """Load config from disk, falling back to defaults."""
  cfg = configparser.ConfigParser()
  for section, values in DEFAULTS.items():
    cfg[section] = values

  if CONFIG_PATH.exists():
    cfg.read(CONFIG_PATH)

  return cfg


def ensure_dirs():
  """Create runtime directories if they don't exist."""
  LOG_DIR.mkdir(parents=True, exist_ok=True)
