"""End-to-end tests for the generation pipeline.

Integration tests: require Atlas indexes and a populated chunks collection.
"""

import pytest
from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.generation.pipeline import answer
from backend.retrieval.pipeline import retrieve

_QUERY = "What GPA do I need to apply for exchange?"


async def _embed(text: str) -> list[float]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


@pytest.fixture(autouse=True)
async def db_connection():
    await connect()
    yield get_database()
    await disconnect()


@pytest.mark.asyncio
async def test_answer_end_to_end(db_connection):
    """Full pipeline: retrieve real chunks then generate a grounded response."""
    collection = db_connection[settings.mongodb_collection_chunks]
    embedding = await _embed(_QUERY)
    chunks = await retrieve(_QUERY, embedding, collection, top_k=5)

    result = await answer(_QUERY, chunks)

    assert len(result.paragraphs) >= 1
    assert all(len(p.text.strip()) > 0 for p in result.paragraphs)
    assert result.insufficient_context is False
    assert all(len(p.citations) >= 1 for p in result.paragraphs)
