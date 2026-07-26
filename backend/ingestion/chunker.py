"""Hybrid document chunking via Docling."""

import asyncio
from typing import Any

from docling.chunking import HybridChunker
from docling_core.types.doc import DoclingDocument

from backend.ingestion.models import ChunkData

_MAX_TOKENS = 512


def _document_title(doc: DoclingDocument, document_type: str, headings: list[str]) -> str:
    """Resolve the document-level title for a chunk.

    HTML sources (Word-exported D2L country-guide pages) typically have no
    real page title and only a single generic heading (e.g. "Tips"), so for
    "html" the filename-derived doc.name is used instead of headings. Other
    source types keep the existing heading-first behavior.

    Args:
        doc: Parsed Docling document.
        document_type: Source type ("web", "pdf", or "html").
        headings: Ordered headings collected for the current chunk.

    Returns:
        The resolved document title.
    """
    if document_type == "html":
        return doc.name or ""
    return headings[0] if headings else (doc.name or "")


def _extract_chunks(doc: DoclingDocument, source_meta: dict[str, Any]) -> list[ChunkData]:
    """Run the hybrid chunker synchronously and map output to ChunkData.

    Args:
        doc: Parsed Docling document.
        source_meta: Dict with keys ``type`` ("web"/"pdf"/"html") and either
            ``url`` (web) or ``path`` (pdf/html).

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
        document_title = _document_title(doc, document_type, headings)
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
        doc: Parsed DoclingDocument (from loader.load_url / load_pdf /
            load_html).
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
