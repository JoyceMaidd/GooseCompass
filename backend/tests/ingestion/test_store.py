"""Tests for backend/ingestion/store.py.

These are integration tests that write to a real MongoDB collection.
A dedicated test collection is used and cleaned up after each test.
"""

import pytest

from backend.db import connect, disconnect, get_database
from backend.ingestion.models import Chunk
from backend.ingestion.store import prune_stale_chunks, upsert_chunks

_TEST_COLLECTION = "test_chunks_store"


def _make_chunk(index: int, source_url: str = "https://example.com/page") -> Chunk:
    return Chunk(
        content=f"Chunk content number {index}",
        embedding=[0.1] * 1536,
        source_url=source_url,
        document_title="Test Document",
        section_title="Test Section",
        document_type="web",
        chunk_index=index,
    )


@pytest.fixture(autouse=True)
async def clean_collection():
    await connect()
    db = get_database()
    await db[_TEST_COLLECTION].drop()
    yield db[_TEST_COLLECTION]
    await db[_TEST_COLLECTION].drop()
    await disconnect()


class TestUpsertChunks:
    async def test_inserts_three_chunks(self, clean_collection):
        chunks = [_make_chunk(i) for i in range(3)]
        count = await upsert_chunks(chunks, clean_collection)
        assert count == 3

    async def test_no_duplicates_on_second_upsert(self, clean_collection):
        chunks = [_make_chunk(i) for i in range(3)]
        await upsert_chunks(chunks, clean_collection)
        await upsert_chunks(chunks, clean_collection)
        total = await clean_collection.count_documents({})
        assert total == 3

    async def test_second_upsert_returns_modified_count(self, clean_collection):
        chunks = [_make_chunk(i) for i in range(3)]
        await upsert_chunks(chunks, clean_collection)
        count = await upsert_chunks(chunks, clean_collection)
        assert count == 3

    async def test_documents_have_correct_fields(self, clean_collection):
        chunk = _make_chunk(0)
        await upsert_chunks([chunk], clean_collection)
        doc = await clean_collection.find_one({"chunk_id": chunk.chunk_id})
        assert doc is not None
        assert doc["content"] == chunk.content
        assert doc["source_url"] == chunk.source_url
        assert len(doc["embedding"]) == 1536

    async def test_empty_input_returns_zero(self, clean_collection):
        count = await upsert_chunks([], clean_collection)
        assert count == 0

    async def test_partial_overlap_upserts_correctly(self, clean_collection):
        first_batch = [_make_chunk(i) for i in range(3)]
        await upsert_chunks(first_batch, clean_collection)

        second_batch = [_make_chunk(i) for i in range(2, 5)]
        await upsert_chunks(second_batch, clean_collection)

        total = await clean_collection.count_documents({})
        assert total == 5


class TestPruneStaleChunks:
    async def test_removes_chunks_for_dropped_source(self, clean_collection):
        kept = _make_chunk(0, source_url="https://example.com/kept")
        stale = _make_chunk(0, source_url="https://example.com/stale")
        await upsert_chunks([kept, stale], clean_collection)

        deleted = await prune_stale_chunks({"https://example.com/kept"}, clean_collection)

        assert deleted == 1
        remaining = await clean_collection.find_one({"source_url": "https://example.com/stale"})
        assert remaining is None
        assert await clean_collection.count_documents({}) == 1

    async def test_no_deletions_when_all_sources_current(self, clean_collection):
        chunks = [_make_chunk(i) for i in range(3)]
        await upsert_chunks(chunks, clean_collection)

        deleted = await prune_stale_chunks({"https://example.com/page"}, clean_collection)

        assert deleted == 0
        assert await clean_collection.count_documents({}) == 3

    async def test_empty_current_urls_deletes_everything(self, clean_collection):
        chunks = [_make_chunk(i) for i in range(3)]
        await upsert_chunks(chunks, clean_collection)

        deleted = await prune_stale_chunks(set(), clean_collection)

        assert deleted == 3
        assert await clean_collection.count_documents({}) == 0
