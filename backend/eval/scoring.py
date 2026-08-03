"""Shared hard-gate/soft-warn scoring logic for the eval pipeline."""

import asyncio

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


async def score_test_case(
    test_case: LLMTestCase,
    hard_metrics: list[BaseMetric],
    soft_metrics: list[BaseMetric],
) -> list[BaseMetric]:
    """Measure all metrics concurrently, then assert on the hard-gate ones.

    Every metric's a_measure() runs in parallel via asyncio.gather, with
    DeepEval's built-in progress indicator explicitly disabled
    (_show_indicator=False). That indicator is a rich Live display, and
    rendering more than one at once (across metrics, or across examples in a
    caller that runs several test cases concurrently) is what caused the
    flashing/stale-progress-bar terminal output seen previously -- disabling
    it removes the conflict at the source, rather than serializing work
    around it. Nothing is printed here; the caller builds and prints its own
    report once scoring finishes, so concurrent callers can't interleave
    mid-line either.

    Args:
        test_case: The pipeline output to score.
        hard_metrics: Metrics that must pass; failures raise AssertionError.
        soft_metrics: Metrics that are measured but never fail the caller.

    Returns:
        The soft_metrics list, each populated with .score/.reason/.success
        after measurement.

    Raises:
        AssertionError: If any hard metric falls below its threshold.
    """
    all_metrics = hard_metrics + soft_metrics
    await asyncio.gather(*(metric.a_measure(test_case, _show_indicator=False) for metric in all_metrics))

    failed = [metric for metric in hard_metrics if not metric.is_successful()]
    if failed:
        details = ", ".join(
            f"{metric.__name__} (score: {metric.score:.2f}, threshold: {metric.threshold})" for metric in failed
        )
        raise AssertionError(f"Metrics: {details} failed.")

    return soft_metrics
