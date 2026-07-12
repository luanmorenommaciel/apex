"""Local deterministic Commander detectors."""

from apex.commander.diagnostics_config import load_diagnostics_config
from apex.commander.findings import build_finding

DIAGNOSTICS = load_diagnostics_config()
SHUFFLE = DIAGNOSTICS["shuffle"]
GC = DIAGNOSTICS["gc"]
PLANS = DIAGNOSTICS["plans"]


def detect_findings(envelope):
    findings = []
    findings.extend(_detect_shuffle_spill(envelope))
    findings.extend(_detect_gc_pressure(envelope))
    findings.extend(_detect_oom(envelope))
    findings.extend(_detect_plan_patterns(envelope))
    findings.extend(_detect_plan_aqe(envelope))
    return findings


def _detect_shuffle_spill(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        disk_spilled = int(stage.get("disk_bytes_spilled") or 0)
        memory_spilled = int(stage.get("memory_bytes_spilled") or 0)
        spilled = disk_spilled + memory_spilled
        shuffle_bytes = int(stage.get("shuffle_read_bytes") or 0)
        has_min_shuffle = shuffle_bytes >= int(SHUFFLE["min_shuffle_bytes"])
        has_warning_shuffle = shuffle_bytes >= int(SHUFFLE["warning_shuffle_bytes"])
        has_critical_shuffle = shuffle_bytes >= int(SHUFFLE["critical_shuffle_bytes"])
        has_disk_spill = disk_spilled > 0
        has_memory_spill = memory_spilled > 0

        if has_min_shuffle and (has_warning_shuffle or has_disk_spill or has_memory_spill):
            severity = "critical" if has_critical_shuffle or has_disk_spill else "warning"
            findings.append(
                build_finding(
                    "shuffle_spill_candidate",
                    envelope["job_id"],
                    severity,
                    "high" if severity == "critical" else "medium",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
                        "shuffle_read_bytes": shuffle_bytes,
                        "disk_bytes_spilled": disk_spilled,
                        "memory_bytes_spilled": memory_spilled,
                        "spilled_bytes": spilled,
                    },
                    [
                        "Validar particionamento e reduzir spill de shuffle antes de escalar recursos."
                    ],
                )
            )
    return findings


def _detect_gc_pressure(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        run_time = int(stage.get("executor_run_time_ms") or 0)
        gc_time = int(stage.get("jvm_gc_time_ms") or 0)
        ratio = gc_time / run_time if run_time else 0
        if run_time < int(GC["min_stage_duration_ms"]):
            continue
        if ratio >= float(GC["warning_ratio"]):
            severity = "critical" if ratio >= float(GC["critical_ratio"]) else "warning"
            findings.append(
                build_finding(
                    "gc_pressure_candidate",
                    envelope["job_id"],
                    severity,
                    "high" if severity == "critical" else "medium",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
                        "gc_ratio": ratio,
                        "jvm_gc_time_ms": gc_time,
                        "executor_run_time_ms": run_time,
                    },
                    [
                        "Avaliar tamanho de particoes, cache e memoria antes de aumentar executores."
                    ],
                )
            )
    return findings


def _detect_oom(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        reasons = stage.get("failure_reasons") or []
        oom_reasons = [
            reason
            for reason in reasons
            if _is_oom_reason(reason)
        ]
        if oom_reasons:
            findings.append(
                build_finding(
                    "oom_candidate",
                    envelope["job_id"],
                    "critical",
                    "high",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
                        "failure_reasons": oom_reasons,
                    },
                    [
                        "Revisar volume por particao, joins e configuracao de memoria antes de reexecutar."
                    ],
                )
            )
    return findings


def _is_oom_reason(reason):
    lowered = reason.lower()
    return (
        "outofmemoryerror" in lowered
        or "executorlostfailure" in lowered
        or "oom" in lowered
        or "memory" in lowered
    )


def _detect_plan_patterns(envelope):
    findings = []
    for plan_entry in envelope.get("physical_plans", []):
        plan = plan_entry.get("plan") or ""
        if "CartesianProduct" in plan:
            findings.append(
                _plan_pattern_finding(
                    envelope,
                    plan_entry,
                    "cartesian_product_candidate",
                    "CartesianProduct",
                    "critical",
                )
            )
        elif "BroadcastNestedLoopJoin" in plan:
            findings.append(
                _plan_pattern_finding(
                    envelope,
                    plan_entry,
                    "broadcast_nested_loop_join_candidate",
                    "BroadcastNestedLoopJoin",
                    "warning",
                )
            )
    return findings


def _plan_pattern_finding(envelope, plan_entry, kind, operator, severity):
    return build_finding(
        kind,
        envelope["job_id"],
        severity,
        "high" if severity == "critical" else "medium",
        {
            "app_id": envelope.get("app_id"),
            "execution_id": plan_entry.get("execution_id"),
            "operator": operator,
            "plan_excerpt": (plan_entry.get("plan") or "")[:500],
        },
        [
            "Inspecionar plano fisico e validar join keys antes de liberar reexecucao automatica."
        ],
    )


def _detect_plan_aqe(envelope):
    event_counts = envelope.get("event_counts") or {}
    replan_count = int(event_counts.get("SparkListenerSQLAdaptiveExecutionUpdate") or 0)
    if replan_count < int(PLANS["info_replan_count"]):
        return []
    return [
        build_finding(
            "plan_aqe_replan_candidate",
            envelope["job_id"],
            "info",
            "medium",
            {
                "app_id": envelope.get("app_id"),
                "adaptive_execution_updates": replan_count,
            },
            [
                "Inspecionar plano AQE para entender mudancas de join, shuffle e coalescing."
            ],
        )
    ]
