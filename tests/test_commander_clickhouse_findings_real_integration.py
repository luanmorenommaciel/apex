import os
import uuid

import pytest

from apex.commander.clickhouse_adapter import ClickHouseTelemetryStore
from apex.commander.clickhouse_findings import (
    ClickHouseFindingStore,
    persist_validated_findings,
)
from apex.commander.clickhouse_http_client import ClickHouseHttpClient
from apex.commander.diagnostic_mvp import diagnose_findings


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
        "app_id": "app-clickhouse-findings-real",
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


def test_real_clickhouse_persists_validated_findings():
    config = real_clickhouse_config()
    client = ClickHouseHttpClient(
        config["url"],
        user=config["user"],
        password=config["password"],
    )
    telemetry_table = f"commander_gate8_telemetry_{uuid.uuid4().hex}"
    finding_table = f"commander_gate8_findings_{uuid.uuid4().hex}"
    telemetry_store = ClickHouseTelemetryStore(client, table=telemetry_table)
    finding_store = ClickHouseFindingStore(client, table=finding_table)
    job_id = f"gate8-real-{uuid.uuid4().hex}"

    try:
        client.command(f"DROP TABLE IF EXISTS {telemetry_table}")
        client.command(f"DROP TABLE IF EXISTS {finding_table}")
        telemetry_store.ensure_schema()
        finding_store.ensure_schema()
        telemetry_store.append_envelope(skew_envelope(job_id))

        findings = diagnose_findings(telemetry_store, job_id)
        persisted_records = persist_validated_findings(finding_store, findings)
        queried_records = finding_store.query_by_job_id(job_id)

        assert persisted_records[0]["validation"]["accepted"] is True
        assert queried_records[0]["finding"]["kind"] == "shuffle_skew_candidate"
        assert queried_records[0]["validation"]["status"] == "valid"
    finally:
        client.command(f"DROP TABLE IF EXISTS {finding_table}")
        client.command(f"DROP TABLE IF EXISTS {telemetry_table}")
