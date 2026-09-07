"""Tests for backend/planner/retrieval_tool.py.

Integration tests: require both Atlas indexes (vector_index, text_index) to
be Active and the chunks collection to be populated from Phase 1 ingestion.
"""

import pytest

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.planner.retrieval_tool import research_lookup
from backend.retrieval.models import SearchResult

_QUERY = "What GPA do I need to apply for exchange?"


@pytest.fixture(autouse=True)
async def db_connection():
    """Connect to Mongo for each test."""
    await connect()
    yield get_database()
    await disconnect()


@pytest.mark.integration
async def test_research_lookup_returns_search_results(db_connection):
    """research_lookup must return grounded SearchResult items for a real query."""
    collection = db_connection[settings.mongodb_collection_chunks]
    results = await research_lookup(_QUERY, collection)
    assert len(results) > 0
    for r in results:
        assert isinstance(r, SearchResult)
        assert r.content.strip() != ""


@pytest.mark.integration
async def test_research_lookup_respects_top_k(db_connection):
    """research_lookup must respect the top_k parameter."""
    collection = db_connection[settings.mongodb_collection_chunks]
    results = await research_lookup(_QUERY, collection, top_k=2)
    assert len(results) == 2
