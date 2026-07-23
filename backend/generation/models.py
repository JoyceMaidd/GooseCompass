"""Pydantic models for the generation pipeline."""

from pydantic import BaseModel, Field


class RawCitedParagraph(BaseModel):
    """A single response paragraph as emitted by the LLM.

    The LLM can only reference sources by numbered index ("1", "[1]") or by
    a raw URL — it has no knowledge of chunk metadata. This is the
    PydanticAI structured-output contract, resolved into a `CitedParagraph`
    by `backend.generation.pipeline._resolve_citations`.

    Args:
        text: The paragraph text.
        citations: Raw citation references (index strings, bracketed
            indices, or URLs) supporting the claims in this paragraph.
    """

    text: str
    citations: list[str]


class RawGeneratedResponse(BaseModel):
    """Structured LLM output before citation resolution.

    Args:
        paragraphs: Ordered list of raw cited paragraphs forming the answer.
        insufficient_context: True when retrieved context was not enough to
            answer the query. The paragraphs list may still contain a
            refusal message in this case.
    """

    paragraphs: list[RawCitedParagraph]
    insufficient_context: bool = Field(default=False)


class Citation(BaseModel):
    """A single structured source citation resolved from a retrieved chunk.

    Args:
        id: Stable identifier — the source chunk's chunk_id when resolved
            from a numbered context reference, or the raw citation string
            itself for passthrough citations with no matching chunk.
        title: Document/source title. Falls back to the raw citation string
            for passthrough citations.
        url: Original source URL, if known.
        snippet: Short preview of the supporting chunk text.
        source_type: The chunk's document type ("web" or "pdf"), if known.
    """

    id: str
    title: str
    url: str | None = None
    snippet: str | None = None
    source_type: str | None = None


class CitedParagraph(BaseModel):
    """A single response paragraph with its supporting citations.

    Args:
        text: The paragraph text.
        citations: Structured citations that support the claims in this
            paragraph.
    """

    text: str
    citations: list[Citation]


class GeneratedResponse(BaseModel):
    """Structured LLM response with paragraph-level citations.

    Args:
        paragraphs: Ordered list of cited paragraphs forming the answer.
        insufficient_context: True when retrieved context was not enough to
            answer the query. The paragraphs list may still contain a
            refusal message in this case.
    """

    paragraphs: list[CitedParagraph]
    insufficient_context: bool = Field(default=False)
