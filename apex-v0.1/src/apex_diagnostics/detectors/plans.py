from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import PlanThresholds, load_plan_patterns
from apex_diagnostics.models import Finding, Severity

PLANS_SQL = """
SELECT execution_id,
       count(DISTINCT event_uid) AS replan_count
FROM spark_sql_adaptive_plans
WHERE app_id = {app_id:String}
GROUP BY execution_id
ORDER BY execution_id
"""

# Pattern scan runs over BOTH the initial physical plan (spark_sql_executions)
# and every AQE-adaptive plan version (spark_sql_adaptive_plans). With AQE the
# executed plan can differ from the initial one, so a dangerous join pattern may
# appear only in the adaptive plan (false negative if we read the initial plan
# alone) or be removed by AQE. Scanning both and de-duplicating per
# (execution_id, pattern) flags the pattern whenever it is present in any plan
# version the engine actually considered.
PLAN_TEXT_SQL = """
SELECT execution_id, physical_plan
FROM spark_sql_executions
WHERE app_id = {app_id:String}
ORDER BY execution_id
"""

ADAPTIVE_PLAN_TEXT_SQL = """
SELECT execution_id, physical_plan
FROM spark_sql_adaptive_plans
WHERE app_id = {app_id:String}
ORDER BY execution_id
"""

# Loaded once from src/config/anti_patterns.yaml (Seam 1b). Previously a
# hardcoded list; externalizing it means a new plan-text pattern is a YAML edit,
# not a code change, and the catalog stays in sync with the KB spec
# (.claude/kb/spark/specs/anti-patterns.yaml).
PLAN_PATTERNS = load_plan_patterns()


def detect_plans(client: CHClient, app_id: str, thresholds: PlanThresholds) -> list[Finding]:
    findings: list[Finding] = []

    for row in client.query(PLANS_SQL, {"app_id": app_id}):
        replans = int(row["replan_count"])
        if replans < thresholds.info_replan_count:
            continue
        findings.append(
            Finding(
                detector="plans",
                severity=Severity.INFO,
                app_id=app_id,
                execution_id=int(row["execution_id"]),
                title=f"SQL execution {row['execution_id']}: AQE re-planned {replans} times",
                evidence={"replan_count": replans},
            )
        )

    # Scan initial + adaptive plans; dedup so a pattern present in several plan
    # versions of the same execution yields a single finding.
    seen: set[tuple[int, str]] = set()
    for sql in (PLAN_TEXT_SQL, ADAPTIVE_PLAN_TEXT_SQL):
        for row in client.query(sql, {"app_id": app_id}):
            execution_id = int(row["execution_id"])
            plan_text = str(row["physical_plan"])
            for pattern in PLAN_PATTERNS:
                if pattern.signal in plan_text and (execution_id, pattern.name) not in seen:
                    seen.add((execution_id, pattern.name))
                    findings.append(
                        Finding(
                            detector="plans",
                            severity=pattern.severity,
                            app_id=app_id,
                            execution_id=execution_id,
                            title=f"SQL execution {execution_id}: plano contém {pattern.name} — {pattern.explanation}",
                            evidence={"pattern": pattern.name, "anti_pattern_id": pattern.id},
                        )
                    )
    return findings
