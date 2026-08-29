"""Memory watcher — DETERMINISTIC. Three rules, strongest evidence first.

1. an explicit OOM / executor-lost failure reason  -> BLOCKER, measured
2. spill to disk or memory above a real floor      -> SPILL, measured
3. GC time eating executor runtime                 -> MEMORY, ratio

Rule 3 needs an executor-runtime denominator. `executor_run_time_ms` is now a
typed column on `spark_events`, but it is read through a fallback rather than
directly: rows written before that column existed carry the value only in
`attributes`, where it defaults to zero in the typed column. Reading the typed
column alone would silently demote those rows from `measured` to the proxy, so
the SQL prefers the typed column and falls back to the map. When neither is
present the watcher falls back to `task_count * p50` as a runtime proxy and says
so in the evidence, rather than silently reporting a ratio against a made-up
denominator.
"""

from __future__ import annotations

from ..context import JobContext
from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import GIB, MIB, human_bytes, stage_finding

NAME = "memory_watcher"

SPILL_WARNING_BYTES = 64 * MIB
SPILL_CRITICAL_BYTES = 1 * GIB
GC_WARNING_RATIO = 0.10
GC_CRITICAL_RATIO = 0.25
OOM_MARKERS = ("outofmemoryerror", "executorlostfailure", "killed by yarn", "oom")

SQL = """
SELECT
  job_id, any(app_id) AS app_id, stage_id,
  argMax(spill_disk_bytes, ts)            AS spill_disk_bytes,
  argMax(spill_mem_bytes, ts)             AS spill_mem_bytes,
  argMax(gc_time_ms, ts)                  AS gc_time_ms,
  argMax(peak_execution_mem_bytes, ts)    AS peak_execution_mem_bytes,
  argMax(task_count, ts)                  AS task_count,
  argMax(task_duration_p50_ms, ts)        AS task_duration_p50_ms,
  argMax(if(executor_run_time_ms > 0,
            executor_run_time_ms,
            toInt64OrZero(attributes['executor_run_time_ms'])), ts) AS executor_run_time_ms,
  argMax(attributes['failure_reason'], ts) AS failure_reason
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING spill_disk_bytes > 0 OR spill_mem_bytes > 0 OR gc_time_ms > 0 OR failure_reason != ''
ORDER BY stage_id
"""


def evaluate(stage: StageAggregate, ctx: JobContext | None = None) -> Finding | None:
    reason = stage.failure_reason.lower()
    if any(marker in reason for marker in OOM_MARKERS):
        return stage_finding(
            stage,
            finding_type=FindingType.DRIVER_OOM,
            severity=Severity.BLOCKER,
            confidence_score=0.95,
            evidence=f"stage failure reason reports an out-of-memory condition (peak_exec_mem={human_bytes(stage.peak_execution_mem_bytes)})",
            impact="The stage cannot complete at all until memory or data shape changes.",
            fix=(
                "Raise executor memory / lower spark.sql.shuffle.partitions data per task, "
                "and check for a skewed partition forcing one executor to hold everything."
            ),
            detected_by=NAME,
            details={"failure_reason": stage.failure_reason,
                     "peak_execution_mem_bytes": stage.peak_execution_mem_bytes},
        )

    spilled = stage.spilled_bytes
    if spilled >= SPILL_WARNING_BYTES:
        critical = spilled >= SPILL_CRITICAL_BYTES
        return stage_finding(
            stage,
            finding_type=FindingType.SPILL,
            severity=Severity.CRITICAL if critical else Severity.WARNING,
            confidence_score=0.9 if critical else 0.75,
            evidence=(
                f"spilled {human_bytes(spilled)} "
                f"(disk={human_bytes(stage.spill_disk_bytes)}, mem={human_bytes(stage.spill_mem_bytes)}) "
                f"across {stage.task_count} tasks"
            ),
            impact="Data that did not fit in execution memory was written to and re-read from local disk.",
            fix=(
                "Increase spark.memory.fraction or the partition count so each task's working "
                "set fits in execution memory; drop unused columns before the aggregation."
            ),
            detected_by=NAME,
            details={"spilled_bytes": spilled, "spill_disk_bytes": stage.spill_disk_bytes,
                     "spill_mem_bytes": stage.spill_mem_bytes},
        )

    runtime_ms, basis = _runtime_basis(stage)
    if runtime_ms <= 0:
        return None
    gc_ratio = stage.gc_time_ms / runtime_ms
    if gc_ratio < GC_WARNING_RATIO:
        return None

    critical = gc_ratio >= GC_CRITICAL_RATIO
    return stage_finding(
        stage,
        finding_type=FindingType.MEMORY,
        severity=Severity.CRITICAL if critical else Severity.WARNING,
        # A proxy denominator is weaker evidence than a measured one, and the
        # lower score makes the proxy case gate-eligible instead of asserted.
        confidence_score=(0.85 if critical else 0.62) if basis == "measured" else 0.45,
        evidence=f"GC consumed {gc_ratio:.1%} of executor runtime ({stage.gc_time_ms}ms of {runtime_ms:.0f}ms, {basis})",
        impact="Executors spend a material share of the stage collecting garbage instead of computing.",
        fix=(
            "Reduce per-task working set (more partitions, fewer cached objects) before "
            "adding heap; check for a wide row explosion in this stage."
        ),
        detected_by=NAME,
        details={"gc_ratio": gc_ratio, "gc_time_ms": stage.gc_time_ms,
                 "executor_runtime_ms": runtime_ms, "runtime_basis": basis},
    )


def _runtime_basis(stage: StageAggregate) -> tuple[float, str]:
    """Measured executor runtime when available, else a task*p50 proxy."""
    if stage.executor_run_time_ms > 0:
        return float(stage.executor_run_time_ms), "measured"
    proxy = stage.task_count * stage.task_duration_p50_ms
    return (proxy, "estimated from task_count x p50") if proxy > 0 else (0.0, "unavailable")
