"""Reciprocal Rank Fusion for combining ranked result lists."""

from backend.retrieval.models import SearchResult


def reciprocal_rank_fusion(
    results_a: list[SearchResult],
    results_b: list[SearchResult],
    k: int = 60,
) -> list[SearchResult]:
    """Merge two ranked result lists using Reciprocal Rank Fusion.

    Each document's fused score is the sum of 1/(k + rank) across every list
    it appears in (1-based rank). Documents that appear in both lists receive
    contributions from each. Deduplicates by ``chunk_id``.

    Args:
        results_a: First ranked list (e.g. from vector search).
        results_b: Second ranked list (e.g. from text search).
        k: Ranking constant that dampens the impact of top-ranked documents.
            Default of 60 is the standard RRF value from the original paper.

    Returns:
        Deduplicated list of SearchResult sorted by fused score descending,
        with ``score`` replaced by the RRF score.
    """
    fused_scores: dict[str, float] = {}
    # chunk_id -> original SearchResult (to preserve content/metadata)
    seen: dict[str, SearchResult] = {}

    for rank, result in enumerate(results_a, start=1):
        fused_scores[result.chunk_id] = fused_scores.get(result.chunk_id, 0.0) + 1.0 / (k + rank)
        seen.setdefault(result.chunk_id, result)

    for rank, result in enumerate(results_b, start=1):
        fused_scores[result.chunk_id] = fused_scores.get(result.chunk_id, 0.0) + 1.0 / (k + rank)
        seen.setdefault(result.chunk_id, result)

    return [
        seen[chunk_id].model_copy(update={"score": score})
        for chunk_id, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
