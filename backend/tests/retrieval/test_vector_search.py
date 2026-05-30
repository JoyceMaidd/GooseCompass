"""Tests for backend/retrieval/vector_search.py.

Integration tests: require the Atlas vector_index to be Active and the
chunks collection to be populated from Phase 1 ingestion.
"""

import pytest
from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.retrieval.models import SearchResult
from backend.retrieval.vector_search import vector_search

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


class TestVectorSearch:
    async def test_returns_nonempty_results(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await vector_search(embedding, collection, k=10)
        assert len(results) > 0

    async def test_returns_search_result_models(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await vector_search(embedding, collection, k=5)
        for r in results:
            assert isinstance(r, SearchResult)

    async def test_all_results_have_content(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await vector_search(embedding, collection, k=10)
        for r in results:
            assert r.content.strip() != ""

    async def test_scores_are_positive(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await vector_search(embedding, collection, k=10)
        for r in results:
            assert r.score > 0

    async def test_results_capped_at_k(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await vector_search(embedding, collection, k=5)
        assert len(results) <= 5

    async def test_results_are_sorted_by_score_descending(self, db_connection):
        embedding = await _embed(_QUERY)
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await vector_search(embedding, collection, k=10)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
