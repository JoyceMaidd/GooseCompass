"""MongoDB upsert for embedded chunks."""

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReplaceOne

from backend.ingestion.models import Chunk


async def upsert_chunks(chunks: list[Chunk], collection: AsyncIOMotorCollection) -> int:
    """Upsert a list of chunks into MongoDB by chunk_id.

    Replaces existing documents with matching chunk_id; inserts new ones.
    Uses a single bulk_write call for efficiency.

    Args:
        chunks: Fully populated Chunk models with embeddings.
        collection: Motor collection to write into.

    Returns:
        Total number of documents upserted (inserted + replaced).
    """
    if not chunks:
        return 0

    operations = [
        ReplaceOne(
            filter={"chunk_id": chunk.chunk_id},
            replacement=chunk.model_dump(),
            upsert=True,
        )
        for chunk in chunks
    ]

    result = await collection.bulk_write(operations, ordered=False)
    return result.upserted_count + result.modified_count
