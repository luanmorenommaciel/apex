"""ClickHouse-backed telemetry store adapter for Commander."""

import json
import re

COLUMNS = (
    "schema_version",
    "job_id",
    "app_id",
    "event_counts_json",
    "stages_json",
    "skew_candidates_json",
    "envelope_json",
)


class ClickHouseTelemetryStore:
    def __init__(self, client, table="commander_telemetry"):
        self.client = client
        self.table = _validate_identifier(table)

    def ensure_schema(self):
        self.client.command(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table}
            (
                schema_version String,
                job_id String,
                app_id Nullable(String),
                event_counts_json String,
                stages_json String,
                skew_candidates_json String,
                envelope_json String,
                inserted_at DateTime DEFAULT now()
            )
            ENGINE = MergeTree
            ORDER BY (job_id, inserted_at)
            """
        )

    def append_envelope(self, envelope):
        self.client.insert(
            self.table,
            [_row_from_envelope(envelope)],
            column_names=COLUMNS,
        )

    def query_by_job_id(self, job_id):
        result = self.client.query(
            f"""
            SELECT envelope_json
            FROM {self.table}
            WHERE job_id = {{job_id:String}}
            ORDER BY inserted_at ASC
            """,
            parameters={"job_id": job_id},
        )
        return [json.loads(row[0]) for row in result.result_rows]


def _row_from_envelope(envelope):
    return (
        envelope.get("schema_version", ""),
        envelope["job_id"],
        envelope.get("app_id"),
        json.dumps(envelope.get("event_counts", {}), sort_keys=True),
        json.dumps(envelope.get("stages", []), sort_keys=True),
        json.dumps(envelope.get("skew_candidates", []), sort_keys=True),
        json.dumps(envelope, sort_keys=True),
    )


def _validate_identifier(identifier):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise ValueError("unsafe_table_name")
    return identifier
