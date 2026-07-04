"""Deterministic diagnosis for the Commander V0.1 local harness."""

from apex.commander.clickstack_mvp import query_by_job_id


def diagnose_job(store_path, job_id):
    """Diagnose one job from the local ClickStack MVP store."""
    envelopes = query_by_job_id(store_path, job_id)
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
    candidates = envelope.get("skew_candidates") or []
    if not candidates:
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

    candidate = max(candidates, key=lambda item: item["ratio"])
    return {
        "status": "finding",
        "job_id": job_id,
        "title": "shuffle_skew_candidate",
        "confidence": "medium",
        "evidence": {
            "schema_version": envelope.get("schema_version"),
            "app_id": envelope.get("app_id"),
            "stage_id": candidate["stage_id"],
            "ratio": candidate["ratio"],
            "hot_records": candidate["hot_records"],
            "median_cold_records": candidate["median_cold_records"],
            "task_count": candidate["task_count"],
        },
        "recommendations": [
            "Validar habilitacao de spark.sql.adaptive.skewJoin.enabled para este job.",
            "Confirmar chave de join e avaliar salting/repartition antes de aplicar mudanca.",
        ],
    }
