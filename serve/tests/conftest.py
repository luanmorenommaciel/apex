"""Shared fakes — the diagnosis layer is pure, so no ClickHouse is needed."""

from __future__ import annotations

from typing import Any

import pytest

from apex_mcp.ch import ReadStore

FINGERPRINT_A = "a" * 64
FINGERPRINT_B = "b" * 64


def stage_row(
    stage_id: int = 2,
    *,
    job_id: str = "job-1",
    p50_ms: int = 100,
    p99_ms: int = 100,
    spill_disk_bytes: int = 0,
    spill_mem_bytes: int = 0,
    shuffle_read_bytes: int = 0,
    shuffle_write_bytes: int = 0,
    gc_time_ms: int = 0,
    task_count: int = 50,
    plan_fingerprint: str = FINGERPRINT_A,
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "stage_attempt": 0,
        "app_id": f"app-{job_id}",
        "app_name": "test-app",
        "task_count": task_count,
        "shuffle_read_bytes": shuffle_read_bytes,
        "shuffle_write_bytes": shuffle_write_bytes,
        "spill_disk_bytes": spill_disk_bytes,
        "spill_mem_bytes": spill_mem_bytes,
        "gc_time_ms": gc_time_ms,
        "input_bytes": 0,
        "output_bytes": 0,
        "peak_execution_mem_bytes": 0,
        "p50_ms": p50_ms,
        "p99_ms": p99_ms,
        "plan_fingerprint": plan_fingerprint,
    }


def finding_row(
    *,
    job_id: str = "job-1",
    stage_id: int = 2,
    finding_id: str = "finding-1",
    type: str = "SKEW_ON_JOIN",
    severity: str = "critical",
    evidence: str = "p99/p50 = 20x",
    impact: str = "slow",
    fix: str = "enable AQE skew join",
    confidence: str = "HIGH",
    confidence_score: float = 0.0,
    hot_key: str = "",
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "job_id": job_id,
        "app_id": f"app-{job_id}",
        "stage_id": stage_id,
        "type": type,
        "severity": severity,
        "evidence": evidence,
        "hot_key": hot_key,
        "impact": impact,
        "fix": fix,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "detected_by": "skew_watcher",
    }


def transition_row(
    transition_type: str = "skew_split",
    *,
    confidence: str = "HIGH",
    detail: str = "AQEShuffleRead skewed x4",
    execution_id: int = 1,
    update_seq: int = 0,
) -> dict[str, Any]:
    return {
        "execution_id": execution_id,
        "update_seq": update_seq,
        "transition_type": transition_type,
        "detail": detail,
        "before": "1 skewed",
        "after": "4 skewed",
        "confidence": confidence,
    }


class FakeResult:
    def __init__(self, rows: list[dict]) -> None:
        self._rows = rows

    def named_results(self) -> list[dict]:
        return self._rows


class FakeClient:
    """Routes on the SQL's shape so tests never depend on exact SQL text."""

    def __init__(
        self,
        stages: dict[str, list[dict]] | None = None,
        findings: dict[str, list[dict]] | None = None,
        transitions: dict[str, list[dict]] | None = None,
        search: list[dict] | None = None,
        columns: list[str] | None = None,
    ) -> None:
        self.stages = stages or {}
        self.findings = findings or {}
        self.transitions = transitions or {}
        self.search = search or []
        self.columns = columns
        self.calls: list[tuple[str, dict]] = []

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        parameters = parameters or {}
        self.calls.append((query, parameters))
        job_id = parameters.get("job_id", "")
        if "system.columns" in query:
            names = (
                self.columns
                if self.columns is not None
                else [
                    "finding_id",
                    "job_id",
                    "app_id",
                    "stage_id",
                    "type",
                    "severity",
                    "evidence",
                    "hot_key",
                    "impact",
                    "fix",
                    "confidence",
                    "confidence_score",
                    "detected_by",
                    "ts",
                ]
            )
            return FakeResult([{"name": name} for name in names])
        if "positionCaseInsensitive" in query:
            return FakeResult(list(self.search))
        if "apex.plan_transitions" in query:
            return FakeResult(list(self.transitions.get(job_id, [])))
        if "apex.findings" in query:
            return FakeResult(list(self.findings.get(job_id, [])))
        return FakeResult(list(self.stages.get(job_id, [])))


@pytest.fixture
def store_factory():
    def build(**kwargs) -> ReadStore:
        return ReadStore(FakeClient(**kwargs))

    return build
