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
