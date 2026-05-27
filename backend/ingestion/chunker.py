"""Hybrid document chunking via Docling."""

import asyncio
from typing import Any

from docling.chunking import HybridChunker
from docling_core.types.doc import DoclingDocument

from backend.ingestion.models import ChunkData

_MAX_TOKENS = 512


def _extract_chunks(doc: DoclingDocument, source_meta: dict[str, Any]) -> list[ChunkData]:
    """Run the hybrid chunker synchronously and map output to ChunkData.

    Args:
        doc: Parsed Docling document.
        source_meta: Dict with keys ``type`` ("web"/"pdf") and either
            ``url`` (web) or ``path`` (pdf).

    Returns:
        List of ChunkData ready for embedding.
    """
    source_url = source_meta.get("url") or source_meta.get("path", "")
    document_type = source_meta.get("type", "web")

    chunker = HybridChunker(max_tokens=_MAX_TOKENS)
    raw_chunks = list(chunker.chunk(doc))

    result: list[ChunkData] = []
    for idx, chunk in enumerate(raw_chunks):
        text = chunk.text.strip()
        if not text:
            continue

        headings: list[str] = chunk.meta.headings or []
        document_title = headings[0] if headings else (doc.name or "")
        section_title = headings[-1] if headings else ""

        result.append(
            ChunkData(
                content=text,
                source_url=source_url,
                document_title=document_title,
                section_title=section_title,
                document_type=document_type,
                chunk_index=idx,
            )
        )

    return result


async def chunk_document(
    doc: DoclingDocument, source_meta: dict[str, Any]
) -> list[ChunkData]:
    """Chunk a parsed document into embeddable pieces.

    Args:
        doc: Parsed DoclingDocument (from loader.load_url / load_pdf).
        source_meta: Dict with ``type`` and either ``url`` or ``path``.

    Returns:
        Non-empty list of ChunkData with content and metadata populated.
        Embedding is not performed here.

    Raises:
        ValueError: If the document produces no non-empty chunks.
    """
    chunks = await asyncio.to_thread(_extract_chunks, doc, source_meta)
    if not chunks:
        raise ValueError(f"Document produced no chunks: {source_meta}")
    return chunks
