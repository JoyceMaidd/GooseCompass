"""Tests for backend/retrieval/embeddings.py."""

import pytest

from backend.retrieval.embeddings import embed_query

_QUERY = "What GPA do I need to apply for exchange?"


@pytest.mark.integration
async def test_embed_query_returns_1536_dim_vector():
    """embed_query must return a 1536-dimensional embedding vector of floats."""
    embedding = await embed_query(_QUERY)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)
