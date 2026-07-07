from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.models import Finding, Severity

# FINAL + per-attempt grouping: see the note in skew.py. Without FINAL a
# re-ingested failed task would be counted twice, inflating the oom/lost counts.
OOM_SQL = """
SELECT stage_id,
       stage_attempt_id,
       countIf(reason LIKE '%OutOfMemoryError%')      AS oom_tasks,
       countIf(reason LIKE '%ExecutorLostFailure%')   AS executor_lost_tasks,
       count()                                        AS failed_tasks,
       any(left(reason, 400))                         AS sample_reason
FROM spark_tasks FINAL
WHERE app_id = {app_id:String} AND successful = 0
GROUP BY stage_id, stage_attempt_id
ORDER BY stage_id, stage_attempt_id
"""


def detect_oom(client: CHClient, app_id: str) -> list[Finding]:
    """Classifica falhas de task por assinatura de memória.

    OOM explícito ou executor perdido durante o stage são críticos: ambos
    indicam morte do processo por pressão de memória (o executor perdido é a
    assinatura típica quando o kernel/JVM mata antes de o erro ser reportado).
    """
    findings: list[Finding] = []
    for row in client.query(OOM_SQL, {"app_id": app_id}):
        oom = int(row["oom_tasks"])
        lost = int(row["executor_lost_tasks"])
        if oom == 0 and lost == 0:
            continue
        label = "OutOfMemoryError" if oom else "executor perdido (possível OOM)"
        findings.append(
            Finding(
                detector="oom",
                severity=Severity.CRITICAL,
                app_id=app_id,
                stage_id=int(row["stage_id"]),
                title=f"Stage {row['stage_id']}: {oom + lost} task(s) mortas por {label}",
                evidence={
                    "stage_attempt_id": int(row["stage_attempt_id"]),
                    "oom_tasks": oom,
                    "executor_lost_tasks": lost,
                    "failed_tasks": int(row["failed_tasks"]),
                    "sample_reason": str(row["sample_reason"]),
                },
            )
        )
    return findings
