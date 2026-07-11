#!/usr/bin/env python3
"""
EvidenceValidator (composicao V1) — portado do kimi-Py (ISSUE-A03).

Valida o bundle de evidencia ANTES do diagnostico: se a evidencia e ruim,
nenhum detector (nem LLM) deve opinar. Original acoplado ao ClickHouse do
fork Gabriel; aqui e PURO sobre linhas — mesma regra para event log (Mundo A)
e ClickHouse (Mundo B), conforme o contrato de telemetria v1.

Regras (7):
  R1 provenance    — bundle nao-vazio (hash de scenario e verificado a montante
                     pelo apexlib.validate_provenance no Mundo A)
  R2 schema        — campos minimos presentes nas tasks
  R3 tasks         — tasks de execucao presentes (duracao > 0 em alguma)
  R4 correlation   — ha variancia (records OU duracao) para correlacionar
  R5 distribution  — >= min_tasks e mediana > 0 (anti-colapso)
  R6 structural    — contagem de tasks consistente com o stage
  R7 single_app    — bundle isolado por aplicacao

Status: valid | indeterminate | invalid. INVALID bloqueia diagnostico.
"""
from statistics import median, pvariance

VALID, INDET, INVALID = "valid", "indeterminate", "invalid"
REQUIRED_TASK_FIELDS = ("duration_ms", "shuffle_records")
MIN_TASKS = 2


def _rule(rule, status, message):
    return {"rule": rule, "status": status, "message": message}


def validate_rows(stage_rows, tasks_by_stage, app_ids=None, min_tasks=MIN_TASKS):
    """Valida stage_rows + tasks_by_stage (formatos do t1_triage). Retorna report."""
    results = []
    all_tasks = [t for ts in (tasks_by_stage or {}).values() for t in ts]

    # R1 provenance — bundle existe
    if not stage_rows and not all_tasks:
        results.append(_rule("R1_provenance", INVALID, "bundle vazio — job nao encontrado na fonte"))
    else:
        results.append(_rule("R1_provenance", VALID,
                             f"{len(stage_rows)} stage(s), {len(all_tasks)} task(s)"))

    # R2 schema minimo
    if all_tasks:
        missing = [f for f in REQUIRED_TASK_FIELDS if not any(f in t for t in all_tasks)]
        results.append(_rule("R2_schema", INVALID if missing else VALID,
                             f"campos ausentes: {missing}" if missing else "campos minimos presentes"))
    else:
        results.append(_rule("R2_schema", INDET, "sem tasks para validar schema"))

    # R3 tasks de execucao
    durs = [int(t.get("duration_ms", 0)) for t in all_tasks]
    results.append(_rule("R3_tasks", VALID if any(d > 0 for d in durs) else INDET,
                         "tasks com duracao presentes" if any(d > 0 for d in durs)
                         else "nenhuma task com duracao > 0"))

    # R4 correlation — variancia em alguma serie
    recs = [int(t.get("shuffle_records", 0)) for t in all_tasks]
    var_ok = (len(durs) > 1 and pvariance(durs) > 0) or (len(recs) > 1 and pvariance(recs) > 0)
    results.append(_rule("R4_correlation", VALID if var_ok else INDET,
                         "variancia suficiente para correlacao" if var_ok
                         else "variancia zero — correlacao nao confiavel"))

    # R5 distribution — anti-colapso (a regra que pegou o bug do 15392x)
    if not all_tasks:
        results.append(_rule("R5_distribution", INDET, "sem tasks"))
    elif len(all_tasks) < min_tasks:
        results.append(_rule("R5_distribution", INVALID,
                             f"colapso: {len(all_tasks)} task(s) < {min_tasks}"))
    elif median(durs) == 0 and median(recs) == 0:
        results.append(_rule("R5_distribution", INVALID, "mediana zero — evidencia insuficiente"))
    else:
        results.append(_rule("R5_distribution", VALID,
                             f"{len(all_tasks)} tasks, mediana dur={median(durs)}ms recs={median(recs)}"))

    # R6 structural — num_tasks declarado vs observado
    inconsistent = []
    for s in stage_rows or []:
        sid = int(s.get("stage_id", -1))
        declared = int(s.get("num_tasks", 0))
        observed = len((tasks_by_stage or {}).get(sid, []))
        if declared and observed and observed > declared:
            inconsistent.append(sid)
    results.append(_rule("R6_structural", INDET if inconsistent else VALID,
                         f"stages com mais tasks que o declarado (dedup?): {inconsistent}"
                         if inconsistent else "contagem de tasks consistente"))

    # R7 single application
    apps = set(app_ids or [])
    if len(apps) > 1:
        results.append(_rule("R7_single_app", INVALID, f"bundle mistura {len(apps)} app_ids"))
    else:
        results.append(_rule("R7_single_app", VALID, "bundle isolado por aplicacao"))

    if any(r["status"] == INVALID for r in results):
        final = INVALID
    elif any(r["status"] == INDET for r in results):
        final = INDET
    else:
        final = VALID
    return {
        "status": final,
        "rules": results,
        "passed": sum(1 for r in results if r["status"] == VALID),
        "failed": sum(1 for r in results if r["status"] == INVALID),
        "indeterminate": sum(1 for r in results if r["status"] == INDET),
    }
