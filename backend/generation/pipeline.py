"""Generation pipeline orchestrator: prompt assembly + structured response."""

from backend.generation.agent import generate_response
from backend.generation.models import CitedParagraph, GeneratedResponse
from backend.generation.prompt import build_prompt
from backend.retrieval.models import SearchResult


def _resolve_citations(
    response: GeneratedResponse, chunks: list[SearchResult]
) -> GeneratedResponse:
    """Replace numeric citation references with actual source URLs.

    The LLM may return index numbers ("1", "[1]") instead of full URLs.
    This maps each such reference back to the source URL of the corresponding
    context chunk.

    Args:
        response: Raw GeneratedResponse from the LLM.
        chunks: Context chunks in prompt order (1-indexed).

    Returns:
        GeneratedResponse with citations resolved to source URLs.
    """
    url_by_index = {str(i): chunk.source_url for i, chunk in enumerate(chunks, start=1)}

    resolved = []
    for para in response.paragraphs:
        seen: set[str] = set()
        urls: list[str] = []
        for citation in para.citations:
            key = citation.strip("[]").strip()
            url = url_by_index.get(key, citation)
            if url not in seen:
                seen.add(url)
                urls.append(url)
        resolved.append(CitedParagraph(text=para.text, citations=urls))

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
        A GeneratedResponse with paragraph-level citations resolved to source URLs.
    """
    prompt = build_prompt(query, context_chunks)
    response = await generate_response(prompt)
    return _resolve_citations(response, context_chunks)
