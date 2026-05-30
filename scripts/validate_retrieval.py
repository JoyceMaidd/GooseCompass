"""Interactive CLI for validating retrieval quality."""

import asyncio
import sys

from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.retrieval.pipeline import retrieve

_PREVIEW_LEN = 300


async def _embed(text: str, client: AsyncOpenAI) -> list[float]:
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def _print_results(results) -> None:
    if not results:
        print("  (no results)\n")
        return
    for i, r in enumerate(results, 1):
        preview = r.content.replace("\n", " ")[:_PREVIEW_LEN]
        if len(r.content) > _PREVIEW_LEN:
            preview += "…"
        print(f"  [{i}] score={r.score:.4f}  {r.source_url}")
        print(f"       {r.document_title} › {r.section_title}")
        print(f"       {preview}")
        print()


async def run() -> None:
    """Main async loop: embed query → retrieve → print → repeat."""
    await connect()
    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    print("GooseCompass — retrieval validator")
    print("Enter a query to retrieve top-10 chunks. Type 'q' to quit.\n")

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
                embedding = await _embed(query, client)
                results = await retrieve(query, embedding, collection, top_k=10)
                _print_results(results)
            except Exception as exc:
                print(f"  ERROR: {exc}\n", file=sys.stderr)
    finally:
        await disconnect()


def main() -> None:
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()