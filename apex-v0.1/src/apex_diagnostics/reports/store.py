import os
import uuid
from typing import Any

from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.models import DiagnosticReport

REPORTS_TABLE = "spark_diagnostic_reports"

LATEST_REPORT_SQL = """
SELECT report_json
FROM spark_diagnostic_reports
WHERE app_id = {app_id:String}
ORDER BY generated_at DESC
LIMIT 1
"""

LIST_RUNS_SQL = """
SELECT t.app_id AS app_id,
       max(t.finish_time_ms) AS last_task_finish_ms,
       count(DISTINCT r.report_uid) AS report_count
FROM spark_tasks AS t
LEFT JOIN spark_diagnostic_reports AS r ON r.app_id = t.app_id
GROUP BY t.app_id
ORDER BY last_task_finish_ms DESC
LIMIT {limit:UInt32}
"""

UNANALYZED_RUNS_SQL = """
SELECT app_id, max(finish_time_ms) AS last_task_finish_ms
FROM spark_tasks
WHERE app_id NOT IN (SELECT DISTINCT app_id FROM spark_diagnostic_reports)
GROUP BY app_id
ORDER BY last_task_finish_ms DESC
LIMIT {limit:UInt32}
"""


def save_report(client: CHClient, report: DiagnosticReport) -> str:
    report_uid = uuid.uuid4().hex
    client.insert(
        REPORTS_TABLE,
        [
            {
                "app_id": report.app_id,
                "report_uid": report_uid,
                "status": report.status,
                "max_severity": report.max_severity(),
                "findings_count": len(report.findings),
                "report_json": report.model_dump_json(),
                "llm_model": os.environ.get("CREW_LLM_MODEL", "") if report.status == "full" else "",
            }
        ],
    )
    return report_uid


def get_report(client: CHClient, app_id: str) -> DiagnosticReport | None:
    rows = client.query(LATEST_REPORT_SQL, {"app_id": app_id})
    if not rows:
        return None
    return DiagnosticReport.model_validate_json(rows[0]["report_json"])


def list_runs(client: CHClient, limit: int = 20) -> list[dict[str, Any]]:
    return client.query(LIST_RUNS_SQL, {"limit": limit})


def unanalyzed_runs(client: CHClient, limit: int = 25) -> list[str]:
    return [row["app_id"] for row in client.query(UNANALYZED_RUNS_SQL, {"limit": limit})]
