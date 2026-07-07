from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import GCThresholds
from apex_diagnostics.models import Finding, Severity

# FINAL + per-attempt grouping: see the note in skew.py. Duplicated tasks would
# inflate both gc_ms and total_ms; the ratio is somewhat self-correcting but the
# absolute min_stage_duration_ms guard is not, so dedup still matters here.
GC_SQL = """
SELECT stage_id,
       stage_attempt_id,
       sum(jvm_gc_time_ms)       AS gc_ms,
       sum(duration_ms)          AS total_ms,
       max(jvm_gc_time_ms)       AS max_gc_ms,
       count()                   AS n_tasks
FROM spark_tasks FINAL
WHERE app_id = {app_id:String} AND successful = 1
GROUP BY stage_id, stage_attempt_id
ORDER BY stage_id, stage_attempt_id
"""


def detect_gc(client: CHClient, app_id: str, thresholds: GCThresholds) -> list[Finding]:
    findings: list[Finding] = []
    for row in client.query(GC_SQL, {"app_id": app_id}):
        total_ms = int(row["total_ms"])
        gc_ms = int(row["gc_ms"])
        if total_ms < thresholds.min_stage_duration_ms:
            continue
        ratio = gc_ms / max(total_ms, 1)
        if ratio < thresholds.warning_ratio:
            continue
        severity = Severity.CRITICAL if ratio >= thresholds.critical_ratio else Severity.WARNING
        findings.append(
            Finding(
                detector="gc",
                severity=severity,
                app_id=app_id,
                stage_id=int(row["stage_id"]),
                title=f"Stage {row['stage_id']}: {ratio * 100:.0f}% do tempo de task gasto em GC",
                evidence={
                    "stage_attempt_id": int(row["stage_attempt_id"]),
                    "gc_ms": gc_ms,
                    "total_ms": total_ms,
                    "gc_ratio": round(ratio, 3),
                    "max_gc_ms": int(row["max_gc_ms"]),
                    "n_tasks": int(row["n_tasks"]),
                },
            )
        )
    return findings
