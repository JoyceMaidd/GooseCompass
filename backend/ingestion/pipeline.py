"""Ingestion pipeline orchestrator: fetch → chunk → embed → store."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.config import settings
from backend.ingestion.chunker import chunk_document
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.loader import load_pdf, load_url
from backend.ingestion.store import upsert_chunks


async def ingest_source(source: dict, db: AsyncIOMotorDatabase) -> int:
    """Run the full ingestion pipeline for a single source.

    Fetches and parses the document, chunks it, embeds each chunk,
    then upserts into MongoDB.

    Args:
        source: Dict with ``type`` ("web"/"pdf") and either ``url`` (web)
            or ``path`` (pdf).
        db: Motor database handle; chunks are written to the configured
            collection.

    Returns:
        Number of chunks upserted into the database.

    Raises:
        ValueError: If ``source`` has an unknown ``type``.
        RuntimeError: If the document fails to load or produces no chunks.
    """
    source_type = source.get("type")

    if source_type == "web":
        doc = await load_url(source["url"])
    elif source_type == "pdf":
        doc = await load_pdf(source["path"])
    else:
        raise ValueError(f"Unknown source type: {source_type!r}")

    chunks_data = await chunk_document(doc, source)
    chunks = await embed_chunks(chunks_data)
    collection = db[settings.mongodb_collection_chunks]
    return await upsert_chunks(chunks, collection)
