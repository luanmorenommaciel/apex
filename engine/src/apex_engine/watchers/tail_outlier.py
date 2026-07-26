"""Sparse tail-outlier watcher for highly parallel stages.

Nearest-rank p99 can exclude one or two extreme tasks once a stage reaches
100+ tasks. This rule is deliberately complementary to the canonical skew
watcher: it runs only when p99/p50 did not already identify the stage.
"""

from __future__ import annotations

from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import stage_finding
from .skew import SKEW_WARNING_RATIO

NAME = "tail_outlier_watcher"
MIN_TASKS_FOR_TAIL = 100
TAIL_WARNING_RATIO = 10.0

SQL = """
SELECT
  job_id,
  any(app_id) AS app_id,
  stage_id,
  max(stage_attempt) AS attempt,
  argMax(task_duration_p50_ms, ts) AS task_duration_p50_ms,
  argMax(task_duration_p99_ms, ts) AS task_duration_p99_ms,
  argMax(task_duration_max_ms, ts) AS task_duration_max_ms,
  argMax(task_count, ts) AS task_count,
  round(argMax(task_duration_max_ms, ts) /
    nullIf(argMax(task_duration_p50_ms, ts), 0), 2) AS tail_ratio,
  round(argMax(task_duration_p99_ms, ts) /
    nullIf(argMax(task_duration_p50_ms, ts), 0), 2) AS skew_ratio
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING task_count >= 100 AND tail_ratio > 10 AND skew_ratio <= 5
ORDER BY tail_ratio DESC
"""


def evaluate(stage: StageAggregate) -> Finding | None:
    if stage.task_count < MIN_TASKS_FOR_TAIL:
        return None
    if stage.skew_ratio > SKEW_WARNING_RATIO:
        return None
    ratio = stage.tail_ratio
    if ratio <= TAIL_WARNING_RATIO:
        return None

    return stage_finding(
        stage,
        finding_type=FindingType.SKEW_ON_JOIN,
        severity=Severity.WARNING,
        confidence_score=0.72,
        evidence=(
            f"max/p50 = {ratio:.2f}x with p99/p50 = {stage.skew_ratio:.2f}x "
            f"on stage {stage.stage_id} (max={stage.task_duration_max_ms:.0f}ms, "
            f"p99={stage.task_duration_p99_ms:.0f}ms, "
            f"p50={stage.task_duration_p50_ms:.0f}ms, {stage.task_count} tasks)"
        ),
        impact=(
            "A sparse extreme tail can hold the stage open even when p99 remains "
            "healthy; the metric alone does not prove join-key skew."
        ),
        fix=(
            "Inspect the slow task, executor and join-key distribution; correlate "
            "with AQE skew_split before applying salting or repartitioning."
        ),
        detected_by=NAME,
        details={
            "tail_outlier_candidate": True,
            "tail_ratio": ratio,
            "skew_ratio": stage.skew_ratio,
            "task_duration_p50_ms": stage.task_duration_p50_ms,
            "task_duration_p99_ms": stage.task_duration_p99_ms,
            "task_duration_max_ms": stage.task_duration_max_ms,
            "task_count": stage.task_count,
            "plan_fingerprint": stage.plan_fingerprint,
        },
    )
