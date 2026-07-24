"""Canonical in-memory models for the frozen APEX v0.2 contract."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class FindingType(str, Enum):
    SHUFFLE = "SHUFFLE"
    SKEW_ON_JOIN = "SKEW_ON_JOIN"
    MEMORY = "MEMORY"
    DRIVER_OOM = "DRIVER_OOM"
    COST = "COST"
    CARTESIAN_PRODUCT = "CARTESIAN_PRODUCT"
    AQE_REPLAN = "AQE_REPLAN"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKER = "blocker"

    @property
    def rank(self) -> int:
        return list(type(self)).index(self)

    def at_least(self, other: "Severity") -> bool:
        return self.rank >= other.rank


class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class StageEvent(BaseModel):
    """One completed Spark stage matching contract/sample_event.json.

    The optional failure and executor fields are additive runtime observations.
    They are never required for a v0.2 fixture to be valid.
    """

    model_config = ConfigDict(extra="ignore")

    job_id: str = Field(min_length=1)
    app_id: str = Field(min_length=1)
    app_name: str = ""
    stage_id: int = Field(ge=0)
    stage_attempt: int = Field(ge=0)
    ts: int = Field(ge=0)
    shuffle_read_bytes: int = Field(ge=0)
    shuffle_write_bytes: int = Field(ge=0)
    spill_disk_bytes: int = Field(ge=0)
    spill_mem_bytes: int = Field(ge=0)
    gc_time_ms: int = Field(ge=0)
    input_bytes: int = Field(ge=0)
    output_bytes: int = Field(ge=0)
    peak_execution_mem_bytes: int = Field(ge=0)
    task_count: int = Field(ge=0)
    task_duration_p50_ms: float = Field(ge=0)
    task_duration_p99_ms: float = Field(ge=0)
    plan_fingerprint: str = ""
    plan_json: str = ""
    executor_run_time_ms: int = Field(default=0, ge=0)
    failure_reason: str = ""

    @property
    def p99_p50_ratio(self) -> float:
        return self.task_duration_p99_ms / self.task_duration_p50_ms if self.task_duration_p50_ms else 0.0

    @property
    def gc_ratio(self) -> float:
        return self.gc_time_ms / self.executor_run_time_ms if self.executor_run_time_ms else 0.0


class Finding(BaseModel):
    """Finding whose persisted row matches contract/findings.ddl.sql exactly."""

    model_config = ConfigDict(frozen=True)

    finding_id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str = Field(min_length=1)
    stage_id: int = Field(ge=0)
    type: FindingType
    severity: Severity
    evidence: str = Field(min_length=1)
    hot_key: str = ""
    impact: str = Field(min_length=1)
    fix: str = Field(min_length=1)
    confidence: Confidence
    detected_by: str = Field(min_length=1)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict[str, Any] = Field(default_factory=dict, exclude=True)

    def to_clickhouse_row(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "job_id": self.job_id,
            "stage_id": self.stage_id,
            "type": self.type.value,
            "severity": self.severity.value,
            "evidence": self.evidence,
            "hot_key": self.hot_key,
            "impact": self.impact,
            "fix": self.fix,
            "confidence": self.confidence.value,
            "detected_by": self.detected_by,
            "ts": self.ts,
        }

