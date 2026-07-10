"""
Apex V1 — T1 Triage deterministico [G4].

Roda ANTES do Crew.ai: regras deterministicas sobre apex.stage_metrics /
apex.task_metrics (mesmos thresholds de apex/diagnostics.yaml usados pelos
watchers do Mundo A — detector le o contrato, nao a fonte).

Se o T1 produz finding com confidence >= 0.6, o LLM NEM E CHAMADO.
LLM vira fallback para casos ambiguos (contrato do Tier 2/3) — G4 do framework.

Uso standalone:
    python v1-skeleton/analysis/t1_triage.py --app-id <app_id>

Import (sem dependencia de crewai):
    from t1_triage import triage, triage_rows
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DIAGNOSTICS = ROOT / "apex" / "diagnostics.yaml"

CH_HOST = os.getenv("APEX_CH_HOST", "localhost")
CH_PORT = int(os.getenv("APEX_CH_PORT", "8123"))
CH_USER = os.getenv("APEX_CH_USER", "apex")
CH_PASSWORD = os.getenv("APEX_CH_PASSWORD", "apex123")

# confianca deterministica por severidade — >= 0.6 dispensa o LLM
CONFIDENCE = {"critical": 0.9, "high": 0.8, "warning": 0.7}

RECOMMENDATIONS = {  # runbooks curtos (padrao kimi) — fix concreto por padrao
    "skew": ("Habilitar spark.sql.adaptive.skewJoin.enabled=true; considerar salting da chave "
             "quente (concat(key, '_', pmod(rand()*N, N))) ou broadcast do lado pequeno."),
    "spill": ("Aumentar spark.executor.memory ou spark.memory.fraction; reduzir volume por task "
              "com repartition(N) antes do shuffle; revisar spark.sql.shuffle.partitions."),
    "gc_pressure": ("Reduzir pressao de objetos: aumentar spark.executor.memory, usar tipos "
                    "primitivos/colunar (evitar collect_list amplo), considerar G1GC "
                    "(spark.executor.defaultJavaOptions=-XX:+UseG1GC)."),
    "oom": ("Aumentar spark.executor.memory / memoryOverhead; evitar agregacoes que materializam "
            "particoes inteiras (collect_list sem groupBy seletivo); habilitar AQE."),
    "parallelism_collapse": ("Aumentar spark.sql.shuffle.partitions / spark.default.parallelism; "
                             "usar repartition() apos leitura de input grande."),
}


def load_thresholds(path=None):
    with open(path or DIAGNOSTICS) as f:
        return yaml.safe_load(f)


def _finding(pattern, severity, stage_id, root_cause, evidence):
    return {
        "pattern": pattern,
        "severity": "critical" if severity == "critical" else "high",
        "confidence": CONFIDENCE.get(severity, 0.7),
        "bottleneck_stage_id": stage_id,
        "root_cause": root_cause[:500],
        "recommendation": RECOMMENDATIONS.get(pattern, "Investigar com o Crew.ai (Tier 2).")[:500],
        "evidence": evidence,
        "pipeline": "t1-deterministic",
        "llm_model": "none",
    }


def triage_rows(stage_rows, tasks_by_stage=None, thresholds=None):
    """Regras T1 sobre linhas de apex.stage_metrics (+ tasks opcionais por stage).

    stage_rows: [{stage_id, num_tasks, failed_tasks, duration_ms, input_bytes,
                  shuffle_read, shuffle_write, memory_spill, disk_spill, gc_time_ms}]
    tasks_by_stage: {stage_id: [duration_ms, ...]} (para skew por distribuicao)
    """
    t = thresholds or load_thresholds()
    tasks_by_stage = tasks_by_stage or {}
    findings = []

    for s in stage_rows:
        sid = int(s["stage_id"])
        shuffle_bytes = int(s.get("shuffle_read", 0)) + int(s.get("shuffle_write", 0))
        duration = int(s.get("duration_ms", 0))

        # oom / falha de task
        if int(s.get("failed_tasks", 0)) > 0:
            findings.append(_finding(
                "oom", "critical", sid,
                f"{s['failed_tasks']} task(s) falharam no stage {sid} — assinatura tipica de "
                f"pressao de memoria (confirmar reason no event log)",
                {"key_metric": "failed_tasks", "key_value": str(s["failed_tasks"]),
                 "expected_value": "0"}))

        # spill (guard de volume minimo de shuffle)
        if shuffle_bytes >= t["shuffle"]["min_shuffle_bytes"]:
            if int(s.get("disk_spill", 0)) > 0 or shuffle_bytes > t["shuffle"]["critical_shuffle_bytes"]:
                findings.append(_finding(
                    "spill", "critical", sid,
                    f"Stage {sid}: {shuffle_bytes / 2**20:.0f} MiB de shuffle com "
                    f"{int(s.get('disk_spill', 0)) / 2**20:.0f} MiB de spill em disco",
                    {"key_metric": "disk_spill", "key_value": str(s.get("disk_spill", 0)),
                     "expected_value": "0"}))
            elif int(s.get("memory_spill", 0)) > 0 or shuffle_bytes > t["shuffle"]["warning_shuffle_bytes"]:
                findings.append(_finding(
                    "spill", "warning", sid,
                    f"Stage {sid}: {shuffle_bytes / 2**20:.0f} MiB de shuffle com spill em memoria",
                    {"key_metric": "memory_spill", "key_value": str(s.get("memory_spill", 0)),
                     "expected_value": "0"}))

        # gc pressure
        if duration >= t["gc"]["min_stage_duration_ms"]:
            ratio = int(s.get("gc_time_ms", 0)) / max(duration, 1)
            if ratio >= t["gc"]["warning_ratio"]:
                sev = "critical" if ratio >= t["gc"]["critical_ratio"] else "warning"
                findings.append(_finding(
                    "gc_pressure", sev, sid,
                    f"Stage {sid}: {ratio * 100:.0f}% do tempo em GC",
                    {"key_metric": "gc_ratio", "key_value": f"{ratio:.2f}",
                     "expected_value": f"< {t['gc']['warning_ratio']}"}))

        # parallelism collapse
        if (int(s.get("num_tasks", 0)) < t["parallelism"]["min_tasks"]
                and int(s.get("input_bytes", 0)) > t["parallelism"]["min_input_bytes"]):
            findings.append(_finding(
                "parallelism_collapse", "high", sid,
                f"Stage {sid}: {s['num_tasks']} task(s) para "
                f"{int(s['input_bytes']) / 2**30:.1f} GiB de input",
                {"key_metric": "num_tasks", "key_value": str(s["num_tasks"]),
                 "expected_value": f">= {t['parallelism']['min_tasks']}"}))

        # skew por distribuicao de duracao das tasks
        durs = sorted(tasks_by_stage.get(sid, []))
        if len(durs) >= t["skew"]["min_tasks"]:
            median = durs[len(durs) // 2]
            ratio = durs[-1] / max(median, 1)
            if ratio >= t["skew"]["ratio_min"]:
                findings.append(_finding(
                    "skew", "critical" if ratio >= 3 * t["skew"]["ratio_min"] else "high", sid,
                    f"Stage {sid}: task mais lenta {durs[-1]}ms vs mediana {median}ms "
                    f"-> ratio {ratio:.1f}x ({len(durs)} tasks)",
                    {"key_metric": "task_duration_ratio", "key_value": f"{ratio:.1f}x",
                     "expected_value": f"< {t['skew']['ratio_min']}x"}))

    findings.sort(key=lambda f: (-f["confidence"], f["pattern"]))
    return findings


def fetch_rows(app_id):
    import clickhouse_connect
    ch = clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT,
                                       username=CH_USER, password=CH_PASSWORD)
    stage_rows = list(ch.query("""
        SELECT stage_id, num_tasks, failed_tasks, duration_ms, input_bytes,
               shuffle_read, shuffle_write, memory_spill, disk_spill, gc_time_ms
        FROM apex.stage_metrics WHERE app_id = {app_id:String}
    """, parameters={"app_id": app_id}).named_results())
    tasks = {}
    for r in ch.query("""
        SELECT stage_id, duration_ms FROM apex.task_metrics
        WHERE app_id = {app_id:String} AND status = 'SUCCESS'
    """, parameters={"app_id": app_id}).named_results():
        tasks.setdefault(int(r["stage_id"]), []).append(int(r["duration_ms"]))
    return stage_rows, tasks


def triage(app_id):
    """T1 completo: ClickHouse -> findings deterministicos. Retorna (findings, elapsed_ms)."""
    t0 = time.perf_counter()
    stage_rows, tasks = fetch_rows(app_id)
    findings = triage_rows(stage_rows, tasks)
    for f in findings:
        f["app_id"] = app_id
    return findings, (time.perf_counter() - t0) * 1000


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Apex T1 — triage deterministico")
    p.add_argument("--app-id", required=True)
    args = p.parse_args()
    findings, ms = triage(args.app_id)
    print(json.dumps(findings, indent=2, ensure_ascii=False))
    print(f"\nT1 em {ms:.0f}ms — {len(findings)} finding(s)", file=sys.stderr)
