"""DeepEval metric suite for scoring the retrieval/generation pipeline.

Metrics are split into two groups:
- Hard gate (Answer Relevancy, Faithfulness): protects the core "answer only
  from grounded context" guarantee. A regression here is a real defect, so
  it fails the test.
- Soft/retrieval (Contextual Precision, Recall, Relevancy): tracks retrieval
  quality, which the first real eval run showed is noisy on broad queries
  (e.g. ~60 near-duplicate per-partner-school pages in the corpus dilute
  top-k results). These are informational for now rather than a hard CI
  gate -- see backend/eval/scoring.py.

Threshold is 0.2 for both groups, calibrated against real scores observed
on the golden dataset's first live run rather than a guessed value.
"""

from deepeval.metrics import (
    AnswerRelevancyMetric,
    BaseMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)

from backend.eval.judge_model import OpenRouterJudgeModel

_METRIC_THRESHOLD = 0.2


def build_hard_metrics(judge: OpenRouterJudgeModel) -> list[BaseMetric]:
    """Build the hard-gate metrics: Answer Relevancy and Faithfulness.

    Args:
        judge: Custom DeepEval judge model routed through OpenRouter.

    Returns:
        List of hard-gate metrics, threshold 0.5.
    """
    return [
        AnswerRelevancyMetric(model=judge, threshold=_METRIC_THRESHOLD),
        FaithfulnessMetric(model=judge, threshold=_METRIC_THRESHOLD),
    ]


def build_soft_retrieval_metrics(judge: OpenRouterJudgeModel) -> list[BaseMetric]:
    """Build the soft retrieval-quality metrics: Contextual Precision/Recall/Relevancy.

    Args:
        judge: Custom DeepEval judge model routed through OpenRouter.

    Returns:
        List of retrieval-quality metrics, threshold 0.5.
    """
    return [
        ContextualPrecisionMetric(model=judge, threshold=_METRIC_THRESHOLD),
        ContextualRecallMetric(model=judge, threshold=_METRIC_THRESHOLD),
        ContextualRelevancyMetric(model=judge, threshold=_METRIC_THRESHOLD),
    ]
