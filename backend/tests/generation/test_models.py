"""Tests for backend/generation/models.py."""

import pytest
from pydantic import ValidationError

from backend.generation.models import (
    Citation,
    CitedParagraph,
    GeneratedResponse,
    RawCitedParagraph,
    RawGeneratedResponse,
)


class TestCitation:
    def test_valid_construction_all_fields(self):
        c = Citation(
            id="chunk-1",
            title="Exchange Eligibility Requirements",
            url="https://uwaterloo.ca/exchange",
            snippet="Students must maintain a 70% GPA.",
            source_type="web",
        )
        assert c.id == "chunk-1"
        assert c.title == "Exchange Eligibility Requirements"

    def test_optional_fields_default_to_none(self):
        c = Citation(id="chunk-1", title="Doc")
        assert c.url is None
        assert c.snippet is None
        assert c.source_type is None

    def test_missing_id_raises(self):
        with pytest.raises(ValidationError):
            Citation(title="Doc")

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            Citation(id="chunk-1")


class TestRawCitedParagraph:
    def test_valid_construction(self):
        p = RawCitedParagraph(text="Students need a 70% GPA.", citations=["1"])
        assert p.text == "Students need a 70% GPA."
        assert p.citations == ["1"]

    def test_empty_citations_allowed(self):
        p = RawCitedParagraph(text="Some text.", citations=[])
        assert p.citations == []


class TestRawGeneratedResponse:
    def test_valid_construction(self):
        response = RawGeneratedResponse(
            paragraphs=[RawCitedParagraph(text="Answer here.", citations=["1"])],
        )
        assert len(response.paragraphs) == 1
        assert response.insufficient_context is False

    def test_insufficient_context_defaults_to_false(self):
        response = RawGeneratedResponse(paragraphs=[])
        assert response.insufficient_context is False


class TestCitedParagraph:
    def test_valid_construction(self):
        p = CitedParagraph(
            text="Students need a 70% GPA.",
            citations=[Citation(id="chunk-1", title="Exchange Guide", url="https://uwaterloo.ca/exchange")],
        )
        assert p.text == "Students need a 70% GPA."
        assert len(p.citations) == 1

    def test_empty_citations_allowed(self):
        p = CitedParagraph(text="Some text.", citations=[])
        assert p.citations == []

    def test_multiple_citations(self):
        p = CitedParagraph(
            text="See sources.",
            citations=[
                Citation(id="a", title="A"),
                Citation(id="b", title="B"),
                Citation(id="c", title="C"),
            ],
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
                CitedParagraph(text="Answer here.", citations=[Citation(id="a", title="A")])
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
                CitedParagraph(text="Para 1.", citations=[Citation(id="a", title="A")]),
                CitedParagraph(text="Para 2.", citations=[Citation(id="b", title="B")]),
            ]
        )
        assert len(response.paragraphs) == 2

    def test_missing_paragraphs_raises(self):
        with pytest.raises(ValidationError):
            GeneratedResponse()
