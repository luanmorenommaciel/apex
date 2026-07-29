import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from apex_engine.clickhouse import FINDING_COLUMNS, STAGE_EVENTS_SQL, EngineStore
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
