"""Data models for the golden Q&A evaluation dataset."""

from pydantic import BaseModel


class GoldenExample(BaseModel):
    """A single hand-authored ground-truth Q&A pair for eval scoring.

    Args:
        id: Short unique identifier for the example.
        query: The user question sent through the pipeline.
        expected_output: Reference answer used as ground truth by DeepEval.
        category: Optional grouping label for reporting (e.g. "eligibility").
    """

    id: str
    query: str
    expected_output: str
    category: str | None = None
