"""Local tool contract for Commander before a real MCP server is introduced."""

from apex.commander.diagnostic_mvp import diagnose_findings, diagnose_job
from apex.commander.evidence_validator import validate_finding
from apex.commander.telemetry_store import query_envelopes


def debug_job(store_path, job_id):
    """Return findings plus validation status for one job_id."""
    findings = diagnose_findings(store_path, job_id)
    if findings:
        validations = [validate_finding(finding) for finding in findings]
        finding = findings[0]
        validation = validations[0]
    else:
        finding = diagnose_job(store_path, job_id)
        validation = {
            "rule_set": "apex.commander.evidence_validator.v1",
            "accepted": False,
            "status": "invalid",
            "issues": [finding.get("status", "no_finding")],
        }
        validations = []
    return {
        "job_id": job_id,
        "finding": finding,
        "validation": validation,
        "findings": findings,
        "validations": validations,
    }


def explain_evidence(store_path, job_id):
    """Return the latest stored telemetry envelope for one job_id."""
    matches = query_envelopes(store_path, job_id)
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


def query_persisted_findings(finding_store, job_id):
    """Return findings that were already validated and persisted."""
    if finding_store is None:
        return {
            "job_id": job_id,
            "status": "not_configured",
            "count": 0,
            "records": [],
        }
    if not hasattr(finding_store, "query_by_job_id"):
        raise ValueError("finding_store_not_queryable")

    records = finding_store.query_by_job_id(job_id)
    return {
        "job_id": job_id,
        "status": "found" if records else "not_found",
        "count": len(records),
        "records": records,
    }
