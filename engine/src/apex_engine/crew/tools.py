"""A READ-ONLY, bounded ClickHouse tool for the correlation agent (T13).

Guarantees, in order of importance:
  1. the agent never writes — only Tier-1 Python and the sink write;
  2. the agent never composes SQL — it picks a named query and supplies a
     job_id/stage_id, which are bound as server-side parameters;
  3. every result is LIMITed, so a wide job cannot blow up the context.

The agent is deliberately NOT given a free-text SQL field. An LLM that can write
arbitrary SQL against the telemetry store is a much larger attack surface than
the correlation task needs, and `plan_json` in the store is attacker-influenced
text that reaches the model.
"""

from __future__ import annotations

from typing import Any

MAX_ROWS = 25

# Named, fixed, parameterized queries. This mapping IS the tool's whole surface.
QUERIES: dict[str, str] = {
    "stage_metrics": """
        SELECT stage_id,
               argMax(task_duration_p50_ms, ts)  AS p50_ms,
               argMax(task_duration_p99_ms, ts)  AS p99_ms,
               argMax(shuffle_read_bytes, ts)    AS shuffle_read_bytes,
               argMax(spill_disk_bytes, ts)      AS spill_disk_bytes,
               argMax(gc_time_ms, ts)            AS gc_time_ms,
               argMax(input_bytes, ts)           AS input_bytes,
               argMax(task_count, ts)            AS task_count
        FROM apex.spark_events
        WHERE job_id = {job_id:String} AND stage_id = {stage_id:Int32}
        GROUP BY stage_id
        LIMIT {limit:Int32}
    """,
    "job_stage_overview": """
        SELECT stage_id,
               argMax(task_duration_p50_ms, ts) AS p50_ms,
               argMax(task_duration_p99_ms, ts) AS p99_ms,
               argMax(spill_disk_bytes, ts)     AS spill_disk_bytes,
               argMax(shuffle_read_bytes, ts)   AS shuffle_read_bytes
        FROM apex.spark_events
        WHERE job_id = {job_id:String}
        GROUP BY stage_id
        ORDER BY p99_ms / nullIf(p50_ms, 0) DESC
        LIMIT {limit:Int32}
    """,
    "plan_transitions": """
        SELECT execution_id, update_seq, transition_type, detail, before, after, confidence
        FROM apex.plan_transitions
        WHERE job_id = {job_id:String}
        ORDER BY execution_id, update_seq
        LIMIT {limit:Int32}
    """,
}


def run_named_query(store, query_name: str, job_id: str, stage_id: int = -1) -> dict[str, Any]:
    """Execute one whitelisted read. Anything else is refused."""
    sql = QUERIES.get(query_name)
    if sql is None:
        return {"error": f"unknown_query:{query_name}", "allowed": sorted(QUERIES)}
    if not job_id:
        return {"error": "job_id_required"}

    result = store.client.query(
        sql,
        parameters={"job_id": job_id, "stage_id": int(stage_id), "limit": MAX_ROWS},
    )
    return {"query": query_name, "rows": [dict(r) for r in result.named_results()][:MAX_ROWS]}


def build_clickhouse_tool(store):
    """Wrap `run_named_query` as a CrewAI tool bound to one store."""
    from crewai.tools import tool

    @tool("clickhouse_read")
    def clickhouse_read(query_name: str, job_id: str, stage_id: int = -1) -> str:
        """Read Spark telemetry from ClickHouse. READ-ONLY.

        query_name: one of "stage_metrics", "job_stage_overview", "plan_transitions".
        job_id: the job to inspect. stage_id: required by "stage_metrics" only.
        Returns at most 25 rows as JSON. Arbitrary SQL is not supported.
        """
        import json

        return json.dumps(run_named_query(store, query_name, job_id, stage_id), default=str)

    return clickhouse_read
