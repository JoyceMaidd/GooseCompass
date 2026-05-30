"""Retrieval pipeline orchestrator: parallel search + RRF fusion."""

import asyncio

from motor.motor_asyncio import AsyncIOMotorCollection

from backend.retrieval.models import SearchResult
from backend.retrieval.rrf import reciprocal_rank_fusion
from backend.retrieval.text_search import text_search
from backend.retrieval.vector_search import vector_search

# Fetch more candidates per leg than top_k so RRF has a rich pool to fuse.
_CANDIDATES_PER_LEG = 20


async def retrieve(
    query: str,
    query_embedding: list[float],
    collection: AsyncIOMotorCollection,
    top_k: int = 10,
) -> list[SearchResult]:
    """Run parallel vector + text search and fuse results with RRF.

    Args:
        query: Original (or rewritten) query string for text search.
        query_embedding: Dense query vector (1536 dims) for vector search.
        collection: Motor collection containing ingested chunks.
        top_k: Number of results to return after fusion.

    Returns:
        Top-``top_k`` SearchResult items sorted by fused RRF score descending.
    """
    vector_results, text_results = await asyncio.gather(
        vector_search(query_embedding, collection, k=_CANDIDATES_PER_LEG),
        text_search(query, collection, k=_CANDIDATES_PER_LEG),
    )

    fused = reciprocal_rank_fusion(vector_results, text_results)
    return fused[:top_k]
