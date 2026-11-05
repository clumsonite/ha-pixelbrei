"""Time windows for pages and the quiet time (pure Python, no Home Assistant imports)."""

from __future__ import annotations

from datetime import time
from typing import Any


def parse_time(value: Any) -> time | None:
    """'HH:MM' or 'HH:MM:SS' (time selector) or a time; None/empty/invalid -> None."""
    if isinstance(value, time):
        return value
    if not value or not isinstance(value, str):
        return None
    try:
        parts = [int(p) for p in value.strip().split(":")]
    except ValueError:
        return None
    if not 2 <= len(parts) <= 3:
        return None
    try:
        return time(*parts)
    except ValueError:
        return None


def format_time(value: time) -> str:
    """The form the time selector stores: 'HH:MM:SS'."""
    return value.strftime("%H:%M:%S")


def in_window(now: time, start: Any, end: Any) -> bool:
    """True while now lies in [start, end); windows may run past midnight (22:00-06:00).

    A missing start means "from midnight", a missing end "until midnight"; no limits or
    start == end mean "always".
    """
    start, end = parse_time(start), parse_time(end)
    if start is None and end is None:
        return True
    if start is None:
        return now < end
    if end is None:
        return now >= start
    if start == end:
        return True
    if start < end:
        return start <= now < end
    return now >= start or now < end


def in_quiet_time(now: time, start: Any, end: Any) -> bool:
    """Quiet time needs both limits; an incomplete or empty setting means no quiet time."""
    start, end = parse_time(start), parse_time(end)
    if start is None or end is None or start == end:
        return False
    return in_window(now, start, end)
