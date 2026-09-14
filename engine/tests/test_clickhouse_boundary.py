import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from apex_engine.clickhouse import (
    FINDING_COLUMNS,
    STAGE_AGGREGATES_SQL,
    STAGE_EVENTS_SQL,
    EngineStore,
    aggregate_events,
)
from apex_engine.schema import FindingType
from apex_engine.pipeline import analyze_job


ROOT = Path(__file__).resolve().parents[2]


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def named_results(self):
        return self._rows


class FakeInsertResult:
    def __init__(self, written_rows):
        self.written_rows = written_rows


class FakeClient:
    def __init__(self, rows, written_rows=None):
        self.rows = rows
        self.written_rows = written_rows
        self.query_calls = []
        self.insert_calls = []

    def query(self, query, parameters):
        self.query_calls.append((query, parameters))
        return FakeResult(self.rows)

    def insert(self, **kwargs):
        self.insert_calls.append(kwargs)
        return FakeInsertResult(self.written_rows if self.written_rows is not None else len(kwargs["data"]))


def fixture_row():
    payload = json.loads((ROOT / "contract" / "sample_event.json").read_text(encoding="utf-8"))
    payload["ts"] = datetime.fromtimestamp(payload["ts"] / 1000, timezone.utc)
    return payload


def test_store_parameterizes_job_id_and_normalizes_datetime():
    client = FakeClient([fixture_row()])
    events = EngineStore(client).stage_events("job'with quote")
    assert "{job_id:String}" in STAGE_EVENTS_SQL
    assert "job'with quote" not in STAGE_EVENTS_SQL
    assert client.query_calls[0][1] == {"job_id": "job'with quote"}
    assert events[0].ts == 1718553999000


def test_raw_and_aggregate_sql_project_every_v05_field():
    fields = {
        "executor_run_time_ms",
        "task_duration_max_ms",
        "task_duration_sample_count",
        "successful_task_duration_p50_ms",
        "successful_task_duration_p99_ms",
        "successful_task_duration_max_ms",
        "successful_task_sample_count",
        "successful_task_shuffle_read_bytes_p50",
        "successful_task_shuffle_read_bytes_max",
        "successful_task_shuffle_read_bytes_sample_count",
        "task_attempt_count",
        "task_failed_attempt_count",
        "task_counted_failure_attempt_count",
        "task_killed_attempt_count",
        "task_speculative_attempt_count",
    }
    assert all(field in STAGE_EVENTS_SQL for field in fields)
    assert all(field in STAGE_AGGREGATES_SQL for field in fields)


def test_raw_stage_events_uses_the_historical_executor_runtime_fallback():
    """The raw and aggregate paths must bridge pre-typed-column v0.5 rows."""
    normalized_sql = " ".join(STAGE_EVENTS_SQL.split())
    assert (
        "if(executor_run_time_ms > 0, executor_run_time_ms, "
        "toInt64OrZero(attributes['executor_run_time_ms'])) AS executor_run_time_ms"
    ) in normalized_sql

    # This is the named result of the SQL fallback for a transition row whose
    # typed column is 0 but whose historical attributes map carries 4321.
    transition_row = fixture_row()
    transition_row["executor_run_time_ms"] = 4_321
    event = EngineStore(FakeClient([transition_row])).stage_events(transition_row["job_id"])[0]

    assert event.executor_run_time_ms == 4_321
    assert aggregate_events([event])[0].executor_run_time_ms == 4_321


def test_complete_v05_row_is_projected_analyzed_and_persisted():
    row = fixture_row()
    row.update(
        task_attempt_count=62,
        task_failed_attempt_count=5,
        task_counted_failure_attempt_count=3,
        task_killed_attempt_count=4,
        task_speculative_attempt_count=8,
    )
    client = FakeClient([row])

    result = analyze_job(EngineStore(client), row["job_id"])

    retry_findings = [f for f in result["findings"] if f.type is FindingType.RETRY_PRESSURE]
    assert len(retry_findings) == 1
    inserted_types = {
        values[FINDING_COLUMNS.index("type")]
        for call in client.insert_calls
        for values in call["data"]
    }
    assert FindingType.RETRY_PRESSURE.value in inserted_types


def test_analyze_job_persists_only_contract_columns():
    client = FakeClient([fixture_row()])
    result = analyze_job(EngineStore(client), "ax151sasadds114")
    assert result["llm_calls"] == 0
    assert result["written_rows"] == len(result["findings"])
    insert = client.insert_calls[0]
    assert insert["table"] == "findings"
    assert insert["database"] == "apex"
    assert insert["column_names"] == FINDING_COLUMNS
    assert len(insert["data"][0]) == len(FINDING_COLUMNS)


def test_store_rejects_partial_insert():
    client = FakeClient([fixture_row()], written_rows=0)
    with pytest.raises(RuntimeError, match="finding_insert_count_mismatch"):
        analyze_job(EngineStore(client), "ax151sasadds114")
