"""T-20261103-infra-mv-single-query — mv_spark_events has three byte-equal copies.

Offline: 020 (fresh-volume CREATE), 040 (single MODIFY QUERY for old volumes) and
collect/ddl/30 (lane source) carry the same SELECT; 034–039 carry only ADD COLUMNs; the
live helper never names an infra container.
Live (APEX_INFRA_LIVE=1): a fresh initdb and an upgraded old volume end on the same MV.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from _live import (
    CONTAINER_PREFIX,
    REPO,
    SQL_DIR,
    DisposableClickHouse,
    live_only,
    normalize_sql,
    sql_files,
)

CONTRACT = REPO / "contract" / "spark_events.ddl.sql"
COPIES = {
    "020": SQL_DIR / "020_mv_reshape.sql",
    "040": SQL_DIR / "040_mv_spark_events_resync.sql",
    "collect/30": REPO / "collect" / "ddl" / "30_mv_spark_events.sql",
}
ADDITIVE = sorted(SQL_DIR.glob("03[4-9]_*.sql"))

# The v0.1 reshape query 020 carried before this leaf: the state of every volume
# created before the additive migrations existed. Embedded so the upgrade test needs
# no git history.
MV_V01 = """CREATE MATERIALIZED VIEW IF NOT EXISTS apex.mv_spark_events TO apex.spark_events AS
SELECT
  SpanAttributes['job_id']                                      AS job_id,
  SpanAttributes['app_id']                                      AS app_id,
  SpanAttributes['app_name']                                    AS app_name,
  toInt32OrZero(SpanAttributes['stage_id'])                     AS stage_id,
  toInt32OrZero(SpanAttributes['stage_attempt'])                AS stage_attempt,
  fromUnixTimestamp64Milli(toInt64OrZero(SpanAttributes['ts'])) AS ts,
  toInt64OrZero(SpanAttributes['shuffle_read_bytes'])           AS shuffle_read_bytes,
  toInt64OrZero(SpanAttributes['shuffle_write_bytes'])          AS shuffle_write_bytes,
  toInt64OrZero(SpanAttributes['spill_disk_bytes'])             AS spill_disk_bytes,
  toInt64OrZero(SpanAttributes['spill_mem_bytes'])              AS spill_mem_bytes,
  toInt64OrZero(SpanAttributes['gc_time_ms'])                   AS gc_time_ms,
  toInt64OrZero(SpanAttributes['input_bytes'])                  AS input_bytes,
  toInt64OrZero(SpanAttributes['output_bytes'])                 AS output_bytes,
  toInt64OrZero(SpanAttributes['peak_execution_mem_bytes'])     AS peak_execution_mem_bytes,
  toInt32OrZero(SpanAttributes['task_count'])                   AS task_count,
  toInt64OrZero(SpanAttributes['task_duration_p50_ms'])         AS task_duration_p50_ms,
  toInt64OrZero(SpanAttributes['task_duration_p99_ms'])         AS task_duration_p99_ms,
  toFixedString(SpanAttributes['plan_fingerprint'], 64)         AS plan_fingerprint,
  SpanAttributes['plan_json']                                   AS plan_json,
  CAST(SpanAttributes, 'Map(String, String)')                   AS attributes
FROM apex.otel_traces
WHERE SpanName = 'apex.stage'
  AND SpanAttributes['job_id'] != '';
"""


def mv_select(path: Path) -> str:
    """The SELECT body of mv_spark_events in *path* (CREATE ... AS or MODIFY QUERY)."""
    text = normalize_sql(path.read_text())
    m = re.search(
        r"mv_spark_events (?:TO apex\.spark_events AS|MODIFY QUERY) (SELECT .*?)(?= CREATE | ALTER |$)",
        text,
    )
    assert m, f"no mv_spark_events SELECT in {path}"
    return m.group(1).strip().rstrip(";").strip()


def v05_columns() -> list[str]:
    return [
        line.split()[0]
        for line in CONTRACT.read_text().splitlines()
        if "v0.5" in line and re.match(r"\s+\w+\s+(Int|UInt|Float|String|Date|Fixed)", line)
    ]


# -- offline ---------------------------------------------------------------------


def test_mv_copies_are_byte_equal():
    bodies = {k: mv_select(p) for k, p in COPIES.items()}
    assert bodies["020"] == bodies["collect/30"], "020 drifted from collect/ddl/30"
    assert bodies["040"] == bodies["collect/30"], "040 drifted from collect/ddl/30"


def test_mv_copies_select_every_v05_column():
    cols = v05_columns()
    assert len(cols) >= 15, cols
    body = mv_select(COPIES["020"])
    missing = [c for c in cols if f" AS {c}" not in body + " "]
    assert not missing, missing


def test_additive_files_have_no_query():
    assert len(ADDITIVE) == 6, [p.name for p in ADDITIVE]
    for path in ADDITIVE:
        text = normalize_sql(path.read_text())
        assert "MODIFY QUERY" not in text, path.name
        assert "ADD COLUMN IF NOT EXISTS" in text, path.name


def test_single_resync_file_is_a_modify_query():
    text = normalize_sql(COPIES["040"].read_text())
    assert text.startswith("ALTER TABLE apex.mv_spark_events MODIFY QUERY SELECT")
    assert text.count("MODIFY QUERY") == 1


def test_helper_never_touches_infra():
    source = (Path(__file__).parent / "_live.py").read_text()
    assert "apex-infra" not in source
    assert CONTAINER_PREFIX == "apex-disposable-"
    assert 'sock.bind(("127.0.0.1", 0))' in source, "port must come from the kernel"
    for literal in ("8123:8123", "18123", "28123"):
        assert literal not in source


# -- live ------------------------------------------------------------------------

MARKERS = ("executor_run_time_ms", "successful_task_shuffle_read_bytes_sample_count")


@live_only
def test_fresh_volume_mv_selects_v05():
    with DisposableClickHouse(sql_files()) as ch:
        live = ch.create_table_query("mv_spark_events")
        for marker in MARKERS:
            assert marker in live, marker


@live_only
def test_upgraded_volume_mv_matches_fresh():
    with DisposableClickHouse(sql_files()) as fresh:
        expected = normalize_sql(fresh.create_table_query("mv_spark_events"))
    old_files = sql_files(lambda n: n < 34)
    with DisposableClickHouse(old_files, overrides={"020_mv_reshape.sql": MV_V01}) as old:
        before = old.create_table_query("mv_spark_events")
        assert "executor_run_time_ms" not in before, "fixture is not the v0.1 query"
        old.apply(sql_files(lambda n: n >= 34))
        assert normalize_sql(old.create_table_query("mv_spark_events")) == expected
