"""Query embedding via OpenAI."""

from openai import AsyncOpenAI

from backend.config import settings

_EMBEDDING_MODEL = "text-embedding-3-small"


async def embed_query(text: str) -> list[float]:
    """Embed text using OpenAI text-embedding-3-small.

    Args:
        text: The string to embed.

    Returns:
        A 1536-dimensional embedding vector.
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(input=text, model=_EMBEDDING_MODEL)
    return response.data[0].embedding
