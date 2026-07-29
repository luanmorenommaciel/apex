"""Shuffle watcher — DETERMINISTIC. Large shuffle volume, worse when it spills.

Deliberately floored at 1 GiB: shuffling a few MB is normal and flagging it
would make the engine noise. The severity escalates only when the shuffle
actually spilled to disk, which is measured, not inferred.
"""

from __future__ import annotations

from ..context import JobContext
from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import GIB, human_bytes, stage_finding

NAME = "shuffle_watcher"

MIN_SHUFFLE_BYTES = 1 * GIB
HEAVY_SHUFFLE_BYTES = 20 * GIB

SQL = """
SELECT
  job_id, any(app_id) AS app_id, stage_id,
  argMax(shuffle_read_bytes, ts)  AS shuffle_read_bytes,
  argMax(shuffle_write_bytes, ts) AS shuffle_write_bytes,
  argMax(spill_disk_bytes, ts)    AS spill_disk_bytes,
  argMax(spill_mem_bytes, ts)     AS spill_mem_bytes,
  argMax(task_count, ts)          AS task_count
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING shuffle_read_bytes >= {min_shuffle:Int64}
ORDER BY shuffle_read_bytes DESC
"""


def evaluate(stage: StageAggregate, ctx: JobContext | None = None) -> Finding | None:
    if stage.shuffle_read_bytes < MIN_SHUFFLE_BYTES:
        return None

    spilled = stage.spilled_bytes
    heavy = stage.shuffle_read_bytes >= HEAVY_SHUFFLE_BYTES
    if spilled:
        severity, confidence_score = Severity.CRITICAL, 0.9
    elif heavy:
        severity, confidence_score = Severity.WARNING, 0.7
    else:
        severity, confidence_score = Severity.INFO, 0.5

    return stage_finding(
        stage,
        finding_type=FindingType.SHUFFLE,
        severity=severity,
        confidence_score=confidence_score,
        evidence=(
            f"shuffle_read={human_bytes(stage.shuffle_read_bytes)}, "
            f"shuffle_write={human_bytes(stage.shuffle_write_bytes)}, "
            f"spilled={human_bytes(spilled)} across {stage.task_count} tasks"
        ),
        impact=(
            "Shuffle moves this volume across the network and, once it spills, through "
            "local disk as well — usually the dominant cost of the stage."
        ),
        fix=(
            "Size spark.sql.shuffle.partitions to the data (target ~128-200 MiB per "
            "partition), and prune/aggregate before the exchange rather than after it."
        ),
        detected_by=NAME,
        details={
            "shuffle_read_bytes": stage.shuffle_read_bytes,
            "shuffle_write_bytes": stage.shuffle_write_bytes,
            "spilled_bytes": spilled,
            "task_count": stage.task_count,
        },
    )
