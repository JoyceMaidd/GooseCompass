"""Quota/spend-cap period utilities."""

from datetime import datetime, timezone


def start_of_current_month() -> datetime:
    """Return the start of the current UTC calendar month (00:00:00 UTC on the 1st).

    Returns:
        A timezone-aware datetime at UTC midnight on the 1st of this month.
    """
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
