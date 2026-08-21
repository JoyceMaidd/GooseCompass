"""Tests for POST /query.

Integration test: requires Atlas indexes, populated chunks collection,
OpenAI embeddings API, and OpenRouter generation API.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

import backend.db
from backend.api.app import app
from backend.db import connect, connect_postgres, disconnect, disconnect_postgres
from backend.monitoring.models import UsageLog
from backend.monitoring.quota import DEMO_USER_ID


@pytest.fixture(autouse=True)
async def db_connection():
    """Set up database connection and reset quota usage for each test."""
    await connect()
    await connect_postgres()

    sessionmaker = backend.db._pg_sessionmaker
    if sessionmaker is not None:
        async with sessionmaker() as session:
            # check_user_quota enforces against DEMO_USER_ID regardless of
            # caller identity, so tests must clear usage logged against it.
            await session.execute(delete(UsageLog).where(UsageLog.user_id == DEMO_USER_ID))
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
async def test_query_returns_200():
    """POST /query with a valid question must return 200 OK."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={"query": "What GPA do I need to apply for exchange?"},
            timeout=120,
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_query_response_has_paragraphs():
    """Response must contain at least one non-empty paragraph with a citation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={"query": "What GPA do I need to apply for exchange?"},
            timeout=120,
        )
    body = response.json()
    assert len(body["paragraphs"]) >= 1
    assert body["paragraphs"][0]["text"].strip() != ""
    citations = body["paragraphs"][0]["citations"]
    assert len(citations) >= 1
    assert "id" in citations[0]
    assert "title" in citations[0]
