from __future__ import annotations

from datetime import datetime, timedelta
from typing import Tuple, Union

IntervalType = Union[str, int, None]


def parse_interval_to_days(interval: IntervalType, default_days: int = 365) -> int:
    if interval is None:
        return default_days

    try:
        if isinstance(interval, int):
            return max(1, interval)

        s = str(interval).strip().lower()
        if not s:
            return default_days

        if s.isdigit():
            return max(1, int(s))

        unit = s[-1]
        value = s[:-1]
        if not value.isdigit():
            return default_days

        n = int(value)
        if unit == "d":
            return max(1, n)
        if unit == "m":
            return max(1, n * 30)
        if unit == "y":
            return max(1, n * 365)

        return default_days
    except Exception:
        return default_days


def calc_date_range(interval: IntervalType) -> Tuple[str, str, str]:
    days = parse_interval_to_days(interval)
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days)
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"), f"{days}d"
