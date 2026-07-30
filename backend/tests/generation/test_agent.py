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
async def response() -> tuple[RawGeneratedResponse, int, int]:
    """Single API call shared across all assertions in this module."""
    prompt = build_prompt("What GPA do I need to go on exchange?", _mock_chunks())
    return await generate_response(prompt)


@pytest.mark.asyncio
async def test_generate_response_returns_generated_response(response: tuple[RawGeneratedResponse, int, int]):
    """generate_response must return a RawGeneratedResponse and token counts."""
    generated_response, input_tokens, output_tokens = response
    assert isinstance(generated_response, RawGeneratedResponse)
    assert isinstance(input_tokens, int) and input_tokens > 0
    assert isinstance(output_tokens, int) and output_tokens > 0


@pytest.mark.asyncio
async def test_generate_response_has_paragraphs(response: tuple[RawGeneratedResponse, int, int]):
    """Response must contain at least one non-empty paragraph."""
    generated_response, _, _ = response
    assert len(generated_response.paragraphs) >= 1
    assert all(len(p.text.strip()) > 0 for p in generated_response.paragraphs)


@pytest.mark.asyncio
async def test_generate_response_not_insufficient(response: tuple[RawGeneratedResponse, int, int]):
    """Response should not flag insufficient context when chunks are relevant."""
    generated_response, _, _ = response
    assert generated_response.insufficient_context is False
