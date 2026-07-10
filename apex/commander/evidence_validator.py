"""Evidence validation for Commander findings before delivery to MCP or agents."""

RULE_SET = "apex.commander.evidence_validator.v1"
MIN_SKEW_RATIO = 10.0
MIN_TASK_COUNT = 2
SUPPORTED_KINDS = {
    "shuffle_skew_candidate",
    "shuffle_spill_candidate",
    "gc_pressure_candidate",
    "oom_candidate",
    "plan_aqe_replan_candidate",
}
STAGE_LEVEL_KINDS = SUPPORTED_KINDS - {"plan_aqe_replan_candidate"}


def validate_finding(finding):
    """Return a machine-readable validation result for a Commander finding."""
    issues = []

    if not finding.get("job_id"):
        issues.append("missing_job_id")
    if finding.get("status") != "finding":
        issues.append("not_a_finding")

    kind = finding.get("kind") or finding.get("title")
    if kind not in SUPPORTED_KINDS:
        issues.append("unsupported_finding_kind")

    evidence = finding.get("evidence")
    if not isinstance(evidence, dict):
        issues.append("missing_evidence")
        evidence = {}

    if kind in STAGE_LEVEL_KINDS and evidence.get("stage_id") is None:
        issues.append("missing_stage_id")
    if not evidence.get("app_id"):
        issues.append("missing_app_id")

    if kind == "shuffle_skew_candidate":
        _validate_skew_evidence(evidence, issues)
    elif kind == "shuffle_spill_candidate":
        _validate_positive_evidence(evidence, issues, "spilled_bytes", "missing_spilled_bytes")
    elif kind == "gc_pressure_candidate":
        _validate_positive_evidence(evidence, issues, "gc_ratio", "missing_gc_ratio")
    elif kind == "oom_candidate" and not evidence.get("failure_reasons"):
        issues.append("missing_failure_reasons")
    elif kind == "plan_aqe_replan_candidate":
        _validate_positive_evidence(
            evidence,
            issues,
            "adaptive_execution_updates",
            "missing_adaptive_execution_updates",
        )

    if not finding.get("recommendations"):
        issues.append("missing_recommendations")

    return {
        "rule_set": RULE_SET,
        "accepted": not issues,
        "status": "valid" if not issues else "invalid",
        "issues": issues,
    }


def _validate_skew_evidence(evidence, issues):
    ratio = evidence.get("ratio")
    if ratio is None:
        issues.append("missing_skew_ratio")
    elif ratio < MIN_SKEW_RATIO:
        issues.append("skew_ratio_below_threshold")

    task_count = evidence.get("task_count")
    if task_count is None:
        issues.append("missing_task_count")
    elif task_count < MIN_TASK_COUNT:
        issues.append("insufficient_task_count")


def _validate_positive_evidence(evidence, issues, field, issue):
    value = evidence.get(field)
    if value is None or value <= 0:
        issues.append(issue)
