"""Tests for POST /planner/assistant.

Integration test: requires Atlas indexes, populated chunks collection,
Postgres connectivity, and a live OpenRouter API key.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

import backend.db
from backend.api.app import app
from backend.db import connect, connect_postgres, disconnect, disconnect_postgres
from backend.monitoring.models import UsageLog
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner.models import ExchangePlan


@pytest.fixture(autouse=True)
async def db_connection():
    """Set up database connections and reset quota usage and planner rows for each test."""
    await connect()
    await connect_postgres()

    sessionmaker = backend.db._pg_sessionmaker
    if sessionmaker is not None:
        async with sessionmaker() as session:
            # check_user_quota enforces against DEMO_USER_ID regardless of
            # caller identity, so tests must clear usage logged against it.
            await session.execute(delete(UsageLog).where(UsageLog.user_id == DEMO_USER_ID))
            # Deleting the plan cascades to its host schools and course matches.
            await session.execute(delete(ExchangePlan).where(ExchangePlan.user_id == DEMO_USER_ID))
            await session.commit()

    yield

    try:
        await disconnect_postgres()
    except Exception:
        pass
    try:
        await disconnect()
    except Exception:
        pass


@pytest.mark.asyncio
async def test_planner_assistant_returns_200():
    """POST /planner/assistant with a valid message must return 200 OK."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/planner/assistant",
            json={"message": "What phase am I in and what should I do next?"},
            timeout=120,
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_planner_assistant_response_has_message():
    """Response must contain a non-empty synthesized message."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/planner/assistant",
            json={"message": "What phase am I in and what should I do next?"},
            timeout=120,
        )
    body = response.json()
    assert body["message"].strip() != ""


@pytest.mark.asyncio
async def test_planner_assistant_logs_usage():
    """A successful call must write a UsageLog row for the current user."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/planner/assistant",
            json={"message": "What phase am I in and what should I do next?"},
            timeout=120,
        )
    assert response.status_code == 200

    sessionmaker = backend.db._pg_sessionmaker
    async with sessionmaker() as session:
        result = await session.execute(select(UsageLog).where(UsageLog.user_id == DEMO_USER_ID))
        logs = result.scalars().all()
    assert len(logs) == 1
    assert logs[0].tokens_used > 0
