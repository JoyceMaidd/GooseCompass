"""Interactive CLI for validating the full generation pipeline."""

import asyncio
import sys

from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.generation.pipeline import answer
from backend.generation.rewriter import rewrite_query
from backend.retrieval.pipeline import retrieve


async def _embed(text: str, client: AsyncOpenAI) -> list[float]:
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def _print_response(response) -> None:
    if response.insufficient_context:
        print("  ⚠  Insufficient context — the system could not answer from retrieved documents.\n")

    for i, paragraph in enumerate(response.paragraphs, 1):
        print(f"  {paragraph.text}")
        if paragraph.citations:
            for url in paragraph.citations:
                print(f"    [{i}] {url}")
        print()


async def run() -> None:
    """Main async loop: rewrite → embed → retrieve → generate → print → repeat."""
    await connect()
    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    embed_client = AsyncOpenAI(api_key=settings.openai_api_key)

    print("GooseCompass — generation validator")
    print("Enter a query to get a grounded answer. Type 'q' to quit.\n")

    try:
        while True:
            try:
                query = input("Query: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if query.lower() == "q":
                break
            if not query:
                continue

            print()
            try:
                rewritten = await rewrite_query(query)
                print(f"  Rewritten: {rewritten}")
                print()

                embedding = await _embed(rewritten, embed_client)
                chunks = await retrieve(rewritten, embedding, collection, top_k=10)
                print(f"  Retrieved {len(chunks)} chunks. Generating...\n")

                response = await answer(query, chunks)
                _print_response(response)
            except Exception as exc:
                print(f"  ERROR: {exc}\n", file=sys.stderr)
    finally:
        await disconnect()


def main() -> None:
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
