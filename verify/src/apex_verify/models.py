"""Typed results for the verify lane.

Design rule that shapes every model here: **this lane's output is evidence, not
authority.** It never carries an "apply this" flag, and `Verdict` has no field
that could be read as permission. `serve.suggest_fix` keeps `applied=False` /
`requires_human_approval=True`; verify only strengthens (or demolishes) its
rationale.

The confidence ladder matches `engine`'s exactly (< 0.60 LOW, < 0.85 MEDIUM,
else HIGH) so a verification tier and a finding tier mean the same thing to a
human reading them side by side.

**Asymmetric confidence** is deliberate and load-bearing. Proving a fix *cannot*
help is a deduction from facts already in hand ("that flag is already set");
predicting *how much* it will help is an extrapolation from two order
statistics. So a refusal may be HIGH while an un-replayed improvement is capped
at MEDIUM. See `PREDICTED_IMPROVEMENT_SCORE_CAP`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

# Tier boundaries — identical to engine/src/apex_engine/config.py.
CONFIDENCE_LOW_MAX = 0.60
CONFIDENCE_MEDIUM_MAX = 0.85

# An improvement we have only PREDICTED (never executed) may not claim HIGH.
# 0.74 lands mid-MEDIUM. A refusal is not subject to this cap.
PREDICTED_IMPROVEMENT_SCORE_CAP = 0.74

# The work total is estimated from (p50, p99, task_count) because
# `executor_run_time_ms` exists in engine's in-memory StageEvent but is NOT a
# column in apex.spark_events (verified against system.columns). Any prediction
# resting on the work estimate is therefore bracketed, never point-valued.
WORK_IS_ESTIMATED = True


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


class VerifyMethod(str, Enum):
    """How the verdict was reached. `REFUSED` is a first-class success."""

    PREDICTED = "predicted"   # analytic only — nothing was executed
    REPLAYED = "replayed"     # measured on the synthetic bench
    REFUSED = "refused"       # not verifiable, or provably pointless


class ReplayVerdict(str, Enum):
    """Contract rule 4: mechanism and runtime are SEPARATE first-class verdicts.

    Forced by real data: on the calibrated bench the skew fix's mechanism
    PROVABLY fired (skew_split 3/3, tail ratio 18–24x → 1.4–2.6x, ~−90% vs a
    ~13% ratio floor) while the runtime delta stayed unresolvable (−9.9% vs a
    ±17% floor). Reporting that as "nothing" would be a lie; reporting −9.9%
    would be a bigger one. So a replay emits a PAIR:

      * MECHANISM_CONFIRMED — the fix observably acted (ground-truth transition
        and/or tail-ratio collapse beyond its own measured floor). Does NOT
        require clearing the runtime floor.
      * RUNTIME_CERTIFIED   — |delta| >= measured CV floor AND >= 2 distinct
        configs (rules 2+3). The ratified significance rule; SE-of-median was
        considered and REJECTED (reps on a shared host are not independent;
        and it invites adding reps until significance appears).
      * RUNTIME_UNRESOLVED  — the honest verdict when the mechanism fired but
        the magnitude cannot clear the floor. Emitted WITH mechanism_confirmed:
        the bench certifies mechanism today and defers magnitude.
    """

    MECHANISM_CONFIRMED = "mechanism_confirmed"
    RUNTIME_CERTIFIED = "runtime_certified"
    RUNTIME_UNRESOLVED = "runtime_unresolved"


class Predictor(str, Enum):
    NOOP_GATE = "noop_gate"                    # the config is already active
    MECHANISM_CHECK = "mechanism_check"        # the claimed pathology is impossible here
    NOISE_FLOOR = "noise_floor"                # the signal is inside run-to-run variance
    AMDAHL_TAIL_SHARE = "amdahl_tail_share"    # work-bound vs tail-bound ceiling
    PARTITION_SIZING = "partition_sizing"
    NONE = "none"


class SafetyVerdict(str, Enum):
    ALLOW = "allow"
    BLOCK_SIZE = "block_size"            # optimizedPlan.stats.sizeInBytes over budget
    BLOCK_SIZE_UNKNOWN = "block_size_unknown"  # stats absent (Long.MaxValue) -> fail closed
    BLOCK_AST = "block_ast"              # code contains a write/DDL op
    BLOCK_NO_BENCH = "block_no_bench"    # no synthetic bench reproduces this shape
    NOT_APPLICABLE = "not_applicable"    # nothing was going to be executed anyway


class ConfigKnowledge(str, Enum):
    """Whether we actually know the observed run's effective SparkConf.

    Contract v0.4 (`apex.job_conf`) made ClickHouse the primary source, so the
    no-op gate works on any platform that ships Apex telemetry. The History
    Server REST API remains as fallback for pre-v0.4 runs (see
    `config_source.py`). `UNKNOWN` is not a failure — it is a confidence cap
    plus an explicit caveat. Separately, even a KNOWN conf may not carry
    `spark.executor.*` (captured only if explicitly set), so cluster width can
    still be undeterminable — that caps confidence too (contract rule 1).
    """

    KNOWN = "known"
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"


class StageObservation(BaseModel):
    """The captured metrics for one stage — the only input the predictor trusts."""

    model_config = ConfigDict(extra="ignore")

    stage_id: int
    task_count: int = Field(ge=0)
    task_duration_p50_ms: float = Field(ge=0)
    task_duration_p99_ms: float = Field(ge=0)
    shuffle_read_bytes: int = Field(default=0, ge=0)
    shuffle_write_bytes: int = Field(default=0, ge=0)
    input_bytes: int = Field(default=0, ge=0)
    spill_disk_bytes: int = Field(default=0, ge=0)
    plan_fingerprint: str = ""
    plan_json: str = ""

    @property
    def skew_ratio(self) -> float:
        p50 = self.task_duration_p50_ms
        return self.task_duration_p99_ms / p50 if p50 else 0.0

    @property
    def bytes_touched(self) -> int:
        """Bytes this stage actually moved. Skew is a property of data volume."""
        return self.shuffle_read_bytes + self.shuffle_write_bytes + self.input_bytes

    @property
    def bytes_per_task(self) -> float:
        return self.bytes_touched / self.task_count if self.task_count else 0.0


class FindingRef(BaseModel):
    """The subset of contract `findings` that verification needs."""

    model_config = ConfigDict(extra="ignore")

    finding_id: str
    job_id: str
    app_id: str = ""
    stage_id: int
    type: str
    severity: str = ""
    evidence: str = ""
    fix: str = ""
    confidence_score: float = 0.0
    detected_by: str = ""


class Guardrail(BaseModel):
    """One deterministic check that can veto or bound a prediction."""

    name: Predictor
    fired: bool
    verdict: str          # short machine-ish label, e.g. "already_active"
    detail: str           # human-readable derivation, Apex-authored
    caps_delta_at_zero: bool = False
    score: float | None = None   # confidence this guardrail alone justifies


class Prediction(BaseModel):
    """Analytic estimate. Always bracketed — never a bare point value."""

    predictor: Predictor
    delta_pct: float          # signed; negative = faster
    low_pct: float            # least improvement in the bracket
    high_pct: float           # most improvement in the bracket
    evidence: str
    caveats: str = ""
    guardrails: list[Guardrail] = Field(default_factory=list)


class Measurement(BaseModel):
    """Result of a two-arm replay on the synthetic bench.

    Two contract rules are enforced by the `significant` property:

    * RULE 2 (noise floor): `noise_floor_pct` is the run-to-run coefficient of
      variation of the BASELINE arm, measured at the level and scale being
      compared — never inherited from another level (5.8% job/tiny → 9.2%
      job/calibrated → 37.7% shape). When the baseline arm had too few reps to
      measure it, `floor_measured` is False and no delta may be quoted.
    * RULE 3 (attributability): the comparison must contain ≥ 2 distinct
      configurations. When both arms canonicalise to the same conf (the
      fix-already-on case) `attributable` is False and the verdict is
      "unattributable", never "0% improvement".

    When `significant` is False, `resolved_delta_pct` is None and consumers
    MUST NOT render the number — they show "indistinguishable from zero",
    "floor unmeasured", or "unattributable" instead.
    """

    delta_pct: float
    baseline_ms: float
    treatment_ms: float
    noise_floor_pct: float
    floor_measured: bool = True
    reps: int = Field(ge=1)
    bench: str
    shape_fidelity: float = Field(ge=0.0, le=1.0)
    attributable: bool = True
    attribution_detail: str = ""
    # Contract rule 4: mechanism evidence, independent of the runtime verdict.
    # None = no mechanism data was collected; True/False = it fired / it didn't.
    mechanism_confirmed: bool | None = None
    mechanism_detail: str = ""
    baseline_samples_ms: list[float] = Field(default_factory=list)
    treatment_samples_ms: list[float] = Field(default_factory=list)

    @property
    def significant(self) -> bool:
        return (
            self.attributable
            and self.floor_measured
            and abs(self.delta_pct) >= self.noise_floor_pct
        )

    @property
    def resolved_delta_pct(self) -> float | None:
        """The only delta a consumer may quote. None ⇒ no quotable number."""
        return self.delta_pct if self.significant else None

    @property
    def runtime_verdict(self) -> "ReplayVerdict | None":
        """The runtime half of the rule-4 pair. None when rule 3 voids the
        comparison entirely (unattributable arms get no verdict of any kind)."""
        if not self.attributable:
            return None
        if self.significant:
            return ReplayVerdict.RUNTIME_CERTIFIED
        return ReplayVerdict.RUNTIME_UNRESOLVED

    @property
    def verdicts(self) -> list["ReplayVerdict"]:
        """The rule-4 pair, e.g. [mechanism_confirmed, runtime_unresolved]."""
        out: list[ReplayVerdict] = []
        if self.mechanism_confirmed:
            out.append(ReplayVerdict.MECHANISM_CONFIRMED)
        rv = self.runtime_verdict
        if rv is not None:
            out.append(rv)
        return out


class SafetyReport(BaseModel):
    safe: bool
    verdict: SafetyVerdict
    detail: str = ""


class Verdict(BaseModel):
    """What `serve.suggest_fix` consumes. Carries no authority to apply anything."""

    model_config = ConfigDict(extra="ignore")

    verification_id: str = Field(default_factory=lambda: str(uuid4()))
    finding_id: str
    job_id: str
    app_id: str = ""
    proposed_config: dict[str, str]

    method: VerifyMethod
    predictor: Predictor
    predicted_delta_pct: float
    predicted_low_pct: float
    predicted_high_pct: float

    measurement: Measurement | None = None
    safety: SafetyReport
    config_knowledge: ConfigKnowledge = ConfigKnowledge.UNKNOWN

    confidence: Confidence
    confidence_score: float
    evidence: str
    caveats: str = ""
    guardrails: list[Guardrail] = Field(default_factory=list)
    verify_version: str = "0.1.0"
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # This lane produces evidence only. These are Literal-style invariants held
    # by construction so a Verdict can never be read as authorisation.
    applied: bool = Field(default=False, frozen=True)
    requires_human_approval: bool = Field(default=True, frozen=True)

    @property
    def measured_delta_pct(self) -> float | None:
        return self.measurement.delta_pct if self.measurement else None

    def headline(self) -> str:
        """One sentence a human can act on. Honest by construction."""
        if self.method is VerifyMethod.REFUSED:
            return f"NOT WORTH APPLYING — {self.evidence}"
        if self.measurement is not None:
            m = self.measurement
            if not m.attributable:
                return (
                    f"UNATTRIBUTABLE — replayed on {m.bench} but the comparison holds "
                    "fewer than 2 distinct configurations, so the observed "
                    f"{m.delta_pct:+.1f}% is run-to-run variance with nothing to "
                    "credit it to (contract rule 3). This is the fix-already-on case: "
                    "it is not a 0% improvement, it is no measurement at all"
                )
            if not m.floor_measured:
                return (
                    f"FLOOR UNMEASURED — replayed on {m.bench} with too few baseline "
                    "reps to measure the noise floor at this level and scale "
                    f"(contract rule 2); the observed {m.delta_pct:+.1f}% may not be quoted"
                )
            resolved = m.resolved_delta_pct
            if resolved is None:
                if m.mechanism_confirmed:
                    return (
                        f"MECHANISM CONFIRMED, RUNTIME UNRESOLVED — {m.mechanism_detail} "
                        f"But the measured {m.delta_pct:+.1f}% is inside the "
                        f"±{m.noise_floor_pct:.1f}% floor on {m.bench}: magnitude "
                        "deferred, not denied (contract rule 4)"
                    )
                return (
                    f"NO MEASURABLE CHANGE — replayed on {m.bench}; "
                    f"the {m.delta_pct:+.1f}% observed is inside the "
                    f"±{m.noise_floor_pct:.1f}% noise floor of the bench"
                )
            return (
                f"VERIFIED {resolved:+.1f}% runtime, replayed on "
                f"{m.bench} (predicted {self.predicted_delta_pct:+.1f}%)"
            )
        return (
            f"UNVERIFIED, PREDICTED ONLY — {self.predicted_delta_pct:+.1f}% "
            f"(bracket {self.predicted_low_pct:+.1f}%..{self.predicted_high_pct:+.1f}%), "
            f"{self.confidence.value} confidence"
        )

    def to_row(self) -> dict[str, Any]:
        """Flatten to one apex.fix_verifications row (proposed contract v0.3)."""
        import json

        m = self.measurement
        return {
            "verification_id": self.verification_id,
            "finding_id": self.finding_id,
            "job_id": self.job_id,
            "app_id": self.app_id,
            "proposed_config": json.dumps(self.proposed_config, sort_keys=True),
            "method": self.method.value,
            "predictor": self.predictor.value,
            "predicted_delta_pct": self.predicted_delta_pct,
            "predicted_low_pct": self.predicted_low_pct,
            "predicted_high_pct": self.predicted_high_pct,
            # NULL ⇒ never replayed. 0.0 ⇒ replayed, no change. Not the same thing.
            "measured_delta_pct": m.delta_pct if m else None,
            "baseline_ms": m.baseline_ms if m else None,
            "treatment_ms": m.treatment_ms if m else None,
            # NULL when the baseline arm had too few reps to measure a floor —
            # an unmeasured floor is not a 0% floor.
            "noise_floor_pct": (m.noise_floor_pct if m and m.floor_measured else None) if m else None,
            "replay_reps": m.reps if m else 0,
            "bench": m.bench if m else "",
            "shape_fidelity": m.shape_fidelity if m else 0.0,
            "safe": 1 if self.safety.safe else 0,
            "safety_verdict": self.safety.verdict.value,
            "safety_detail": self.safety.detail,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "evidence": self.evidence,
            "caveats": self.caveats,
            "verify_version": self.verify_version,
            "verified_at": self.verified_at,
        }
