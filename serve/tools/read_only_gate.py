"""Run the C2 read-only MCP service gate against a disposable ClickHouse stack.

This tool seeds its isolated test database directly. The MCP service tested below
only issues SELECT statements; fixture writes are deliberately outside that boundary.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import clickhouse_connect

from apex_mcp.service import ApexReadService
from apex_mcp.store import ReadStore


BEFORE_JOB_ID = "codex-mcp-before-20260722"
AFTER_JOB_ID = "codex-mcp-after-20260722"
FINGERPRINT = "0" * 64


def event_row(job_id: str, app_id: str, p99_ms: int, spilled_bytes: int) -> list[object]:
    return [
        job_id, app_id, "codex-mcp-gate", 2, 0, datetime.now(timezone.utc),
        1_000_000, 1_000_000, spilled_bytes, 0, 0, 1_000_000, 0, 0, 1,
        100, p99_ms, FINGERPRINT, "SortMergeJoin", {},
    ]


def main() -> None:
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "apex"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev"),
        database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
    )
    client.insert(
        "spark_events",
        [
            event_row(BEFORE_JOB_ID, "app-codex-mcp-before", 2_950, 2_097_152),
            event_row(AFTER_JOB_ID, "app-codex-mcp-after", 100, 0),
        ],
        column_names=[
            "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
            "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes", "spill_mem_bytes",
            "gc_time_ms", "input_bytes", "output_bytes", "peak_execution_mem_bytes", "task_count",
            "task_duration_p50_ms", "task_duration_p99_ms", "plan_fingerprint", "plan_json", "attributes",
        ],
    )
    client.insert(
        "findings",
        [[
            "codex-mcp-finding-20260722", BEFORE_JOB_ID, 2, "SKEW_ON_JOIN", "critical",
            "p99/p50=29.5x", "", "high tail latency", "enable AQE skew join", "HIGH",
            "skew_watcher", datetime.now(timezone.utc),
        ]],
        column_names=[
            "finding_id", "job_id", "stage_id", "type", "severity", "evidence", "hot_key",
            "impact", "fix", "confidence", "detected_by", "ts",
        ],
    )

    service = ApexReadService(ReadStore(client))
    diagnosis = service.analyze_run(BEFORE_JOB_ID)
    comparison = service.compare_runs(BEFORE_JOB_ID, AFTER_JOB_ID)
    assert diagnosis.status == "findings"
    assert len(diagnosis.findings) == 1
    assert comparison.status == "improved"
    assert all(item.status != "regressed" for item in comparison.comparisons)
    print(json.dumps({
        "gate": "C2",
        "mcp_tools": ["analyze_run", "compare_runs"],
        "external_llm_calls": 0,
        "diagnosis": diagnosis.model_dump(mode="json"),
        "comparison": comparison.model_dump(mode="json"),
        "status": "passed",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
