"""T-20261103-infra-dedup-window-base-ddl — the dedup window lives in the base DDL.

Offline: 004, 010 and 011 declare non_replicated_deduplication_window = 100 in their
CREATE; the three plan_transitions copies (contract, collect, infra) are identical.
Live (APEX_INFRA_LIVE=1): a volume initialised from 001–032 already has the window
before 033 runs, and a retried identical block lands once in otel_traces and once in
spark_events — the property the collector's retry path relies on.
"""
from __future__ import annotations

import re
import time

from _live import REPO, SQL_DIR, DisposableClickHouse, live_only, normalize_sql, sql_files

WINDOW = "non_replicated_deduplication_window = 100"
BASE = {
    "spark_jobs_1m": SQL_DIR / "004_rollup_mv.sql",
    "otel_traces": SQL_DIR / "010_otel_traces.sql",
    "plan_transitions": SQL_DIR / "011_plan_transitions.sql",
    "spark_events": SQL_DIR / "002_spark_events.sql",
}
PLAN_TRANSITIONS_COPIES = [
    REPO / "contract" / "plan_transitions.ddl.sql",
    REPO / "collect" / "ddl" / "21_plan_transitions.sql",
    SQL_DIR / "011_plan_transitions.sql",
]
DEDUP_TARGETS = ("otel_traces", "spark_events", "plan_transitions", "spark_jobs_1m")


def create_statement(path, table: str) -> str:
    text = normalize_sql(path.read_text())
    m = re.search(rf"CREATE TABLE (?:IF NOT EXISTS )?apex\.{table} \(.*?\)\s*ENGINE.*?(?=;| CREATE |$)", text)
    assert m, f"no CREATE TABLE apex.{table} in {path}"
    return m.group(0)


# -- offline ---------------------------------------------------------------------


def test_dedup_window_in_base_ddl():
    for table, path in BASE.items():
        stmt = create_statement(path, table)
        assert WINDOW in stmt, f"{path.name} does not declare the window for {table}"


def test_plan_transitions_copies_agree():
    bodies = {p: create_statement(p, "plan_transitions").replace("IF NOT EXISTS ", "") for p in PLAN_TRANSITIONS_COPIES}
    first = next(iter(bodies.values()))
    for path, body in bodies.items():
        assert body == first, f"{path} drifted from {PLAN_TRANSITIONS_COPIES[0]}"


def test_033_is_documented_as_existing_volume_only():
    text = (SQL_DIR / "033_dedup_window_additive.sql").read_text()
    assert "Existing-volume migration ONLY" in text


# -- live ------------------------------------------------------------------------


@live_only
def test_dedup_window_before_033():
    with DisposableClickHouse(sql_files(lambda n: n < 33)) as ch:
        for table in DEDUP_TARGETS:
            assert WINDOW in ch.create_table_query(table), table


@live_only
def test_retried_block_lands_once():
    now_ms = int(time.time() * 1000)
    job = "dedup-" + str(now_ms)
    attrs = "{'job_id':'%s','app_id':'app-1','app_name':'dedup','stage_id':'1','stage_attempt':'0','ts':'%d','task_count':'4','task_duration_p50_ms':'10','task_duration_p99_ms':'50','plan_fingerprint':'%s','plan_json':'{}'}" % (job, now_ms, "a" * 64)
    insert = (
        "INSERT INTO apex.otel_traces (Timestamp, TraceId, SpanId, SpanName, ServiceName, SpanAttributes) "
        "SETTINGS insert_deduplicate = 1, deduplicate_blocks_in_dependent_materialized_views = 1 "
        f"VALUES (fromUnixTimestamp64Milli({now_ms}), 'trace-{job}', 'span-1', 'apex.stage', 'apex-jar', {attrs})"
    )
    with DisposableClickHouse(sql_files()) as ch:
        ch.query(insert, fmt=None)
        ch.query(insert, fmt=None)  # the retry: identical rows => identical block hash
        raw = ch.query(f"SELECT count() FROM apex.otel_traces WHERE SpanAttributes['job_id'] = '{job}'").strip()
        reshaped = ch.query(f"SELECT count() FROM apex.spark_events WHERE job_id = '{job}'").strip()
        assert (raw, reshaped) == ("1", "1"), (raw, reshaped)
