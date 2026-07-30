"""Tests for quota/spend-cap period utilities."""

from datetime import datetime, timezone

from backend.monitoring.period import start_of_current_month


def test_start_of_current_month_is_first_of_month_utc():
    """start_of_current_month must return 00:00:00 UTC on the 1st of this month."""
    result = start_of_current_month()
    now = datetime.now(timezone.utc)

    assert result.day == 1
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0
    assert result.month == now.month
    assert result.year == now.year
    assert result.tzinfo == timezone.utc
