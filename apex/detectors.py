#!/usr/bin/env python3
"""
Detectores deterministicos do Apex (v4) — portados do spike/apex-v0.1 (ISSUE-A01 / G2).

No spike os detectores leem ClickHouse (Mundo B); aqui as MESMAS regras rodam
sobre o event log parseado pelo apexlib (Mundo A). A logica e identica — so a
fonte muda. Quando o Mundo B consolidar, este modulo e a referencia da regra.

Cada detector retorna lista de findings: dicts com detector, severity
(info|warning|critical), stage/execution, title e evidence.
Guards de falso positivo vem de apex/diagnostics.yaml (G1: baseline nunca dispara).
"""
import os
from collections import defaultdict

import yaml

DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), "diagnostics.yaml")


def load_thresholds(path=None):
    with open(path or DEFAULT_CONFIG) as f:
        return yaml.safe_load(f)


# ------------------------------------------------------------------ agregacao
def stage_task_metrics(events):
    """Agrega TaskEnd por stage: duracao, gc, shuffle bytes, spill, falhas."""
    stages = defaultdict(lambda: {
        "duration_ms": 0, "gc_ms": 0, "max_gc_ms": 0,
        "shuffle_bytes": 0, "memory_spilled": 0, "disk_spilled": 0,
        "n_tasks": 0, "oom_tasks": 0, "executor_lost_tasks": 0,
        "failed_tasks": 0, "sample_reason": "",
    })
    for e in events:
        if e.get("Event") != "SparkListenerTaskEnd":
            continue
        sid = e.get("Stage ID")
        m = e.get("Task Metrics") or {}
        info = e.get("Task Info") or {}
        s = stages[sid]

        reason = e.get("Task End Reason") or {}
        reason_txt = str(reason)
        failed = info.get("Failed", False) or reason.get("Reason", "Success") != "Success"
        if failed:
            s["failed_tasks"] += 1
            if "OutOfMemoryError" in reason_txt:
                s["oom_tasks"] += 1
            if "ExecutorLostFailure" in reason_txt:
                s["executor_lost_tasks"] += 1
            if not s["sample_reason"]:
                s["sample_reason"] = reason_txt[:400]
            continue  # metricas de task falhada nao entram nos agregados de sucesso

        gc = int(m.get("JVM GC Time", 0))
        s["duration_ms"] += int(m.get("Executor Run Time", 0))
        s["gc_ms"] += gc
        s["max_gc_ms"] = max(s["max_gc_ms"], gc)
        sr = m.get("Shuffle Read Metrics") or {}
        sw = m.get("Shuffle Write Metrics") or {}
        s["shuffle_bytes"] += int(sr.get("Remote Bytes Read", 0)) + int(sr.get("Local Bytes Read", 0))
        s["shuffle_bytes"] += int(sw.get("Shuffle Bytes Written", 0))
        s["memory_spilled"] += int(m.get("Memory Bytes Spilled", 0))
        s["disk_spilled"] += int(m.get("Disk Bytes Spilled", 0))
        s["n_tasks"] += 1
    return dict(stages)


def _plan_texts(events):
    """(execution_id, plano) de execucoes iniciais E updates AQE — ver plans.py do spike."""
    out = []
    for e in events:
        ev = e.get("Event", "")
        if ev.endswith("SparkListenerSQLExecutionStart") or ev.endswith("SparkListenerSQLAdaptiveExecutionUpdate"):
            out.append((e.get("executionId", e.get("sqlExecutionId", 0)),
                        e.get("physicalPlanDescription", "") or ""))
    return out


# ------------------------------------------------------------------ detectores
def detect_gc(events, thresholds):
    t = thresholds["gc"]
    findings = []
    for sid, s in sorted(stage_task_metrics(events).items()):
        if s["duration_ms"] < t["min_stage_duration_ms"]:
            continue
        ratio = s["gc_ms"] / max(s["duration_ms"], 1)
        if ratio < t["warning_ratio"]:
            continue
        sev = "critical" if ratio >= t["critical_ratio"] else "warning"
        findings.append({
            "detector": "gc", "severity": sev, "stage": sid,
            "title": f"Stage {sid}: {ratio * 100:.0f}% do tempo de task gasto em GC",
            "evidence": {"gc_ms": s["gc_ms"], "total_ms": s["duration_ms"],
                         "gc_ratio": round(ratio, 3), "max_gc_ms": s["max_gc_ms"],
                         "n_tasks": s["n_tasks"]},
        })
    return findings


def detect_shuffle(events, thresholds):
    t = thresholds["shuffle"]
    findings = []
    for sid, s in sorted(stage_task_metrics(events).items()):
        if s["shuffle_bytes"] < t["min_shuffle_bytes"]:
            continue
        sev = None
        if s["disk_spilled"] > 0 or s["shuffle_bytes"] > t["critical_shuffle_bytes"]:
            sev = "critical"
        elif s["memory_spilled"] > 0 or s["shuffle_bytes"] > t["warning_shuffle_bytes"]:
            sev = "warning"
        if sev is None:
            continue
        note = ("com spill em disco" if s["disk_spilled"] > 0
                else "com spill em memoria" if s["memory_spilled"] > 0 else "sem spill")
        findings.append({
            "detector": "shuffle", "severity": sev, "stage": sid,
            "title": f"Stage {sid}: {s['shuffle_bytes'] / 2**20:.0f} MiB de shuffle {note}",
            "evidence": {"shuffle_bytes": s["shuffle_bytes"],
                         "memory_bytes_spilled": s["memory_spilled"],
                         "disk_bytes_spilled": s["disk_spilled"], "n_tasks": s["n_tasks"]},
        })
    return findings


def detect_oom(events, thresholds=None):
    findings = []
    for sid, s in sorted(stage_task_metrics(events).items()):
        if s["oom_tasks"] == 0 and s["executor_lost_tasks"] == 0:
            continue
        label = "OutOfMemoryError" if s["oom_tasks"] else "executor perdido (possivel OOM)"
        findings.append({
            "detector": "oom", "severity": "critical", "stage": sid,
            "title": f"Stage {sid}: {s['oom_tasks'] + s['executor_lost_tasks']} task(s) mortas por {label}",
            "evidence": {"oom_tasks": s["oom_tasks"],
                         "executor_lost_tasks": s["executor_lost_tasks"],
                         "failed_tasks": s["failed_tasks"],
                         "sample_reason": s["sample_reason"]},
        })
    return findings


PLAN_PATTERNS = [
    ("CartesianProduct", "critical",
     "produto cartesiano (cross join sem chave) — custo cresce com N*M"),
    ("BroadcastNestedLoopJoin", "warning",
     "nested-loop join broadcast — geralmente join sem condicao de igualdade"),
]


def detect_plans(events, thresholds):
    t = thresholds["plans"]
    findings = []
    replans = defaultdict(int)
    for e in events:
        if e.get("Event", "").endswith("SparkListenerSQLAdaptiveExecutionUpdate"):
            replans[e.get("executionId", 0)] += 1
    for exec_id, n in sorted(replans.items()):
        if n >= t["info_replan_count"]:
            findings.append({
                "detector": "plans", "severity": "info", "execution": exec_id,
                "title": f"SQL execution {exec_id}: AQE re-planejou {n} vezes",
                "evidence": {"replan_count": n},
            })
    seen = set()
    for exec_id, plan in _plan_texts(events):
        for pattern, sev, why in PLAN_PATTERNS:
            if pattern in plan and (exec_id, pattern) not in seen:
                seen.add((exec_id, pattern))
                findings.append({
                    "detector": "plans", "severity": sev, "execution": exec_id,
                    "title": f"SQL execution {exec_id}: plano contem {pattern} — {why}",
                    "evidence": {"pattern": pattern},
                })
    return findings


ALL_DETECTORS = {
    "gc": detect_gc,
    "shuffle": detect_shuffle,
    "oom": detect_oom,
    "plans": detect_plans,
}


def run_all(events, thresholds=None):
    t = thresholds or load_thresholds()
    findings = []
    for fn in ALL_DETECTORS.values():
        findings.extend(fn(events, t))
    return findings
