"""apex-verify — turn "try this" into "predicted X%, VERIFIED against a replay".

This lane NEVER applies a fix and NEVER touches customer data. It produces
evidence for `serve.suggest_fix`, which keeps `applied=False` /
`requires_human_approval=True` regardless of what this lane concludes.

Pipeline: PREDICT (analytic bound + guardrails) → REPLAY (two-arm measurement
with positive control) → SAFETY (read-only AST + size gate). The observed run's
conf comes from `config_source` — ClickHouse `apex.job_conf` (contract v0.4)
first, History Server REST as fallback.
"""

from .config_source import (
    ClickHouseJobConfSource,
    ConfigResult,
    HistoryServerSource,
    resolve_config,
    slots_from_conf,
)
from .models import (
    Confidence,
    ConfigKnowledge,
    FindingRef,
    Measurement,
    Prediction,
    Predictor,
    ReplayVerdict,
    SafetyReport,
    SafetyVerdict,
    StageObservation,
    Verdict,
    VerifyMethod,
)
from .replay import (
    Arm,
    BenchShape,
    MechanismEvidence,
    analyse_replay,
    evaluate_mechanism,
    evaluate_positive_control,
    shape_fidelity,
    verdict_from_replay,
)

__all__ = [
    "Arm",
    "BenchShape",
    "ClickHouseJobConfSource",
    "Confidence",
    "ConfigKnowledge",
    "ConfigResult",
    "FindingRef",
    "HistoryServerSource",
    "Measurement",
    "MechanismEvidence",
    "Prediction",
    "Predictor",
    "ReplayVerdict",
    "SafetyReport",
    "SafetyVerdict",
    "StageObservation",
    "Verdict",
    "VerifyMethod",
    "analyse_replay",
    "evaluate_mechanism",
    "evaluate_positive_control",
    "resolve_config",
    "shape_fidelity",
    "slots_from_conf",
    "verdict_from_replay",
]
__version__ = "0.3.0"
