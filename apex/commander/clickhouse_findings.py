"""ClickHouse-backed finding persistence for Commander."""

import json
import re

from apex.commander.evidence_validator import validate_finding

FINDING_COLUMNS = (
    "job_id",
    "kind",
    "status",
    "severity",
    "confidence",
    "accepted",
    "validation_status",
    "finding_json",
    "validation_json",
)


class ClickHouseFindingStore:
    def __init__(self, client, table="commander_findings"):
        self.client = client
        self.table = _validate_identifier(table)

    def ensure_schema(self):
        self.client.command(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table}
            (
                job_id String,
                kind String,
                status String,
                severity String,
                confidence String,
                accepted UInt8,
                validation_status String,
                finding_json String,
                validation_json String,
                inserted_at DateTime DEFAULT now()
            )
            ENGINE = MergeTree
            ORDER BY (job_id, kind, inserted_at)
            """
        )

    def append_record(self, finding, validation):
        self.client.insert(
            self.table,
            [_row_from_record(finding, validation)],
            column_names=FINDING_COLUMNS,
        )

    def query_by_job_id(self, job_id):
        result = self.client.query(
            f"""
            SELECT finding_json, validation_json
            FROM {self.table}
            WHERE job_id = {{job_id:String}}
            ORDER BY inserted_at ASC
            """,
            parameters={"job_id": job_id},
        )
        return [
            {"finding": json.loads(row[0]), "validation": json.loads(row[1])}
            for row in result.result_rows
        ]


def persist_validated_findings(store, findings):
    records = []
    for finding in findings:
        validation = validate_finding(finding)
        store.append_record(finding, validation)
        records.append({"finding": finding, "validation": validation})
    return records


def _row_from_record(finding, validation):
    return (
        finding["job_id"],
        finding.get("kind") or finding.get("title", ""),
        finding.get("status", ""),
        finding.get("severity", ""),
        finding.get("confidence", ""),
        1 if validation.get("accepted") else 0,
        validation.get("status", ""),
        json.dumps(finding, sort_keys=True),
        json.dumps(validation, sort_keys=True),
    )


def _validate_identifier(identifier):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise ValueError("unsafe_table_name")
    return identifier
