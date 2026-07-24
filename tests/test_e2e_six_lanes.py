from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
for source_dir in (ROOT, ROOT / "engine" / "src"):
    source = str(source_dir)
    if source not in sys.path:
        sys.path.insert(0, source)

from apex_engine.schema import Confidence, Finding, FindingType, Severity, StageEvent
from scripts.e2e_six_lanes import GateFailure, run_gate


class Result:
    def __init__(self, rows):
        self._rows = rows

    def named_results(self):
        return self._rows


class InsertResult:
    def __init__(self, written_rows):
        self.written_rows = written_rows


class FakeClient:
    def __init__(self, events, findings=None):
        self.events = events
        self.findings = list(findings or [])
        self.insert_calls = 0

    def query(self, query, parameters):
        rows = self.events if "spark_events" in query else self.findings
        return Result(rows)

    def insert(self, table, data, column_names, database):
        self.insert_calls += 1
        self.findings.extend(dict(zip(column_names, row)) for row in data)
        return InsertResult(len(data))


def event():
    return StageEvent(
        job_id="job-1", app_id="app-1", app_name="canonical", stage_id=2,
        stage_attempt=0, ts=1, shuffle_read_bytes=100, shuffle_write_bytes=50,
        spill_disk_bytes=0, spill_mem_bytes=0, gc_time_ms=0, input_bytes=10,
        output_bytes=20, peak_execution_mem_bytes=1000, task_count=4,
        task_duration_p50_ms=10, task_duration_p99_ms=20,
        plan_fingerprint="a" * 64, plan_json="{}",
    ).model_dump()


def finding():
    return Finding(
        finding_id="finding-1", job_id="job-1", stage_id=2,
        type=FindingType.SHUFFLE, severity=Severity.WARNING,
        evidence="observed shuffle", impact="possible pressure", fix="inspect partitioning",
        confidence=Confidence.HIGH, detected_by="test_watcher",
        ts=datetime(2026, 7, 22, tzinfo=timezone.utc),
    )


def analyzer(_events):
    return {"mode": "deterministic", "llm_calls": 0, "findings": [finding()], "rejected": []}


def full_analyzer(_job_id, _store):
    # Mirrors `analyzer`'s findings so the gate's expected set matches (the two seams
    # must agree in tests; in production full_analyzer is the real AQE-inclusive analyze()).
    return {"mode": "deterministic", "llm_calls": 0, "findings": [finding()], "rejected": []}


def probe(findings):
    async def call(job_id):
        return {
            "tools": [{"name": "analyze_run", "read_only": True}],
            "diagnosis": {
                "job_id": job_id,
                "status": "findings" if findings else "healthy",
                "stages": [{"stage_id": 2}],
                "findings": findings,
            },
        }

    return call


def test_gate_persists_once_and_validates_mcp():
    client = FakeClient([event()])
    result = asyncio.run(run_gate(job_id="job-1", client=client, mcp_probe=probe([finding().model_dump(mode="json")]), analyzer=analyzer, full_analyzer=full_analyzer))
    assert result["status"] == "passed"
    assert result["lanes"]["engine"]["persistence"]["mode"] == "inserted"
    assert client.insert_calls == 1


def test_gate_is_idempotent_when_matching_findings_exist():
    persisted = finding().to_clickhouse_row()
    client = FakeClient([event()], [persisted])
    result = asyncio.run(run_gate(job_id="job-1", client=client, mcp_probe=probe([persisted]), analyzer=analyzer, full_analyzer=full_analyzer))
    assert result["lanes"]["engine"]["persistence"]["mode"] == "already_present"
    assert client.insert_calls == 0


def test_gate_fails_without_canonical_telemetry():
    client = FakeClient([])
    try:
        asyncio.run(run_gate(job_id="job-1", client=client, mcp_probe=probe([]), analyzer=analyzer, full_analyzer=full_analyzer))
    except GateFailure as exc:
        assert str(exc) == "canonical_telemetry_not_found"
    else:
        raise AssertionError("GateFailure was not raised")


def test_gate_fails_on_mcp_finding_divergence():
    client = FakeClient([event()])
    try:
        asyncio.run(run_gate(job_id="job-1", client=client, mcp_probe=probe([]), analyzer=analyzer, full_analyzer=full_analyzer))
    except GateFailure as exc:
        assert str(exc).startswith("mcp_finding_mismatch:")
    else:
        raise AssertionError("GateFailure was not raised")
