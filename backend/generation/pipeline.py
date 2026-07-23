"""Generation pipeline orchestrator: prompt assembly + structured response."""

from backend.generation.agent import generate_response
from backend.generation.models import (
    Citation,
    CitedParagraph,
    GeneratedResponse,
    RawGeneratedResponse,
)
from backend.generation.prompt import build_prompt
from backend.retrieval.models import SearchResult

_INSUFFICIENT_CONTEXT_MESSAGE = (
    "The current context is insufficient to answer the question."
)

_SNIPPET_MAX_LEN = 150


def _snippet(content: str, max_len: int = _SNIPPET_MAX_LEN) -> str:
    """Truncate chunk content into a short preview snippet.

    Args:
        content: Raw chunk text content.
        max_len: Maximum snippet length before truncation.

    Returns:
        The content, truncated with a trailing ellipsis if it exceeds max_len.
    """
    stripped = content.strip()
    if len(stripped) <= max_len:
        return stripped
    return stripped[:max_len].rstrip() + "…"


def _citation_from_chunk(chunk: SearchResult) -> Citation:
    """Build a rich Citation from a retrieved chunk.

    The citation id is the chunk's source_url rather than its chunk_id, so
    multiple chunks retrieved from the same document resolve to the same
    citation identity and collapse into one entry during dedup.

    Args:
        chunk: The context chunk this citation refers to.

    Returns:
        A Citation populated from the chunk's metadata.
    """
    return Citation(
        id=chunk.source_url,
        title=chunk.document_title,
        url=chunk.source_url,
        snippet=_snippet(chunk.content),
        source_type=chunk.document_type,
    )


def _resolve_citations(
    response: RawGeneratedResponse, chunks: list[SearchResult]
) -> GeneratedResponse:
    """Replace raw citation references with structured Citation objects.

    The LLM is instructed to cite by index number ("1", "[1]") only. Each
    reference is mapped back to its context chunk and resolved into a rich
    Citation; references that don't match any known chunk index are dropped
    rather than surfaced, since an unmatched reference isn't a verified,
    grounded source. Citations are deduped by source document (source_url),
    so multiple cited chunks from the same document collapse into one entry.

    Args:
        response: Raw LLM response with unresolved citation references.
        chunks: Context chunks in prompt order (1-indexed).

    Returns:
        GeneratedResponse with citations resolved to structured Citation objects.
    """
    chunk_by_index = {str(i): chunk for i, chunk in enumerate(chunks, start=1)}

    resolved = []
    for para in response.paragraphs:
        seen: set[str] = set()
        citations: list[Citation] = []
        for raw in para.citations:
            key = raw.strip("[]").strip()
            chunk = chunk_by_index.get(key)
            if chunk is None or chunk.source_url in seen:
                continue
            seen.add(chunk.source_url)
            citations.append(_citation_from_chunk(chunk))
        resolved.append(CitedParagraph(text=para.text, citations=citations))

    if response.insufficient_context and not resolved:
        resolved.append(CitedParagraph(text=_INSUFFICIENT_CONTEXT_MESSAGE, citations=[]))

    return GeneratedResponse(paragraphs=resolved, insufficient_context=response.insufficient_context)


async def answer(query: str, context_chunks: list[SearchResult]) -> GeneratedResponse:
    """Generate a grounded, cited response for a query given retrieved context.

    Assembles the prompt from the query and context chunks, then runs the
    PydanticAI agent to produce a structured response. Retrieval and query
    rewriting are upstream concerns — this function does not call them.

    Args:
        query: The (rewritten) user question.
        context_chunks: Top-k retrieved chunks from the retrieval pipeline.

    Returns:
        A GeneratedResponse with paragraph-level citations resolved to
        structured Citation objects.
    """
    prompt = build_prompt(query, context_chunks)
    response = await generate_response(prompt)
    return _resolve_citations(response, context_chunks)
