"""Detect macOS sleep/wake via monotonic vs wall clock drift.

time.monotonic() pauses during sleep; time.time() does not.
If wall clock advanced much more than monotonic between polls,
the machine was asleep.
"""

import time


class SleepDetector:
  def __init__(self, drift_threshold=30):
    self.drift_threshold = drift_threshold
    self._last_monotonic = time.monotonic()
    self._last_wall = time.time()

  def check(self):
    """Return sleep duration in seconds if sleep detected, else 0."""
    now_mono = time.monotonic()
    now_wall = time.time()

    mono_elapsed = now_mono - self._last_monotonic
    wall_elapsed = now_wall - self._last_wall
    drift = wall_elapsed - mono_elapsed

    self._last_monotonic = now_mono
    self._last_wall = now_wall

    if drift > self.drift_threshold:
      return drift
    return 0
