"""ClickHouse boundary for the engine lane.

Two rules hold everywhere in this file:
  * reads bind every caller-supplied value as a server-side `{name:Type}`
    parameter — never string interpolation;
  * writes go through the native `client.insert(...)` (parameter binding is
    SELECT-only in clickhouse-connect) and are verified via `written_rows`.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any, Protocol

from .config import ClickHouseSettings
from .schema import Finding, PlanTransition, StageAggregate, StageEvent

FINDING_COLUMNS = (
    "finding_id", "job_id", "app_id", "stage_id", "type", "severity", "evidence",
    "hot_key", "impact", "fix", "confidence", "confidence_score", "detected_by", "ts",
)

STAGE_EVENTS_SQL = """
SELECT
  job_id, app_id, app_name, stage_id, stage_attempt, ts,
  shuffle_read_bytes, shuffle_write_bytes, spill_disk_bytes, spill_mem_bytes,
  gc_time_ms, input_bytes, output_bytes, peak_execution_mem_bytes, task_count,
  task_duration_p50_ms, task_duration_p99_ms, task_duration_max_ms,
  plan_fingerprint, plan_json
FROM apex.spark_events
WHERE job_id = {job_id:String}
ORDER BY stage_id, stage_attempt, ts
"""

# The canonical per-stage reduction every watcher reads. The argMax(..., ts)
# shape is lifted verbatim from infra/sql/005_skew.sql (A): for each
# (job_id, stage_id) take the LATEST attempt's values rather than max() across
# attempts, so a retried stage cannot manufacture a ratio out of two attempts.
#
# Deliberate deviation from 005_skew.sql: no `ts >= now() - INTERVAL 6 HOUR`
# window. That window is right for a dashboard tile, wrong for the engine —
# analyze(job_id) must return the same answer for a job whether it ran five
# minutes or five days ago. The job_id predicate is the bound instead.
STAGE_AGGREGATES_SQL = """
SELECT
  job_id,
  any(app_id)                                          AS app_id,
  stage_id,
  max(stage_attempt)                                   AS attempt,
  argMax(task_duration_p50_ms, ts)                     AS task_duration_p50_ms,
  argMax(task_duration_p99_ms, ts)                     AS task_duration_p99_ms,
  argMax(task_duration_max_ms, ts)                     AS task_duration_max_ms,
  argMax(shuffle_read_bytes, ts)                       AS shuffle_read_bytes,
  argMax(shuffle_write_bytes, ts)                      AS shuffle_write_bytes,
  argMax(spill_disk_bytes, ts)                         AS spill_disk_bytes,
  argMax(spill_mem_bytes, ts)                          AS spill_mem_bytes,
  argMax(gc_time_ms, ts)                               AS gc_time_ms,
  argMax(input_bytes, ts)                              AS input_bytes,
  argMax(output_bytes, ts)                             AS output_bytes,
  argMax(peak_execution_mem_bytes, ts)                 AS peak_execution_mem_bytes,
  argMax(task_count, ts)                               AS task_count,
  argMax(plan_fingerprint, ts)                         AS plan_fingerprint,
  argMax(plan_json, ts)                                AS plan_json,
  -- additive observations ride the contract's Map escape hatch when present;
  -- a missing key yields '' -> 0, so their rules simply do not fire.
  toInt64OrZero(argMax(attributes['executor_run_time_ms'], ts)) AS executor_run_time_ms,
  argMax(attributes['failure_reason'], ts)             AS failure_reason
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY job_id, stage_id
ORDER BY stage_id
"""

PLAN_TRANSITIONS_SQL = """
SELECT job_id, execution_id, update_seq, transition_type, detail, before, after, confidence
FROM apex.plan_transitions
WHERE job_id = {job_id:String}
ORDER BY execution_id, update_seq
"""

EXISTING_FINDINGS_SQL = """
SELECT stage_id, type, detected_by, evidence
FROM apex.findings
WHERE job_id = {job_id:String}
"""


class QueryResult(Protocol):
    def named_results(self) -> Iterable[dict[str, Any]]: ...


class ClickHouseClient(Protocol):
    def query(self, query: str, parameters: dict[str, str]) -> QueryResult: ...

    def insert(self, table: str, data: list[Any], column_names: tuple[str, ...], database: str) -> Any: ...


class EngineStore:
    def __init__(self, client: ClickHouseClient, *, database: str = "apex") -> None:
        self._client = client
        self._database = database

    @classmethod
    def connect(cls, settings: ClickHouseSettings | None = None) -> "EngineStore":
        """Open a real clickhouse-connect client from the environment."""
        settings = settings or ClickHouseSettings()
        return cls(settings.connect(), database=settings.database)

    @property
    def client(self) -> ClickHouseClient:
        return self._client

    # --- reads -------------------------------------------------------------

    def stage_events(self, job_id: str) -> list[StageEvent]:
        """Raw per-attempt stage rows. Kept for the E2E gate's app_id check."""
        rows = self._rows(STAGE_EVENTS_SQL, job_id)
        return [StageEvent.model_validate(_normalize_row(row)) for row in rows]

    def stage_aggregates(self, job_id: str) -> list[StageAggregate]:
        """One row per stage, reduced exactly as the watcher rules expect."""
        rows = self._rows(STAGE_AGGREGATES_SQL, job_id)
        return [StageAggregate.model_validate(row) for row in rows]

    def plan_transitions(self, job_id: str) -> list[PlanTransition]:
        """AQE runtime re-plans for this job. A missing table means no ground
        truth available, not a crash: plan_transitions is optional in v0.2."""
        try:
            rows = self._rows(PLAN_TRANSITIONS_SQL, job_id)
        except Exception:  # noqa: BLE001 - optional table, degrade to heuristics
            return []
        return [PlanTransition.model_validate(row) for row in rows]

    def _rows(self, sql: str, job_id: str) -> list[dict[str, Any]]:
        if not job_id:
            raise ValueError("job_id_required")
        result = self._client.query(sql, parameters={"job_id": job_id})
        return list(result.named_results())

    # --- writes ------------------------------------------------------------

    def existing_signatures(self, job_id: str) -> set[tuple[int, str, str, str]]:
        """Identity of the findings already stored for this job."""
        return {
            (int(row["stage_id"]), row["type"], row["detected_by"], row["evidence"])
            for row in self._rows(EXISTING_FINDINGS_SQL, job_id)
        }

    def persist_new_findings(self, job_id: str, findings: Iterable[Finding]) -> dict[str, Any]:
        """Insert only findings this job does not already have.

        `apex.findings` is a plain MergeTree — it does not deduplicate, so a
        second `analyze()` of the same job would otherwise append a second copy
        of every finding. Re-analysis has to converge, not accumulate.
        """
        findings = list(findings)
        existing = self.existing_signatures(job_id)
        fresh = [f for f in findings if _signature(f) not in existing]
        written = self.persist_findings(fresh)
        return {
            "mode": "inserted" if written else ("already_present" if findings else "no_findings"),
            "written_rows": written,
            "skipped_existing": len(findings) - len(fresh),
        }

    def persist_findings(self, findings: Iterable[Finding]) -> int:
        rows_by_name = [finding.to_clickhouse_row() for finding in findings]
        if not rows_by_name:
            return 0
        rows = [[row[column] for column in FINDING_COLUMNS] for row in rows_by_name]
        result = self._client.insert(
            table="findings",
            data=rows,
            column_names=FINDING_COLUMNS,
            database=self._database,
        )
        written = int(getattr(result, "written_rows", len(rows)))
        if written != len(rows):
            raise RuntimeError(f"finding_insert_count_mismatch:{written}!={len(rows)}")
        return written


def _signature(finding: Finding) -> tuple[int, str, str, str]:
    """What makes two findings the same finding. Deliberately excludes
    finding_id (a fresh uuid every run) and ts (the run's clock)."""
    return (finding.stage_id, finding.type.value, finding.detected_by, finding.evidence)


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    ts = normalized.get("ts")
    if isinstance(ts, datetime):
        normalized["ts"] = int(ts.timestamp() * 1000)
    return normalized


def aggregate_events(events: Iterable[StageEvent]) -> list[StageAggregate]:
    """Offline equivalent of STAGE_AGGREGATES_SQL.

    Performs the same reduction the SQL does (latest attempt wins per stage), so
    the fixture/in-memory path and the ClickHouse path feed watchers identical
    rows and the two can never drift apart.
    """
    latest: dict[int, StageEvent] = {}
    for event in events:
        seen = latest.get(event.stage_id)
        if seen is None or (event.stage_attempt, event.ts) >= (seen.stage_attempt, seen.ts):
            latest[event.stage_id] = event
    return [
        StageAggregate(
            job_id=event.job_id,
            app_id=event.app_id,
            stage_id=event.stage_id,
            attempt=event.stage_attempt,
            task_duration_p50_ms=event.task_duration_p50_ms,
            task_duration_p99_ms=event.task_duration_p99_ms,
            task_duration_max_ms=event.task_duration_max_ms,
            shuffle_read_bytes=event.shuffle_read_bytes,
            shuffle_write_bytes=event.shuffle_write_bytes,
            spill_disk_bytes=event.spill_disk_bytes,
            spill_mem_bytes=event.spill_mem_bytes,
            gc_time_ms=event.gc_time_ms,
            input_bytes=event.input_bytes,
            output_bytes=event.output_bytes,
            peak_execution_mem_bytes=event.peak_execution_mem_bytes,
            task_count=event.task_count,
            plan_fingerprint=event.plan_fingerprint,
            plan_json=event.plan_json,
            executor_run_time_ms=event.executor_run_time_ms,
            failure_reason=event.failure_reason,
        )
        for _, event in sorted(latest.items())
    ]
