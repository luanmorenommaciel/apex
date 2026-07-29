"""APEX deterministic engine built against contract v0.2.

Tier 1 (five deterministic SQL watchers + the AQE ground-truth watcher) answers
almost everything at $0. CrewAI is reached only through `gate.should_escalate`.
"""

from .clickhouse import EngineStore
from .gate import should_escalate
from .pipeline import analyze, analyze_aggregates, analyze_events, analyze_job
from .schema import (
    Confidence,
    Finding,
    FindingType,
    PlanTransition,
    Severity,
    StageAggregate,
    StageEvent,
)

__all__ = [
    "Confidence",
    "EngineStore",
    "Finding",
    "FindingType",
    "PlanTransition",
    "Severity",
    "StageAggregate",
    "StageEvent",
    "analyze",
    "analyze_aggregates",
    "analyze_events",
    "analyze_job",
    "should_escalate",
]
