"""POST /query and POST /query/stream routes — full RAG pipeline."""

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

from backend.config import settings
from backend.db import get_database
from backend.generation.models import GeneratedResponse
from backend.generation.pipeline import answer
from backend.generation.rewriter import rewrite_query
from backend.retrieval.pipeline import retrieve

router = APIRouter()

_TOP_K = 10


class QueryRequest(BaseModel):
    """Incoming query payload.

    Args:
        query: The user's natural-language question.
        session_history: Reserved for future multi-turn support; unused in MVP.
    """

    query: str
    session_history: list = []


async def _embed(text: str) -> list[float]:
    """Embed text using OpenAI text-embedding-3-small.

    Args:
        text: The string to embed.

    Returns:
        A 1536-dimensional embedding vector.
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


@router.post("/query", response_model=GeneratedResponse)
async def query(request: QueryRequest) -> GeneratedResponse:
    """Run the full RAG pipeline for a user query.

    Pipeline: rewrite → embed → retrieve → generate.

    Args:
        request: The query payload.

    Returns:
        A structured GeneratedResponse with paragraph-level citations.
    """
    rewritten = await rewrite_query(request.query)
    embedding = await _embed(rewritten)

    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    chunks = await retrieve(rewritten, embedding, collection, top_k=_TOP_K)

    return await answer(request.query, chunks)


async def _sse_event(payload: dict) -> str:
    """Format a dict as a single SSE data line.

    Args:
        payload: JSON-serialisable dict to send.

    Returns:
        An SSE-formatted string ending with the required double newline.
    """
    return f"data: {json.dumps(payload)}\n\n"


async def _stream_response(response: GeneratedResponse) -> AsyncIterator[str]:
    """Yield SSE events from a GeneratedResponse.

    Streams each paragraph word-by-word as token events, then emits a single
    final citations event containing all unique citation URLs.

    Args:
        response: The fully generated structured response.

    Yields:
        SSE-formatted strings.
    """
    all_citations: list[str] = []

    for paragraph in response.paragraphs:
        words = paragraph.text.split(" ")
        for i, word in enumerate(words):
            text = word if i == len(words) - 1 else word + " "
            yield await _sse_event({"type": "token", "text": text})
            await asyncio.sleep(0)  # yield control to the event loop

        all_citations.extend(paragraph.citations)

    seen: set[str] = set()
    unique_citations = [c for c in all_citations if not (c in seen or seen.add(c))]  # type: ignore[func-returns-value]
    yield await _sse_event({"type": "citations", "citations": unique_citations})


@router.post("/query/stream")
async def query_stream(request: QueryRequest) -> StreamingResponse:
    """Run the full RAG pipeline and stream the response as SSE.

    Token events arrive word-by-word; the final event carries all citations.

    Args:
        request: The query payload.

    Returns:
        A text/event-stream StreamingResponse.
    """
    rewritten = await rewrite_query(request.query)
    embedding = await _embed(rewritten)

    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    chunks = await retrieve(rewritten, embedding, collection, top_k=_TOP_K)

    response = await answer(request.query, chunks)

    return StreamingResponse(
        _stream_response(response),
        media_type="text/event-stream",
    )
