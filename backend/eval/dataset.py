"""Loader for the checked-in golden Q&A fixture."""

import json
from pathlib import Path

from backend.eval.models import GoldenExample

DEFAULT_FIXTURE_PATH = Path(__file__).parent.parent / "tests" / "fixtures" / "golden_dataset.json"


def load_golden_dataset(path: Path = DEFAULT_FIXTURE_PATH) -> list[GoldenExample]:
    """Load and validate the golden Q&A fixture.

    Args:
        path: Path to the JSON fixture file.

    Returns:
        Validated list of GoldenExample entries.

    Raises:
        pydantic.ValidationError: If an entry doesn't match the schema.
    """
    raw = json.loads(path.read_text())
    return [GoldenExample.model_validate(entry) for entry in raw]
