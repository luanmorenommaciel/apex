"""Executable negative baselines for Commander detector false-positive control."""

from apex.commander.diagnostic_mvp import diagnose_findings


def evaluate_negative_baseline(store_path, job_id):
    findings = diagnose_findings(store_path, job_id)
    return {
        "job_id": job_id,
        "status": "failed" if findings else "passed",
        "unexpected_findings": findings,
        "unexpected_finding_count": len(findings),
    }
