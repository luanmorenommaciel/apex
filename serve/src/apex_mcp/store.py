"""Parameterized ClickHouse reads for MCP tools."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol


STAGES_SQL = """
SELECT
  stage_id,
  argMax(app_id, ts) AS app_id,
  argMax(shuffle_read_bytes, ts) AS shuffle_read_bytes,
  argMax(spill_disk_bytes, ts) + argMax(spill_mem_bytes, ts) AS spilled_bytes,
  argMax(task_duration_p50_ms, ts) AS p50_ms,
  argMax(task_duration_p99_ms, ts) AS p99_ms
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY stage_id
ORDER BY stage_id
"""

FINDINGS_SQL = """
SELECT finding_id, job_id, stage_id, type, severity, evidence, impact, fix, confidence, detected_by
FROM apex.findings
WHERE job_id = {job_id:String}
ORDER BY ts ASC
"""


class QueryResult(Protocol):
    def named_results(self) -> Iterable[dict[str, Any]]: ...


class ClickHouseClient(Protocol):
    def query(self, query: str, parameters: dict[str, str]) -> QueryResult: ...


class ReadStore:
    def __init__(self, client: ClickHouseClient) -> None:
        self._client = client

    def stages(self, job_id: str) -> list[dict[str, Any]]:
        return self._query(STAGES_SQL, job_id)

    def findings(self, job_id: str) -> list[dict[str, Any]]:
        return self._query(FINDINGS_SQL, job_id)

    def _query(self, query: str, job_id: str) -> list[dict[str, Any]]:
        if not job_id:
            raise ValueError("job_id_required")
        result = self._client.query(query, parameters={"job_id": job_id})
        return [dict(row) for row in result.named_results()]
