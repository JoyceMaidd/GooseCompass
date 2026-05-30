"""Tests for backend/retrieval/text_search.py.

Integration tests: require the Atlas text_index to be Active and the
chunks collection to be populated from Phase 1 ingestion.
"""

import pytest

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.retrieval.models import SearchResult
from backend.retrieval.text_search import text_search

_QUERY = "GPA eligibility requirements exchange application documents"


@pytest.fixture(autouse=True)
async def db_connection():
    await connect()
    yield get_database()
    await disconnect()


class TestTextSearch:
    async def test_returns_nonempty_results(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search(_QUERY, collection, k=10)
        assert len(results) > 0

    async def test_returns_search_result_models(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search(_QUERY, collection, k=5)
        for r in results:
            assert isinstance(r, SearchResult)

    async def test_all_results_have_content(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search(_QUERY, collection, k=10)
        for r in results:
            assert r.content.strip() != ""

    async def test_scores_are_positive(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search(_QUERY, collection, k=10)
        for r in results:
            assert r.score > 0

    async def test_results_capped_at_k(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search(_QUERY, collection, k=5)
        assert len(results) <= 5

    async def test_results_are_sorted_by_score_descending(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search(_QUERY, collection, k=10)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    async def test_keyword_match_returns_relevant_results(self, db_connection):
        collection = db_connection[settings.mongodb_collection_chunks]
        results = await text_search("exchange GPA eligibility", collection, k=10)
        # At least one top result should mention exchange or eligibility
        combined = " ".join(r.content.lower() for r in results[:3])
        assert any(kw in combined for kw in ("exchange", "eligibility", "gpa", "grade"))
