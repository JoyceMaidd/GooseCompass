"""POST /query and POST /query/stream routes — full RAG pipeline."""

import asyncio
import json
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_database, get_session
from backend.generation.models import Citation, CitedParagraph, GeneratedResponse
from backend.generation.pipeline import answer_with_usage
from backend.generation.rewriter import rewrite_query
from backend.monitoring.logging import log_usage_to_db
from backend.monitoring.quota import check_user_quota
from backend.monitoring.spend_cap import check_spend_cap
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


@router.post("/query", response_model=GeneratedResponse, response_model_exclude_none=True)
async def query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(check_user_quota),
    _: None = Depends(check_spend_cap),
) -> GeneratedResponse:
    """Run the full RAG pipeline for a user query.

    Pipeline: rewrite → embed → retrieve → generate. Checks quota before
    generation and spend-cap before LLM call. Logs usage asynchronously.

    Args:
        request: The query payload.
        background_tasks: FastAPI background task runner.
        session: Postgres async session (for quota/spend-cap/logging).
        user_id: User ID (from quota check; returned if under limit).
        _: Spend-cap check (raises if exceeded).

    Returns:
        A structured GeneratedResponse with paragraph-level citations.
    """
    start_time = time.time()
    rewritten = await rewrite_query(request.query)
    embedding = await _embed(rewritten)

    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    chunks = await retrieve(rewritten, embedding, collection, top_k=_TOP_K)

    response, input_tokens, output_tokens = await answer_with_usage(request.query, chunks)

    latency_ms = int((time.time() - start_time) * 1000)
    background_tasks.add_task(
        log_usage_to_db,
        session,
        user_id,
        input_tokens,
        output_tokens,
        200,
        latency_ms,
    )

    return response


async def _sse_event(payload: dict) -> str:
    """Format a dict as a single SSE data line.

    Args:
        payload: JSON-serialisable dict to send.

    Returns:
        An SSE-formatted string ending with the required double newline.
    """
    return f"data: {json.dumps(payload)}\n\n"


def _dedupe_citations(citations: list[Citation]) -> list[Citation]:
    """Remove duplicate citations (by id) while preserving order.

    Args:
        citations: Citations, possibly containing duplicates.

    Returns:
        The same citations with duplicates removed, order preserved.
    """
    seen: set[str] = set()
    deduped: list[Citation] = []
    for citation in citations:
        if citation.id not in seen:
            seen.add(citation.id)
            deduped.append(citation)
    return deduped


async def _stream_paragraph(paragraph: CitedParagraph) -> AsyncIterator[str]:
    """Stream one paragraph as word-by-word token events, then its paragraph_end.

    Args:
        paragraph: The cited paragraph to stream.

    Yields:
        SSE-formatted "token" events for each word, followed by one
        "paragraph_end" event carrying this paragraph's citations.
    """
    words = paragraph.text.split(" ")
    for i, word in enumerate(words):
        text = word if i == len(words) - 1 else word + " "
        yield await _sse_event({"type": "token", "text": text})
        await asyncio.sleep(0)  # yield control to the event loop

    citations = _dedupe_citations(paragraph.citations)
    yield await _sse_event(
        {
            "type": "paragraph_end",
            "citations": [c.model_dump(exclude_none=True) for c in citations],
        }
    )


async def _stream_response(response: GeneratedResponse) -> AsyncIterator[str]:
    """Yield SSE events from a GeneratedResponse, preserving paragraph boundaries.

    Each paragraph streams as token events followed by a paragraph_end event
    carrying that paragraph's own citations. The HTTP stream closing signals
    completion to the client — no separate "done" event is sent.

    Args:
        response: The fully generated structured response.

    Yields:
        SSE-formatted strings.
    """
    for paragraph in response.paragraphs:
        async for event in _stream_paragraph(paragraph):
            yield event


@router.post("/query/stream")
async def query_stream(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(check_user_quota),
    _: None = Depends(check_spend_cap),
) -> StreamingResponse:
    """Run the full RAG pipeline and stream the response as SSE.

    Token events arrive word-by-word within each paragraph; a paragraph_end
    event follows each paragraph's tokens, carrying that paragraph's own
    citations. The stream closes once the last paragraph_end has been sent.
    Checks quota before generation and spend-cap before LLM call. Logs usage
    asynchronously after streaming completes.

    Args:
        request: The query payload.
        background_tasks: FastAPI background task runner.
        session: Postgres async session (for quota/spend-cap/logging).
        user_id: User ID (from quota check; returned if under limit).
        _: Spend-cap check (raises if exceeded).

    Returns:
        A text/event-stream StreamingResponse.
    """
    start_time = time.time()
    rewritten = await rewrite_query(request.query)
    embedding = await _embed(rewritten)

    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    chunks = await retrieve(rewritten, embedding, collection, top_k=_TOP_K)

    response, input_tokens, output_tokens = await answer_with_usage(request.query, chunks)

    async def _stream_with_logging() -> AsyncIterator[str]:
        try:
            async for event in _stream_response(response):
                yield event
        finally:
            latency_ms = int((time.time() - start_time) * 1000)
            await log_usage_to_db(
                session,
                user_id,
                input_tokens,
                output_tokens,
                200,
                latency_ms,
            )

    return StreamingResponse(
        _stream_with_logging(),
        media_type="text/event-stream",
    )
