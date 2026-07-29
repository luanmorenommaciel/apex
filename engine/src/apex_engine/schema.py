"""Canonical in-memory models for the frozen APEX v0.2 contract.

The `Finding` row matches `contract/findings.ddl.sql`, which CONTRACT.md names
authoritative when prose and DDL disagree.

Confidence is carried in TWO forms, and both are persisted (contract v0.2):
  * `confidence_score` — the raw 0-1 Float32. This is what the escalation gate
    reasons about and what serve's `compare_runs` reads.
  * `confidence`       — the human-facing Enum8('LOW','MEDIUM','HIGH') tier that
    drives display.
Either one may be supplied at construction; the other is derived, so the two can
never contradict each other in a stored row.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .config import CONFIDENCE_LOW_MAX, CONFIDENCE_MEDIUM_MAX


class FindingType(str, Enum):
    SHUFFLE = "SHUFFLE"
    SKEW_ON_JOIN = "SKEW_ON_JOIN"
    # A tail-bound stage with real volume but NO plan evidence of a join. It is
    # a separate type because the fix is different in kind: `skewJoin.*` applies
    # only to joins, and calling a map-stage tail `SKEW_ON_JOIN` is the exact
    # fabrication that made stage 4 of app-20260724160310-0000 a false positive.
    # `findings.type` is an open `String` column in the contract DDL, so this is
    # an additive value, not a schema change.
    TASK_SKEW = "TASK_SKEW"
    MEMORY = "MEMORY"
    DRIVER_OOM = "DRIVER_OOM"
    COST = "COST"
    CARTESIAN_PRODUCT = "CARTESIAN_PRODUCT"
    AQE_REPLAN = "AQE_REPLAN"
    SPILL = "SPILL"
    DUPLICATE_SCAN = "DUPLICATE_SCAN"


class Severity(str, Enum):
    """Contract ladder — `info` < `warning` < `critical` < `blocker`.

    The gate is specified as `severity >= high`; this ladder has no `high`, so
    the third rung (`critical`) is the equivalent and is what `gate.py` uses.
    """

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

    @classmethod
    def from_score(cls, score: float) -> "Confidence":
        if score < CONFIDENCE_LOW_MAX:
            return cls.LOW
        if score < CONFIDENCE_MEDIUM_MAX:
            return cls.MEDIUM
        return cls.HIGH

    @property
    def representative_score(self) -> float:
        """Mid-bucket score, used when a Finding is built from the enum alone."""
        return {"LOW": 0.45, "MEDIUM": 0.72, "HIGH": 0.92}[self.value]


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


class StageAggregate(BaseModel):
    """One (job_id, stage_id) reduced to the shape every stage watcher reads.

    This is the single row shape produced by BOTH feeds — the ClickHouse
    watcher SQL (`argMax(..., ts)` over attempts, exactly like
    `infra/sql/005_skew.sql`) and the offline in-memory path. Watchers evaluate
    this, never raw events, so the two feeds cannot drift apart.
    """

    model_config = ConfigDict(extra="ignore")

    job_id: str = Field(min_length=1)
    app_id: str = ""
    stage_id: int = Field(ge=0)
    attempt: int = Field(default=0, ge=0)
    task_duration_p50_ms: float = Field(default=0.0, ge=0)
    task_duration_p99_ms: float = Field(default=0.0, ge=0)
    shuffle_read_bytes: int = Field(default=0, ge=0)
    shuffle_write_bytes: int = Field(default=0, ge=0)
    spill_disk_bytes: int = Field(default=0, ge=0)
    spill_mem_bytes: int = Field(default=0, ge=0)
    gc_time_ms: int = Field(default=0, ge=0)
    input_bytes: int = Field(default=0, ge=0)
    output_bytes: int = Field(default=0, ge=0)
    peak_execution_mem_bytes: int = Field(default=0, ge=0)
    task_count: int = Field(default=0, ge=0)
    plan_fingerprint: str = ""
    plan_json: str = ""
    executor_run_time_ms: int = Field(default=0, ge=0)
    failure_reason: str = ""

    @property
    def skew_ratio(self) -> float:
        """p99/p50, guarded exactly like `nullIf(p50, 0)` in 005_skew.sql."""
        return self.task_duration_p99_ms / self.task_duration_p50_ms if self.task_duration_p50_ms else 0.0

    @property
    def spilled_bytes(self) -> int:
        return self.spill_disk_bytes + self.spill_mem_bytes

    @property
    def bytes_touched(self) -> int:
        """Bytes this stage actually moved. Skew is a property of data volume.

        Identical definition to verify/'s `StageObservation.bytes_touched`, so a
        stage that is volume-ineligible in one lane is ineligible in the other.
        """
        return self.shuffle_read_bytes + self.shuffle_write_bytes + self.input_bytes

    @property
    def bytes_per_task(self) -> float:
        return self.bytes_touched / self.task_count if self.task_count else 0.0

    @property
    def gc_ratio(self) -> float:
        return self.gc_time_ms / self.executor_run_time_ms if self.executor_run_time_ms else 0.0


class PlanTransition(BaseModel):
    """One AQE runtime re-plan — contract v0.2 `apex.plan_transitions`.

    Spark's OWN optimization decision. A `skew_split` or `coalesce` here is
    ground truth, not a heuristic: it is what makes the engine's skew call
    stronger than a p99/p50 ratio alone, and it costs $0.
    """

    model_config = ConfigDict(extra="ignore")

    job_id: str = Field(min_length=1)
    execution_id: int = 0
    update_seq: int = 0
    transition_type: str = "other"
    detail: str = ""
    before: str = ""
    after: str = ""
    confidence: str = "BEST_EFFORT"  # HIGH | BEST_EFFORT, per contract v0.2

    @property
    def is_ground_truth(self) -> bool:
        """HIGH-confidence structural signals only (contract § Detection tiers)."""
        return self.confidence.upper() == "HIGH"


class Finding(BaseModel):
    """Finding whose persisted row matches contract/findings.ddl.sql exactly."""

    model_config = ConfigDict(frozen=True)

    finding_id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str = Field(min_length=1)
    app_id: str = ""
    # -1 is the job-level sentinel (see watchers/base.JOB_LEVEL_STAGE_ID): a
    # finding that contract v0.2 cannot yet attribute to a single stage, such
    # as an AQE transition keyed only by (job_id, execution_id).
    stage_id: int = Field(ge=-1)
    type: FindingType
    severity: Severity
    evidence: str = Field(min_length=1)
    hot_key: str = ""
    impact: str = Field(min_length=1)
    fix: str = Field(min_length=1)
    confidence: Confidence
    confidence_score: float = Field(default=-1.0, ge=-1.0, le=1.0)
    detected_by: str = Field(min_length=1)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Structured backing for `evidence`. In-memory only: the validator reads it
    # to prove a finding's prose is supported by a real measurement, and the
    # crew reads it as context. There is no such column.
    details: dict[str, Any] = Field(default_factory=dict, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def _reconcile_confidence(cls, data: Any) -> Any:
        """Accept either representation and fill in the other.

        Callers may pass `confidence=Confidence.HIGH` (the P0 runner does) or
        `confidence_score=0.55` (the watchers do). Both end up consistent.
        """
        if not isinstance(data, dict):
            return data
        data = dict(data)
        score = data.get("confidence_score")
        has_score = score is not None and float(score) >= 0.0
        if data.get("confidence") is None and has_score:
            data["confidence"] = Confidence.from_score(float(score))
        elif not has_score and data.get("confidence") is not None:
            data["confidence_score"] = Confidence(data["confidence"]).representative_score
        return data

    def to_clickhouse_row(self) -> dict[str, Any]:
        """Exactly the columns of contract/findings.ddl.sql, nothing else."""
        return {
            "finding_id": self.finding_id,
            "job_id": self.job_id,
            "app_id": self.app_id,
            "stage_id": self.stage_id,
            "type": self.type.value,
            "severity": self.severity.value,
            "evidence": self.evidence,
            "hot_key": self.hot_key,
            "impact": self.impact,
            "fix": self.fix,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "detected_by": self.detected_by,
            "ts": self.ts,
        }
