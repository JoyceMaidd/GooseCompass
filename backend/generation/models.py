"""Pydantic models for the generation pipeline."""

from pydantic import BaseModel, Field


class CitedParagraph(BaseModel):
    """A single response paragraph with its supporting source URLs.

    Args:
        text: The paragraph text.
        citations: Source URLs that support the claims in this paragraph.
    """

    text: str
    citations: list[str]


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
