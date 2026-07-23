"""Tests for POST /query/stream.

Integration test: requires Atlas indexes, populated chunks collection,
OpenAI embeddings API, and OpenRouter generation API.
"""

import json

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.app import app
from backend.api.routes.query import _stream_response
from backend.db import connect, disconnect
from backend.generation.models import Citation, CitedParagraph, GeneratedResponse


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
async def test_stream_paragraph_end_events_follow_tokens():
    """Each paragraph's token events must be followed by a paragraph_end event."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/query/stream",
            json={"query": "What GPA do I need to apply for exchange?"},
            timeout=120,
        )
    events = _parse_sse(response.text)

    assert events[-1]["type"] == "paragraph_end"
    assert not any(e["type"] == "citations" for e in events)
    token_events = [e for e in events if e["type"] == "token"]
    assert len(token_events) >= 1


@pytest.mark.asyncio
async def test_stream_response_paragraph_end_count_matches_paragraphs():
    """_stream_response must emit one paragraph_end event per paragraph, in order."""
    response = GeneratedResponse(
        paragraphs=[
            CitedParagraph(
                text="First idea.",
                citations=[Citation(id="a", title="A", url="https://a.example")],
            ),
            CitedParagraph(
                text="Second idea.",
                citations=[
                    Citation(id="b", title="B", url="https://b.example"),
                    Citation(id="c", title="C", url="https://c.example"),
                ],
            ),
        ]
    )

    events = [json.loads(raw[len("data: "):].strip()) async for raw in _stream_response(response)]

    paragraph_ends = [e for e in events if e["type"] == "paragraph_end"]
    assert len(paragraph_ends) == 2
    assert [c["id"] for c in paragraph_ends[0]["citations"]] == ["a"]
    assert [c["id"] for c in paragraph_ends[1]["citations"]] == ["b", "c"]
    assert events[-1]["type"] == "paragraph_end"


@pytest.mark.asyncio
async def test_stream_response_dedupes_citations_per_paragraph():
    """Duplicate citations within a paragraph must be deduped in paragraph_end."""
    response = GeneratedResponse(
        paragraphs=[
            CitedParagraph(
                text="Some text.",
                citations=[
                    Citation(id="a", title="A", url="https://a.example"),
                    Citation(id="a", title="A", url="https://a.example"),
                    Citation(id="b", title="B", url="https://b.example"),
                ],
            ),
        ]
    )

    events = [json.loads(raw[len("data: "):].strip()) async for raw in _stream_response(response)]

    paragraph_ends = [e for e in events if e["type"] == "paragraph_end"]
    assert [c["id"] for c in paragraph_ends[0]["citations"]] == ["a", "b"]


@pytest.mark.asyncio
async def test_stream_response_citation_shape_omits_none_fields():
    """paragraph_end citations must omit unset optional fields, not send them as null."""
    response = GeneratedResponse(
        paragraphs=[
            CitedParagraph(
                text="Some text.",
                citations=[Citation(id="a", title="A")],
            ),
        ]
    )

    events = [json.loads(raw[len("data: "):].strip()) async for raw in _stream_response(response)]

    paragraph_ends = [e for e in events if e["type"] == "paragraph_end"]
    citation = paragraph_ends[0]["citations"][0]
    assert citation == {"id": "a", "title": "A"}
    assert "url" not in citation
    assert "snippet" not in citation
    assert "source_type" not in citation


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
