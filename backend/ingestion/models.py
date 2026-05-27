"""Pydantic models for the ingestion pipeline."""

import hashlib

from pydantic import BaseModel, Field, model_validator


class ChunkData(BaseModel):
    """Intermediate chunk produced by the chunker, before embedding.

    Args:
        content: Raw text content of the chunk.
        source_url: URL or file path of the originating document.
        document_title: Title of the source document.
        section_title: Title of the section containing this chunk.
        document_type: Either "web" or "pdf".
        chunk_index: Zero-based position of this chunk within the document.
    """

    content: str
    source_url: str
    document_title: str
    section_title: str
    document_type: str
    chunk_index: int


class Chunk(BaseModel):
    """Fully populated chunk ready for storage in MongoDB.

    Args:
        chunk_id: Stable SHA-256 hash of (source_url, chunk_index).
        content: Raw text content of the chunk.
        embedding: Dense vector from text-embedding-3-small (1536 dims).
        source_url: URL or file path of the originating document.
        document_title: Title of the source document.
        section_title: Title of the section containing this chunk.
        document_type: Either "web" or "pdf".
        chunk_index: Zero-based position of this chunk within the document.
    """

    chunk_id: str = Field(default="")
    content: str
    embedding: list[float]
    source_url: str
    document_title: str
    section_title: str
    document_type: str
    chunk_index: int

    @model_validator(mode="after")
    def _set_chunk_id(self) -> "Chunk":
        """Derive chunk_id from source_url and chunk_index if not provided."""
        if not self.chunk_id:
            raw = f"{self.source_url}:{self.chunk_index}"
            self.chunk_id = hashlib.sha256(raw.encode()).hexdigest()
        return self
