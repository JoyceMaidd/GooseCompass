"""Tests for backend/retrieval/pipeline.py.

Integration tests: require both Atlas indexes (vector_index, text_index) to
be Active and the chunks collection to be populated from Phase 1 ingestion.
"""

import pytest
from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.retrieval.models import SearchResult
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


class TestRetrieve:
    async def test_returns_ten_results(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=10)
        assert len(results) == 10

    async def test_returns_search_result_models(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=10)
        for r in results:
            assert isinstance(r, SearchResult)

    async def test_all_results_have_content(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=10)
        for r in results:
            assert r.content.strip() != ""

    async def test_all_results_have_source_url(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=10)
        for r in results:
            assert r.source_url.strip() != ""

    async def test_no_duplicate_chunk_ids(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=10)
        ids = [r.chunk_id for r in results]
        assert len(ids) == len(set(ids))

    async def test_sorted_by_score_descending(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=10)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    async def test_top_k_respected(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await retrieve(_QUERY, embedding, collection, top_k=3)
        assert len(results) == 3
