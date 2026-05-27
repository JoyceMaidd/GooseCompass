"""Tests for backend/ingestion/embedder.py.

These are integration tests that call the real OpenAI API.
They require OPENAI_API_KEY to be set in .env.
"""

import pytest

from backend.ingestion.embedder import embed_chunks
from backend.ingestion.models import Chunk, ChunkData

_EMBEDDING_DIM = 1536


def _make_chunk_data(content: str, index: int = 0) -> ChunkData:
    return ChunkData(
        content=content,
        source_url="https://example.com",
        document_title="Test Doc",
        section_title="Test Section",
        document_type="web",
        chunk_index=index,
    )


class TestEmbedChunks:
    async def test_returns_correct_count(self):
        chunks = [
            _make_chunk_data("Exchange students must maintain a 70% GPA.", 0),
            _make_chunk_data("Apply at least six months before departure.", 1),
            _make_chunk_data("Housing options vary by partner university.", 2),
        ]
        result = await embed_chunks(chunks)
        assert len(result) == 3

    async def test_each_embedding_is_1536_dims(self):
        chunks = [
            _make_chunk_data("Exchange students must maintain a 70% GPA.", 0),
            _make_chunk_data("Apply at least six months before departure.", 1),
            _make_chunk_data("Housing options vary by partner university.", 2),
        ]
        result = await embed_chunks(chunks)
        for chunk in result:
            assert len(chunk.embedding) == _EMBEDDING_DIM

    async def test_no_empty_embeddings(self):
        chunks = [
            _make_chunk_data("Short text A.", 0),
            _make_chunk_data("Short text B.", 1),
        ]
        result = await embed_chunks(chunks)
        for chunk in result:
            assert chunk.embedding
            assert any(v != 0.0 for v in chunk.embedding)

    async def test_returns_chunk_models(self):
        chunks = [_make_chunk_data("Some content.", 0)]
        result = await embed_chunks(chunks)
        assert isinstance(result[0], Chunk)
        assert result[0].content == "Some content."
        assert result[0].chunk_id  # auto-derived SHA-256

    async def test_metadata_preserved(self):
        chunk_data = _make_chunk_data("Content with metadata.", 5)
        result = await embed_chunks([chunk_data])
        r = result[0]
        assert r.source_url == "https://example.com"
        assert r.document_title == "Test Doc"
        assert r.section_title == "Test Section"
        assert r.document_type == "web"
        assert r.chunk_index == 5

    async def test_empty_input_returns_empty_list(self):
        result = await embed_chunks([])
        assert result == []
