"""Cost watcher — DETERMINISTIC. Work performed vs. work that left the stage.

Two independent wasteful shapes:
  * amplification — the stage shuffles far more than it read;
  * wide read      — the stage read a lot and emitted almost nothing, i.e. it
                     paid for columns/rows a pushed-down filter could have skipped.

Stages with `input_bytes = 0` are shuffle-fed, not source-fed; their ratio is
meaningless and they are skipped rather than flagged.
"""

from __future__ import annotations

from ..schema import Finding, FindingType, Severity, StageAggregate
from .base import GIB, MIB, human_bytes, stage_finding

NAME = "cost_watcher"

AMPLIFICATION_RATIO = 50.0
WIDE_READ_MIN_INPUT = 1 * GIB
WIDE_READ_OUTPUT_RATIO = 0.01  # emitted < 1% of what it read
MIN_INPUT_BYTES = 16 * MIB     # below this, ratios are noise

SQL = """
SELECT
  job_id, any(app_id) AS app_id, stage_id,
  argMax(input_bytes, ts)        AS input_bytes,
  argMax(output_bytes, ts)       AS output_bytes,
  argMax(shuffle_read_bytes, ts) AS shuffle_read_bytes,
  argMax(task_count, ts)         AS task_count
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
HAVING input_bytes >= {min_input:Int64}
ORDER BY input_bytes DESC
"""


def evaluate(stage: StageAggregate) -> Finding | None:
    if stage.input_bytes < MIN_INPUT_BYTES:
        return None

    amplification = stage.shuffle_read_bytes / stage.input_bytes
    if amplification >= AMPLIFICATION_RATIO:
        return stage_finding(
            stage,
            finding_type=FindingType.COST,
            severity=Severity.WARNING,
            confidence_score=0.65,
            evidence=(
                f"shuffle/input = {amplification:.1f}x "
                f"(shuffle_read={human_bytes(stage.shuffle_read_bytes)} from "
                f"input={human_bytes(stage.input_bytes)})"
            ),
            impact="The stage moves far more data than it reads — the exchange, not the scan, is the bill.",
            fix="Filter and aggregate before the exchange; check for a join exploding row counts.",
            detected_by=NAME,
            details={"shuffle_to_input_ratio": amplification,
                     "input_bytes": stage.input_bytes,
                     "shuffle_read_bytes": stage.shuffle_read_bytes},
        )

    if stage.input_bytes >= WIDE_READ_MIN_INPUT and stage.output_bytes > 0:
        emitted = stage.output_bytes / stage.input_bytes
        if emitted < WIDE_READ_OUTPUT_RATIO:
            return stage_finding(
                stage,
                finding_type=FindingType.COST,
                severity=Severity.WARNING,
                confidence_score=0.58,
                evidence=(
                    f"read {human_bytes(stage.input_bytes)} and emitted "
                    f"{human_bytes(stage.output_bytes)} ({emitted:.2%})"
                ),
                impact="Nearly everything scanned was discarded — the scan is paid for, the data is not used.",
                fix=(
                    "Push the predicate into the scan and select only needed columns; "
                    "partition or Z-order the source on the filter column."
                ),
                detected_by=NAME,
                details={"output_to_input_ratio": emitted,
                         "input_bytes": stage.input_bytes,
                         "output_bytes": stage.output_bytes},
            )
    return None
