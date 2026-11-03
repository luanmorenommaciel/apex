"""T-20261103-infra-rollup-v05-columns — every v0.5 column has a home in spark_jobs_1m.

Offline: each contract v0.5 column of spark_events has an aggFn__column in 004, and
004's MV SELECT equals 041's. Live (APEX_INFRA_LIVE=1): a successful sample merges
back out of the sketch, and a volume that predates the columns converges on the
fresh-volume SHOW CREATE after 041.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from _live import REPO, SQL_DIR, DisposableClickHouse, live_only, normalize_sql, sql_files

CONTRACT = REPO / "contract" / "spark_events.ddl.sql"
ROLLUP = SQL_DIR / "004_rollup_mv.sql"
ADDITIVE = SQL_DIR / "041_rollup_v05_additive.sql"
# 004 as it was before this leaf (v0.1 rollup): the state of every pre-existing volume.
# Embedded so the upgrade test needs no git history and no fixture file.
ROLLUP_V01 = """-- Apex infra · job-level rollup — AggregatingMergeTree target + incremental MV.
--
-- WHY: stage rows in spark_events are fine for point queries, but HyperDX time tiles and the
-- rollup skew query want per-(minute, job) summaries. This rolls stage rows up to 1-minute
-- buckets. We store quantile SKETCHES (quantilesState), NOT finalized values, so any percentile
-- (p50, p95, p99, ...) is recoverable later from one state via quantilesMerge.
--
-- CONVENTIONS (do not deviate — HyperDX auto-acceleration maps queries to MV columns by these):
--   * column naming  <aggFn>__<sourceColumn>   e.g. sum__shuffle_read_bytes, quantiles__task_duration_p99_ms
--   * 1-minute buckets (toStartOfMinute) — composes with 15-min charts; NEVER 10-min.
--   * source types are Int64 (contract) -> the state/simple-agg types are Int64 to match.
--
-- ⚠️ Incremental MVs are BETA and NOT backfilled: spark_jobs_1m only contains rows inserted
--    into spark_events AFTER this MV exists. No POPULATE (can miss rows). When registering in
--    HyperDX set the source "min date" = min(ts). Backfill manually if needed (see README).

CREATE TABLE IF NOT EXISTS apex.spark_jobs_1m (
  bucket                          DateTime,
  job_id                          String,
  app_id                          String,
  count__                         AggregateFunction(count),
  sum__shuffle_read_bytes         SimpleAggregateFunction(sum, Int64),
  sum__shuffle_write_bytes        SimpleAggregateFunction(sum, Int64),
  sum__spill_disk_bytes           SimpleAggregateFunction(sum, Int64),
  sum__spill_mem_bytes            SimpleAggregateFunction(sum, Int64),
  sum__input_bytes                SimpleAggregateFunction(sum, Int64),
  sum__output_bytes               SimpleAggregateFunction(sum, Int64),
  max__gc_time_ms                 SimpleAggregateFunction(max, Int64),
  max__peak_execution_mem_bytes   SimpleAggregateFunction(max, Int64),
  quantiles__task_duration_p50_ms AggregateFunction(quantiles(0.5, 0.99), Int64),
  quantiles__task_duration_p99_ms AggregateFunction(quantiles(0.5, 0.99), Int64)
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (bucket, job_id, app_id)
TTL bucket + INTERVAL 90 DAY
SETTINGS non_replicated_deduplication_window = 100;

CREATE MATERIALIZED VIEW IF NOT EXISTS apex.spark_jobs_1m_mv TO apex.spark_jobs_1m AS
SELECT
  toStartOfMinute(ts)                              AS bucket,
  job_id,
  app_id,
  countState()                                     AS count__,
  sumSimpleState(shuffle_read_bytes)               AS sum__shuffle_read_bytes,
  sumSimpleState(shuffle_write_bytes)              AS sum__shuffle_write_bytes,
  sumSimpleState(spill_disk_bytes)                 AS sum__spill_disk_bytes,
  sumSimpleState(spill_mem_bytes)                  AS sum__spill_mem_bytes,
  sumSimpleState(input_bytes)                      AS sum__input_bytes,
  sumSimpleState(output_bytes)                     AS sum__output_bytes,
  maxSimpleState(gc_time_ms)                       AS max__gc_time_ms,
  maxSimpleState(peak_execution_mem_bytes)         AS max__peak_execution_mem_bytes,
  quantilesState(0.5, 0.99)(task_duration_p50_ms)  AS quantiles__task_duration_p50_ms,
  quantilesState(0.5, 0.99)(task_duration_p99_ms)  AS quantiles__task_duration_p99_ms
FROM apex.spark_events
GROUP BY bucket, job_id, app_id;
"""


def v05_columns() -> list[str]:
    return [
        line.split()[0]
        for line in CONTRACT.read_text().splitlines()
        if "v0.5" in line and re.match(r"\s+\w+\s+(Int|UInt|Float|String|Date|Fixed)", line)
    ]


def rollup_columns() -> list[str]:
    block = re.search(r"CREATE TABLE IF NOT EXISTS apex\.spark_jobs_1m \((.*?)\)\s*ENGINE", normalize_sql(ROLLUP.read_text()), re.S).group(1)
    return [part.strip().split()[0] for part in block.split(",") if "__" in part.split()[0] or part.strip().split()[0] in ("bucket", "job_id", "app_id")]


def mv_select(path: Path) -> str:
    text = normalize_sql(path.read_text())
    m = re.search(r"spark_jobs_1m_mv (?:TO apex\.spark_jobs_1m AS|MODIFY QUERY) (SELECT .*?)(?= CREATE | ALTER |$)", text)
    assert m, path
    return m.group(1).strip()


# -- offline ---------------------------------------------------------------------


def test_rollup_covers_v05():
    cols = v05_columns()
    assert len(cols) >= 15
    names = rollup_columns()
    missing = [c for c in cols if not any(n.endswith("__" + c) for n in names)]
    assert not missing, missing


def test_rollup_mv_select_matches_additive():
    assert mv_select(ROLLUP) == mv_select(ADDITIVE)


def test_additive_adds_every_new_column_in_declared_order():
    declared = [n for n in rollup_columns() if "__" in n]
    added = re.findall(r"ADD COLUMN IF NOT EXISTS (\w+)", ADDITIVE.read_text())
    assert added == declared[len(declared) - len(added):], "041 must append in 004's order"
    assert all(n.split("__")[0] in ("sum", "max", "quantiles", "quantilesIf", "count") for n in declared)


# -- live ------------------------------------------------------------------------


def stage_span(job: str, now_ms: int, **attrs) -> str:
    base = {"job_id": job, "app_id": "app-1", "app_name": "rollup", "stage_id": "7", "stage_attempt": "0",
            "ts": str(now_ms), "task_count": "8", "task_duration_p50_ms": "100", "task_duration_p99_ms": "200",
            "plan_fingerprint": "b" * 64, "plan_json": "{}"}
    base.update({k: str(v) for k, v in attrs.items()})
    m = ",".join(f"'{k}':'{v}'" for k, v in base.items())
    return ("INSERT INTO apex.otel_traces (Timestamp, TraceId, SpanId, SpanName, ServiceName, SpanAttributes) "
            f"VALUES (fromUnixTimestamp64Milli({now_ms}), 'trace-{job}', 'span-{attrs.get('stage_id', 7)}', 'apex.stage', 'apex-jar', {{{m}}})")


@live_only
def test_rollup_successful_sample_merges_back():
    now_ms = int(time.time() * 1000)
    job = f"rollup-{now_ms}"
    with DisposableClickHouse(sql_files()) as ch:
        ch.query(stage_span(job, now_ms, successful_task_duration_p50_ms=1000, successful_task_duration_p99_ms=9000,
                            successful_task_sample_count=4, task_failed_attempt_count=2), fmt=None)
        ch.query(stage_span(job, now_ms, stage_id=8), fmt=None)  # legacy row: no successful sample
        row = ch.query(
            "SELECT quantilesIfMerge(0.5, 0.99)(quantilesIf__successful_task_duration_p99_ms), "
            "quantilesIfMerge(0.5, 0.99)(quantilesIf__successful_task_duration_p50_ms), "
            "sum(sum__successful_task_sample_count), sum(sum__task_failed_attempt_count), countMerge(count__) "
            f"FROM apex.spark_jobs_1m WHERE job_id = '{job}'"
        ).strip().split("\t")
        assert row == ["[9000,9000]", "[1000,1000]", "4", "2", "2"], row


@live_only
def test_rollup_upgrade_converges():
    with DisposableClickHouse(sql_files()) as fresh:
        expected = {n: normalize_sql(fresh.create_table_query(n)) for n in ("spark_jobs_1m", "spark_jobs_1m_mv")}
    with DisposableClickHouse(sql_files(lambda n: n < 41), overrides={"004_rollup_mv.sql": ROLLUP_V01}) as old:
        assert "successful" not in old.create_table_query("spark_jobs_1m")
        old.apply(sql_files(lambda n: n >= 41))
        for name, want in expected.items():
            assert normalize_sql(old.create_table_query(name)) == want, name
