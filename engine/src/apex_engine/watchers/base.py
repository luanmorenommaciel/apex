"""Shared plumbing for the Tier-1 watchers.

Every watcher in this package is a DETERMINISTIC rule. It runs parameterized
SQL against ClickHouse, evaluates a threshold in plain Python, and returns
`Finding`s. None of them calls an LLM, none of them is a CrewAI agent, and none
of them is `@tool`-wrapped — that is the whole point of the two-tier design and
it is what keeps 95%+ of findings at $0.

Each watcher exposes:
  * `SQL`        — the parameterized query it pushes down (documentation + the
                   pushdown the ClickHouse path uses);
  * `evaluate()` — the pure rule over a `StageAggregate` / list of them, which
                   re-checks the threshold so the offline path is equally correct.
"""

from __future__ import annotations

from typing import Any

from ..schema import Finding, FindingType, Severity, StageAggregate

# Job-level findings are not attributable to one stage. Contract v0.2 is
# explicit that linking an AQE transition to specific stage_ids "needs an
# execution_id->job->stage map ... a later enhancement, not blocking", so the
# engine writes this sentinel rather than inventing a stage attribution.
JOB_LEVEL_STAGE_ID = -1

MIB = 1024 * 1024
GIB = 1024 * MIB


def build_finding(
    *,
    job_id: str,
    app_id: str,
    stage_id: int,
    finding_type: FindingType,
    severity: Severity,
    confidence_score: float,
    evidence: str,
    impact: str,
    fix: str,
    detected_by: str,
    details: dict[str, Any] | None = None,
    hot_key: str = "",
) -> Finding:
    return Finding(
        job_id=job_id,
        stage_id=stage_id,
        type=finding_type,
        severity=severity,
        evidence=evidence,
        hot_key=hot_key,
        impact=impact,
        fix=fix,
        confidence_score=confidence_score,
        detected_by=detected_by,
        app_id=app_id,
        details=dict(details or {}),
    )


def stage_finding(stage: StageAggregate, **kwargs: Any) -> Finding:
    """`build_finding` with identity filled in from the stage row."""
    return build_finding(job_id=stage.job_id, app_id=stage.app_id, stage_id=stage.stage_id, **kwargs)


def human_bytes(value: int) -> str:
    if value >= GIB:
        return f"{value / GIB:.2f} GiB"
    if value >= MIB:
        return f"{value / MIB:.2f} MiB"
    return f"{value} B"
