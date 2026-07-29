"""Evidence validation — nothing leaves the engine on an unsupported claim.

This runs on EVERY finding, Tier-1 or crew-produced. Its job is to prove the
structured `details` actually contain the measurement the finding's prose
asserts, so a judged/LLM-adjusted finding cannot invent evidence that Tier 1
never observed.
"""

from __future__ import annotations

from .config import CONFIDENCE_MEDIUM_MAX, ESCALATE_BELOW_CONFIDENCE
from .physics import MIN_TASKS_FOR_RATIO, SLOTS_UNKNOWN, TAIL_BOUND
from .schema import Finding, FindingType
from .watchers.skew import MIN_BYTES_PER_TASK

RULE_SET = "apex.engine.evidence_validator.v0.4"

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

    if finding_type in (FindingType.SKEW_ON_JOIN, FindingType.TASK_SKEW):
        return _skew_issues(finding, details)

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


def _skew_issues(finding: Finding, details: dict[str, object]) -> list[str]:
    """The second net under the three defects the skew watcher was rebuilt for.

    The validator does not re-derive the verdict; it refuses to let a skew claim
    out unless the structured evidence records that each rule was actually
    applied. That matters most for a JUDGED finding: the crew may recalibrate a
    finding, but it cannot launder a fabricated type or an unevaluated threshold
    past this, and the old `skew_ratio >= 5` floor here would have re-admitted
    exactly the fixed threshold CONTRACT.md rule 1 removes.
    """
    # An AQE skew_split is Spark's own runtime decision — ground truth that needs
    # no p99/p50 ratio behind it.
    if details.get("ground_truth"):
        return []

    issues = _floor(details, "skew_ratio", 1.0, "missing_skew_ratio")
    issues += _floor(details, "task_count", float(MIN_TASKS_FOR_RATIO), "task_count_below_distribution")
    # BUG 3 — a ratio over kilobytes is not a statistic.
    issues += _floor(details, "bytes_per_task", float(MIN_BYTES_PER_TASK), "volume_below_skew_floor")

    # BUG 2 — rule 1 must have been evaluated, and must not have said work-bound.
    verdict = details.get("tail_bound_verdict")
    if verdict is None:
        issues.append("missing_tail_bound_verdict")
    elif verdict not in (TAIL_BOUND, SLOTS_UNKNOWN):
        issues.append(f"not_tail_bound:{verdict}")
    elif verdict == SLOTS_UNKNOWN and finding.confidence_score >= _unknown_width_cap(details):
        # Rule 1: an unknown width caps confidence. AQE ground truth may lift the
        # cap to the MEDIUM ceiling — it proves the skew, not what it costs — but
        # nothing may assert HIGH without the width the closed form needs.
        issues.append("uncapped_confidence_without_cluster_width")

    # BUG 1 — the type must follow the plan.
    if finding.type is FindingType.SKEW_ON_JOIN:
        if not details.get("join_node"):
            issues.append("join_skew_without_join_node")
        if not float(details.get("shuffle_read_bytes", 0) or 0) > 0:
            issues.append("join_skew_without_shuffle_read")
    return issues


def _unknown_width_cap(details: dict[str, object]) -> float:
    return CONFIDENCE_MEDIUM_MAX if details.get("aqe_corroborated") else ESCALATE_BELOW_CONFIDENCE


def _floor(details: dict[str, object], field: str, minimum: float, issue: str) -> list[str]:
    value = details.get(field)
    if value is None:
        return [issue]
    try:
        return [] if float(value) >= minimum else [issue]
    except (TypeError, ValueError):
        return [issue]
