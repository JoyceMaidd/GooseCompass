"""Tests for backend/ingestion/models.py."""

import pytest
from pydantic import ValidationError

from backend.ingestion.models import Chunk, ChunkData


def _make_chunk(**overrides) -> dict:
    base = {
        "content": "Sample content",
        "embedding": [0.1] * 1536,
        "source_url": "https://example.com/page",
        "document_title": "Example Doc",
        "section_title": "Intro",
        "document_type": "web",
        "chunk_index": 0,
    }
    return {**base, **overrides}


class TestChunkData:
    def test_valid_construction(self):
        data = ChunkData(
            content="Hello",
            source_url="https://example.com",
            document_title="Title",
            section_title="Section",
            document_type="web",
            chunk_index=2,
        )
        assert data.content == "Hello"
        assert data.chunk_index == 2
        assert data.document_type == "web"

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            ChunkData(
                content="Hello",
                source_url="https://example.com",
                document_title="Title",
                # section_title missing
                document_type="web",
                chunk_index=0,
            )


class TestChunk:
    def test_valid_construction(self):
        chunk = Chunk(**_make_chunk())
        assert isinstance(chunk.chunk_id, str)
        assert len(chunk.chunk_id) == 64  # SHA-256 hex digest
        assert isinstance(chunk.embedding, list)
        assert len(chunk.embedding) == 1536

    def test_chunk_id_is_stable(self):
        chunk_a = Chunk(**_make_chunk())
        chunk_b = Chunk(**_make_chunk())
        assert chunk_a.chunk_id == chunk_b.chunk_id

    def test_chunk_id_differs_for_different_index(self):
        chunk_a = Chunk(**_make_chunk(chunk_index=0))
        chunk_b = Chunk(**_make_chunk(chunk_index=1))
        assert chunk_a.chunk_id != chunk_b.chunk_id

    def test_explicit_chunk_id_preserved(self):
        chunk = Chunk(**_make_chunk(chunk_id="custom-id"))
        assert chunk.chunk_id == "custom-id"

    def test_missing_required_field_raises(self):
        params = _make_chunk()
        del params["content"]
        with pytest.raises(ValidationError):
            Chunk(**params)

    def test_field_types(self):
        chunk = Chunk(**_make_chunk())
        assert isinstance(chunk.content, str)
        assert isinstance(chunk.source_url, str)
        assert isinstance(chunk.document_title, str)
        assert isinstance(chunk.section_title, str)
        assert isinstance(chunk.document_type, str)
        assert isinstance(chunk.chunk_index, int)
