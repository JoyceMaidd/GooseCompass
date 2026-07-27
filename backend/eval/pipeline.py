"""Runs a golden example through the retrieval/generation pipeline for scoring."""

from deepeval.test_case import LLMTestCase
from motor.motor_asyncio import AsyncIOMotorCollection
from openai import AsyncOpenAI

from backend.eval.models import GoldenExample
from backend.generation.pipeline import answer
from backend.retrieval.pipeline import retrieve

_EMBEDDING_MODEL = "text-embedding-3-small"


async def _embed(text: str, client: AsyncOpenAI) -> list[float]:
    """Embed a query string for vector search.

    Args:
        text: Text to embed.
        client: Shared AsyncOpenAI client.

    Returns:
        The dense embedding vector.
    """
    response = await client.embeddings.create(input=text, model=_EMBEDDING_MODEL)
    return response.data[0].embedding


async def run_pipeline_for_example(
    example: GoldenExample,
    collection: AsyncIOMotorCollection,
    embed_client: AsyncOpenAI,
) -> LLMTestCase:
    """Run one golden example through retrieve() + answer() and build an LLMTestCase.

    Args:
        example: The golden Q&A example to run.
        collection: Motor collection containing ingested chunks.
        embed_client: Shared AsyncOpenAI client used for query embedding.

    Returns:
        An LLMTestCase populated with the pipeline's actual output and
        retrieval context, ready to score against DeepEval metrics.
    """
    embedding = await _embed(example.query, embed_client)
    context_chunks = await retrieve(example.query, embedding, collection)
    response = await answer(example.query, context_chunks)

    actual_output = "\n\n".join(paragraph.text for paragraph in response.paragraphs)
    retrieval_context = [chunk.content for chunk in context_chunks]

    return LLMTestCase(
        input=example.query,
        actual_output=actual_output,
        expected_output=example.expected_output,
        retrieval_context=retrieval_context,
    )
