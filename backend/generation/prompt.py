"""Prompt builder for the generation pipeline."""

from backend.retrieval.models import SearchResult

_SYSTEM_INSTRUCTION = (
    "You are a helpful assistant for University of Waterloo outbound exchange students. "
    "Answer the user's question using ONLY the context provided below. "
    "If the context is insufficient to answer the question, say so explicitly — "
    "do not draw on outside knowledge. "
    "After each paragraph, cite the source URLs that support the claims in that paragraph."
)


def build_prompt(query: str, context_chunks: list[SearchResult]) -> str:
    """Assemble the full LLM prompt from a query and retrieved context chunks.

    The prompt contains:
    1. A system grounding instruction.
    2. A numbered context section with each chunk's content and source URL.
    3. The user query.

    Args:
        query: The (rewritten) user question.
        context_chunks: Ordered list of retrieved chunks to ground the answer.

    Returns:
        A fully assembled prompt string ready to send to the LLM.
    """
    context_lines: list[str] = []
    for i, chunk in enumerate(context_chunks, start=1):
        context_lines.append(
            f"[{i}] {chunk.document_title} — {chunk.section_title}\n"
            f"Source: {chunk.source_url}\n"
            f"{chunk.content}"
        )
    context_section = "\n\n".join(context_lines)

    return (
        f"{_SYSTEM_INSTRUCTION}\n\n"
        f"--- CONTEXT ---\n\n"
        f"{context_section}\n\n"
        f"--- QUESTION ---\n\n"
        f"{query}"
    )
