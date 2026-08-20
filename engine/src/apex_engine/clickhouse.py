"""ClickHouse boundary for the engine lane.

Two rules hold everywhere in this file:
  * reads bind every caller-supplied value as a server-side `{name:Type}`
    parameter — never string interpolation;
  * writes go through the native `client.insert(...)` (parameter binding is
    SELECT-only in clickhouse-connect) and are verified via `written_rows`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Any, Protocol

from .config import ClickHouseSettings
from .context import ShapeSample
from .jobconf import JobConf
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
  task_duration_p50_ms, task_duration_p99_ms, plan_fingerprint, plan_json
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
  -- executor runtime is a typed column, read with the Map as a FALLBACK, not
  -- as the source: rows written before the column existed default it to zero
  -- while still carrying the value under `attributes`. Preferring the column
  -- and falling back keeps those rows `measured` instead of silently demoting
  -- them to the task_count*p50 proxy.
  argMax(if(executor_run_time_ms > 0,
            executor_run_time_ms,
            toInt64OrZero(attributes['executor_run_time_ms'])), ts) AS executor_run_time_ms,
  -- still a pure Map escape hatch; a missing key yields '' so the rule does not fire.
  argMax(attributes['failure_reason'], ts)             AS failure_reason,
  -- retry-safe scheduler counters (CONTRACT.md v0.5): typed columns with
  -- DEFAULT 0 since their own migration, so no Map fallback is needed here
  -- the way executor_run_time_ms above still needs one.
  argMax(task_attempt_count, ts)                       AS task_attempt_count,
  argMax(task_failed_attempt_count, ts)                AS task_failed_attempt_count,
  argMax(task_counted_failure_attempt_count, ts)       AS task_counted_failure_attempt_count,
  argMax(task_speculative_attempt_count, ts)           AS task_speculative_attempt_count,
  -- raw fields the tail-outlier watcher needs; also DEFAULT 0 typed columns,
  -- no Map fallback required, same reasoning as the retry-safe counters above.
  argMax(task_duration_max_ms, ts)                     AS task_duration_max_ms,
  argMax(task_duration_sample_count, ts)               AS task_duration_sample_count,
  argMax(successful_task_duration_p50_ms, ts)          AS successful_task_duration_p50_ms,
  argMax(successful_task_duration_p99_ms, ts)          AS successful_task_duration_p99_ms,
  argMax(successful_task_duration_max_ms, ts)          AS successful_task_duration_max_ms,
  argMax(successful_task_sample_count, ts)             AS successful_task_sample_count,
  argMax(successful_task_shuffle_read_bytes_p50, ts)   AS successful_task_shuffle_read_bytes_p50,
  argMax(successful_task_shuffle_read_bytes_max, ts)   AS successful_task_shuffle_read_bytes_max,
  argMax(successful_task_shuffle_read_bytes_sample_count, ts) AS successful_task_shuffle_read_bytes_sample_count
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

# contract v0.4. One row per job_id; `argMax(conf, ts)` because a logical job_id
# reused across runs (spark.apex.job_id) legitimately has several, and MergeTree
# is at-least-once, so a duplicate row must not turn into two configurations.
JOB_CONF_SQL = """
SELECT job_id, argMax(app_id, ts) AS app_id, argMax(app_name, ts) AS app_name,
       argMax(conf, ts) AS conf
FROM apex.job_conf
WHERE job_id = {job_id:String}
GROUP BY job_id
"""

JOB_CONFS_SQL = """
SELECT job_id, argMax(app_id, ts) AS app_id, argMax(app_name, ts) AS app_name,
       argMax(conf, ts) AS conf
FROM apex.job_conf
WHERE job_id IN {job_ids:Array(String)}
GROUP BY job_id
"""

# Repeated observations of the same stage shape, for the MEASURED noise floor
# (CONTRACT.md rule 2) and the distinct-config count (rule 3).
#
# Keyed on plan_fingerprint, which is NOT the table's ORDER BY, so this is a
# scan. It is bounded by the fingerprint set of ONE job and by MAX_SHAPE_ROWS,
# and it deliberately carries no time window: analyze(job_id) must return the
# same answer for a job whether it ran five minutes or five days ago — the same
# reason STAGE_AGGREGATES_SQL drops 005_skew.sql's 6-hour window.
#
# The aggregate aliases must NOT reuse the filtered column's name: aliasing
# `argMax(plan_fingerprint, ts) AS plan_fingerprint` makes ClickHouse resolve the
# WHERE clause to the aggregate and fail with ILLEGAL_AGGREGATION (code 184).
SHAPE_HISTORY_SQL = """
SELECT
  job_id,
  stage_id,
  argMax(plan_fingerprint, ts)      AS shape_fingerprint,
  argMax(task_count, ts)            AS shape_task_count,
  argMax(task_duration_p50_ms, ts)  AS p50_ms,
  argMax(task_duration_p99_ms, ts)  AS p99_ms,
  argMax(shuffle_read_bytes, ts)
    + argMax(shuffle_write_bytes, ts)
    + argMax(input_bytes, ts)       AS bytes_touched
FROM apex.spark_events
WHERE plan_fingerprint IN {fingerprints:Array(String)}
GROUP BY job_id, stage_id
ORDER BY job_id, stage_id
LIMIT {limit:Int32}
"""

# A shape's floor needs a handful of runs, not a corpus. 2000 rows covers ~100
# runs of a 20-stage job; past that the floor does not get more honest, and a
# truncated read is reported rather than silently treated as the whole history.
MAX_SHAPE_ROWS = 2000


class QueryResult(Protocol):
    def named_results(self) -> Iterable[dict[str, Any]]: ...


class ClickHouseClient(Protocol):
    def query(self, query: str, parameters: dict[str, Any]) -> QueryResult: ...

    def insert(self, table: str, data: list[Any], column_names: tuple[str, ...], database: str) -> Any: ...


class EngineStore:
    def __init__(self, client: ClickHouseClient, *, database: str = "apex") -> None:
        self._client = client
        self._database = database
        # Optional reads degrade instead of crashing, which is right for a table
        # a deployment may not have applied yet — but degradation must never be
        # SILENT. A broken query and an absent table look identical from the
        # caller's side otherwise (a shadowed alias in SHAPE_HISTORY_SQL hid here
        # and cost every finding its noise floor with no symptom).
        self._read_warnings: list[str] = []

    @classmethod
    def connect(cls, settings: ClickHouseSettings | None = None) -> "EngineStore":
        """Open a real clickhouse-connect client from the environment."""
        settings = settings or ClickHouseSettings()
        return cls(settings.connect(), database=settings.database)

    @property
    def client(self) -> ClickHouseClient:
        return self._client

    @property
    def read_warnings(self) -> list[str]:
        """Optional reads that failed, so `analyze()` can report the degradation."""
        return list(self._read_warnings)

    def _warn(self, read: str, exc: Exception) -> None:
        message = f"{read}:{type(exc).__name__}:{str(exc).splitlines()[0][:160]}"
        if message not in self._read_warnings:
            self._read_warnings.append(message)

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

    def job_conf(self, job_id: str) -> JobConf:
        """The run's allowlisted resolved SparkConf (contract v0.4).

        A missing table or missing row is NOT an error: v0.4 is additive and a
        cluster that has not applied it must still be analyzable. The absence is
        returned as `JobConf.missing()`, which every rule reads as UNKNOWN —
        never as "the key was not set".
        """
        try:
            rows = self._rows(JOB_CONF_SQL, job_id)
            return JobConf.from_row(rows[0]) if rows else JobConf.missing(job_id)
        except Exception as exc:  # noqa: BLE001 - optional v0.4 table
            self._warn("job_conf", exc)
            return JobConf.missing(job_id)

    def job_confs(self, job_ids: Sequence[str]) -> dict[str, JobConf]:
        """`job_conf` for many runs at once, for the distinct-config count."""
        if not job_ids:
            return {}
        try:
            rows = self._query(JOB_CONFS_SQL, {"job_ids": list(job_ids)})
            confs = [JobConf.from_row(row) for row in rows]
        except Exception as exc:  # noqa: BLE001 - optional v0.4 table
            self._warn("job_confs", exc)
            return {}
        return {conf.job_id: conf for conf in confs}

    def shape_history(self, fingerprints: Sequence[str]) -> list[ShapeSample]:
        """Every run's measurement of the given plan shapes (rules 2 and 3).

        Best-effort by design: a noise floor is an enrichment, so a store that
        cannot serve this read costs the finding its floor, not its existence.
        """
        if not fingerprints:
            return []
        try:
            rows = self._query(
                SHAPE_HISTORY_SQL,
                {"fingerprints": list(fingerprints), "limit": MAX_SHAPE_ROWS},
            )
            return [
                ShapeSample(
                    job_id=_as_text(row["job_id"]),
                    stage_id=int(row["stage_id"]),
                    plan_fingerprint=_as_text(row["shape_fingerprint"]),
                    task_count=int(row["shape_task_count"]),
                    task_duration_p50_ms=float(row["p50_ms"]),
                    task_duration_p99_ms=float(row["p99_ms"]),
                    bytes_touched=int(row["bytes_touched"]),
                )
                for row in rows
            ]
        except Exception as exc:  # noqa: BLE001 - a floor is optional, a crash is not
            self._warn("shape_history", exc)
            return []

    def _rows(self, sql: str, job_id: str) -> list[dict[str, Any]]:
        if not job_id:
            raise ValueError("job_id_required")
        return self._query(sql, {"job_id": job_id})

    def _query(self, sql: str, parameters: dict[str, Any]) -> list[dict[str, Any]]:
        result = self._client.query(sql, parameters=parameters)
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


def _as_text(value: Any) -> str:
    """Decode a ClickHouse value to the same `str` a pydantic model would hold.

    `plan_fingerprint` is `FixedString(64)`, which clickhouse-connect returns as
    `bytes`. `StageAggregate` goes through pydantic and ends up with `str`, so a
    plain `str(value)` here yields `"b'11e45…'"` and every shape key silently
    fails to match — no exception, no warning, just a noise floor that is never
    measured. Decode explicitly instead.
    """
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "replace").rstrip("\x00")
    return "" if value is None else str(value)


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
