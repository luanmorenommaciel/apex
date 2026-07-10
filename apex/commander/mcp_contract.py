"""Local tool contract for Commander before a real MCP server is introduced."""

from apex.commander.clickstack_mvp import query_by_job_id
from apex.commander.diagnostic_mvp import diagnose_job
from apex.commander.evidence_validator import validate_finding


def debug_job(store_path, job_id):
    """Return a finding plus validation status for one job_id."""
    finding = diagnose_job(store_path, job_id)
    if finding.get("status") == "finding":
        validation = validate_finding(finding)
    else:
        validation = {
            "rule_set": "apex.commander.evidence_validator.v1",
            "accepted": False,
            "status": "invalid",
            "issues": [finding.get("status", "no_finding")],
        }
    return {
        "job_id": job_id,
        "finding": finding,
        "validation": validation,
    }


def explain_evidence(store_path, job_id):
    """Return the latest stored telemetry envelope for one job_id."""
    matches = query_by_job_id(store_path, job_id)
    if not matches:
        return {
            "job_id": job_id,
            "status": "not_found",
            "event_counts": {},
            "stages": [],
            "skew_candidates": [],
        }
    latest = matches[-1]
    return {
        "job_id": job_id,
        "status": "found",
        "app_id": latest.get("app_id"),
        "event_counts": latest.get("event_counts", {}),
        "stages": latest.get("stages", []),
        "skew_candidates": latest.get("skew_candidates", []),
    }
