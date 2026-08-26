"""Retry-pressure watcher — factual scheduler-budget use, not cause inference.

`task_counted_failure_attempt_count` mirrors Spark's own
`TaskFailedReason.countTowardsTaskFailures`: it says whether a failed attempt
was charged against the scheduler's consecutive-failure budget for a stage.
It does not say *why* the attempt failed — that reason lives in sanitized
`TaskEndReason` categories and executor/host logs this watcher does not have.
Reporting the counted-vs-observed split as a fact, at INFO, is the honest
scope; anything stronger would be guessing at a root cause this counter
cannot support.
"""

from __future__ import annotations

from ..context import JobContext
from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import stage_finding

NAME = "retry_pressure_watcher"

SQL = """
SELECT
  job_id, any(app_id) AS app_id, stage_id,
  argMax(task_attempt_count, ts)                 AS task_attempt_count,
  argMax(task_failed_attempt_count, ts)          AS task_failed_attempt_count,
  argMax(task_counted_failure_attempt_count, ts) AS task_counted_failure_attempt_count
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING task_counted_failure_attempt_count > 0
ORDER BY task_counted_failure_attempt_count DESC
"""


def evaluate(stage: StageAggregate, ctx: JobContext | None = None) -> Finding | None:
    counted = stage.task_counted_failure_attempt_count
    if counted <= 0:
        return None

    attempts = stage.task_attempt_count
    observed_failed = stage.task_failed_attempt_count
    return stage_finding(
        stage,
        finding_type=FindingType.RETRY_PRESSURE,
        severity=Severity.INFO,
        confidence_score=0.95,
        evidence=(
            f"scheduler-counted task failures = {counted} "
            f"of {attempts} observed attempts; failed attempts observed = {observed_failed}"
        ),
        impact=(
            "The stage consumed Spark's task-failure budget; this counter "
            "does not classify the root cause."
        ),
        fix=(
            "Correlate sanitized TaskEndReason categories with executor and "
            "host logs before proposing a code, infrastructure, or "
            "retry-policy change."
        ),
        detected_by=NAME,
        details={
            "task_attempt_count": attempts,
            "task_failed_attempt_count": observed_failed,
            "task_counted_failure_attempt_count": counted,
        },
    )
