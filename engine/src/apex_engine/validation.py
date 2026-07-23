"""Evidence validation before a deterministic finding can leave the engine."""

from __future__ import annotations

from .schema import Finding, FindingType

RULE_SET = "apex.engine.evidence_validator.v0.2"


def validate_finding(finding: Finding) -> dict[str, object]:
    issues: list[str] = []
    details = finding.details
    if not finding.job_id:
        issues.append("missing_job_id")
    if finding.stage_id < 0:
        issues.append("invalid_stage_id")
    if not finding.evidence:
        issues.append("missing_evidence")
    if not finding.impact:
        issues.append("missing_impact")
    if not finding.fix:
        issues.append("missing_fix")
    if finding.type is FindingType.SKEW_ON_JOIN:
        _minimum(details, "p99_p50_ratio", issues, "missing_skew_ratio", 5.0)
        _minimum(details, "task_count", issues, "missing_task_count", 2.0)
    elif finding.type is FindingType.SHUFFLE:
        _minimum(details, "shuffle_read_bytes", issues, "missing_shuffle_bytes", 1.0)
    elif finding.type is FindingType.MEMORY:
        _minimum(details, "gc_ratio", issues, "missing_gc_ratio", 0.1)
    elif finding.type is FindingType.DRIVER_OOM and not details.get("failure_reason"):
        issues.append("missing_failure_reason")
    elif finding.type is FindingType.COST:
        _minimum(details, "shuffle_to_input_ratio", issues, "missing_cost_ratio", 50.0)
    elif finding.type is FindingType.CARTESIAN_PRODUCT and not details.get("operator"):
        issues.append("missing_plan_operator")
    return {"rule_set": RULE_SET, "accepted": not issues,
            "status": "valid" if not issues else "invalid", "issues": issues}


def _minimum(details: dict[str, object], field: str, issues: list[str], issue: str, minimum: float) -> None:
    value = details.get(field)
    if value is None or float(value) < minimum:
        issues.append(issue)

