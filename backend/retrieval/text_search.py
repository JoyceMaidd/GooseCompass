"""MongoDB Atlas full-text search retrieval."""

from motor.motor_asyncio import AsyncIOMotorCollection

from backend.retrieval.models import SearchResult

_TEXT_INDEX = "text_index"


async def text_search(
    query: str,
    collection: AsyncIOMotorCollection,
    k: int = 20,
) -> list[SearchResult]:
    """Retrieve the top-k chunks most relevant to a keyword query.

    Uses MongoDB Atlas $search on the ``content``, ``document_title``, and
    ``section_title`` fields with the lucene.standard analyzer.

    Args:
        query: Natural-language or keyword query string.
        collection: Motor collection containing ingested chunks.
        k: Maximum number of results to return.

    Returns:
        List of SearchResult sorted by descending text relevance score.
    """
    pipeline = [
        {
            "$search": {
                "index": _TEXT_INDEX,
                "text": {
                    "query": query,
                    "path": ["content", "document_title", "section_title"],
                },
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
                "score": {"$meta": "searchScore"},
            }
        },
        {"$limit": k},
    ]

    cursor = collection.aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append(SearchResult(**doc))
    return results
