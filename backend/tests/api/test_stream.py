"""Tests for POST /query/stream.

Integration test: requires Atlas indexes, populated chunks collection,
OpenAI embeddings API, and OpenRouter generation API.
"""

import json

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.app import app
from backend.db import connect, disconnect


@pytest.fixture(autouse=True)
async def db_connection():
    await connect()
    yield
    await disconnect()


def _parse_sse(raw: str) -> list[dict]:
    """Parse a raw SSE response body into a list of event payloads.

    Args:
        raw: The full response text from a text/event-stream response.

    Returns:
        Ordered list of parsed JSON payloads.
    """
    events = []
    for line in raw.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: "):]))
    return events


@pytest.mark.asyncio
async def test_stream_returns_200():
    """POST /query/stream must return 200 with text/event-stream content type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/query/stream",
            json={"query": "What GPA do I need to apply for exchange?"},
            timeout=120,
        )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_stream_token_events_before_citations():
    """Token events must arrive before the final citations event."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/query/stream",
            json={"query": "What GPA do I need to apply for exchange?"},
            timeout=120,
        )
    events = _parse_sse(response.text)

    assert events[-1]["type"] == "citations"
    token_events = [e for e in events[:-1] if e["type"] == "token"]
    assert len(token_events) >= 1


@pytest.mark.asyncio
async def test_stream_reconstructed_text_nonempty():
    """Full text reconstructed from token events must be non-empty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/query/stream",
            json={"query": "What GPA do I need to apply for exchange?"},
            timeout=120,
        )
    events = _parse_sse(response.text)
    full_text = "".join(e["text"] for e in events if e["type"] == "token")
    assert full_text.strip() != ""
