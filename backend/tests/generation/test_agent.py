"""Tests for the PydanticAI generation agent."""

import pytest

from backend.generation.agent import generate_response
from backend.generation.models import RawGeneratedResponse
from backend.generation.prompt import build_prompt
from backend.retrieval.models import SearchResult


def _mock_chunks() -> list[SearchResult]:
    return [
        SearchResult(
            chunk_id="chunk-1",
            content=(
                "University of Waterloo exchange students must maintain a minimum cumulative "
                "GPA of 70% to remain eligible for their exchange placement."
            ),
            source_url="https://uwaterloo.ca/beyond-canada/exchange-eligibility",
            document_title="Exchange Eligibility Requirements",
            section_title="GPA Requirements",
            document_type="web",
            score=0.95,
        ),
        SearchResult(
            chunk_id="chunk-2",
            content=(
                "ETH Zurich accepts exchange students from partner universities. "
                "Academic performance requirements are set by ETH Zurich admissions."
            ),
            source_url="https://uwaterloo.ca/beyond-canada/eth-zurich",
            document_title="ETH Zurich Exchange Program",
            section_title="Admission Requirements",
            document_type="web",
            score=0.88,
        ),
    ]


@pytest.fixture(scope="module")
async def response() -> RawGeneratedResponse:
    """Single API call shared across all assertions in this module."""
    prompt = build_prompt("What GPA do I need to go on exchange?", _mock_chunks())
    return await generate_response(prompt)


@pytest.mark.asyncio
async def test_generate_response_returns_generated_response(response: RawGeneratedResponse):
    """generate_response must return a RawGeneratedResponse instance."""
    assert isinstance(response, RawGeneratedResponse)


@pytest.mark.asyncio
async def test_generate_response_has_paragraphs(response: RawGeneratedResponse):
    """Response must contain at least one non-empty paragraph."""
    assert len(response.paragraphs) >= 1
    assert all(len(p.text.strip()) > 0 for p in response.paragraphs)


@pytest.mark.asyncio
async def test_generate_response_not_insufficient(response: RawGeneratedResponse):
    """Response should not flag insufficient context when chunks are relevant."""
    assert response.insufficient_context is False
