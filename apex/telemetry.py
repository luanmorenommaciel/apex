#!/usr/bin/env python3
"""
Envelope de telemetria (composicao V1) — portado do codex
(apex-official: apex/commander/telemetry.py, schema apex.commander.telemetry.v1).

E a identidade unica do contrato v1 (docs/specs/telemetry-schema-contract-v1.md):
todo dado carrega job_id resolvido pela MESMA regra, seja qual for a fonte.
E a chave da experiencia do Luan: "debuga esse job ID".
"""
from collections import Counter

SCHEMA_VERSION = "apex.telemetry.v1"


def infer_job_id(events):
    """job_id estavel: app_id -> spark-job-<Job ID> -> local-job (contrato codex)."""
    app_id = infer_app_id(events)
    if app_id:
        return app_id
    for e in events:
        jid = e.get("Job ID")
        if jid is not None:
            return f"spark-job-{jid}"
    return "local-job"


def infer_app_id(events):
    for e in events:
        app_id = e.get("App ID")
        if app_id:
            return app_id
    return None


def build_envelope(events, job_id=None):
    """Normaliza eventos Spark no envelope v1 (identidade + resumo por stage)."""
    events = list(events)
    from apex.detectors import stage_task_metrics  # agregacao canonica (G2)
    stages = stage_task_metrics(events)
    return {
        "schema_version": SCHEMA_VERSION,
        "job_id": job_id or infer_job_id(events),
        "app_id": infer_app_id(events),
        "event_counts": dict(Counter(e.get("Event", "unknown") for e in events)),
        "stages": [
            {"stage_id": sid, "n_tasks": s["n_tasks"], "failed_tasks": s["failed_tasks"],
             "duration_ms": s["duration_ms"], "shuffle_bytes": s["shuffle_bytes"],
             "gc_ms": s["gc_ms"], "memory_spilled": s["memory_spilled"],
             "disk_spilled": s["disk_spilled"]}
            for sid, s in sorted(stages.items())
        ],
    }
