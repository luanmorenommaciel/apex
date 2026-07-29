"""The escalation gate — the single place that decides whether money is spent.

BOTH conditions must hold (docs/lanes/ENGINE.md T10):

    confidence < 0.6  AND  severity >= high

`severity >= high` is expressed against the contract ladder, which has no
`high` rung: `info < warning < critical < blocker`. `critical` is the third
rung, the same position `high` occupies in a four-rung ladder, so it is the
threshold. See `Severity` in schema.py.

A finding that is confident, or that is not severe, never reaches an LLM. A
clean job produces no candidates at all and therefore makes zero LLM calls.
"""

from __future__ import annotations

from collections.abc import Iterable

from .config import ESCALATE_BELOW_CONFIDENCE
from .schema import Finding, Severity

ESCALATION_SEVERITY = Severity.CRITICAL


def should_escalate(finding: Finding) -> bool:
    return (
        finding.confidence_score < ESCALATE_BELOW_CONFIDENCE
        and finding.severity.at_least(ESCALATION_SEVERITY)
    )


def partition(findings: Iterable[Finding]) -> tuple[list[Finding], list[Finding]]:
    """Split into (emit straight from Tier 1, escalate to the crew)."""
    direct: list[Finding] = []
    escalate: list[Finding] = []
    for finding in findings:
        (escalate if should_escalate(finding) else direct).append(finding)
    return direct, escalate


def explain(finding: Finding) -> str:
    """Why this finding did or did not escalate — for the trace."""
    confident = finding.confidence_score >= ESCALATE_BELOW_CONFIDENCE
    severe = finding.severity.at_least(ESCALATION_SEVERITY)
    if confident and severe:
        return f"no_escalation:confident({finding.confidence_score:.2f})"
    if confident:
        return f"no_escalation:confident({finding.confidence_score:.2f})+below_severity({finding.severity.value})"
    if not severe:
        return f"no_escalation:below_severity({finding.severity.value})"
    return f"escalate:low_confidence({finding.confidence_score:.2f})+severity({finding.severity.value})"
