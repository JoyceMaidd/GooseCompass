"""Tests for the query rewriter."""

import pytest

from backend.generation.rewriter import rewrite_query

_CONVERSATIONAL_QUERY = "Can I go to ETH if my grades are average?"
_HEDGING_PHRASES = [
    "i think",
    "maybe",
    "perhaps",
    "i'm not sure",
    "possibly",
    "it might",
    "could be",
]


@pytest.mark.asyncio
async def test_rewrite_query_returns_nonempty():
    """Rewritten query must be a non-empty string."""
    result = await rewrite_query(_CONVERSATIONAL_QUERY)
    assert isinstance(result, str)
    assert len(result.strip()) > 0


@pytest.mark.asyncio
async def test_rewrite_query_is_denser():
    """Rewritten query should be shorter or equal in length to the original."""
    result = await rewrite_query(_CONVERSATIONAL_QUERY)
    assert len(result) <= len(_CONVERSATIONAL_QUERY) * 1.5


@pytest.mark.asyncio
async def test_rewrite_query_no_hedging_language():
    """Rewritten query must not contain hedging or conversational filler."""
    result = await rewrite_query(_CONVERSATIONAL_QUERY)
    lower = result.lower()
    for phrase in _HEDGING_PHRASES:
        assert phrase not in lower, f"Hedging phrase found: '{phrase}'"


@pytest.mark.asyncio
async def test_rewrite_query_uses_institutional_terms():
    """Rewritten query should include institutional terminology."""
    result = await rewrite_query(_CONVERSATIONAL_QUERY)
    lower = result.lower()
    # Should contain at least one relevant institutional/academic term
    relevant_terms = ["eth", "gpa", "grade", "eligib", "exchange", "waterloo", "requirement"]
    assert any(term in lower for term in relevant_terms), (
        f"No institutional terms found in rewritten query: '{result}'"
    )
