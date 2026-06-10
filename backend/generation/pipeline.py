"""Generation pipeline orchestrator: prompt assembly + structured response."""

from backend.generation.agent import generate_response
from backend.generation.models import GeneratedResponse
from backend.generation.prompt import build_prompt
from backend.retrieval.models import SearchResult


async def answer(query: str, context_chunks: list[SearchResult]) -> GeneratedResponse:
    """Generate a grounded, cited response for a query given retrieved context.

    Assembles the prompt from the query and context chunks, then runs the
    PydanticAI agent to produce a structured response. Retrieval and query
    rewriting are upstream concerns — this function does not call them.

    Args:
        query: The (rewritten) user question.
        context_chunks: Top-k retrieved chunks from the retrieval pipeline.

    Returns:
        A GeneratedResponse with paragraph-level citations.
    """
    prompt = build_prompt(query, context_chunks)
    return await generate_response(prompt)
