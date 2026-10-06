"""Sparse effective-duration tails that the p99 skew signal does not own.

This is a deterministic, warning-level diagnostic candidate.  It does not
claim join skew or a root cause: the regular skew watcher remains responsible
for volume-aware, tail-bound skew verdicts.
"""

from __future__ import annotations

from ..context import JobContext, context_for
from ..schema import Finding, FindingType, Severity, StageAggregate
from . import skew
from .base import stage_finding

NAME = "tail_outlier_watcher"
MIN_TASKS_FOR_TAIL = 100
MIN_DURATION_SAMPLES_FOR_TAIL = 100
TAIL_WARNING_RATIO = 10.0
CONFIDENCE_SCORE = 0.72


def evaluate(stage: StageAggregate, ctx: JobContext | None = None) -> Finding | None:
    """Report a sparse effective-duration tail outside current skew ownership."""
    ctx = context_for(ctx)

    if (
        stage.task_count < MIN_TASKS_FOR_TAIL
        or stage.duration_sample_count < MIN_DURATION_SAMPLES_FOR_TAIL
        or stage.effective_task_duration_p50_ms <= 0
        or stage.tail_ratio <= TAIL_WARNING_RATIO
    ):
        return None

    # Do not restate the stronger, volume-aware decision.  Calling the current
    # watcher rather than reproducing its gates keeps ownership aligned as its
    # closed-form and noise policy evolves.
    if skew.evaluate(stage, ctx) is not None:
        return None

    return stage_finding(
        stage,
        finding_type=FindingType.TAIL_OUTLIER,
        severity=Severity.WARNING,
        confidence_score=CONFIDENCE_SCORE,
        evidence=(
            f"max/p50 = {stage.tail_ratio:.2f}x with p99/p50 = {stage.skew_ratio:.2f}x "
            f"on stage {stage.stage_id} (max={stage.effective_task_duration_max_ms:.0f}ms, "
            f"p99={stage.effective_task_duration_p99_ms:.0f}ms, "
            f"p50={stage.effective_task_duration_p50_ms:.0f}ms, "
            f"source={stage.duration_sample_source}, samples={stage.duration_sample_count})"
        ),
        impact=(
            "A sparse extreme duration tail can hold the stage open; duration "
            "evidence alone does not establish join skew or a root cause."
        ),
        fix=(
            "Inspect the slow task and executor context, then correlate with "
            "plan and shuffle evidence before changing partitioning or skew settings."
        ),
        detected_by=NAME,
        details={
            "tail_ratio": stage.tail_ratio,
            "skew_ratio": stage.skew_ratio,
            "legacy_skew_ratio": stage.legacy_skew_ratio,
            "task_count": stage.task_count,
            "duration_sample_count": stage.duration_sample_count,
            "duration_sample_source": stage.duration_sample_source,
            "effective_task_duration_p50_ms": stage.effective_task_duration_p50_ms,
            "effective_task_duration_p99_ms": stage.effective_task_duration_p99_ms,
            "effective_task_duration_max_ms": stage.effective_task_duration_max_ms,
        },
    )
