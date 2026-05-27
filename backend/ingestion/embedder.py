"""Chunk embedding via OpenAI text-embedding-3-small."""

from openai import AsyncOpenAI

from backend.config import settings
from backend.ingestion.models import Chunk, ChunkData

_MODEL = "text-embedding-3-small"
_BATCH_SIZE = 100


async def embed_chunks(chunks: list[ChunkData]) -> list[Chunk]:
    """Embed a list of chunks using OpenAI text-embedding-3-small.

    Sends chunks to the API in batches of up to 100. The returned list
    preserves the input order.

    Args:
        chunks: Pre-chunked documents without embeddings.

    Returns:
        Fully populated Chunk models with 1536-dimensional embeddings.

    Raises:
        openai.OpenAIError: If the API call fails.
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    result: list[Chunk] = []

    for batch_start in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[batch_start : batch_start + _BATCH_SIZE]
        response = await client.embeddings.create(
            input=[c.content for c in batch],
            model=_MODEL,
        )
        # response.data is ordered to match the input
        for chunk_data, embedding_obj in zip(batch, response.data):
            result.append(
                Chunk(
                    content=chunk_data.content,
                    embedding=embedding_obj.embedding,
                    source_url=chunk_data.source_url,
                    document_title=chunk_data.document_title,
                    section_title=chunk_data.section_title,
                    document_type=chunk_data.document_type,
                    chunk_index=chunk_data.chunk_index,
                )
            )

    return result
