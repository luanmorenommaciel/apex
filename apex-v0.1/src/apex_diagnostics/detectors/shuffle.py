from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import ShuffleThresholds
from apex_diagnostics.models import Finding, Severity

# FINAL + per-attempt grouping: see the note in skew.py. Without FINAL a
# re-ingested task inflates every sum() below (shuffle/spill), producing phantom
# critical spill findings.
SHUFFLE_SQL = """
SELECT stage_id,
       stage_attempt_id,
       sum(shuffle_read_bytes) + sum(shuffle_write_bytes) AS shuffle_bytes,
       sum(memory_bytes_spilled)                          AS memory_spilled,
       sum(disk_bytes_spilled)                            AS disk_spilled,
       max(jvm_gc_time_ms)                                AS max_gc_ms,
       count()                                            AS n_tasks
FROM spark_tasks FINAL
WHERE app_id = {app_id:String} AND successful = 1
GROUP BY stage_id, stage_attempt_id
ORDER BY stage_id, stage_attempt_id
"""


def detect_shuffle(client: CHClient, app_id: str, thresholds: ShuffleThresholds) -> list[Finding]:
    findings: list[Finding] = []
    for row in client.query(SHUFFLE_SQL, {"app_id": app_id}):
        shuffle_bytes = int(row["shuffle_bytes"])
        memory_spilled = int(row["memory_spilled"])
        disk_spilled = int(row["disk_spilled"])
        if shuffle_bytes < thresholds.min_shuffle_bytes:
            continue

        severity: Severity | None = None
        if disk_spilled > 0 or shuffle_bytes > thresholds.critical_shuffle_bytes:
            severity = Severity.CRITICAL
        elif memory_spilled > 0 or shuffle_bytes > thresholds.warning_shuffle_bytes:
            severity = Severity.WARNING
        if severity is None:
            continue

        spill_note = "with disk spill" if disk_spilled > 0 else ("with memory spill" if memory_spilled > 0 else "no spill")
        findings.append(
            Finding(
                detector="shuffle",
                severity=severity,
                app_id=app_id,
                stage_id=int(row["stage_id"]),
                title=f"Stage {row['stage_id']}: {shuffle_bytes / (1024 * 1024):.0f} MiB shuffled {spill_note}",
                evidence={
                    "stage_attempt_id": int(row["stage_attempt_id"]),
                    "shuffle_bytes": shuffle_bytes,
                    "memory_bytes_spilled": memory_spilled,
                    "disk_bytes_spilled": disk_spilled,
                    "max_gc_ms": int(row["max_gc_ms"]),
                    "n_tasks": int(row["n_tasks"]),
                },
            )
        )
    return findings
