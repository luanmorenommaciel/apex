"""Finding helpers for Commander detector output."""


def build_finding(kind, job_id, severity, confidence, evidence, recommendations):
    return {
        "status": "finding",
        "kind": kind,
        "title": kind,
        "severity": severity,
        "confidence": confidence,
        "job_id": job_id,
        "evidence": evidence,
        "recommendations": recommendations,
    }
