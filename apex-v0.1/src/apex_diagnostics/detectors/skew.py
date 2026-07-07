from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import SkewThresholds
from apex_diagnostics.models import Finding, Severity

# FINAL dedups not-yet-merged ReplacingMergeTree rows so re-ingested tasks are
# not double-counted; grouping by (stage_id, stage_attempt_id) keeps a retried
# stage's attempts separate instead of mixing a failed attempt's tasks into the
# median/max of the successful one.
SKEW_SQL = """
SELECT stage_id,
       stage_attempt_id,
       max(duration_ms)                AS max_ms,
       quantileExact(0.5)(duration_ms) AS p50_ms,
       count()                         AS n_tasks
FROM spark_tasks FINAL
WHERE app_id = {app_id:String} AND successful = 1
GROUP BY stage_id, stage_attempt_id
ORDER BY stage_id, stage_attempt_id
"""


def detect_skew(client: CHClient, app_id: str, thresholds: SkewThresholds) -> list[Finding]:
    findings: list[Finding] = []
    for row in client.query(SKEW_SQL, {"app_id": app_id}):
        if row["n_tasks"] < thresholds.min_tasks or row["max_ms"] < thresholds.min_duration_ms:
            continue
        ratio = row["max_ms"] / max(row["p50_ms"], 1)
        if ratio < thresholds.warning_ratio:
            continue
        severity = Severity.CRITICAL if ratio >= thresholds.critical_ratio else Severity.WARNING
        findings.append(
            Finding(
                detector="skew",
                severity=severity,
                app_id=app_id,
                stage_id=int(row["stage_id"]),
                title=f"Stage {row['stage_id']}: slowest task {ratio:.1f}x the median task duration",
                evidence={
                    "stage_attempt_id": int(row["stage_attempt_id"]),
                    "max_ms": int(row["max_ms"]),
                    "p50_ms": int(row["p50_ms"]),
                    "ratio": round(ratio, 1),
                    "n_tasks": int(row["n_tasks"]),
                },
            )
        )
    return findings
