import os
import uuid

import pytest

from apex.commander.clickhouse_adapter import ClickHouseTelemetryStore
from apex.commander.clickhouse_http_client import ClickHouseHttpClient
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.mcp_contract import explain_evidence


def real_clickhouse_config():
    url = os.environ.get("APEX_CLICKHOUSE_REAL_URL")
    if not url:
        pytest.skip("APEX_CLICKHOUSE_REAL_URL is not set")
    return {
        "url": url,
        "user": os.environ.get("APEX_CLICKHOUSE_REAL_USER"),
        "password": os.environ.get("APEX_CLICKHOUSE_REAL_PASSWORD"),
    }


def skew_envelope(job_id):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-clickhouse-real",
        "event_counts": {"SparkListenerTaskEnd": 4},
        "stages": [
            {
                "stage_id": 2,
                "task_count": 8,
                "records": [165297, 5596, 5600, 5700],
                "total_records": 182193,
                "max_records": 165297,
                "median_cold_records": 5596,
                "ratio": 29.5,
                "evidence_status": "valid",
                "quality_issues": [],
                "disk_bytes_spilled": 0,
                "memory_bytes_spilled": 0,
                "jvm_gc_time_ms": 0,
                "executor_run_time_ms": 10000,
                "failure_reasons": [],
            }
        ],
        "skew_candidates": [
            {
                "kind": "shuffle_skew_candidate",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
                "task_count": 8,
            }
        ],
    }


def test_real_clickhouse_roundtrip_and_diagnosis():
    config = real_clickhouse_config()
    client = ClickHouseHttpClient(
        config["url"],
        user=config["user"],
        password=config["password"],
    )
    table = f"commander_gate7_{uuid.uuid4().hex}"
    store = ClickHouseTelemetryStore(client, table=table)
    job_id = f"gate7-real-{uuid.uuid4().hex}"

    try:
        client.command(f"DROP TABLE IF EXISTS {table}")
        store.ensure_schema()
        store.append_envelope(skew_envelope(job_id))

        assert store.query_by_job_id(job_id)[0]["job_id"] == job_id
        assert diagnose_findings(store, job_id)[0]["kind"] == "shuffle_skew_candidate"
        assert explain_evidence(store, job_id)["status"] == "found"
    finally:
        client.command(f"DROP TABLE IF EXISTS {table}")
