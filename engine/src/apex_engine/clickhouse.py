"""Small ClickHouse boundary for the engine lane.

The boundary keeps user/model-controlled values in query parameters and writes only
the exact columns defined by contract/findings.ddl.sql.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any, Protocol

from .schema import Finding, StageEvent

FINDING_COLUMNS = (
    "finding_id", "job_id", "stage_id", "type", "severity", "evidence",
    "hot_key", "impact", "fix", "confidence", "detected_by", "ts",
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


class QueryResult(Protocol):
    def named_results(self) -> Iterable[dict[str, Any]]: ...


class ClickHouseClient(Protocol):
    def query(self, query: str, parameters: dict[str, str]) -> QueryResult: ...

    def insert(self, table: str, data: list[dict[str, Any]], column_names: tuple[str, ...], database: str) -> Any: ...


class EngineStore:
    def __init__(self, client: ClickHouseClient, *, database: str = "apex") -> None:
        self._client = client
        self._database = database

    def stage_events(self, job_id: str) -> list[StageEvent]:
        if not job_id:
            raise ValueError("job_id_required")
        result = self._client.query(STAGE_EVENTS_SQL, parameters={"job_id": job_id})
        return [StageEvent.model_validate(_normalize_row(row)) for row in result.named_results()]

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


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    ts = normalized.get("ts")
    if isinstance(ts, datetime):
        normalized["ts"] = int(ts.timestamp() * 1000)
    return normalized
