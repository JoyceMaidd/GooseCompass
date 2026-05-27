"""Ingestion CLI — reads scripts/sources.json and ingests all sources."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

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


async def run(dry_run: bool) -> None:
    """Main async entry point.

    Args:
        dry_run: If True, list sources without ingesting.
    """
    sources = _load_sources()
    total = len(sources)
    print(f"Sources: {total} found in {SOURCES_FILE}")

    if dry_run:
        print("\n-- dry-run mode: no ingestion performed --\n")
        for i, source in enumerate(sources, 1):
            kind = source.get("type", "?").upper()
            print(f"  {i:>2}. [{kind}] {_label(source)}")
        return

    from backend.db import connect, disconnect, get_database
    await connect()
    db = get_database()

    print(f"\nIngesting {total} sources concurrently...\n")
    try:
        tasks = [
            _ingest_one(source, db, i, total)
            for i, source in enumerate(sources, 1)
        ]
        results = await asyncio.gather(*tasks)
    finally:
        await disconnect()

    total_chunks = sum(count for _, count, _ in results)
    errors = [src for src, _, err in results if err is not None]

    print(f"\nDone. {total_chunks} chunks stored across {total - len(errors)}/{total} sources.")
    if errors:
        print(f"  {len(errors)} source(s) failed:", file=sys.stderr)
        for src in errors:
            print(f"    {_label(src)}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Parse arguments and run the ingestion pipeline."""
    parser = argparse.ArgumentParser(description="Ingest sources into GooseCompass.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List all sources without ingesting.",
    )
    args = parser.parse_args()
    asyncio.run(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
