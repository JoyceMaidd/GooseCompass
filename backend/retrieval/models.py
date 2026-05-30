"""Pydantic models for the retrieval pipeline."""

from pydantic import BaseModel


class SearchResult(BaseModel):
    """A single retrieved chunk with its relevance score.

    Args:
        chunk_id: Stable SHA-256 hash identifying the chunk.
        content: Raw text content of the chunk.
        source_url: URL or file path of the originating document.
        document_title: Title of the source document.
        section_title: Title of the section containing this chunk.
        score: Relevance score (higher is more relevant).
    """

    chunk_id: str
    content: str
    source_url: str
    document_title: str
    section_title: str
    score: float
