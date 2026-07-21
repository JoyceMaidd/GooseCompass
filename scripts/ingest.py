"""Ingestion CLI — reads scripts/sources.json and ingests all sources."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from backend.config import settings

SOURCES_FILE = Path(__file__).parent / "sources.json"


def _load_sources() -> list[dict]:
    """Load and return the sources list from sources.json.

    Returns:
        List of source dicts with ``type`` and ``url``/``path``.

    Raises:
        SystemExit: If the file is missing or contains invalid JSON.
    """
    if not SOURCES_FILE.exists():
        print(f"ERROR: sources file not found: {SOURCES_FILE}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(SOURCES_FILE.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {SOURCES_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def _label(source: dict) -> str:
    """Return a human-readable label for a source."""
    return source.get("url") or source.get("path", "?")


async def _ingest_one(source: dict, db, index: int, total: int) -> tuple[dict, int, Exception | None]:
    """Ingest a single source, returning (source, chunk_count, error_or_None)."""
    from backend.ingestion.pipeline import ingest_source
    try:
        count = await ingest_source(source, db)
        print(f"  [{index}/{total}] OK  {count:>4} chunks  {_label(source)}")
        return source, count, None
    except Exception as exc:
        print(f"  [{index}/{total}] ERR {_label(source)}: {exc}", file=sys.stderr)
        return source, 0, exc


async def _prune(sources: list[dict], db, dry_run: bool) -> None:
    """Delete chunks whose source is no longer in sources.json.

    Args:
        sources: Current sources list, used to compute the set of URLs/paths
            that should still have chunks in the database.
        db: Motor database handle.
        dry_run: If True, report what would be deleted without deleting.
    """
    from backend.ingestion.store import prune_stale_chunks

    current_urls = {source.get("url") or source.get("path") for source in sources}
    collection = db[settings.mongodb_collection_chunks]

    if dry_run:
        stale = await collection.count_documents({"source_url": {"$nin": list(current_urls)}})
        print(f"\n-- dry-run: {stale} stale chunk(s) would be deleted --")
        return

    deleted = await prune_stale_chunks(current_urls, collection)
    print(f"\nPruned {deleted} stale chunk(s) no longer in {SOURCES_FILE}.")


async def run(dry_run: bool, prune: bool) -> None:
    """Main async entry point.

    Args:
        dry_run: If True, list sources / report prune counts without
            ingesting or deleting anything.
        prune: If True, after ingesting, delete chunks whose source is no
            longer present in sources.json.
    """
    sources = _load_sources()
    total = len(sources)
    print(f"Sources: {total} found in {SOURCES_FILE}")

    if dry_run:
        print("\n-- dry-run mode: no ingestion performed --\n")
        for i, source in enumerate(sources, 1):
            kind = source.get("type", "?").upper()
            print(f"  {i:>2}. [{kind}] {_label(source)}")
        if not prune:
            return

    from backend.db import connect, disconnect, get_database
    await connect()
    db = get_database()

    had_errors = False
    try:
        if not dry_run:
            print(f"\nIngesting {total} sources concurrently...\n")
            tasks = [
                _ingest_one(source, db, i, total)
                for i, source in enumerate(sources, 1)
            ]
            results = await asyncio.gather(*tasks)

            total_chunks = sum(count for _, count, _ in results)
            errors = [src for src, _, err in results if err is not None]
            had_errors = bool(errors)

            print(f"\nDone. {total_chunks} chunks stored across {total - len(errors)}/{total} sources.")
            if errors:
                print(f"  {len(errors)} source(s) failed:", file=sys.stderr)
                for src in errors:
                    print(f"    {_label(src)}", file=sys.stderr)

        if prune:
            await _prune(sources, db, dry_run)
    finally:
        await disconnect()

    if had_errors:
        sys.exit(1)


def main() -> None:
    """Parse arguments and run the ingestion pipeline."""
    parser = argparse.ArgumentParser(description="Ingest sources into GooseCompass.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List all sources without ingesting.",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help=(
            "After ingesting, delete chunks whose source is no longer in "
            "sources.json. Combine with --dry-run to preview the count "
            "without deleting."
        ),
    )
    args = parser.parse_args()
    asyncio.run(run(dry_run=args.dry_run, prune=args.prune))


if __name__ == "__main__":
    main()
