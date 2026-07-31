"""Tests for usage logging."""

from unittest.mock import AsyncMock

from backend.monitoring.logging import log_usage_to_db


async def test_log_usage_to_db_creates_row():
    """log_usage_to_db must create a UsageLog row with correct values."""
    mock_session = AsyncMock()
    user_id = 1
    input_tokens = 100
    output_tokens = 50
    status_code = 200
    latency_ms = 123

    await log_usage_to_db(mock_session, user_id, input_tokens, output_tokens, status_code, latency_ms)

    # Verify session.add was called with a UsageLog instance.
    assert mock_session.add.called
    log_entry = mock_session.add.call_args[0][0]
    assert log_entry.user_id == user_id
    assert log_entry.tokens_used == 150  # input + output
    assert log_entry.status_code == status_code
    assert log_entry.latency_ms == latency_ms
    # Cost: (100 / 1M) * 0.10 + (50 / 1M) * 0.40 = 0.00001 + 0.00002 = 0.00003
    assert abs(log_entry.cost_usd - 0.00003) < 0.000001


async def test_log_usage_to_db_cost_calculation():
    """Cost must be calculated correctly based on token counts and pricing."""
    # Test with known values: 1M input tokens, 1M output tokens
    # Cost = (1M / 1M) * 0.10 + (1M / 1M) * 0.40 = 0.50
    mock_session = AsyncMock()
    await log_usage_to_db(mock_session, 1, 1_000_000, 1_000_000, 200, 100)

    log_entry = mock_session.add.call_args[0][0]
    assert abs(log_entry.cost_usd - 0.50) < 0.0001
