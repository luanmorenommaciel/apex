import pytest

from apex.commander.clickhouse_adapter import ClickHouseTelemetryStore
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.mcp_contract import explain_evidence


class FakeQueryResult:
    def __init__(self, result_rows):
        self.result_rows = result_rows


class FakeClickHouseClient:
    def __init__(self):
        self.commands = []
        self.inserts = []
        self.rows = []

    def command(self, sql):
        self.commands.append(sql)

    def insert(self, table, rows, column_names):
        self.inserts.append(
            {"table": table, "rows": rows, "column_names": column_names}
        )
        for row in rows:
            self.rows.append(dict(zip(column_names, row)))

    def query(self, sql, parameters):
        job_id = parameters["job_id"]
        rows = [
            [row["envelope_json"]]
            for row in self.rows
            if row["job_id"] == job_id
        ]
        return FakeQueryResult(rows)


def telemetry_envelope(job_id="job-42"):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-clickhouse",
        "event_counts": {"SparkListenerTaskEnd": 1},
        "stages": [{"stage_id": 1, "task_count": 1}],
        "skew_candidates": [],
    }


def test_clickhouse_adapter_creates_schema():
    client = FakeClickHouseClient()
    store = ClickHouseTelemetryStore(client, table="commander_telemetry")

    store.ensure_schema()

    assert len(client.commands) == 1
    assert "CREATE TABLE IF NOT EXISTS commander_telemetry" in client.commands[0]
    assert "envelope_json String" in client.commands[0]
    assert "ENGINE = MergeTree" in client.commands[0]


def test_clickhouse_adapter_appends_and_queries_by_job_id():
    client = FakeClickHouseClient()
    store = ClickHouseTelemetryStore(client)
    envelope = telemetry_envelope()

    store.append_envelope(envelope)

    assert client.inserts[0]["table"] == "commander_telemetry"
    assert store.query_by_job_id("job-42") == [envelope]
    assert store.query_by_job_id("missing-job") == []


def test_clickhouse_adapter_rejects_unsafe_table_name():
    with pytest.raises(ValueError, match="unsafe_table_name"):
        ClickHouseTelemetryStore(FakeClickHouseClient(), table="bad;drop")


def skew_envelope():
    envelope = telemetry_envelope("job-skew")
    envelope["stages"] = [
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
    ]
    envelope["skew_candidates"] = [
        {
            "kind": "shuffle_skew_candidate",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        }
    ]
    return envelope


def test_diagnosis_reads_from_clickhouse_adapter():
    store = ClickHouseTelemetryStore(FakeClickHouseClient())
    store.append_envelope(skew_envelope())

    findings = diagnose_findings(store, "job-skew")

    assert [finding["kind"] for finding in findings] == ["shuffle_skew_candidate"]


def test_explain_evidence_reads_from_clickhouse_adapter():
    store = ClickHouseTelemetryStore(FakeClickHouseClient())
    store.append_envelope(skew_envelope())

    result = explain_evidence(store, "job-skew")

    assert result["status"] == "found"
    assert result["job_id"] == "job-skew"
    assert result["stages"][0]["stage_id"] == 2
