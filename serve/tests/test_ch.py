"""ClickHouse layer: binding, latest-attempt SQL, additive columns, tokens."""

from __future__ import annotations

import pytest

from apex_mcp import ch
from apex_mcp.ch import ApexStoreError, ReadStore
from tests.conftest import FakeClient, finding_row, stage_row


def test_every_query_uses_server_side_binding():
    client = FakeClient(stages={"j": [stage_row()]}, findings={"j": []})
    store = ReadStore(client)
    store.stages("j")
    store.findings("j")
    store.plan_transitions("j")
    for sql, parameters in client.calls:
        if "system.columns" in sql:
            continue
        assert "{job_id:String}" in sql
        assert parameters["job_id"] == "j"


def test_latest_attempt_uses_argmax_for_every_metric():
    """A plain GROUP BY would mix attempt 0's spill with attempt 1's p99."""
    sql = ch.STAGES_SQL
    for column in (
        "stage_attempt", "shuffle_read_bytes", "shuffle_write_bytes",
        "spill_disk_bytes", "spill_mem_bytes", "gc_time_ms", "input_bytes",
        "output_bytes", "peak_execution_mem_bytes", "task_count",
        "task_duration_p50_ms", "task_duration_p99_ms", "plan_fingerprint",
    ):
        assert f"argMax({column}, ts)" in sql or f"argMax(toString({column}), ts)" in sql
    assert "GROUP BY stage_id" in sql


def test_additive_columns_are_projected_when_present():
    client = FakeClient(findings={"j": [finding_row()]})
    store = ReadStore(client)
    store.findings("j")
    sql = client.calls[-1][0]
    assert "app_id" in sql
    assert "confidence_score" in sql
    assert "'' AS app_id" not in sql


def test_missing_additive_columns_degrade_to_defaults_instead_of_failing():
    """A cluster whose ALTER has not landed yet must still serve."""
    client = FakeClient(
        findings={"j": [finding_row()]},
        columns=["finding_id", "job_id", "stage_id", "type", "severity",
                 "evidence", "hot_key", "impact", "fix", "confidence",
                 "detected_by", "ts"],
    )
    store = ReadStore(client)
    store.findings("j")
    sql = client.calls[-1][0]
    assert "'' AS app_id" in sql
    assert "toFloat64(0) AS confidence_score" in sql


def test_column_probe_happens_once_and_is_cached():
    client = FakeClient(findings={"j": []})
    store = ReadStore(client)
    store.findings("j")
    store.findings("j")
    store.findings("j")
    probes = [c for c in client.calls if "system.columns" in c[0]]
    assert len(probes) == 1


def test_search_binds_every_token_and_clamps_top_k():
    client = FakeClient(search=[])
    store = ReadStore(client)
    store.search(["spill", "shuffle"], top_k=9999)
    _, parameters = client.calls[-1]
    assert parameters["t0"] == "spill"
    assert parameters["t1"] == "shuffle"
    assert parameters["top_k"] == 50  # clamped


def test_search_with_no_tokens_issues_no_query():
    client = FakeClient()
    assert ReadStore(client).search([], 5) == []
    assert client.calls == []


def test_search_covers_findings_and_plan_text():
    client = FakeClient(search=[])
    ReadStore(client).search(["spill"], 5)
    queried = " ".join(sql for sql, _ in client.calls)
    assert "apex.findings" in queried
    assert "apex.spark_events" in queried


@pytest.mark.parametrize(
    "query,expected",
    [
        ("shuffle spill", ["shuffle", "spill"]),
        ("SPILL spill Spill", ["SPILL"]),           # de-duped case-insensitively
        ("a bb ccc", ["bb", "ccc"]),                 # single chars dropped
        ("spark.sql.adaptive.enabled", ["spark.sql.adaptive.enabled"]),
        ("", []),
        ("!!! ???", []),
    ],
)
def test_tokenize(query, expected):
    assert ch.tokenize(query) == expected


def test_tokenize_caps_the_token_count():
    assert len(ch.tokenize(" ".join(f"tok{i}" for i in range(50)))) == 8


def test_blank_job_id_never_reaches_the_database():
    client = FakeClient()
    with pytest.raises(ApexStoreError, match="job_id_required"):
        ReadStore(client).findings("")
    assert client.calls == []


# --------------------------------------------------------------------------
# store_health — the one read not keyed by job_id
# --------------------------------------------------------------------------
class OperationalError(Exception):
    """Name-shaped like the driver's, since _sanitize routes on the class name."""


class _HealthClient:
    """Local double: FakeClient routes on job_id, and health has none.

    Defined here rather than in conftest so this task stays inside its
    declared blast radius.
    """

    def __init__(self, rows: list[dict] | None = None, raises: Exception | None = None):
        self.rows = rows if rows is not None else []
        self.raises = raises
        self.calls: list[tuple[str, dict]] = []

    def query(self, query: str, parameters: dict | None = None):
        self.calls.append((query, parameters or {}))
        if self.raises:
            raise self.raises
        return type("R", (), {"named_results": lambda _self: list(self.rows)})()


def test_store_health_reports_counts_and_freshness():
    store = ReadStore(
        _HealthClient([{"row_count": 17, "job_count": 3, "latest_ts": "2026-08-17T10:00:00"}])
    )

    health = store.store_health()

    assert health["row_count"] == 17
    assert health["job_count"] == 3
    assert health["latest_ts"] == "2026-08-17T10:00:00"


def test_store_health_on_empty_table_is_zeros_and_no_timestamp():
    """ClickHouse returns the zero DateTime for max() over no rows; 1970 is
    not a freshness reading, so an empty store reports None instead."""
    store = ReadStore(
        _HealthClient([{"row_count": 0, "job_count": 0, "latest_ts": "1970-01-01T00:00:00"}])
    )

    health = store.store_health()

    assert health == {"row_count": 0, "job_count": 0, "latest_ts": None}


def test_store_health_on_unreachable_store_raises_sanitized():
    store = ReadStore(_HealthClient(raises=OperationalError("connect refused to 10.0.0.5")))

    with pytest.raises(ApexStoreError) as excinfo:
        store.store_health()

    assert "clickhouse_unavailable" in str(excinfo.value)
    assert "10.0.0.5" not in str(excinfo.value)


def test_store_health_sql_is_bound_not_interpolated():
    store = ReadStore(_HealthClient([{"row_count": 0, "job_count": 0, "latest_ts": None}]))
    store.store_health()

    sql, parameters = store._client.calls[0]  # noqa: SLF001 — asserting the wire
    assert "{" not in sql
    assert parameters == {}
    assert "apex.spark_events" in sql



# --------------------------------------------------------------------------
# runs() — the read that does not need a job_id
# --------------------------------------------------------------------------
def _run_row(job_id: str = "job-1", app_name: str = "nightly_etl", stages: int = 4) -> dict:
    return {
        "job_id": job_id,
        "app_id": f"app-{job_id}",
        "app_name": app_name,
        "first_ts": "2026-08-19T09:00:00",
        "last_ts": "2026-08-19T09:12:00",
        "stage_count": stages,
        "spill_disk_bytes": 0,
        "worst_p99_ms": 410,
    }


def test_runs_aggregates_one_row_per_job():
    """B-1 — one row per job_id, not one per stage."""
    client = _HealthClient([_run_row("job-a"), _run_row("job-b")])
    store = ReadStore(client)

    runs = store.runs()

    assert [r["job_id"] for r in runs] == ["job-a", "job-b"]
    assert runs[0]["stage_count"] == 4
    sql, _ = client.calls[0]
    assert "GROUP BY job_id" in sql
    assert "ORDER BY last_ts DESC" in sql


def test_runs_filters_by_app_name():
    """B-2 — the filter reaches the query as a bound parameter."""
    client = _HealthClient([_run_row(app_name="nightly_etl")])
    store = ReadStore(client)

    store.runs(app_name="nightly_etl")

    sql, parameters = client.calls[0]
    assert parameters["app_name"] == "nightly_etl"
    assert "{app_name:String}" in sql
    assert "nightly_etl" not in sql


def test_runs_binds_hostile_app_name():
    """B-4 — a SQL fragment binds as data; it never reaches the statement."""
    hostile = "' OR 1=1 --"
    client = _HealthClient([])
    store = ReadStore(client)

    runs = store.runs(app_name=hostile)

    assert runs == []
    sql, parameters = client.calls[0]
    assert parameters["app_name"] == hostile
    assert hostile not in sql


def test_runs_bounds_the_scan_on_ts():
    """B-3 — without a ts predicate this is a full scan on a job_id-sorted table."""
    client = _HealthClient([])
    store = ReadStore(client)

    store.runs(since_hours=24)

    sql, parameters = client.calls[0]
    assert "ts >= {since:DateTime}" in sql
    assert parameters["since"]


def test_runs_clamps_a_caller_supplied_limit():
    """B-3 — a caller must not be able to ask for the whole table."""
    client = _HealthClient([])
    store = ReadStore(client)

    store.runs(limit=10_000)

    _, parameters = client.calls[0]
    assert parameters["limit"] == ReadStore.MAX_RUNS


# --------------------------------------------------------------------------
# Cross-run memory — apex.plan_memory + apex.run_outcomes (contract v0.3)
#
# These are ADDITIVE tables, so the double has to model three deployments: one
# that carries them, one that does not, and one that raises the schema error
# mid-read. FakeClient routes on job_id and neither table is keyed by one, so
# the double lives here rather than in conftest.
# --------------------------------------------------------------------------
FP_SELF = "1" * 64
FP_NEAR = "2" * 64
FP_FAR = "3" * 64


class TableError(Exception):
    """Name-shaped like the driver's, so _sanitize routes it to schema_missing."""


class _MemoryClient:
    def __init__(
        self,
        *,
        plans: list[dict] | None = None,
        outcomes: list[dict] | None = None,
        tables: tuple[str, ...] = ("plan_memory", "run_outcomes"),
        raises: Exception | None = None,
        tables_raises: Exception | None = None,
    ) -> None:
        self.plans = plans or []
        self.outcomes = outcomes or []
        self.tables = tables
        self.raises = raises
        self.tables_raises = tables_raises
        self.calls: list[tuple[str, dict]] = []

    def query(self, query: str, parameters: dict | None = None):
        self.calls.append((query, parameters or {}))
        if "system.tables" in query:
            if self.tables_raises:
                raise self.tables_raises
            rows = [{"name": name} for name in self.tables]
            return type("R", (), {"named_results": lambda _s: rows})()
        if self.raises:
            raise self.raises
        rows = self.outcomes if "apex.run_outcomes" in query else self.plans
        return type("R", (), {"named_results": lambda _s: list(rows)})()


def _plan_row(fingerprint: str, similarity: float) -> dict:
    return {
        "plan_fingerprint": fingerprint,
        "similarity": similarity,
        "node_count": 12,
        "join_count": 1,
        "agg_count": 1,
        "exchange_count": 2,
        "scan_count": 2,
        "last_seen": "2026-08-19T09:00:00",
    }


def _outcome_row(job_id: str, wall_clock_ms: int, observed_at: str) -> dict:
    return {
        "job_id": job_id,
        "app_id": f"app-{job_id}",
        "app_name": "nightly_etl",
        "plan_fingerprint": FP_SELF,
        "conf_shuffle_partitions": 200,
        "conf_executor_instances": 4,
        "conf_executor_cores": 4,
        "conf_executor_memory_mb": 8192,
        "conf_driver_cores": 2,
        "conf_driver_memory_mb": 4096,
        "conf_extra": {},
        "config_source": "observed",
        "stage_count": 4,
        "task_count": 200,
        "wall_clock_ms": wall_clock_ms,
        "task_time_ms": wall_clock_ms * 3,
        "shuffle_read_bytes": 0,
        "shuffle_write_bytes": 0,
        "spill_disk_bytes": 0,
        "spill_mem_bytes": 0,
        "gc_time_ms": 0,
        "input_bytes": 0,
        "output_bytes": 0,
        "peak_execution_mem_bytes": 0,
        "max_skew_ratio": 1.2,
        "aqe_skew_splits": 0,
        "aqe_coalesces": 1,
        "finding_count": 0,
        "worst_severity": "",
        "outcome_source": "apex",
        "observed_at": observed_at,
    }


def test_similar_plans_ranks_by_cosine_distance():
    """B-1 — neighbours come back ranked, gated on a minimum similarity."""
    client = _MemoryClient(plans=[_plan_row(FP_NEAR, 0.94), _plan_row(FP_FAR, 0.83)])
    store = ReadStore(client)

    neighbours = store.similar_plans(FP_SELF, top_k=5)

    assert [n["plan_fingerprint"] for n in neighbours] == [FP_NEAR, FP_FAR]
    sql, parameters = client.calls[-1]
    assert "cosineDistance" in sql
    assert "ORDER BY similarity DESC" in sql
    assert parameters["min_similarity"] == ch.MIN_SIMILARITY
    assert parameters["top_k"] == 5
    # The queried shape is excluded — a plan is not its own neighbour.
    assert "plan_fingerprint != toFixedString" in sql


def test_similar_plans_reads_the_embedding_width_instead_of_assuming_one():
    """The encoder's width is the memory lane's to change; serve matches on the
    shape's own `dim` rather than hardcoding a number.

    The match rides on the JOIN key, not a scalar sub-select — see
    test_similar_plans_joins_the_queried_shape_rather_than_sub_selecting_it.
    """
    client = _MemoryClient(plans=[])
    ReadStore(client).similar_plans(FP_SELF)

    sql, parameters = client.calls[-1]
    assert "p.dim = s.dim" in sql
    assert not any(key.startswith("dim") for key in parameters)


def test_similar_plans_joins_the_queried_shape_rather_than_sub_selecting_it():
    """Proven live on ClickHouse 24.8: a scalar sub-select is constant-folded
    BEFORE the WHERE clause runs, so reading the queried shape that way raises
    code 125 ("scalar subquery returned empty result of type Array(Float32)
    which cannot be Nullable") for any fingerprint absent from plan_memory.

    A plan shape nobody has run before is an ordinary answer, not an error, so
    the shape is INNER JOINed: no match simply yields no rows.
    """
    sql = ch.SIMILAR_PLANS_SQL

    assert "INNER JOIN" in sql
    assert "(SELECT embedding FROM" not in sql
    assert "cosineDistance(p.embedding, s.embedding)" in sql


def test_similar_plans_clamps_a_caller_supplied_top_k():
    client = _MemoryClient(plans=[])
    ReadStore(client).similar_plans(FP_SELF, top_k=10_000)

    _, parameters = client.calls[-1]
    assert parameters["top_k"] == ch.MAX_SIMILAR_PLANS


def test_prior_outcomes_returns_configs_newest_first():
    """B-2 — runs of the given shapes, with their config columns and wall clock."""
    client = _MemoryClient(
        outcomes=[
            _outcome_row("job-new", 60_000, "2026-08-19T09:00:00"),
            _outcome_row("job-old", 90_000, "2026-08-12T09:00:00"),
        ]
    )
    store = ReadStore(client)

    runs = store.prior_outcomes([FP_SELF, FP_NEAR], exclude_job_id="job-current")

    assert [r["job_id"] for r in runs] == ["job-new", "job-old"]
    assert runs[0]["conf_shuffle_partitions"] == 200
    assert runs[0]["config_source"] == "observed"
    assert runs[0]["wall_clock_ms"] == 60_000
    sql, parameters = client.calls[-1]
    assert "ORDER BY observed_at DESC" in sql
    assert parameters["fingerprints"] == [FP_SELF, FP_NEAR]
    assert parameters["exclude_job_id"] == "job-current"


def test_prior_outcomes_never_orders_by_wall_clock():
    """Ranking prior runs by duration would pre-declare a winner, which is the
    one claim CONTRACT.md rule 2 forbids without a measured floor."""
    assert "ORDER BY wall_clock_ms" not in ch.PRIOR_OUTCOMES_SQL
    assert "ORDER BY task_time_ms" not in ch.PRIOR_OUTCOMES_SQL


def test_plan_memory_binds_hostile_fingerprint():
    """B-4 — a SQL fragment binds as data, matches nothing, and never raises."""
    hostile = "' OR 1=1 --"
    client = _MemoryClient(plans=[], outcomes=[])
    store = ReadStore(client)

    assert store.similar_plans(hostile) == []
    assert store.prior_outcomes([hostile]) == []

    for sql, parameters in client.calls:
        assert hostile not in sql
    bound = [p for _, p in client.calls if "fingerprint" in p or "fingerprints" in p]
    assert bound[0]["fingerprint"] == hostile
    assert bound[1]["fingerprints"] == [hostile]
    # A value longer than 64 chars would make toFixedString THROW, so the
    # statement caps it before the cast rather than trusting the caller.
    assert "substring({fingerprint:String}, 1, 64)" in ch.SIMILAR_PLANS_SQL


def test_plan_memory_absent_tables_degrade(caplog):
    """B-3 — a deployment without the v0.3 tables returns empty and logs."""
    client = _MemoryClient(tables=())
    store = ReadStore(client)

    with caplog.at_level("WARNING", logger="apex_mcp.ch"):
        assert store.similar_plans(FP_SELF) == []
        assert store.prior_outcomes([FP_SELF]) == []

    assert store.memory_tables_present() is False
    assert "cross-run memory unavailable" in caplog.text
    # Absent means absent: neither read reached the table.
    assert all("apex.plan_memory" not in sql for sql, _ in client.calls)
    assert all("apex.run_outcomes" not in sql for sql, _ in client.calls)


def test_schema_error_degrades_only_when_the_tables_really_are_gone(caplog):
    """B-3 — the probe can pass and the read still hit a dropped table."""
    client = _MemoryClient(raises=TableError("apex.run_outcomes doesn't exist"))
    store = ReadStore(client)
    store.memory_tables_present()          # probe while they are still there
    client.tables = ()                     # ...and now they are not

    with caplog.at_level("WARNING", logger="apex_mcp.ch"):
        assert store.prior_outcomes([FP_SELF]) == []

    assert "degraded to empty" in caplog.text


def test_a_schema_shaped_error_on_present_tables_still_raises():
    """The masking bug, as a test.

    `_sanitize` routes on the exception's CLASS NAME, and the driver's generic
    class is `DatabaseError` — so nearly every server-side fault arrives
    labelled `clickhouse_schema_missing`. Trusting that label swallowed a real
    code 125 for an entire live session and reported it as "no prior runs".
    Absence is now confirmed by re-probing, not inferred from the message.
    """
    client = _MemoryClient(raises=TableError("some other server-side fault"))
    store = ReadStore(client)

    with pytest.raises(ApexStoreError):
        store.prior_outcomes([FP_SELF])


def test_an_unreachable_store_raises_from_the_probe_too():
    """The probe runs before every recall, so degrading there short-circuits
    the guard in _recall entirely. Proven live: an unreachable ClickHouse
    answered "cross-run memory is unavailable on this deployment", which is a
    confident architectural claim about a store that never replied.
    """
    client = _MemoryClient(tables_raises=OperationalError("connect refused to 10.0.0.5"))
    store = ReadStore(client)

    with pytest.raises(ApexStoreError) as excinfo:
        store.similar_plans(FP_SELF)

    assert "clickhouse_unavailable" in str(excinfo.value)
    assert "10.0.0.5" not in str(excinfo.value)


def test_memory_read_still_raises_when_the_store_is_down():
    """Degrading on an OUTAGE would report "no prior runs" for a store that was
    simply unreachable — a lie in the one place this lane cannot afford one."""
    client = _MemoryClient(raises=OperationalError("connect refused to 10.0.0.5"))
    store = ReadStore(client)

    with pytest.raises(ApexStoreError) as excinfo:
        store.prior_outcomes([FP_SELF])

    assert "clickhouse_unavailable" in str(excinfo.value)
    assert "10.0.0.5" not in str(excinfo.value)


def test_memory_table_probe_happens_once_and_is_cached():
    client = _MemoryClient(plans=[])
    store = ReadStore(client)
    store.similar_plans(FP_SELF)
    store.similar_plans(FP_NEAR)
    store.prior_outcomes([FP_SELF])

    probes = [c for c in client.calls if "system.tables" in c[0]]
    assert len(probes) == 1


def test_memory_reads_short_circuit_on_empty_input():
    client = _MemoryClient()
    store = ReadStore(client)

    assert store.similar_plans("") == []
    assert store.prior_outcomes([]) == []
    assert client.calls == []
