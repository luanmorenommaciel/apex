"""Evidence validation for Commander findings before delivery to MCP or agents."""

RULE_SET = "apex.commander.evidence_validator.v1"
MIN_SKEW_RATIO = 10.0
MIN_TASK_COUNT = 2


def validate_finding(finding):
    """Return a machine-readable validation result for a Commander finding."""
    issues = []

    if not finding.get("job_id"):
        issues.append("missing_job_id")
    if finding.get("status") != "finding":
        issues.append("not_a_finding")
    if finding.get("title") != "shuffle_skew_candidate":
        issues.append("unsupported_finding_title")

    evidence = finding.get("evidence")
    if not isinstance(evidence, dict):
        issues.append("missing_evidence")
        evidence = {}

    if evidence.get("stage_id") is None:
        issues.append("missing_stage_id")
    if not evidence.get("app_id"):
        issues.append("missing_app_id")

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

    if not finding.get("recommendations"):
        issues.append("missing_recommendations")

    return {
        "rule_set": RULE_SET,
        "accepted": not issues,
        "status": "valid" if not issues else "invalid",
        "issues": issues,
    }
