"""Tests for the DeepEval metric suite against the golden dataset.

Integration tests: require both Atlas indexes (vector_index, text_index) to
be Active and the chunks collection to be populated from Phase 1 ingestion,
plus live OpenAI (embeddings) and OpenRouter (generation, judge) calls.

Answer Relevancy and Faithfulness are hard-gated (fail the test on a
threshold miss) since they protect the core "answer only from grounded
context" guarantee. Contextual Precision/Recall/Relevancy are soft-checked:
a threshold miss raises a pytest warning instead of failing
 -- see backend/eval/metrics.py and backend/eval/scoring.py.
"""

import warnings

import pytest
from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.eval.dataset import load_golden_dataset
from backend.eval.judge_model import OpenRouterJudgeModel
from backend.eval.metrics import build_hard_metrics, build_soft_retrieval_metrics
from backend.eval.pipeline import run_pipeline_for_example
from backend.eval.scoring import score_test_case


@pytest.fixture(autouse=True)
async def db_connection():
    await connect()
    yield get_database()
    await disconnect()


@pytest.mark.parametrize("example", load_golden_dataset(), ids=lambda e: e.id)
async def test_example_meets_metric_thresholds(example, db_connection):
    collection = db_connection[settings.mongodb_collection_chunks]
    embed_client = AsyncOpenAI(api_key=settings.openai_api_key)
    test_case = await run_pipeline_for_example(example, collection, embed_client)

    judge = OpenRouterJudgeModel()
    soft_metrics = await score_test_case(
        test_case,
        hard_metrics=build_hard_metrics(judge),
        soft_metrics=build_soft_retrieval_metrics(judge),
    )

    for metric in soft_metrics:
        if not metric.is_successful():
            warnings.warn(
                f"[{example.id}] {metric.__name__} scored {metric.score:.2f} "
                f"(threshold {metric.threshold}): {metric.reason}",
                stacklevel=1,
            )
