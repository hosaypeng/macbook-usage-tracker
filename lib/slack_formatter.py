"""Build Slack mrkdwn message from usage data."""

from datetime import date


def _fmt_duration(seconds):
  """Format seconds as 'Xh Ym'."""
  h = int(seconds) // 3600
  m = (int(seconds) % 3600) // 60
  return f"{h}h {m:02d}m"


def format_report(app_durations, total_seconds, idle_seconds,
                  top_switch_pair, top_switch_count, top_n=5, day=None):
  """Build the Slack message string.

  Args:
    app_durations: dict {app_name: seconds} sorted desc by seconds
    total_seconds: total active (non-idle) tracked time in seconds
    idle_seconds: total idle time in seconds
    top_switch_pair: tuple (app_a, app_b) or None
    top_switch_count: int
    top_n: how many apps to show individually
    day: date object (default: today)
  """
  if day is None:
    day = date.today()

  day_name = day.strftime("%A")
  lines = [f":bar_chart: *App Usage Summary for {day.isoformat()} ({day_name})*"]
  lines.append("")
  lines.append(f"Total tracked time: {_fmt_duration(total_seconds)}")
  lines.append("")

  sorted_apps = sorted(app_durations.items(), key=lambda x: x[1], reverse=True)

  top_apps = sorted_apps[:top_n]
  other_apps = sorted_apps[top_n:]

  # Find max app name length for alignment
  name_widths = [len(name) for name, _ in top_apps]
  if other_apps:
    other_label = f"Other ({len(other_apps)} apps)"
    name_widths.append(len(other_label))
  max_name = max(name_widths) if name_widths else 10

  for name, secs in top_apps:
    pct = (secs / total_seconds * 100) if total_seconds > 0 else 0
    dur = _fmt_duration(secs)
    lines.append(f"  {name:<{max_name}}  {dur}  ({pct:.1f}%)")

  if other_apps:
    other_secs = sum(s for _, s in other_apps)
    pct = (other_secs / total_seconds * 100) if total_seconds > 0 else 0
    dur = _fmt_duration(other_secs)
    other_label = f"Other ({len(other_apps)} apps)"
    lines.append(f"  {other_label:<{max_name}}  {dur}  ({pct:.1f}%)")

  lines.append("")

  if top_switch_pair and top_switch_count > 0:
    a, b = top_switch_pair
    lines.append(f"Top switch: {a} <-> {b} ({top_switch_count} times)")

  lines.append(f"Idle time excluded: {_fmt_duration(idle_seconds)}")

  return "\n".join(lines)
