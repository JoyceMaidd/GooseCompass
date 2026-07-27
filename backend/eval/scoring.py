"""Shared hard-gate/soft-warn scoring logic for the eval pipeline."""

from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


async def score_test_case(
    test_case: LLMTestCase,
    hard_metrics: list[BaseMetric],
    soft_metrics: list[BaseMetric],
) -> list[BaseMetric]:
    """Assert hard metrics and measure soft metrics without failing on them.

    Hard metrics are checked via assert_test, which raises AssertionError on
    any threshold miss -- callers let this propagate as a real failure. Soft
    metrics are measured directly so a low score never raises; callers are
    responsible for surfacing failed soft metrics as warnings/report lines.

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
    assert_test(test_case, hard_metrics)
    for metric in soft_metrics:
        await metric.a_measure(test_case)
    return soft_metrics
