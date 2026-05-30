"""MongoDB Atlas Vector Search retrieval."""

from motor.motor_asyncio import AsyncIOMotorCollection

from backend.retrieval.models import SearchResult

_VECTOR_INDEX = "vector_index"
# numCandidates must be >= limit; 10x gives good recall without excess cost.
_NUM_CANDIDATES_MULTIPLIER = 10


async def vector_search(
    query_embedding: list[float],
    collection: AsyncIOMotorCollection,
    k: int = 20,
) -> list[SearchResult]:
    """Retrieve the top-k most semantically similar chunks.

    Uses MongoDB Atlas $vectorSearch on the ``embedding`` field with cosine
    similarity.

    Args:
        query_embedding: Dense query vector (1536 dims for text-embedding-3-small).
        collection: Motor collection containing ingested chunks.
        k: Maximum number of results to return.

    Returns:
        List of SearchResult sorted by descending vector similarity score.
    """
    pipeline = [
        {
            "$vectorSearch": {
                "index": _VECTOR_INDEX,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": k * _NUM_CANDIDATES_MULTIPLIER,
                "limit": k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "chunk_id": 1,
                "content": 1,
                "source_url": 1,
                "document_title": 1,
                "section_title": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    cursor = collection.aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append(SearchResult(**doc))
    return results
