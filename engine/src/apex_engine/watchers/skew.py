"""Skew watcher — DETERMINISTIC, lifted from infra/sql/005_skew.sql (A).

That SQL is already proven against real rows: it flags stage 4 of
`app-20260724160310-0000` at 21.62x and leaves the job's healthy 1.0x stages
alone. This watcher is the same rule, parameterized by job_id.

Rule: p99 / p50 > 5 is likely skew; > 10 is severe. The divide is guarded with
`nullIf(p50, 0)` server-side and the equivalent zero-check in `StageAggregate.
skew_ratio`, so a stage with p50 = 0 can never divide by zero or be flagged.
"""

from __future__ import annotations

from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import stage_finding

NAME = "skew_watcher"

# Thresholds — the 5x flag is the canonical one from 005_skew.sql.
SKEW_WARNING_RATIO = 5.0
SKEW_CRITICAL_RATIO = 10.0
# A ratio computed over a handful of tasks is not a distribution. Real skew
# needs enough tasks for a p99 to mean anything.
MIN_TASKS_FOR_RATIO = 4

# Pushed down so ClickHouse discards healthy stages before they reach Python.
# Mirrors 005_skew.sql's HAVING; `evaluate` re-checks it so the offline path
# reaches the same verdict without the pushdown.
SQL = """
SELECT
  job_id,
  any(app_id)                                                                     AS app_id,
  stage_id,
  max(stage_attempt)                                                              AS attempt,
  argMax(task_duration_p50_ms, ts)                                                AS task_duration_p50_ms,
  argMax(task_duration_p99_ms, ts)                                                AS task_duration_p99_ms,
  argMax(task_count, ts)                                                          AS task_count,
  argMax(shuffle_read_bytes, ts)                                                  AS shuffle_read_bytes,
  argMax(spill_disk_bytes, ts)                                                    AS spill_disk_bytes,
  argMax(gc_time_ms, ts)                                                          AS gc_time_ms,
  argMax(plan_fingerprint, ts)                                                    AS plan_fingerprint,
  round(argMax(task_duration_p99_ms, ts) / nullIf(argMax(task_duration_p50_ms, ts), 0), 2) AS skew_ratio
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING skew_ratio > 5
ORDER BY skew_ratio DESC
"""


def evaluate(stage: StageAggregate) -> Finding | None:
    ratio = stage.skew_ratio
    if ratio <= SKEW_WARNING_RATIO or stage.task_count < MIN_TASKS_FOR_RATIO:
        return None

    severe = ratio > SKEW_CRITICAL_RATIO
    severity = Severity.CRITICAL if severe else Severity.WARNING
    # Below the gate threshold on purpose in the 5-10x band: that is exactly
    # the ambiguous range where an LLM's cross-signal read earns its cost.
    confidence_score = 0.88 if severe else 0.55

    return stage_finding(
        stage,
        finding_type=FindingType.SKEW_ON_JOIN,
        severity=severity,
        confidence_score=confidence_score,
        evidence=(
            f"p99/p50 = {ratio:.2f}x on stage {stage.stage_id} "
            f"(p99={stage.task_duration_p99_ms:.0f}ms, p50={stage.task_duration_p50_ms:.0f}ms, "
            f"{stage.task_count} tasks)"
        ),
        impact=(
            "Long-tail tasks dominate the stage: the stage cannot finish before its "
            "slowest partition, so most executors idle while one finishes."
        ),
        fix=(
            "Enable AQE skew join (spark.sql.adaptive.skewJoin.enabled=true); if the "
            "hot key survives that, salt it or broadcast the small side."
        ),
        detected_by=NAME,
        details={
            "skew_ratio": ratio,
            "task_duration_p50_ms": stage.task_duration_p50_ms,
            "task_duration_p99_ms": stage.task_duration_p99_ms,
            "task_count": stage.task_count,
            "plan_fingerprint": stage.plan_fingerprint,
        },
    )
