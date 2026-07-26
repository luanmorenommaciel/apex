"""Contract conformance: the Finding shape, the enums, and the fixture path."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from apex_engine import (
    Confidence,
    Finding,
    FindingType,
    Severity,
    StageEvent,
    analyze_events,
)
from apex_engine.clickhouse import aggregate_events
from apex_engine.validation import validate_finding
from apex_engine.watchers import run_all_offline

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "contract" / "sample_event.json"

# Exactly the columns in contract/findings.ddl.sql (v0.2 added app_id +
# confidence_score alongside the confidence enum).
DDL_COLUMNS = {
    "finding_id", "job_id", "app_id", "stage_id", "type", "severity", "evidence",
    "hot_key", "impact", "fix", "confidence", "confidence_score", "detected_by", "ts",
}


def fixture_event(**overrides):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload.update(overrides)
    return StageEvent.model_validate(payload)


def clean_event(**overrides):
    payload = {
        "job_id": "clean-job", "app_id": "clean-app", "stage_id": 1,
        "stage_attempt": 0, "ts": 1, "shuffle_read_bytes": 0,
        "shuffle_write_bytes": 0, "spill_disk_bytes": 0, "spill_mem_bytes": 0,
        "gc_time_ms": 0, "input_bytes": 1_000_000, "output_bytes": 1_000_000,
        "peak_execution_mem_bytes": 0, "task_count": 8,
        "task_duration_p50_ms": 100, "task_duration_p99_ms": 120,
        "task_duration_max_ms": 120,
        "plan_fingerprint": "f" * 64, "plan_json": "Project [id]",
    }
    payload.update(overrides)
    return StageEvent.model_validate(payload)


def test_contract_fixture_becomes_valid_stage_event():
    event = fixture_event()
    assert event.job_id == "ax151sasadds114"
    assert event.p99_p50_ratio > 10
    assert event.max_p50_ratio >= event.p99_p50_ratio


def test_pre_tail_metric_event_remains_compatible():
    payload = clean_event().model_dump()
    payload.pop("task_duration_max_ms")
    event = StageEvent.model_validate(payload)
    assert event.task_duration_max_ms == 0
    assert event.max_p50_ratio == 0


def test_tail_outlier_candidate_passes_evidence_validation():
    event = clean_event(
        task_count=200,
        task_duration_p50_ms=100,
        task_duration_p99_ms=100,
        task_duration_max_ms=3_000,
    )
    findings = run_all_offline(aggregate_events([event]))
    tail = [f for f in findings if f.detected_by == "tail_outlier_watcher"]
    assert len(tail) == 1
    assert validate_finding(tail[0])["accepted"] is True


def test_fixture_detections_are_valid_and_rows_match_ddl_exactly():
    findings = run_all_offline(aggregate_events([fixture_event()]))
    assert {f.type for f in findings} >= {FindingType.SKEW_ON_JOIN, FindingType.SHUFFLE, FindingType.SPILL}
    for finding in findings:
        assert validate_finding(finding)["accepted"] is True
        assert set(finding.to_clickhouse_row()) == DDL_COLUMNS


def test_clean_event_has_zero_findings_and_zero_llm_calls():
    result = analyze_events([clean_event()])
    assert result["findings"] == []
    assert result["rejected"] == []
    assert result["llm_calls"] == 0
    assert result["mode"] == "deterministic"


# --- the Finding <-> DDL reconciliation -----------------------------------

def _finding(**overrides):
    payload = {
        "job_id": "job-1", "stage_id": 2, "type": FindingType.SHUFFLE,
        "severity": Severity.WARNING, "evidence": "e", "impact": "i", "fix": "f",
        "detected_by": "test_watcher",
    }
    payload.update(overrides)
    return Finding(**payload)


def test_enum_confidence_backfills_a_score():
    """The P0 runner constructs findings with the enum; the gate needs a float."""
    finding = _finding(confidence=Confidence.HIGH)
    assert finding.confidence is Confidence.HIGH
    assert finding.confidence_score == pytest.approx(0.92)


def test_score_backfills_the_enum_the_column_stores():
    """The watchers produce a score; the DDL column is Enum8('LOW','MEDIUM','HIGH')."""
    assert _finding(confidence_score=0.55).confidence is Confidence.LOW
    assert _finding(confidence_score=0.72).confidence is Confidence.MEDIUM
    assert _finding(confidence_score=0.95).confidence is Confidence.HIGH


def test_low_confidence_bucket_is_exactly_the_gate_threshold():
    """`confidence == LOW` must mean "escalation-eligible" and nothing else."""
    assert Confidence.from_score(0.599) is Confidence.LOW
    assert Confidence.from_score(0.6) is Confidence.MEDIUM


def test_out_of_range_confidence_raises():
    with pytest.raises(ValidationError):
        _finding(confidence_score=1.4)


def test_both_confidence_forms_are_persisted():
    """v0.2 stores the raw score AND the display tier; they must agree."""
    row = _finding(confidence_score=0.55, app_id="app-9").to_clickhouse_row()
    assert row["confidence_score"] == pytest.approx(0.55)
    assert row["confidence"] == "LOW"
    assert row["app_id"] == "app-9"


def test_row_is_exactly_the_ddl_columns():
    """`details` is in-memory scaffolding — there is no such column."""
    row = _finding(confidence=Confidence.HIGH, details={"k": "v"}).to_clickhouse_row()
    assert set(row) == DDL_COLUMNS
    assert "details" not in row


def test_severity_ladder_orders_as_the_contract_declares():
    assert Severity.CRITICAL.at_least(Severity.CRITICAL)
    assert Severity.BLOCKER.at_least(Severity.CRITICAL)
    assert not Severity.WARNING.at_least(Severity.CRITICAL)
    assert not Severity.INFO.at_least(Severity.WARNING)


def test_enum_values_are_writable_to_the_enum8_columns():
    """A value outside these sets would be rejected by ClickHouse at insert time."""
    assert {s.value for s in Severity} == {"info", "warning", "critical", "blocker"}
    assert {c.value for c in Confidence} == {"LOW", "MEDIUM", "HIGH"}


def test_latest_attempt_wins_when_a_stage_is_retried():
    """aggregate_events must reduce like argMax(col, ts), not max(col)."""
    slow = clean_event(
        stage_id=3, stage_attempt=0, ts=1,
        task_duration_p50_ms=10, task_duration_p99_ms=900, task_duration_max_ms=1_000,
    )
    retry = clean_event(
        stage_id=3, stage_attempt=1, ts=2,
        task_duration_p50_ms=100, task_duration_p99_ms=120, task_duration_max_ms=130,
    )
    aggregates = aggregate_events([slow, retry])
    assert len(aggregates) == 1
    assert aggregates[0].task_duration_p99_ms == 120  # the retry, not the max
    assert aggregates[0].task_duration_max_ms == 130
    assert aggregates[0].skew_ratio < 5
