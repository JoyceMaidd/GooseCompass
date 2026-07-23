"""End-to-end tests for the generation pipeline.

Integration tests: require Atlas indexes and a populated chunks collection.
"""

import pytest
from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.generation.models import Citation, RawCitedParagraph, RawGeneratedResponse
from backend.generation.pipeline import _resolve_citations, answer
from backend.retrieval.models import SearchResult
from backend.retrieval.pipeline import retrieve


def _make_chunk(index: int, url: str, document_type: str = "web", content: str = "content") -> SearchResult:
    return SearchResult(
        chunk_id=f"id-{index}",
        content=content,
        source_url=url,
        document_title=f"Doc {index}",
        section_title="Section",
        document_type=document_type,
        score=1.0,
    )


def test_resolve_citations_numeric_ids():
    chunks = [_make_chunk(i, f"https://example.com/{i}") for i in range(1, 4)]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para one.", citations=["1", "3"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    citations = resolved.paragraphs[0].citations
    assert [c.id for c in citations] == ["https://example.com/1", "https://example.com/3"]
    assert [c.url for c in citations] == ["https://example.com/1", "https://example.com/3"]
    assert all(isinstance(c, Citation) for c in citations)


def test_resolve_citations_bracket_notation():
    chunks = [_make_chunk(1, "https://example.com/a"), _make_chunk(2, "https://example.com/b")]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para.", citations=["[2]", "[1]"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    assert [c.url for c in resolved.paragraphs[0].citations] == [
        "https://example.com/b",
        "https://example.com/a",
    ]


def test_resolve_citations_deduplicates():
    chunks = [_make_chunk(1, "https://example.com/x")]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para.", citations=["1", "1", "[1]"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    assert len(resolved.paragraphs[0].citations) == 1
    assert resolved.paragraphs[0].citations[0].url == "https://example.com/x"


def test_resolve_citations_unmatched_reference_is_dropped():
    chunks = [_make_chunk(1, "https://example.com/x")]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para.", citations=["https://other.com/page"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    assert resolved.paragraphs[0].citations == []


def test_resolve_citations_multiple_chunks_same_document_merge_into_one_citation():
    chunks = [
        _make_chunk(1, "https://example.com/doc", content="Section one content."),
        _make_chunk(2, "https://example.com/doc", content="Section two content."),
    ]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para.", citations=["1", "2"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    citations = resolved.paragraphs[0].citations
    assert len(citations) == 1
    assert citations[0].url == "https://example.com/doc"
    assert citations[0].snippet == "Section one content."


def test_resolve_citations_chunk_metadata_populates_citation():
    chunks = [_make_chunk(1, "https://example.com/x", document_type="pdf", content="Short content.")]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para.", citations=["1"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    citation = resolved.paragraphs[0].citations[0]
    assert citation.title == "Doc 1"
    assert citation.source_type == "pdf"
    assert citation.snippet == "Short content."


def test_resolve_citations_snippet_truncated():
    long_content = "x" * 200
    chunks = [_make_chunk(1, "https://example.com/x", content=long_content)]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="Para.", citations=["1"])],
        insufficient_context=False,
    )
    resolved = _resolve_citations(raw, chunks)
    snippet = resolved.paragraphs[0].citations[0].snippet
    assert len(snippet) == 151  # 150 chars + ellipsis
    assert snippet.endswith("…")


def test_resolve_citations_insufficient_context_empty_paragraphs_gets_fallback():
    chunks = [_make_chunk(1, "https://example.com/x")]
    raw = RawGeneratedResponse(paragraphs=[], insufficient_context=True)
    resolved = _resolve_citations(raw, chunks)
    assert len(resolved.paragraphs) == 1
    assert resolved.paragraphs[0].text
    assert resolved.paragraphs[0].citations == []
    assert resolved.insufficient_context is True


def test_resolve_citations_insufficient_context_with_paragraphs_unchanged():
    chunks = [_make_chunk(1, "https://example.com/x")]
    raw = RawGeneratedResponse(
        paragraphs=[RawCitedParagraph(text="I don't know.", citations=[])],
        insufficient_context=True,
    )
    resolved = _resolve_citations(raw, chunks)
    assert len(resolved.paragraphs) == 1
    assert resolved.paragraphs[0].text == "I don't know."


_QUERY = "What GPA do I need to apply for exchange?"


async def _embed(text: str) -> list[float]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


@pytest.fixture(autouse=True)
async def db_connection():
    await connect()
    yield get_database()
    await disconnect()


@pytest.mark.asyncio
async def test_answer_end_to_end(db_connection):
    """Full pipeline: retrieve real chunks then generate a grounded response."""
    collection = db_connection[settings.mongodb_collection_chunks]
    embedding = await _embed(_QUERY)
    chunks = await retrieve(_QUERY, embedding, collection, top_k=5)

    result = await answer(_QUERY, chunks)

    assert len(result.paragraphs) >= 1
    assert all(len(p.text.strip()) > 0 for p in result.paragraphs)
    assert result.insufficient_context is False
    assert all(len(p.citations) >= 1 for p in result.paragraphs)
    assert all(isinstance(c, Citation) for p in result.paragraphs for c in p.citations)
