"""Get frontmost app and system idle time via macOS system commands."""

import re
import subprocess


def get_frontmost_app():
  """Return the name of the frontmost application, or None on failure."""
  try:
    result = subprocess.run(
      ["osascript", "-e",
       'tell application "System Events" to get name of first application process whose frontmost is true'],
      capture_output=True, text=True, timeout=5,
    )
    name = result.stdout.strip()
    return name if name else None
  except (subprocess.TimeoutExpired, subprocess.SubprocessError):
    return None


def get_idle_seconds():
  """Return seconds since last user input (keyboard/mouse), or None on failure.

  Uses IOKit HIDIdleTime which reports in nanoseconds.
  """
  try:
    result = subprocess.run(
      ["ioreg", "-c", "IOHIDSystem", "-d", "4"],
      capture_output=True, text=True, timeout=5,
    )
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.stdout)
    if match:
      return int(match.group(1)) / 1_000_000_000
    return None
  except (subprocess.TimeoutExpired, subprocess.SubprocessError):
    return None
