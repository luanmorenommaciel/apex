"""Evidence validation — nothing leaves the engine on an unsupported claim.

This runs on EVERY finding, Tier-1 or crew-produced. Its job is to prove the
structured `details` actually contain the measurement the finding's prose
asserts, so a judged/LLM-adjusted finding cannot invent evidence that Tier 1
never observed.
"""

from __future__ import annotations

from .schema import Finding, FindingType

RULE_SET = "apex.engine.evidence_validator.v0.2"

# type -> (details key, minimum value, issue tag) for the simple cases.
_REQUIRED_MEASUREMENTS: dict[FindingType, tuple[str, float, str]] = {
    FindingType.SHUFFLE: ("shuffle_read_bytes", 1.0, "missing_shuffle_bytes"),
    FindingType.MEMORY: ("gc_ratio", 0.10, "missing_gc_ratio"),
    FindingType.SPILL: ("spilled_bytes", 1.0, "missing_spill_bytes"),
    FindingType.DUPLICATE_SCAN: ("rescanned_bytes", 1.0, "missing_rescanned_bytes"),
}

_COST_KEYS = ("shuffle_to_input_ratio", "output_to_input_ratio")


def validate_finding(finding: Finding) -> dict[str, object]:
    issues: list[str] = []
    details = finding.details

    if not finding.job_id:
        issues.append("missing_job_id")
    if not finding.evidence:
        issues.append("missing_evidence")
    if not finding.impact:
        issues.append("missing_impact")
    if not finding.fix:
        issues.append("missing_fix")
    if not 0.0 <= finding.confidence_score <= 1.0:
        issues.append("confidence_score_out_of_range")

    issues.extend(_measurement_issues(finding, details))

    return {
        "rule_set": RULE_SET,
        "accepted": not issues,
        "status": "valid" if not issues else "invalid",
        "issues": issues,
    }


def _measurement_issues(finding: Finding, details: dict[str, object]) -> list[str]:
    finding_type = finding.type

    if finding_type is FindingType.SKEW_ON_JOIN:
        # An AQE skew_split is Spark's own runtime decision — ground truth that
        # needs no p99/p50 ratio to stand behind it.
        if details.get("ground_truth"):
            return []
        if details.get("tail_outlier_candidate"):
            return (
                _floor(details, "tail_ratio", 10.0, "missing_tail_ratio")
                + _floor(details, "task_count", 100.0, "missing_task_count")
            )
        return (
            _floor(details, "skew_ratio", 5.0, "missing_skew_ratio")
            + _floor(details, "task_count", 2.0, "missing_task_count")
        )

    if finding_type is FindingType.DRIVER_OOM:
        return [] if details.get("failure_reason") else ["missing_failure_reason"]

    if finding_type is FindingType.CARTESIAN_PRODUCT:
        return [] if details.get("operator") else ["missing_plan_operator"]

    if finding_type is FindingType.AQE_REPLAN:
        return [] if details.get("transitions") else ["missing_plan_transitions"]

    if finding_type is FindingType.COST:
        return [] if any(key in details for key in _COST_KEYS) else ["missing_cost_ratio"]

    required = _REQUIRED_MEASUREMENTS.get(finding_type)
    if required is None:
        return []
    key, floor, issue = required
    return _floor(details, key, floor, issue)


def _floor(details: dict[str, object], field: str, minimum: float, issue: str) -> list[str]:
    value = details.get(field)
    if value is None:
        return [issue]
    try:
        return [] if float(value) >= minimum else [issue]
    except (TypeError, ValueError):
        return [issue]
