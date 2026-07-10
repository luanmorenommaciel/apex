"""Local deterministic Commander detectors."""

from apex.commander.findings import build_finding

SHUFFLE_SPILL_BYTES_MIN = 1024 * 1024
GC_RATIO_MIN = 0.20
AQE_REPLAN_COUNT_MIN = 3


def detect_findings(envelope):
    findings = []
    findings.extend(_detect_shuffle_spill(envelope))
    findings.extend(_detect_gc_pressure(envelope))
    findings.extend(_detect_oom(envelope))
    findings.extend(_detect_plan_aqe(envelope))
    return findings


def _detect_shuffle_spill(envelope):
    findings = []
    for stage in envelope.get("stages", []):
        spilled = int(stage.get("disk_bytes_spilled") or 0) + int(
            stage.get("memory_bytes_spilled") or 0
        )
        if spilled >= SHUFFLE_SPILL_BYTES_MIN:
            findings.append(
                build_finding(
                    "shuffle_spill_candidate",
                    envelope["job_id"],
                    "warning",
                    "medium",
                    {
                        "app_id": envelope.get("app_id"),
                        "stage_id": stage.get("stage_id"),
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
        if ratio >= GC_RATIO_MIN:
            findings.append(
                build_finding(
                    "gc_pressure_candidate",
                    envelope["job_id"],
                    "warning",
                    "medium",
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
            if "memory" in reason.lower() or "oom" in reason.lower()
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


def _detect_plan_aqe(envelope):
    event_counts = envelope.get("event_counts") or {}
    replan_count = int(event_counts.get("SparkListenerSQLAdaptiveExecutionUpdate") or 0)
    if replan_count < AQE_REPLAN_COUNT_MIN:
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
