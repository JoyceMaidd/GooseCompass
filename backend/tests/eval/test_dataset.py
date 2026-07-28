"""Tests for backend/eval/dataset.py. Pure unit tests, no network calls."""

import json

import pytest
from pydantic import ValidationError

from backend.eval.dataset import load_golden_dataset
from backend.eval.models import GoldenExample


def test_loads_real_fixture():
    examples = load_golden_dataset()
    assert len(examples) >= 8
    assert all(isinstance(e, GoldenExample) for e in examples)


def test_ids_are_unique():
    examples = load_golden_dataset()
    ids = [e.id for e in examples]
    assert len(ids) == len(set(ids))


def test_malformed_entry_raises_validation_error(tmp_path):
    bad_fixture = tmp_path / "bad_dataset.json"
    bad_fixture.write_text(json.dumps([{"id": "missing-fields-only"}]))
    with pytest.raises(ValidationError):
        load_golden_dataset(path=bad_fixture)
