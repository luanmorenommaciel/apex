"""Deterministic diagnosis for the Commander V0.1 local harness."""

from apex.commander.detectors import detect_findings
from apex.commander.findings import build_finding
from apex.commander.telemetry_store import query_envelopes


def diagnose_findings(store_path, job_id):
    """Return all local deterministic findings for one job."""
    envelopes = query_envelopes(store_path, job_id)
    if not envelopes:
        return []

    return _findings_from_envelope(envelopes[-1], job_id)


def diagnose_job(store_path, job_id):
    """Diagnose one job from the local ClickStack MVP store."""
    envelopes = query_envelopes(store_path, job_id)
    if not envelopes:
        return {
            "status": "not_found",
            "job_id": job_id,
            "title": "telemetry_not_found",
            "confidence": "none",
            "evidence": {},
            "recommendations": [
                "Confirme se o SparkListener MVP publicou telemetria para este job_id.",
            ],
        }

    envelope = envelopes[-1]
    findings = _findings_from_envelope(envelope, job_id)
    if not findings:
        return {
            "status": "no_finding",
            "job_id": job_id,
            "title": "no_commander_v01_finding",
            "confidence": "low",
            "evidence": {"schema_version": envelope.get("schema_version")},
            "recommendations": [
                "Sem candidato de skew no contrato V0.1; ampliar Watchers depois do baseline.",
            ],
        }

    return findings[0]


def _findings_from_envelope(envelope, job_id):
    findings = []
    findings.extend(_skew_findings(envelope, job_id))
    findings.extend(detect_findings(envelope))
    return findings


def _skew_findings(envelope, job_id):
    candidates = envelope.get("skew_candidates") or []
    if not candidates:
        return []

    candidate = max(candidates, key=lambda item: item["ratio"])
    return [
        build_finding(
            "shuffle_skew_candidate",
            job_id,
            "warning",
            "medium",
            {
                "schema_version": envelope.get("schema_version"),
                "app_id": envelope.get("app_id"),
                "stage_id": candidate["stage_id"],
                "ratio": candidate["ratio"],
                "hot_records": candidate["hot_records"],
                "median_cold_records": candidate["median_cold_records"],
                "task_count": candidate["task_count"],
            },
            [
                "Validar habilitacao de spark.sql.adaptive.skewJoin.enabled para este job.",
                "Confirmar chave de join e avaliar salting/repartition antes de aplicar mudanca.",
            ],
        )
    ]
