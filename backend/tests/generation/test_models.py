"""Tests for backend/generation/models.py."""

import pytest
from pydantic import ValidationError

from backend.generation.models import CitedParagraph, GeneratedResponse


class TestCitedParagraph:
    def test_valid_construction(self):
        p = CitedParagraph(
            text="Students need a 70% GPA.",
            citations=["https://uwaterloo.ca/exchange"],
        )
        assert p.text == "Students need a 70% GPA."
        assert len(p.citations) == 1

    def test_empty_citations_allowed(self):
        p = CitedParagraph(text="Some text.", citations=[])
        assert p.citations == []

    def test_multiple_citations(self):
        p = CitedParagraph(
            text="See sources.",
            citations=["https://a.com", "https://b.com", "https://c.com"],
        )
        assert len(p.citations) == 3

    def test_missing_text_raises(self):
        with pytest.raises(ValidationError):
            CitedParagraph(citations=[])

    def test_missing_citations_raises(self):
        with pytest.raises(ValidationError):
            CitedParagraph(text="Some text.")


class TestGeneratedResponse:
    def test_valid_construction(self):
        response = GeneratedResponse(
            paragraphs=[
                CitedParagraph(text="Answer here.", citations=["https://example.com"])
            ],
        )
        assert len(response.paragraphs) == 1
        assert response.insufficient_context is False

    def test_insufficient_context_defaults_to_false(self):
        response = GeneratedResponse(paragraphs=[])
        assert response.insufficient_context is False

    def test_insufficient_context_can_be_set_true(self):
        response = GeneratedResponse(paragraphs=[], insufficient_context=True)
        assert response.insufficient_context is True

    def test_empty_paragraphs_allowed(self):
        response = GeneratedResponse(paragraphs=[])
        assert response.paragraphs == []

    def test_multiple_paragraphs(self):
        response = GeneratedResponse(
            paragraphs=[
                CitedParagraph(text="Para 1.", citations=["https://a.com"]),
                CitedParagraph(text="Para 2.", citations=["https://b.com"]),
            ]
        )
        assert len(response.paragraphs) == 2

    def test_missing_paragraphs_raises(self):
        with pytest.raises(ValidationError):
            GeneratedResponse()
