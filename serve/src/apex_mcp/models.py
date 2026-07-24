"""Structured read-only MCP outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FindingView(BaseModel):
    finding_id: str
    job_id: str
    stage_id: int
    type: str
    severity: str
    evidence: str
    impact: str
    fix: str
    confidence: str
    detected_by: str


class StageView(BaseModel):
    stage_id: int
    shuffle_read_bytes: int
    spilled_bytes: int
    p50_ms: float
    p99_ms: float
    p99_p50_ratio: float


class Diagnosis(BaseModel):
    job_id: str
    app_id: str | None = None
    status: Literal["healthy", "findings", "not_found"]
    stages: list[StageView] = Field(default_factory=list)
    findings: list[FindingView] = Field(default_factory=list)
    summary: str


class MetricComparison(BaseModel):
    metric: str
    before: float
    after: float
    delta: float
    direction: Literal["lower_is_better"] = "lower_is_better"
    status: Literal["improved", "regressed", "unchanged"]


class RunComparison(BaseModel):
    baseline_job_id: str
    current_job_id: str
    status: Literal["improved", "regressed", "unchanged", "not_comparable"]
    comparisons: list[MetricComparison] = Field(default_factory=list)
    missing_job_ids: list[str] = Field(default_factory=list)
