"""ClickHouse boundary for the memory lane.

The same two rules the engine lane holds to apply verbatim here:
  * reads bind every caller-supplied value as a server-side `{name:Type}`
    parameter -- never string interpolation. A `job_id` or a `plan_fingerprint`
    reaching recall() is model- or user-influenced;
  * writes go through the native `client.insert(...)` and are verified.

Everything recall() does is a SELECT. The only writes live in the indexer.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from .config import ClickHouseSettings

# ── The "is this a real plan?" predicate, defined once ───────────────────────
# Two kinds of junk fingerprint live in the store and BOTH would corrupt recall
# if treated as plans:
#   * the empty FixedString -- Spark had no plan for that stage (2 rows per job
#     in the live data). Stored as NUL padding, so `!= ''` alone is unreliable.
#   * 64 literal '0' characters -- the synthetic contract fixtures.
# Left un-excluded, every job in the store would "match" every other job on a
# shape that means "no plan", which is the most confident-looking wrong answer
# this lane could possibly produce.
REAL_FINGERPRINT = (
    "match(toString(plan_fingerprint), '^[0-9a-f]{64}$') "
    "AND plan_fingerprint != toFixedString(repeat('0', 64), 64)"
)

# The same predicate with columns table-qualified. Required wherever a SELECT
# aliases an aggregate back to the source column name (`argMax(plan_json, ts) AS
# plan_json`): ClickHouse resolves the bare name in WHERE to the *alias* and
# fails with ILLEGAL_AGGREGATION. Qualifying forces the column. Verified against
# 24.8.14.39 rather than assumed.
REAL_FINGERPRINT_QUALIFIED = (
    "match(toString(spark_events.plan_fingerprint), '^[0-9a-f]{64}$') "
    "AND spark_events.plan_fingerprint != toFixedString(repeat('0', 64), 64)"
)

# Per-stage reduction. `argMax(col, ts)` -- the latest attempt's values -- not a
# bare GROUP BY, which would blend attempt 0's spill with attempt 1's p99. This
# shape is lifted from infra/sql/005_skew.sql and is what engine and serve both
# use; deviating here would make memory disagree with the diagnosis it supports.
_LATEST_ATTEMPT_CTE = f"""
WITH latest AS (
  SELECT
    job_id,
    stage_id,
    argMax(app_id, ts)                    AS app_id,
    argMax(app_name, ts)                  AS app_name,
    argMax(plan_fingerprint, ts)          AS plan_fingerprint,
    argMax(task_count, ts)                AS task_count,
    argMax(task_duration_p50_ms, ts)      AS p50,
    argMax(task_duration_p99_ms, ts)      AS p99,
    argMax(shuffle_read_bytes, ts)        AS shuffle_read_bytes,
    argMax(shuffle_write_bytes, ts)       AS shuffle_write_bytes,
    argMax(spill_disk_bytes, ts)          AS spill_disk_bytes,
    argMax(spill_mem_bytes, ts)           AS spill_mem_bytes,
    argMax(gc_time_ms, ts)                AS gc_time_ms,
    argMax(input_bytes, ts)               AS input_bytes,
    argMax(output_bytes, ts)              AS output_bytes,
    argMax(peak_execution_mem_bytes, ts)  AS peak_execution_mem_bytes,
    -- Aliased `stage_ts`, NOT `ts`: an alias that shadows the source column
    -- makes every sibling `argMax(col, ts)` resolve against the aggregate and
    -- ClickHouse rejects the query (ILLEGAL_AGGREGATION). Same trap as
    -- REAL_FINGERPRINT_QUALIFIED above.
    max(ts)                               AS stage_ts
  FROM apex.spark_events
  WHERE job_id = {{job_id:String}}
  GROUP BY job_id, stage_id
)
"""

# One row per (job_id, plan_fingerprint) -- the run_outcomes grain.
SHAPE_OUTCOMES_SQL = _LATEST_ATTEMPT_CTE + f"""
SELECT
  job_id,
  toString(plan_fingerprint)               AS plan_fingerprint,
  any(app_id)                              AS app_id,
  any(app_name)                            AS app_name,
  count()                                  AS stage_count,
  -- Every column inside these aggregates is qualified with `latest.`. Without
  -- it, `sum(task_count * p50)` resolves `task_count` to the `sum(task_count)`
  -- alias on the line above and ClickHouse rejects the whole query with
  -- "aggregate function found inside another aggregate function".
  sum(latest.task_count)                   AS task_count,
  -- Span of this shape's stages. 0 for a single-stage shape, and NOT a job
  -- duration: stages of different shapes interleave, so this is context, not
  -- the cost metric. task_time_ms below is the metric deltas are computed on.
  dateDiff('millisecond', min(stage_ts), max(stage_ts)) AS wall_clock_ms,
  sum(latest.task_count * latest.p50)      AS task_time_ms,
  sum(latest.shuffle_read_bytes)           AS shuffle_read_bytes,
  sum(latest.shuffle_write_bytes)          AS shuffle_write_bytes,
  sum(latest.spill_disk_bytes)             AS spill_disk_bytes,
  sum(latest.spill_mem_bytes)              AS spill_mem_bytes,
  sum(latest.gc_time_ms)                   AS gc_time_ms,
  sum(latest.input_bytes)                  AS input_bytes,
  sum(latest.output_bytes)                 AS output_bytes,
  max(latest.peak_execution_mem_bytes)     AS peak_execution_mem_bytes,
  ifNull(max(latest.p99 / nullIf(latest.p50, 0)), 0) AS max_skew_ratio,
  max(stage_ts)                            AS observed_at
FROM latest
WHERE {REAL_FINGERPRINT}
GROUP BY job_id, plan_fingerprint
ORDER BY task_time_ms DESC
"""

# AQE corroboration. CONTRACT.md v0.2 keys plan_transitions by
# (job_id, execution_id) and explicitly has no execution->stage map yet, so these
# counts are JOB-level and get denormalised onto every shape row of that job.
# They are corroboration for the job, not proof about a specific shape.
# Only HIGH-confidence transitions count: BEST_EFFORT is parsed from a
# simpleString and the contract calls it corroboration, not ground truth.
JOB_AQE_SQL = """
SELECT
  countIf(transition_type = 'skew_split') AS aqe_skew_splits,
  countIf(transition_type = 'coalesce')   AS aqe_coalesces
FROM apex.plan_transitions
WHERE job_id = {job_id:String} AND confidence = 'HIGH'
"""

# Findings attributed to a shape via stage_id. Job-level findings carry
# stage_id = -1 (the sentinel engine uses for AQE findings) and deliberately do
# not join -- they belong to no single shape and counting them against one would
# overstate that shape's problems.
SHAPE_FINDINGS_SQL = """
SELECT
  toString(s.plan_fingerprint) AS plan_fingerprint,
  count()                      AS finding_count,
  max(toUInt8(f.severity))     AS worst_severity_rank
FROM apex.findings AS f
INNER JOIN (
  SELECT job_id, stage_id, argMax(plan_fingerprint, ts) AS plan_fingerprint
  FROM apex.spark_events
  WHERE job_id = {job_id:String}
  GROUP BY job_id, stage_id
) AS s ON f.job_id = s.job_id AND f.stage_id = s.stage_id
WHERE f.job_id = {job_id:String}
GROUP BY plan_fingerprint
"""

# Every distinct real plan in the store, for (re)building plan_memory.
DISTINCT_PLANS_SQL = f"""
SELECT
  toString(plan_fingerprint) AS plan_fingerprint,
  argMax(plan_json, ts)      AS plan_json,
  min(ts)                    AS first_seen,
  max(ts)                    AS last_seen
FROM apex.spark_events
WHERE spark_events.plan_json != '' AND {REAL_FINGERPRINT_QUALIFIED}
GROUP BY plan_fingerprint
"""

PLANS_FOR_JOB_SQL = f"""
SELECT
  toString(plan_fingerprint) AS plan_fingerprint,
  argMax(plan_json, ts)      AS plan_json,
  count()                    AS stage_count
FROM apex.spark_events
WHERE spark_events.job_id = {{job_id:String}}
  AND spark_events.plan_json != '' AND {REAL_FINGERPRINT_QUALIFIED}
GROUP BY plan_fingerprint
ORDER BY stage_count DESC
"""

# Fuzzy retrieval. Brute-force cosineDistance, deliberately: verified live on
# ClickHouse 24.8.14.39, `vector_similarity` accepts only the 2-arg form and
# needs an experimental flag, while an ANN index would also make these results
# approximate. At Apex's scale an exact scan is both correct and cheaper.
# `FINAL` collapses ReplacingMergeTree duplicates so a re-indexed fingerprint
# cannot appear twice in one top-k.
NEIGHBOURS_SQL = """
SELECT
  toString(plan_fingerprint)                     AS plan_fingerprint,
  1 - cosineDistance(embedding, {vec:Array(Float32)}) AS similarity,
  node_count,
  op_counts,
  sample_plan_json
FROM apex.plan_memory FINAL
WHERE encoder_version = {encoder_version:String}
  AND dim = {dim:UInt16}
  AND length(embedding) > 0
  AND plan_fingerprint != toFixedString({self_fp:String}, 64)
ORDER BY similarity DESC
LIMIT {top_k:UInt32}
"""

OUTCOMES_FOR_FINGERPRINTS_SQL = """
SELECT
  job_id, app_id, app_name, toString(plan_fingerprint) AS plan_fingerprint,
  conf_shuffle_partitions, conf_executor_instances, conf_executor_cores,
  conf_executor_memory_mb, conf_driver_cores, conf_driver_memory_mb,
  conf_extra, config_source,
  stage_count, task_count, wall_clock_ms, task_time_ms,
  shuffle_read_bytes, shuffle_write_bytes, spill_disk_bytes, spill_mem_bytes,
  gc_time_ms, input_bytes, output_bytes, peak_execution_mem_bytes,
  max_skew_ratio, aqe_skew_splits, aqe_coalesces, finding_count, worst_severity,
  outcome_source, observed_at, indexed_at
FROM apex.run_outcomes FINAL
WHERE plan_fingerprint IN {fps:Array(String)}
ORDER BY plan_fingerprint, task_time_ms
"""

# The resolved allowlisted SparkConf for a run (contract v0.4, apex.job_conf).
# A job with no row here ran before conf capture existed, or had it disabled;
# either way the answer is "not captured", never "defaults".
JOB_CONF_SQL = """
SELECT conf
FROM apex.job_conf
WHERE job_id = {job_id:String}
ORDER BY ts DESC
LIMIT 1
"""

ALL_JOB_IDS_SQL = f"""
SELECT DISTINCT job_id
FROM apex.spark_events
WHERE {REAL_FINGERPRINT}
ORDER BY job_id
"""

PLAN_MEMORY_COLUMNS = (
    "plan_fingerprint", "encoder_version", "embedding_kind", "embedding", "dim",
    "op_counts", "node_count", "max_depth", "join_count", "agg_count",
    "exchange_count", "scan_count", "has_udf", "plan_chars", "sample_plan_json",
    "first_seen", "last_seen", "indexed_at",
)

RUN_OUTCOME_COLUMNS = (
    "job_id", "app_id", "app_name", "plan_fingerprint",
    "conf_shuffle_partitions", "conf_executor_instances", "conf_executor_cores",
    "conf_executor_memory_mb", "conf_driver_cores", "conf_driver_memory_mb",
    "conf_extra", "config_source",
    "stage_count", "task_count", "wall_clock_ms", "task_time_ms",
    "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes",
    "spill_mem_bytes", "gc_time_ms", "input_bytes", "output_bytes",
    "peak_execution_mem_bytes", "max_skew_ratio", "aqe_skew_splits",
    "aqe_coalesces", "finding_count", "worst_severity", "outcome_source",
    "observed_at", "indexed_at",
)

# apex.findings.severity is Enum8('info'=1,...,'blocker'=4); max(toUInt8(...))
# gives the rank and this maps it back for display.
SEVERITY_BY_RANK = {0: "", 1: "info", 2: "warning", 3: "critical", 4: "blocker"}


def normalise_fingerprint(value: Any) -> str:
    """FixedString(64) round-trips as bytes or NUL-padded text; make it hex text."""
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8", errors="replace")
    return str(value).replace("\x00", "").strip()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MemoryStore:
    """Thin, lazily-connected wrapper. Mirrors engine's boundary shape."""

    def __init__(self, settings: ClickHouseSettings | None = None, client: Any = None):
        self._settings = settings or ClickHouseSettings()
        self._client = client

    @property
    def client(self):
        if self._client is None:
            self._client = self._settings.connect()
        return self._client

    # ── reads ────────────────────────────────────────────────────────────────
    def query(self, sql: str, parameters: dict[str, Any] | None = None) -> list[dict]:
        result = self.client.query(sql, parameters=parameters or {})
        return [dict(zip(result.column_names, row)) for row in result.result_rows]

    # ── writes (indexer only) ────────────────────────────────────────────────
    def insert(self, table: str, rows: list[Iterable], column_names: Iterable[str]) -> int:
        if not rows:
            return 0
        summary = self.client.insert(table, rows, column_names=list(column_names))
        # clickhouse-connect reports written_rows on the summary; fall back to
        # the submitted count when the driver omits it rather than claiming 0.
        written = getattr(summary, "written_rows", None)
        return int(written) if written is not None else len(rows)
