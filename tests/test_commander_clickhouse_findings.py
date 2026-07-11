from apex.commander.clickhouse_findings import (
    ClickHouseFindingStore,
    persist_validated_findings,
)
from apex.commander.findings import build_finding


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
            [row["finding_json"], row["validation_json"]]
            for row in self.rows
            if row["job_id"] == job_id
        ]
        return FakeQueryResult(rows)


def valid_finding():
    return build_finding(
        "shuffle_skew_candidate",
        "job-42",
        "warning",
        "medium",
        {
            "schema_version": "apex.commander.telemetry.v1",
            "app_id": "app-findings",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
            "task_count": 8,
        },
        ["Validar skew antes de aplicar mudanca."],
    )


def test_finding_store_creates_schema():
    client = FakeClickHouseClient()
    store = ClickHouseFindingStore(client, table="commander_findings")

    store.ensure_schema()

    assert len(client.commands) == 1
    assert "CREATE TABLE IF NOT EXISTS commander_findings" in client.commands[0]
    assert "finding_json String" in client.commands[0]
    assert "validation_json String" in client.commands[0]
    assert "ENGINE = MergeTree" in client.commands[0]


def test_persist_validated_findings_inserts_and_queries_by_job_id():
    client = FakeClickHouseClient()
    store = ClickHouseFindingStore(client)
    records = persist_validated_findings(store, [valid_finding()])

    assert records[0]["validation"]["accepted"] is True
    assert client.inserts[0]["table"] == "commander_findings"

    persisted = store.query_by_job_id("job-42")

    assert persisted[0]["finding"]["kind"] == "shuffle_skew_candidate"
    assert persisted[0]["validation"]["status"] == "valid"


def test_finding_store_rejects_unsafe_table_name():
    try:
        ClickHouseFindingStore(FakeClickHouseClient(), table="bad;drop")
    except ValueError as exc:
        assert str(exc) == "unsafe_table_name"
    else:
        raise AssertionError("expected unsafe table name rejection")
