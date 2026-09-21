"""ClickHouse read layer for the Apex MCP tools.

Three rules this module exists to enforce:

1. **Server-side parameter binding, always.** Every query uses ClickHouse
   placeholders (``{job_id:String}``) with ``parameters={...}``. A ``job_id``
   reaches us from a model or a user, so it is an injection surface; it is
   never formatted into SQL text.
2. **Latest attempt per stage via ``argMax(col, ts)``.** A plain ``GROUP BY
   stage_id`` silently mixes metrics from different stage attempts (attempt 0's
   spill with attempt 1's p99) and produces a wrong diagnosis. ``argMax`` picks
   every column from the newest row per stage.
3. **Sanitized errors.** A raised driver exception carries the host, user and
   sometimes the password of the ClickHouse connection. Those never reach the
   model — they are logged to stderr and replaced with a short opaque code.
"""

from __future__ import annotations

import functools
import logging
import os
import re
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

log = logging.getLogger("apex_mcp.ch")

# Tokens for search_kb: word-ish runs only, so a query can never carry SQL or
# ClickHouse format syntax into the statement even before binding.
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.]{2,64}")
_MAX_TOKENS = 8
_SNIPPET_CHARS = 400


class ApexStoreError(RuntimeError):
    """A sanitized, model-safe store failure. Carries no connection details."""


class QueryResult(Protocol):
    def named_results(self) -> Iterable[dict[str, Any]]: ...


class ClickHouseClient(Protocol):
    def query(
        self, query: str, parameters: dict[str, Any] | None = ...
    ) -> QueryResult: ...


# --------------------------------------------------------------------------
# SQL — every one of these binds server-side.
# --------------------------------------------------------------------------

# argMax(col, ts) per stage_id => the LATEST ATTEMPT's value for every column.
STAGES_SQL = """
SELECT
  stage_id,
  argMax(stage_attempt, ts)            AS stage_attempt,
  argMax(app_id, ts)                   AS app_id,
  argMax(app_name, ts)                 AS app_name,
  argMax(task_count, ts)               AS task_count,
  argMax(shuffle_read_bytes, ts)       AS shuffle_read_bytes,
  argMax(shuffle_write_bytes, ts)      AS shuffle_write_bytes,
  argMax(spill_disk_bytes, ts)         AS spill_disk_bytes,
  argMax(spill_mem_bytes, ts)          AS spill_mem_bytes,
  argMax(gc_time_ms, ts)               AS gc_time_ms,
  argMax(input_bytes, ts)              AS input_bytes,
  argMax(output_bytes, ts)             AS output_bytes,
  argMax(peak_execution_mem_bytes, ts) AS peak_execution_mem_bytes,
  argMax(task_duration_p50_ms, ts)     AS p50_ms,
  argMax(task_duration_p99_ms, ts)     AS p99_ms,
  argMax(toString(plan_fingerprint), ts) AS plan_fingerprint
FROM apex.spark_events
WHERE job_id = {job_id:String}
GROUP BY stage_id
ORDER BY stage_id
"""

# Columns every deployment has. `app_id` and `confidence_score` are v0.2
# ADDITIVE columns — a cluster whose apex.findings predates them must keep
# working, so they are projected only when the table actually has them.
_FINDINGS_CORE = """
  finding_id, job_id, stage_id, toString(type) AS type,
  toString(severity) AS severity, evidence, hot_key, impact, fix,
  toString(confidence) AS confidence, detected_by
"""
_FINDINGS_ADDITIVE = {
    "app_id": ("app_id", "'' AS app_id"),
    # confidence_score is the RAW 0-1 the contract routes to compare_runs;
    # the enum tier is only the human-facing display value.
    "confidence_score": (
        "toFloat64(confidence_score) AS confidence_score",
        "toFloat64(0) AS confidence_score",
    ),
}

# The one read not keyed by job_id: a new user has no job_id yet, and a
# reachable-but-empty store must be distinguishable from a broken one.
# Run discovery. spark_events is ORDER BY (job_id, stage_id, stage_attempt)
# PARTITION BY toYYYYMM(ts), so a newest-first listing is a full scan unless it
# is bounded on ts — the `since` predicate is what lets partitions prune.
# The table alias `e` is load-bearing: the SELECT projects `argMax(app_name, ts)
# AS app_name`, and an unqualified `app_name` in WHERE resolves to that alias,
# which ClickHouse rejects as an aggregate in WHERE (ILLEGAL_AGGREGATION).
# app_name is set by the observed Spark job, so it BINDS; the empty-string test
# expresses "no filter" without building two different statements.
RUNS_SQL = """
SELECT
  job_id,
  argMax(app_id, ts)             AS app_id,
  argMax(app_name, ts)           AS app_name,
  min(ts)                        AS first_ts,
  max(ts)                        AS last_ts,
  uniqExact(stage_id)            AS stage_count,
  sum(spill_disk_bytes)          AS spill_disk_bytes,
  max(task_duration_p99_ms)      AS worst_p99_ms
FROM apex.spark_events AS e
WHERE e.ts >= {since:DateTime}
  AND ({app_name:String} = '' OR e.app_name = {app_name:String})
GROUP BY job_id
ORDER BY last_ts DESC
LIMIT {limit:UInt32}
"""

HEALTH_SQL = """
SELECT
  count()           AS row_count,
  uniqExact(job_id) AS job_count,
  max(ts)           AS latest_ts
FROM apex.spark_events
"""

COLUMNS_SQL = """
SELECT name FROM system.columns
WHERE database = {database:String} AND table = {table:String}
"""


def _findings_sql(present: set[str]) -> str:
    projections = [_FINDINGS_CORE.strip()]
    for column, (available, fallback) in _FINDINGS_ADDITIVE.items():
        projections.append(available if column in present else fallback)
    return f"""
SELECT
  {', '.join(projections)}
FROM apex.findings
WHERE job_id = {{job_id:String}}
ORDER BY ts ASC, finding_id ASC
"""

PLAN_TRANSITIONS_SQL = """
SELECT
  execution_id, update_seq, toString(transition_type) AS transition_type,
  detail, before, after, toString(confidence) AS confidence
FROM apex.plan_transitions
WHERE job_id = {job_id:String}
ORDER BY execution_id, update_seq
"""

# apex.fix_verifications is a v0.3 ADDITIVE table owned by the verify lane.
# Serve reads it; it never writes it and never imports that lane's package —
# the table IS the integration surface (CONTRACT.md: lanes integrate through
# ClickHouse, not through imports).
#
# Enum8/LowCardinality columns are projected through toString() so the driver
# hands back plain strings, the same treatment findings.confidence gets.
# Newest-first because a finding may be re-verified: the latest attempt is the
# one that reflects the current predictor and the current bench.
# `finding_id` is optional and expressed as an empty-string test rather than a
# second statement, exactly like RUNS_SQL's app_name filter — one query text,
# one bound parameter, no branch that could forget to bind.
VERIFICATIONS_SQL = """
SELECT
  verification_id,
  finding_id,
  job_id,
  app_id,
  proposed_config,
  toString(method)          AS method,
  toString(predictor)       AS predictor,
  predicted_delta_pct,
  predicted_low_pct,
  predicted_high_pct,
  measured_delta_pct,
  baseline_ms,
  treatment_ms,
  noise_floor_pct,
  replay_reps,
  bench,
  shape_fidelity,
  safe,
  toString(safety_verdict)  AS safety_verdict,
  safety_detail,
  toString(confidence)      AS confidence,
  confidence_score,
  evidence,
  caveats,
  toString(verify_version)  AS verify_version,
  verified_at
FROM apex.fix_verifications
WHERE job_id = {job_id:String}
  AND ({finding_id:String} = '' OR finding_id = {finding_id:String})
ORDER BY verified_at DESC, verification_id ASC
LIMIT {limit:UInt32}
"""


# --------------------------------------------------------------------------
# Cross-run memory — contract v0.3 ADDITIVE tables.
#
# ``apex.plan_memory`` (one row per plan shape, carrying an L2-NORMALISED
# embedding) and ``apex.run_outcomes`` (one row per shape per run, carrying the
# config it ran under and how it went) are written by the memory lane. serve
# READS them and imports nothing from that lane — the contract tables are the
# integration surface, which is what keeps this package's dependencies at
# ``mcp`` + ``clickhouse-connect`` + ``pydantic``.
#
# They are v0.3 ADDITIVE, so a cluster that has not applied them is normal, not
# broken: every read below degrades to empty and says so.
# --------------------------------------------------------------------------
MEMORY_TABLES = ("plan_memory", "run_outcomes")

# A neighbour below this is not a neighbour. Ranking by raw distance and taking
# top-k returns the k LEAST dissimilar shapes even when all k are unrelated, so
# the gate is on similarity, not on rank — three honest neighbours beat ten of
# which seven are noise. 0.80 is the memory lane's measured cut-off; serve
# mirrors the number rather than inventing a looser one.
MIN_SIMILARITY = 0.80
MAX_SIMILAR_PLANS = 25
MAX_PRIOR_RUNS = 200

TABLES_SQL = """
SELECT name FROM system.tables
WHERE database = {database:String} AND name IN {names:Array(String)}
"""

# Similarity is computed IN ClickHouse: the embedding is already L2-normalised,
# so ``1 - cosineDistance`` is the cosine similarity and serve needs no encoder.
#
# Two details that are load-bearing:
#
# * ``dim`` is read from the queried shape's own row and matched, never
#   hardcoded — the encoder's width is the memory lane's to change, and
#   comparing vectors of different widths is an error, not a weak match.
# * ``substring(..., 1, 64)`` caps the bound value before ``toFixedString``,
#   which THROWS on anything longer than 64. A hostile fingerprint therefore
#   binds as data, matches nothing and returns zero rows instead of raising.
# * The queried shape is INNER JOINed, not read through a scalar sub-select.
#   Proven live on 24.8.14.39: a scalar sub-select is constant-folded before
#   WHERE runs, so an absent fingerprint raises code 125 ("scalar subquery
#   returned empty result of type Array(Float32) which cannot be Nullable")
#   rather than returning nothing. A never-before-seen plan shape is an
#   ordinary answer, not an error. The join also carries the width check:
#   matching on (encoder_version, dim) is what keeps vectors of different
#   widths from being compared at all.
#
# ``FINAL`` collapses the ReplacingMergeTree duplicates a re-index leaves
# behind, so one shape cannot appear twice in a single top-k.
SIMILAR_PLANS_SQL = """
SELECT * FROM (
  SELECT
    toString(p.plan_fingerprint)                  AS plan_fingerprint,
    1 - cosineDistance(p.embedding, s.embedding)  AS similarity,
    p.node_count                                  AS node_count,
    p.join_count                                  AS join_count,
    p.agg_count                                   AS agg_count,
    p.exchange_count                              AS exchange_count,
    p.scan_count                                  AS scan_count,
    p.last_seen                                   AS last_seen
  FROM apex.plan_memory AS p FINAL
  INNER JOIN (
    SELECT embedding, dim, encoder_version
    FROM apex.plan_memory FINAL
    WHERE plan_fingerprint = toFixedString(substring({fingerprint:String}, 1, 64), 64)
      AND length(embedding) > 0
    ORDER BY last_seen DESC
    LIMIT 1
  ) AS s ON p.encoder_version = s.encoder_version AND p.dim = s.dim
  WHERE length(p.embedding) > 0
    AND p.plan_fingerprint != toFixedString(substring({fingerprint:String}, 1, 64), 64)
) WHERE similarity >= {min_similarity:Float64}
ORDER BY similarity DESC
LIMIT {top_k:UInt32}
"""

# Newest first: the question is "what has this shape done lately", and an
# ordering by wall clock would pre-rank the runs into a fastest-is-best list —
# which is exactly the claim serve is not allowed to make without a measured
# floor (CONTRACT.md rule 2).
PRIOR_OUTCOMES_SQL = """
SELECT
  job_id, app_id, app_name,
  toString(plan_fingerprint)         AS plan_fingerprint,
  conf_shuffle_partitions, conf_executor_instances, conf_executor_cores,
  conf_executor_memory_mb, conf_driver_cores, conf_driver_memory_mb,
  conf_extra,
  toString(config_source)            AS config_source,
  stage_count, task_count, wall_clock_ms, task_time_ms,
  shuffle_read_bytes, shuffle_write_bytes, spill_disk_bytes, spill_mem_bytes,
  gc_time_ms, input_bytes, output_bytes, peak_execution_mem_bytes,
  max_skew_ratio, aqe_skew_splits, aqe_coalesces, finding_count,
  toString(worst_severity)           AS worst_severity,
  toString(outcome_source)           AS outcome_source,
  observed_at
FROM apex.run_outcomes FINAL
WHERE plan_fingerprint IN {fingerprints:Array(String)}
  AND job_id != {exclude_job_id:String}
ORDER BY observed_at DESC
LIMIT {limit:UInt32}
"""


# --------------------------------------------------------------------------
# Console reads (ported from front/src/data/queries.ts).
#
# These six answered the console's screens from the BROWSER, against a
# read-only ClickHouse user that shipped to every visitor. They live here so
# the API can serve them and that credential can be retired. The SQL is a
# PORT, not a redesign: the console's rendered numbers are the acceptance
# criterion, so the shape of every result matches what queries.ts returned.
# --------------------------------------------------------------------------

# spark_events is authoritative for WHAT RAN: every stage is here, including
# ones no plan shape claims, so a run stays listed even when the memory lane
# has never indexed it. run_outcomes is read ONLY for shape-attributable
# outcome data — its own stage_count and finding_count exclude unfingerprinted
# stages and stage-less findings, so both would under-report the run, and its
# wall_clock_ms is a per-shape timestamp span rather than a job duration.
def _run_rollup_sql(where: str, tail: str) -> str:
    """The console's run rollup, parameterised by filter and ordering.

    ``where`` and ``tail`` are LITERALS from this module, never a caller's
    value — every user-supplied value in the result is still bound. Sharing
    one body is what stops the single-run and list forms from drifting into
    two different answers to "what is this run".
    """
    return f"""
WITH
base AS (
  SELECT job_id, argMax(app_name, ts) AS app_name,
         uniqExact(stage_id) AS stage_count, min(ts) AS started_at
  FROM apex.spark_events
  {where}
  GROUP BY job_id
),
f AS (
  SELECT job_id, count() AS finding_count,
         max(severity IN ('critical', 'blocker')) AS has_critical
  FROM apex.findings GROUP BY job_id
),
shapes AS (
  SELECT ro.job_id AS job_id,
         sum(ro.task_time_ms)                                  AS task_time_ms,
         toString(argMax(ro.plan_fingerprint, ro.stage_count)) AS plan_fingerprint,
         uniqExact(ro.plan_fingerprint)                        AS shape_count,
         sum(ro.stage_count)                                   AS shaped_stage_count,
         argMax(ro.config_source, ro.observed_at)              AS config_source,
         max(ro.conf_executor_instances)                       AS conf_executor_instances,
         max(ro.conf_shuffle_partitions)                       AS conf_shuffle_partitions
  FROM apex.run_outcomes AS ro FINAL
  GROUP BY ro.job_id
)
SELECT
  b.job_id      AS job_id,
  b.app_name    AS app_name,
  b.stage_count AS stage_count,
  b.started_at  AS started_at,
  ifNull(f.finding_count, 0) AS finding_count,
  ifNull(f.has_critical, 0)  AS has_critical,
  ifNull(s.task_time_ms, -1)       AS task_time_ms,
  ifNull(s.plan_fingerprint, '')   AS plan_fingerprint,
  ifNull(s.shape_count, 0)         AS shape_count,
  ifNull(s.shaped_stage_count, -1) AS shaped_stage_count,
  ifNull(s.config_source, 'unknown') AS config_source,
  s.conf_executor_instances, s.conf_shuffle_partitions
FROM base b
LEFT JOIN f        ON f.job_id = b.job_id
LEFT JOIN shapes s ON s.job_id = b.job_id
{tail}
"""


RUN_ONE_SQL = _run_rollup_sql(
    "WHERE job_id = {job_id:String}", "LIMIT 1"
)
RUN_LIST_SQL = _run_rollup_sql(
    "", "ORDER BY b.started_at DESC LIMIT {limit:UInt32}"
)

# Rule 2 lives in this projection, not in the table. A delta inside the
# measured floor is UNRESOLVABLE, which is not the same as zero, so
# runtime_verdict becomes 'unresolved' and never a direction.
# predicted_saving_pct flips the sign of the stored column, which is signed
# with negative meaning faster. mechanism_confirmed has no source at all and
# stays NULL: deriving it from the safety verdict would collapse rule 4's two
# independent verdicts into one.
FIX_VERIFICATION_SQL = """
WITH slots AS (
  SELECT job_id,
         max(conf_executor_instances) * max(conf_executor_cores) AS cluster_slots
  FROM apex.run_outcomes FINAL
  GROUP BY job_id
)
SELECT
  v.verification_id AS fix_id,
  v.finding_id      AS finding_id,
  v.job_id          AS job_id,
  CAST(NULL AS Nullable(UInt8))       AS mechanism_confirmed,
  toUInt8(v.measured_delta_pct IS NOT NULL
          AND v.noise_floor_pct IS NOT NULL
          AND abs(v.measured_delta_pct) > v.noise_floor_pct) AS runtime_certified,
  multiIf(v.measured_delta_pct IS NULL
            OR v.noise_floor_pct IS NULL
            OR abs(v.measured_delta_pct) <= v.noise_floor_pct, 'unresolved',
          v.measured_delta_pct < 0, 'improved',
          'regressed')                AS runtime_verdict,
  -v.predicted_delta_pct              AS predicted_saving_pct,
  v.noise_floor_pct                   AS noise_floor_pct,
  v.replay_reps                       AS replay_count,
  s.cluster_slots                     AS cluster_slots,
  v.proposed_config                   AS proposed_diff
FROM apex.fix_verifications AS v
LEFT JOIN slots s ON s.job_id = v.job_id
WHERE v.finding_id = {finding_id:String}
ORDER BY v.verified_at DESC
LIMIT 1
"""

# job_conf holds ONE row per job with conf as a Map, while every consumer reads
# one row per key. ARRAY JOIN does the reshape in SQL. An absent key stays
# absent — no LEFT JOIN or COALESCE invents one — which is what lets rule 1
# declare itself vacant rather than assume a cluster width.
JOB_CONF_SQL = """
SELECT
  job_id,
  entry.1 AS key,
  entry.2 AS value,
  ts
FROM apex.job_conf
ARRAY JOIN CAST(conf, 'Array(Tuple(String, String))') AS entry
WHERE job_id = {job_id:String}
ORDER BY key
"""

# Runs that executed at least one of this run's plan shapes. Runs sharing
# nothing are not returned, so the screen can say "no comparable run" instead
# of differencing two unrelated jobs.
BASELINE_CANDIDATES_SQL = """
WITH mine AS (
  SELECT DISTINCT plan_fingerprint
  FROM apex.run_outcomes FINAL
  WHERE job_id = {job_id:String}
)
SELECT
  o.job_id                       AS job_id,
  any(o.app_name)                AS app_name,
  uniqExact(o.plan_fingerprint)  AS shared_shapes,
  max(o.observed_at)             AS observed_at
FROM apex.run_outcomes AS o FINAL
INNER JOIN mine ON mine.plan_fingerprint = o.plan_fingerprint
WHERE o.job_id != {job_id:String}
GROUP BY o.job_id
ORDER BY observed_at DESC
LIMIT {limit:UInt32}
"""

# The INNER JOIN is deliberate: a shape with no outcome row has no history to
# show, and a run whose shape was never indexed is not a shape we know.
PLAN_SHAPES_SQL = """
WITH r AS (
  SELECT plan_fingerprint,
         uniqExact(job_id) AS run_count,
         min(observed_at)  AS first_run,
         max(observed_at)  AS last_run
  FROM apex.run_outcomes FINAL
  GROUP BY plan_fingerprint
)
SELECT
  toString(pm.plan_fingerprint) AS plan_fingerprint,
  r.run_count       AS run_count,
  r.first_run       AS first_run,
  r.last_run        AS last_run,
  pm.node_count     AS node_count,
  pm.join_count     AS join_count,
  pm.agg_count      AS agg_count,
  pm.exchange_count AS exchange_count,
  pm.scan_count     AS scan_count,
  pm.max_depth      AS max_depth,
  pm.has_udf        AS has_udf
FROM apex.plan_memory AS pm FINAL
INNER JOIN r ON r.plan_fingerprint = pm.plan_fingerprint
ORDER BY r.run_count DESC, r.last_run DESC
LIMIT {limit:UInt32}
"""

# ONE redacted exemplar per shape, which the contract's own DDL calls "for
# citation". Read from plan_memory and never from spark_events.plan_json: the
# latter is per stage, so a 34-stage run would ship 34 Catalyst trees to draw
# one. The text is carried verbatim and nothing is parsed out of it.
PLAN_SAMPLE_SQL = """
SELECT toString(sample_plan_json) AS sample_plan_json
FROM apex.plan_memory FINAL
WHERE plan_fingerprint = toFixedString(substring({fingerprint:String}, 1, 64), 64)
ORDER BY indexed_at DESC
LIMIT 1
"""

# task_time_ms is the cost metric, not wall_clock_ms. The conf_* columns stay
# NULL unless the jar emitted job_conf for that run, and null travels through
# as "not captured" so rule 3 can refuse to credit a difference rather than
# compare against an invented default.
SHAPE_RUNS_SQL = """
SELECT
  job_id                  AS job_id,
  app_name                AS app_name,
  task_time_ms            AS task_time_ms,
  finding_count           AS finding_count,
  indexOf(['info', 'warning', 'critical', 'blocker'], worst_severity) AS severity_rank,
  config_source           AS config_source,
  conf_shuffle_partitions AS conf_shuffle_partitions,
  conf_executor_instances AS conf_executor_instances,
  conf_executor_cores     AS conf_executor_cores,
  conf_executor_memory_mb AS conf_executor_memory_mb,
  observed_at             AS observed_at
FROM apex.run_outcomes FINAL
WHERE plan_fingerprint = toFixedString(substring({fingerprint:String}, 1, 64), 64)
ORDER BY observed_at
"""


# The console's stage projection. NOT STAGES_SQL: that one aliases the timings
# AS p50_ms/p99_ms for the MCP's StageView and projects no job_id, stage_name
# or ts at all. Serving it to the console gave undefined timings and NaN
# ratios on three screens. Same table, same argMax discipline, different
# consumer — so it is the eighth console query to move server-side.
CONSOLE_STAGES_SQL = """
SELECT
  se.job_id                                       AS job_id,
  any(se.app_name)                                AS app_name,
  se.stage_id                                     AS stage_id,
  -- No stage name exists in the contract. NULL, never a label invented from
  -- plan_json, which the DDL marks as a tree-string that is never parsed.
  CAST(NULL AS Nullable(String))                  AS stage_name,
  max(se.stage_attempt)                           AS stage_attempt,
  argMax(se.task_count, se.ts)                    AS task_count,
  argMax(se.shuffle_read_bytes, se.ts)            AS shuffle_read_bytes,
  argMax(se.shuffle_write_bytes, se.ts)           AS shuffle_write_bytes,
  argMax(se.input_bytes, se.ts)                   AS input_bytes,
  argMax(se.spill_mem_bytes, se.ts)               AS spill_mem_bytes,
  argMax(se.spill_disk_bytes, se.ts)              AS spill_disk_bytes,
  argMax(se.peak_execution_mem_bytes, se.ts)      AS peak_execution_mem_bytes,
  argMax(se.gc_time_ms, se.ts)                    AS gc_time_ms,
  argMax(se.task_duration_p50_ms, se.ts)          AS task_duration_p50_ms,
  argMax(se.task_duration_p99_ms, se.ts)          AS task_duration_p99_ms,
  -- The pairing key for /compare. A stage with no real fingerprint returns ''
  -- and is reported as unmatched rather than paired on its id, which would
  -- silently compare two different operators.
  if(match(toString(argMax(se.plan_fingerprint, se.ts)), '^[0-9a-f]{64}$')
     AND argMax(se.plan_fingerprint, se.ts) != toFixedString(repeat('0', 64), 64),
     toString(argMax(se.plan_fingerprint, se.ts)), '') AS plan_fingerprint,
  -- Qualified `se.`, every one: the output alias `ts` would otherwise shadow
  -- the source column inside each argMax and ClickHouse rejects the statement
  -- with ILLEGAL_AGGREGATION.
  max(se.ts)                                      AS ts
FROM apex.spark_events AS se
WHERE se.job_id = {job_id:String}
GROUP BY se.job_id, se.stage_id
ORDER BY se.stage_id
"""


def _findings_search_sql(token_params: list[str]) -> str:
    """Build the findings-side search. Placeholder NAMES are generated by us
    (``t0``, ``t1``, …); the token VALUES are always bound, never interpolated.
    """
    haystack = "concat(toString(type),' ',evidence,' ',hot_key,' ',impact,' ',fix,' ',detected_by)"
    score = " + ".join(
        f"toFloat64(positionCaseInsensitive({haystack}, {{{p}:String}}) > 0)"
        for p in token_params
    )
    matched = ", ".join(
        f"if(positionCaseInsensitive({haystack}, {{{p}:String}}) > 0, {{{p}:String}}, '')"
        for p in token_params
    )
    return f"""
SELECT * FROM (
  SELECT
    'findings' AS source, job_id, stage_id, finding_id,
    toString(type) AS type, toString(severity) AS severity,
    concat(toString(type),' | ',evidence,' | ',impact,' | ',fix) AS snippet,
    {score} AS score,
    arrayFilter(x -> x != '', [{matched}]) AS matched_tokens
  FROM apex.findings
) WHERE score > 0
ORDER BY score DESC, job_id ASC, stage_id ASC
LIMIT {{top_k:UInt32}}
"""


def _plans_search_sql(token_params: list[str]) -> str:
    """Search the redacted plan tree-string, deduped per (job_id, fingerprint).

    NOTE: ``plan_json`` is a Catalyst TREE-STRING, not JSON (contract v0.2) —
    we substring it, never parse it.
    """
    score = " + ".join(
        f"max(toFloat64(positionCaseInsensitive(plan_json, {{{p}:String}}) > 0))"
        for p in token_params
    )
    matched = ", ".join(
        f"if(max(positionCaseInsensitive(plan_json, {{{p}:String}})) > 0, {{{p}:String}}, '')"
        for p in token_params
    )
    return f"""
SELECT * FROM (
  SELECT
    'plan_json' AS source, job_id,
    argMax(stage_id, ts) AS stage_id,
    argMax(substring(plan_json, 1, {_SNIPPET_CHARS}), ts) AS snippet,
    toString(plan_fingerprint) AS plan_fingerprint,
    {score} AS score,
    arrayFilter(x -> x != '', [{matched}]) AS matched_tokens
  FROM apex.spark_events
  WHERE plan_json != ''
  GROUP BY job_id, plan_fingerprint
) WHERE score > 0
ORDER BY score DESC, job_id ASC, stage_id ASC
LIMIT {{top_k:UInt32}}
"""


def tokenize(query: str) -> list[str]:
    """Reduce a free-text query to at most ``_MAX_TOKENS`` bindable tokens."""
    seen: list[str] = []
    for match in _TOKEN_RE.findall(query or ""):
        lowered = match.lower()
        if lowered not in [s.lower() for s in seen]:
            seen.append(match)
        if len(seen) >= _MAX_TOKENS:
            break
    return seen


class ReadStore:
    """All ClickHouse access for the MCP tools. Issues SELECTs only."""

    def __init__(self, client: ClickHouseClient, database: str = "apex") -> None:
        self._client = client
        self._database = database
        self._findings_columns: set[str] | None = None
        self._tables_present: dict[str, bool] = {}
        self._memory_tables: set[str] | None = None

    # -- per-job reads ----------------------------------------------------
    def stages(self, job_id: str) -> list[dict[str, Any]]:
        return self._query(STAGES_SQL, {"job_id": _require_job_id(job_id)})

    def findings(self, job_id: str) -> list[dict[str, Any]]:
        # Validate BEFORE the column probe, so a bad job_id costs no round trip.
        job_id = _require_job_id(job_id)
        return self._query(_findings_sql(self.findings_columns()), {"job_id": job_id})

    MAX_RUNS = 200

    def runs(
        self,
        limit: int = 20,
        since_hours: int = 168,
        app_name: str = "",
    ) -> list[dict[str, Any]]:
        """Recent runs, one row per job_id, newest first.

        The read the lane was missing: every other method needs a ``job_id``
        the user has no way to obtain from Apex.

        ``since_hours`` is not a convenience — it is the partition-pruning
        bound. Without a ``ts`` predicate this degrades to a full scan on a
        table sorted by ``job_id``. ``limit`` is clamped so a caller-supplied
        value cannot ask for the whole table.
        """
        limit = max(1, min(int(limit), self.MAX_RUNS))
        hours = max(1, int(since_hours))
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        return self._query(
            RUNS_SQL,
            {
                "since": since.strftime("%Y-%m-%d %H:%M:%S"),
                "app_name": app_name or "",
                "limit": limit,
            },
        )

    def store_health(self) -> dict[str, Any]:
        """Row count, distinct jobs and newest ts across apex.spark_events.

        ``latest_ts`` is normalised to None on an empty table: ClickHouse
        returns the zero DateTime for max() over no rows, and 1970 presented as
        a freshness reading is worse than saying nothing.

        The timestamp is the EMITTER's clock, not ingestion time — a Spark host
        with skewed time shows up here as skewed freshness.
        """
        rows = self._query(HEALTH_SQL, {})
        row = rows[0] if rows else {}
        row_count = int(row.get("row_count") or 0)
        latest = row.get("latest_ts")
        return {
            "row_count": row_count,
            "job_count": int(row.get("job_count") or 0),
            "latest_ts": latest if row_count else None,
        }

    def findings_columns(self) -> set[str]:
        """Which apex.findings columns this deployment actually has.

        The v0.2 additive columns land per-cluster whenever infra applies the
        ALTER, so serve probes once instead of assuming. Probed lazily and
        cached for the process lifetime.
        """
        if self._findings_columns is None:
            try:
                rows = self._query(
                    COLUMNS_SQL, {"database": self._database, "table": "findings"}
                )
                self._findings_columns = {str(row["name"]) for row in rows}
            except ApexStoreError:
                self._findings_columns = set()
            missing = set(_FINDINGS_ADDITIVE) - self._findings_columns
            if missing and self._findings_columns:
                log.warning(
                    "apex.findings is missing additive contract column(s): %s — "
                    "serving defaults. Apply contract/findings.ddl.sql (infra).",
                    ", ".join(sorted(missing)),
                )
        return self._findings_columns

    def plan_transitions(self, job_id: str) -> list[dict[str, Any]]:
        return self._query(
            PLAN_TRANSITIONS_SQL, {"job_id": _require_job_id(job_id)}
        )

    MAX_VERIFICATIONS = 100

    def verifications(
        self, job_id: str, finding_id: str = "", limit: int = 50
    ) -> list[dict[str, Any]]:
        """What the verify lane concluded about this run's proposed fixes.

        Newest first, optionally narrowed to one finding. Serve reports these
        rows; it never recomputes the judgement they carry.

        Returns ``[]`` — not an error — on a deployment whose
        ``apex.fix_verifications`` has not been applied yet. The v0.3 tables
        are ADDITIVE, so an older cluster must degrade to "no verification
        available" rather than fail a tool call it never used to fail.
        """
        # Validate BEFORE the table probe, so a bad job_id costs no round trip.
        job_id = _require_job_id(job_id)
        finding_id = _require_optional_id(finding_id, "finding_id")
        if not self.table_exists("fix_verifications"):
            return []
        return self._query(
            VERIFICATIONS_SQL,
            {
                "job_id": job_id,
                "finding_id": finding_id,
                "limit": max(1, min(int(limit), self.MAX_VERIFICATIONS)),
            },
        )

    def table_exists(self, table: str) -> bool:
        """Whether an ADDITIVE contract table is present on this deployment.

        Same shape as ``findings_columns``: probed once against
        ``system.columns`` and cached for the process lifetime, because the
        answer only changes when infra applies DDL and restarts are cheap.
        A failed probe is treated as absent — the caller degrades either way,
        and guessing "present" would turn a probe failure into a tool failure.
        """
        cached = self._tables_present.get(table)
        if cached is None:
            try:
                rows = self._query(
                    COLUMNS_SQL, {"database": self._database, "table": table}
                )
                cached = bool(rows)
            except ApexStoreError:
                cached = False
            self._tables_present[table] = cached
            if not cached:
                log.warning(
                    "%s.%s is not present on this deployment — serving empty. "
                    "It is an additive contract table; apply it via the infra "
                    "lane to enable the feature that reads it.",
                    self._database,
                    table,
                )
        return cached

    # -- cross-run memory (contract v0.3 additive) -------------------------
    def memory_tables_present(self) -> bool:
        """Does this deployment carry the v0.3 cross-run memory tables?

        Probed once and cached, exactly like the additive findings columns.
        A cluster without them is a normal older deployment, so the answer is
        reported rather than raised — the tools turn it into "cross-run memory
        is unavailable on this deployment", which a user can act on.
        """
        if self._memory_tables is None:
            try:
                rows = self._query(
                    TABLES_SQL,
                    {"database": self._database, "names": list(MEMORY_TABLES)},
                )
            except ApexStoreError as exc:
                # A store that could not be REACHED has told us nothing about
                # which tables it carries. Swallowing that here would turn an
                # outage into a confident architectural statement — "this
                # deployment has no cross-run memory" — and the caller would
                # never learn ClickHouse was down. Proven live: the probe runs
                # before every recall, so this short-circuited the guard in
                # _recall and made an unreachable store answer "no neighbours".
                if str(exc).startswith("clickhouse_unavailable"):
                    raise
                self._memory_tables = set()
            else:
                self._memory_tables = {str(row["name"]) for row in rows}
            missing = set(MEMORY_TABLES) - self._memory_tables
            if missing:
                log.warning(
                    "cross-run memory unavailable: %s absent on this deployment "
                    "— apply memory/sql/030_plan_memory.sql and "
                    "031_run_outcomes.sql (infra), then run the memory lane's "
                    "indexer.",
                    ", ".join(f"{self._database}.{name}" for name in sorted(missing)),
                )
        return not (set(MEMORY_TABLES) - self._memory_tables)

    def similar_plans(
        self,
        plan_fingerprint: str,
        top_k: int = 10,
        min_similarity: float = MIN_SIMILARITY,
    ) -> list[dict[str, Any]]:
        """Plan shapes structurally similar to ``plan_fingerprint``.

        Returns other fingerprints ranked by cosine similarity, gated on
        ``min_similarity``. Empty is a real answer: it means nothing in memory
        resembles this shape, which is more useful than the nearest unrelated
        plan.
        """
        if not plan_fingerprint or not self.memory_tables_present():
            return []
        return self._recall(
            SIMILAR_PLANS_SQL,
            {
                "fingerprint": plan_fingerprint,
                "min_similarity": max(0.0, min(float(min_similarity), 1.0)),
                "top_k": max(1, min(int(top_k), MAX_SIMILAR_PLANS)),
            },
        )

    def prior_outcomes(
        self,
        fingerprints: list[str],
        exclude_job_id: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Runs of the given plan shapes, newest first, with their configs.

        ``exclude_job_id`` drops the run being asked about: a run is not its
        own prior.
        """
        fingerprints = [fp for fp in dict.fromkeys(fingerprints or []) if fp]
        if not fingerprints or not self.memory_tables_present():
            return []
        return self._recall(
            PRIOR_OUTCOMES_SQL,
            {
                "fingerprints": fingerprints,
                "exclude_job_id": exclude_job_id or "",
                "limit": max(1, min(int(limit), MAX_PRIOR_RUNS)),
            },
        )

    def _recall(self, sql: str, parameters: dict[str, Any]) -> list[dict[str, Any]]:
        """Run a memory read, degrading to empty when the tables are absent.

        Only a table that is REALLY GONE degrades, and absence is confirmed by
        re-probing rather than inferred from the error text. ``_sanitize``
        routes on the exception's class name, and the driver's generic class is
        ``DatabaseError`` — so nearly every server-side error arrives labelled
        ``clickhouse_schema_missing``. Trusting that label was enough to
        swallow a genuine SQL fault and report it as "no prior runs", which is
        the one lie this lane can least afford. Proven live: it masked a code
        125 for an entire session, and poisoned the probe cache so every later
        recall claimed cross-run memory was unavailable.
        """
        try:
            return self._query(sql, parameters)
        except ApexStoreError as exc:
            if not str(exc).startswith("clickhouse_schema_missing"):
                raise
            self._memory_tables = None  # force a fresh probe, do not trust the label
            if self.memory_tables_present():
                raise
            log.warning(
                "cross-run memory read degraded to empty: %s", exc, exc_info=False
            )
            return []

    # -- search -----------------------------------------------------------
    def search(self, tokens: list[str], top_k: int) -> list[dict[str, Any]]:
        if not tokens:
            return []
        top_k = max(1, min(int(top_k), 50))
        names = [f"t{i}" for i in range(len(tokens))]
        params: dict[str, Any] = dict(zip(names, tokens))
        params["top_k"] = top_k
        rows = self._query(_findings_search_sql(names), params)
        rows += self._query(_plans_search_sql(names), params)
        return rows

    # -- console reads (ported from the browser) ---------------------------
    MAX_SHAPES = 50
    MAX_BASELINE_CANDIDATES = 20

    def run(self, job_id: str) -> dict[str, Any] | None:
        """One run's rollup row, or None when the job_id is unknown.

        None rather than a zero-filled row on purpose: the console renders a
        synthesised zero as a real but empty run, which is a claim the store
        never made.
        """
        return next(
            iter(self._query(RUN_ONE_SQL, {"job_id": _require_job_id(job_id)})), None
        )

    def run_list(self, limit: int = 50) -> list[dict[str, Any]]:
        """Recent runs in the CONSOLE's rollup shape, newest first.

        Not ``runs()``. That one projects app_id, first_ts, last_ts,
        spill_disk_bytes and worst_p99_ms for the MCP's RunSummary; the console
        needs task_time_ms, finding_count and the shape columns, which runs()
        does not carry. Same name, different question.

        The limit is clamped rather than trusted, and the caller is told when
        the clamp bit so a truncated page is never read as a complete one.
        """
        return self._query(
            RUN_LIST_SQL, {"limit": max(1, min(int(limit), self.MAX_RUNS))}
        )

    def fix_verification(self, finding_id: str) -> dict[str, Any] | None:
        """The verify lane's row for ONE finding, keyed on the finding alone.

        Not ``verifications()``: that requires a job_id and reports the stored
        columns, while this derives rule 2's verdict from the measured delta
        against the measured floor. Both call sites in the console have only a
        finding_id in hand.

        None when the additive table is absent or holds no row for this
        finding — the screen states the emptiness and names the lane that owes
        it, rather than showing a verdict nobody reached.
        """
        finding_id = _require_optional_id(finding_id, "finding_id")
        if not finding_id:
            raise ApexStoreError("finding_id_required: pass a non-empty finding_id.")
        if not self.table_exists("fix_verifications"):
            return None
        # cluster_slots joins run_outcomes, so THAT table is required — but
        # plan_memory is not, and demanding it hid stored verifications during
        # a partial v0.3 rollout. Gate on what this query reads, nothing else.
        if not self.table_exists("run_outcomes"):
            raise ApexStoreError(
                "memory_unavailable: apex.run_outcomes is not present on this "
                "deployment, and this verification joins it for cluster_slots. "
                "This is not an absent verification. Apply the v0.3 DDL via "
                "the infra lane."
            )
        return next(iter(self._query(FIX_VERIFICATION_SQL, {"finding_id": finding_id})), None)

    def console_stages(self, job_id: str) -> list[dict[str, Any]]:
        """Stages in the CONSOLE's projection, one row per stage.

        Not ``stages()``. That one answers the MCP's StageView, aliasing the
        timings to p50_ms/p99_ms and projecting no job_id, stage_name or ts.
        The console reads task_duration_p50_ms/p99_ms and all three of those,
        so serving one as the other gave it undefined values and NaN ratios.
        """
        return self._query(CONSOLE_STAGES_SQL, {"job_id": _require_job_id(job_id)})

    def job_conf(self, job_id: str) -> list[dict[str, Any]]:
        """This job's configuration, one row per key.

        Empty when the jar emitted no job_conf for the run. That is an absence
        of capture, not a run with no configuration.
        """
        return self._query(JOB_CONF_SQL, {"job_id": _require_job_id(job_id)})

    def baseline_candidates(self, job_id: str) -> list[dict[str, Any]]:
        """Other runs sharing at least one of this run's plan shapes."""
        self._require_memory()
        return self._query(
            BASELINE_CANDIDATES_SQL,
            {
                "job_id": _require_job_id(job_id),
                "limit": self.MAX_BASELINE_CANDIDATES,
            },
        )

    def plan_shapes(self) -> list[dict[str, Any]]:
        """Plan shapes the memory lane has indexed, most-run first."""
        self._require_memory()
        return self._query(PLAN_SHAPES_SQL, {"limit": self.MAX_SHAPES})

    def plan_sample(self, fingerprint: str) -> str | None:
        """The redacted exemplar for a shape, or None when unindexed.

        None rather than "" so a caller can tell "the memory lane has not
        reached this shape" from "this shape's plan text is empty".
        """
        self._require_memory()
        rows = self._query(
            PLAN_SAMPLE_SQL,
            {"fingerprint": _require_optional_id(fingerprint, "fingerprint")},
        )
        sample = str(rows[0].get("sample_plan_json") or "") if rows else ""
        return sample or None

    def shape_runs(self, fingerprint: str) -> list[dict[str, Any]]:
        """Every run of one shape, oldest first — the history rule 3 reads."""
        self._require_memory()
        return self._query(
            SHAPE_RUNS_SQL,
            {"fingerprint": _require_optional_id(fingerprint, "fingerprint")},
        )

    def _require_memory(self) -> None:
        """Refuse a memory read on a deployment without the v0.3 tables.

        Raised, not degraded to []. An empty list here would read as "this
        store has no history", when the truth is that it has no TABLE to hold
        one — and the caller acts differently on each.
        """
        if not self.memory_tables_present():
            raise ApexStoreError(
                "memory_unavailable: the contract v0.3 tables "
                "apex.plan_memory and apex.run_outcomes are not present on "
                "this deployment. This is not an empty history. Apply the "
                "v0.3 DDL via the infra lane and run the memory lane's indexer."
            )

    # -- plumbing ---------------------------------------------------------
    def _query(self, sql: str, parameters: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            result = self._client.query(sql, parameters=parameters)
            return [dict(row) for row in result.named_results()]
        except ApexStoreError:
            raise
        except Exception as exc:  # noqa: BLE001 — sanitize everything
            raise _sanitize(exc) from None


def _require_job_id(job_id: str) -> str:
    if not job_id or not job_id.strip():
        raise ApexStoreError("job_id_required: pass a non-empty job_id.")
    if len(job_id) > 512:
        raise ApexStoreError("job_id_too_long: job_id exceeds 512 characters.")
    return job_id


def _require_optional_id(value: str, name: str) -> str:
    """An empty optional id means "no filter"; a huge one is refused.

    The value is still BOUND, never interpolated — the bound is a resource
    guard, not the injection defense.
    """
    value = value or ""
    if len(value) > 512:
        raise ApexStoreError(f"{name}_too_long: {name} exceeds 512 characters.")
    return value


def _sanitize(exc: Exception) -> ApexStoreError:
    """Log the real failure to STDERR; hand the model an opaque code.

    Driver exceptions embed the host/user/password of the connection URL —
    forwarding one to the client would be plain info disclosure.
    """
    log.error("clickhouse query failed: %s", type(exc).__name__, exc_info=exc)
    name = type(exc).__name__.lower()
    if "operational" in name or "connect" in name or "timeout" in name:
        return ApexStoreError(
            "clickhouse_unavailable: the Apex store did not answer. "
            "Check the CLICKHOUSE_* environment of the MCP server."
        )
    if "database" in name or "table" in name:
        return ApexStoreError(
            "clickhouse_schema_missing: the apex schema is not applied. "
            "Apply contract/*.ddl.sql via the infra lane."
        )
    return ApexStoreError(
        "clickhouse_query_failed: the store rejected the query. "
        "See the server's stderr log for details."
    )


# --------------------------------------------------------------------------
# Connection factory
# --------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def get_client() -> ClickHouseClient:
    """Build the shared client from the environment.

    Deliberately lazy: the MCP server must finish ``initialize`` and list its
    tools even when ClickHouse is down, otherwise the client just reports the
    server as failed with no explanation. Connection errors surface per tool
    call, sanitized.
    """
    import clickhouse_connect

    try:
        return clickhouse_connect.get_client(
            host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
            port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
            username=os.getenv("CLICKHOUSE_USER", "apex"),
            password=os.getenv("CLICKHOUSE_PASSWORD", ""),
            database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
            secure=os.getenv("CLICKHOUSE_SECURE", "").lower()
            in {"1", "true", "yes"},
        )
    except Exception as exc:  # noqa: BLE001
        raise _sanitize(exc) from None


def get_store() -> ReadStore:
    return ReadStore(get_client())
