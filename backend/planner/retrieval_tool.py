"""Read-only wrapper around the existing retrieval pipeline for planner agents.

Planner agents may call this to look up institutional facts about host
schools/programs, but nothing here writes to Mongo, and planner data never
flows into it — this module only reads. Retrieval stays deterministic,
non-agentic code (backend/retrieval/) per project rules; this is a thin
call-through, not a modification.
"""

from motor.motor_asyncio import AsyncIOMotorCollection

from backend.retrieval.embeddings import embed_query
from backend.retrieval.models import SearchResult
from backend.retrieval.pipeline import retrieve

_TOP_K = 5


async def research_lookup(
    query: str, collection: AsyncIOMotorCollection, top_k: int = _TOP_K
) -> list[SearchResult]:
    """Look up institutional documents relevant to a planner research query.

    Args:
        query: Natural-language research query.
        collection: Motor collection containing ingested chunks.
        top_k: Number of fused results to return.

    Returns:
        Top retrieved chunks, most relevant first.
    """
    embedding = await embed_query(query)
    return await retrieve(query, embedding, collection, top_k=top_k)
