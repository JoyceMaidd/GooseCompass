"""Tests for the prompt builder."""

from backend.generation.prompt import build_prompt, _SYSTEM_INSTRUCTION
from backend.retrieval.models import SearchResult


def _make_chunk(i: int) -> SearchResult:
    return SearchResult(
        chunk_id=f"chunk-{i}",
        content=f"Content of chunk number {i}.",
        source_url=f"https://example.com/doc{i}",
        document_title=f"Document {i}",
        section_title=f"Section {i}",
        document_type="web",
        score=1.0,
    )


def test_build_prompt_contains_all_chunk_contents():
    """All chunk content strings must appear in the assembled prompt."""
    chunks = [_make_chunk(i) for i in range(1, 4)]
    prompt = build_prompt("What are the requirements?", chunks)
    for chunk in chunks:
        assert chunk.content in prompt


def test_build_prompt_contains_all_source_urls():
    """All chunk source URLs must appear in the assembled prompt."""
    chunks = [_make_chunk(i) for i in range(1, 4)]
    prompt = build_prompt("What are the requirements?", chunks)
    for chunk in chunks:
        assert chunk.source_url in prompt


def test_build_prompt_contains_grounding_instruction():
    """The system grounding instruction must be present in the prompt."""
    chunks = [_make_chunk(i) for i in range(1, 4)]
    prompt = build_prompt("What are the requirements?", chunks)
    assert _SYSTEM_INSTRUCTION in prompt


def test_build_prompt_contains_query():
    """The user query must appear in the prompt."""
    query = "What GPA do I need for ETH Zurich?"
    chunks = [_make_chunk(1)]
    prompt = build_prompt(query, chunks)
    assert query in prompt


def test_build_prompt_empty_chunks():
    """Prompt must still be valid with no context chunks."""
    prompt = build_prompt("Any question?", [])
    assert _SYSTEM_INSTRUCTION in prompt
    assert "Any question?" in prompt
