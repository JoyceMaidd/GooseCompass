"""Tests for backend/retrieval/models.py."""

import pytest
from pydantic import ValidationError

from backend.retrieval.models import SearchResult


def _make_result(**overrides) -> dict:
    base = {
        "chunk_id": "abc123",
        "content": "Exchange students must maintain a 70% GPA.",
        "source_url": "https://uwaterloo.ca/exchange",
        "document_title": "Exchange Program Guide",
        "section_title": "Eligibility",
        "score": 0.92,
    }
    return {**base, **overrides}


class TestSearchResult:
    def test_valid_construction(self):
        result = SearchResult(**_make_result())
        assert result.chunk_id == "abc123"
        assert result.score == 0.92

    def test_field_types(self):
        result = SearchResult(**_make_result())
        assert isinstance(result.chunk_id, str)
        assert isinstance(result.content, str)
        assert isinstance(result.source_url, str)
        assert isinstance(result.document_title, str)
        assert isinstance(result.section_title, str)
        assert isinstance(result.score, float)

    def test_score_as_int_coerces_to_float(self):
        result = SearchResult(**_make_result(score=1))
        assert isinstance(result.score, float)
        assert result.score == 1.0

    def test_missing_required_field_raises(self):
        params = _make_result()
        del params["content"]
        with pytest.raises(ValidationError):
            SearchResult(**params)

    def test_missing_score_raises(self):
        params = _make_result()
        del params["score"]
        with pytest.raises(ValidationError):
            SearchResult(**params)
