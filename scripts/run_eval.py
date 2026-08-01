"""Eval CLI — runs the golden dataset through the pipeline and scores it with DeepEval.

Examples run concurrently (bounded by --concurrency), and within each
example all metrics also run concurrently -- see backend/eval/scoring.py,
which disables DeepEval's own progress indicator so concurrent runs can't
corrupt each other's terminal output. Each example's report is built as one
string and printed only once it's complete, so concurrent examples can't
interleave output mid-line either.

Answer Relevancy and Faithfulness are hard-gated (non-zero exit on a
threshold miss). Contextual Precision/Recall/Relevancy are reported as
warnings only and never affect the exit code -- see backend/eval/metrics.py.
"""

import argparse
import asyncio

from openai import AsyncOpenAI

from backend.config import settings
from backend.db import connect, disconnect, get_database
from backend.eval.dataset import load_golden_dataset
from backend.eval.judge_model import OpenRouterJudgeModel
from backend.eval.metrics import build_hard_metrics, build_soft_retrieval_metrics
from backend.eval.pipeline import run_pipeline_for_example
from backend.eval.scoring import score_test_case

_DEFAULT_CONCURRENCY = 5


async def _run_example(example, collection, embed_client, judge) -> tuple[bool, str]:
    """Run one golden example and build its hard/soft metric report.

    Args:
        example: The golden Q&A example to run.
        collection: Motor collection containing ingested chunks.
        embed_client: Shared AsyncOpenAI client used for query embedding.
        judge: Custom DeepEval judge model routed through OpenRouter.

    Returns:
        A tuple of (passed, report) where passed is True if the example
        cleared the hard metric gate, and report is the full printable
        summary for this example, built as one string so it can't be
        interleaved with another example's output.
    """
    test_case = await run_pipeline_for_example(example, collection, embed_client)
    try:
        soft_metrics = await score_test_case(
            test_case,
            hard_metrics=build_hard_metrics(judge),
            soft_metrics=build_soft_retrieval_metrics(judge),
        )
    except AssertionError as exc:
        return False, f"[{example.id}] FAIL (hard gate): {exc}"

    lines = [f"[{example.id}] PASS (hard gate)"]
    for metric in soft_metrics:
        status = "ok  " if metric.is_successful() else "WARN"
        lines.append(f"    {status} {metric.__name__}: {metric.score:.2f} (threshold {metric.threshold})")
    return True, "\n".join(lines)


async def _run_example_bounded(semaphore, example, collection, embed_client, judge) -> bool:
    """Run one golden example under a concurrency limit and print its report.

    Args:
        semaphore: Bounds how many examples run through the pipeline at once.
        example: The golden Q&A example to run.
        collection: Motor collection containing ingested chunks.
        embed_client: Shared AsyncOpenAI client used for query embedding.
        judge: Custom DeepEval judge model routed through OpenRouter.

    Returns:
        True if the example cleared the hard metric gate, False otherwise.
    """
    async with semaphore:
        passed, report = await _run_example(example, collection, embed_client, judge)
    print(report)
    return passed


async def run(concurrency: int = _DEFAULT_CONCURRENCY) -> bool:
    """Run every golden example through the pipeline and print a metric report.

    Args:
        concurrency: Maximum number of examples scored concurrently.

    Returns:
        True if every example cleared the hard metric gate, False otherwise.
    """
    examples = load_golden_dataset()
    print(f"Golden dataset: {len(examples)} examples (concurrency={concurrency})\n")

    await connect()
    try:
        db = get_database()
        collection = db[settings.mongodb_collection_chunks]
        embed_client = AsyncOpenAI(api_key=settings.openai_api_key)
        judge = OpenRouterJudgeModel()
        semaphore = asyncio.Semaphore(concurrency)

        results = await asyncio.gather(
            *(_run_example_bounded(semaphore, example, collection, embed_client, judge) for example in examples)
        )
    finally:
        await disconnect()

    return all(results)


def main() -> None:
    """Parse arguments and run the eval suite."""
    parser = argparse.ArgumentParser(
        description="Run the golden dataset through the RAG pipeline and score it with DeepEval."
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=_DEFAULT_CONCURRENCY,
        help=f"Maximum number of examples scored concurrently (default: {_DEFAULT_CONCURRENCY}).",
    )
    args = parser.parse_args()
    passed = asyncio.run(run(args.concurrency))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
