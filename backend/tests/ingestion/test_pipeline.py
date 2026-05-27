"""Tests for backend/ingestion/pipeline.py.

Full end-to-end integration test: fetches a real URL, chunks, embeds via
OpenAI, and upserts into a dedicated test MongoDB collection.
"""

import pytest

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.ingestion.pipeline import ingest_source

_TEST_COLLECTION = "test_chunks_pipeline"


@pytest.fixture(autouse=True)
async def clean_collection():
    await connect()
    db = get_database()
    await db[_TEST_COLLECTION].drop()
    yield db
    await db[_TEST_COLLECTION].drop()
    await disconnect()


class TestIngestSource:
    async def test_web_source_returns_positive_count(self, clean_collection, monkeypatch):
        monkeypatch.setattr(settings, "mongodb_collection_chunks", _TEST_COLLECTION)
        db = clean_collection
        count = await ingest_source(
            {"type": "web", "url": "https://uwaterloo.ca/international-experience/exchange-and-study-abroad/go-abroad/getting-started"},
            db,
        )
        assert count > 0

    async def test_chunks_present_in_collection(self, clean_collection, monkeypatch):
        monkeypatch.setattr(settings, "mongodb_collection_chunks", _TEST_COLLECTION)
        db = clean_collection
        await ingest_source(
            {"type": "web", "url": "https://uwaterloo.ca/international-experience/exchange-and-study-abroad/go-abroad/getting-started"},
            db,
        )
        total = await db[_TEST_COLLECTION].count_documents({})
        assert total > 0

    async def test_chunks_have_required_fields(self, clean_collection, monkeypatch):
        monkeypatch.setattr(settings, "mongodb_collection_chunks", _TEST_COLLECTION)
        db = clean_collection
        await ingest_source(
            {"type": "web", "url": "https://uwaterloo.ca/international-experience/exchange-and-study-abroad/go-abroad/getting-started"},
            db,
        )
        doc = await db[_TEST_COLLECTION].find_one({})
        assert doc is not None
        for field in ("chunk_id", "content", "embedding", "source_url", "document_title"):
            assert field in doc, f"Missing field: {field}"
        assert len(doc["embedding"]) == 1536

    async def test_idempotent_reingest(self, clean_collection, monkeypatch):
        monkeypatch.setattr(settings, "mongodb_collection_chunks", _TEST_COLLECTION)
        db = clean_collection
        source = {"type": "web", "url": "https://uwaterloo.ca/international-experience/exchange-and-study-abroad/go-abroad/getting-started"}
        await ingest_source(source, db)
        first_total = await db[_TEST_COLLECTION].count_documents({})
        await ingest_source(source, db)
        second_total = await db[_TEST_COLLECTION].count_documents({})
        assert first_total == second_total

    async def test_unknown_type_raises(self, clean_collection):
        with pytest.raises(ValueError, match="Unknown source type"):
            await ingest_source({"type": "ftp", "url": "ftp://example.com"}, clean_collection)
