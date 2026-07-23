"""Prompt builder for the generation pipeline."""

from backend.retrieval.models import SearchResult

_SYSTEM_INSTRUCTION = (
    "You are a helpful assistant for University of Waterloo outbound exchange students. "
    "Answer the user's question using ONLY the context provided below. "
    "If the context is insufficient to answer the question, say so explicitly — "
    "do not draw on outside knowledge. "
    "When the answer covers more than one point, break it into multiple concise "
    "paragraphs, one idea per paragraph. "
    "Each paragraph has a separate text field and citations field. The text field "
    "must contain ONLY prose — never include reference numbers, brackets, or "
    "parentheses citing sources anywhere in the text, and never end a sentence or "
    "paragraph with something like '(1)' or '(supporting point from 9)'. Instead, "
    "put the numbers of the context items that support that paragraph in the "
    "separate citations field, using only the bracketed number shown before each "
    "context item (for example: 1, 2). Never write out a source's URL or title, "
    "and never cite a source that is not listed in the context below."
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
