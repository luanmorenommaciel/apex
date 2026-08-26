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
# verifications() — the v0.3 ADDITIVE table the verify lane owns
# --------------------------------------------------------------------------
class _VerificationsClient:
    """Serves the fix_verifications read plus its table probe.

    Local to this module rather than in conftest, so this task stays inside
    its declared blast radius. ``columns_rows`` is what ``system.columns``
    returns for the probe: an empty list means the table does not exist on
    this deployment, which is the whole point of B-3.
    """

    def __init__(
        self,
        rows: list[dict] | None = None,
        columns_rows: list[dict] | None = None,
    ) -> None:
        self.rows = rows if rows is not None else []
        self.columns_rows = (
            columns_rows
            if columns_rows is not None
            else [{"name": "verification_id"}, {"name": "finding_id"}]
        )
        self.calls: list[tuple[str, dict]] = []

    def query(self, query: str, parameters: dict | None = None):
        self.calls.append((query, parameters or {}))
        payload = (
            self.columns_rows if "system.columns" in query else list(self.rows)
        )
        return type("R", (), {"named_results": lambda _self: list(payload)})()

    @property
    def reads(self) -> list[tuple[str, dict]]:
        """Calls that are not the table probe."""
        return [c for c in self.calls if "system.columns" not in c[0]]


def _verification_row(
    verification_id: str = "v-1",
    finding_id: str = "finding-1",
    *,
    method: str = "predicted",
    verified_at: str = "2026-08-20T10:00:00.000",
) -> dict:
    return {
        "verification_id": verification_id,
        "finding_id": finding_id,
        "job_id": "job-1",
        "app_id": "app-job-1",
        "proposed_config": '{"spark.sql.shuffle.partitions": "200"}',
        "method": method,
        "predictor": "partition_sizing",
        "predicted_delta_pct": -18.0,
        "predicted_low_pct": -25.0,
        "predicted_high_pct": -8.0,
        "measured_delta_pct": None,
        "baseline_ms": None,
        "treatment_ms": None,
        "noise_floor_pct": None,
        "replay_reps": 0,
        "bench": "",
        "shape_fidelity": 0.0,
        "safe": 1,
        "safety_verdict": "allow",
        "safety_detail": "",
        "confidence": "MEDIUM",
        "confidence_score": 0.62,
        "evidence": "tail share 0.41; partition sizing model",
        "caveats": "not replayed",
        "verify_version": "0.3.0",
        "verified_at": verified_at,
    }


def test_verifications_returns_rows_newest_first():
    """B-1 — the verdict fields the user needs, ordered by the store."""
    client = _VerificationsClient(
        [
            _verification_row("v-new", verified_at="2026-08-20T10:00:00.000"),
            _verification_row("v-old", verified_at="2026-08-19T10:00:00.000"),
        ]
    )
    store = ReadStore(client)

    rows = store.verifications("job-1")

    assert [r["verification_id"] for r in rows] == ["v-new", "v-old"]
    first = rows[0]
    for column in (
        "method", "predictor", "predicted_delta_pct", "predicted_low_pct",
        "predicted_high_pct", "measured_delta_pct", "safety_verdict",
        "confidence", "confidence_score",
    ):
        assert column in first, column
    sql, parameters = client.reads[0]
    assert "ORDER BY verified_at DESC" in sql
    assert parameters["job_id"] == "job-1"


def test_verifications_filters_by_finding_id():
    """B-2 — the narrowing reaches the query as a bound parameter."""
    client = _VerificationsClient([_verification_row(finding_id="finding-7")])
    store = ReadStore(client)

    store.verifications("job-1", finding_id="finding-7")

    sql, parameters = client.reads[0]
    assert parameters["finding_id"] == "finding-7"
    assert "{finding_id:String}" in sql
    assert "finding-7" not in sql


def test_verifications_without_a_finding_id_binds_the_empty_no_filter():
    """One statement, one bound parameter — no unbound second query text."""
    client = _VerificationsClient([])
    ReadStore(client).verifications("job-1")

    _, parameters = client.reads[0]
    assert parameters["finding_id"] == ""


def test_verifications_absent_table_degrades():
    """B-3 — the v0.3 tables are additive; an older cluster must not error."""
    client = _VerificationsClient([_verification_row()], columns_rows=[])
    store = ReadStore(client)

    assert store.verifications("job-1") == []
    assert client.reads == []  # probed, then gave up — never queried the table


def test_verifications_probes_the_absent_table_only_once():
    client = _VerificationsClient([], columns_rows=[])
    store = ReadStore(client)

    store.verifications("job-1")
    store.verifications("job-1")
    store.verifications("job-2")

    probes = [c for c in client.calls if "system.columns" in c[0]]
    assert len(probes) == 1
    assert probes[0][1] == {"database": "apex", "table": "fix_verifications"}


def test_verifications_binds_hostile_finding_id():
    """B-4 — a SQL fragment binds as data; it never reaches the statement."""
    hostile = "' OR 1=1 --"
    client = _VerificationsClient([])
    store = ReadStore(client)

    assert store.verifications("job-1", finding_id=hostile) == []
    sql, parameters = client.reads[0]
    assert parameters["finding_id"] == hostile
    assert hostile not in sql


def test_verifications_blank_job_id_never_reaches_the_database():
    client = _VerificationsClient([])
    with pytest.raises(ApexStoreError, match="job_id_required"):
        ReadStore(client).verifications("")
    assert client.calls == []


def test_verifications_clamps_a_caller_supplied_limit():
    client = _VerificationsClient([])
    ReadStore(client).verifications("job-1", limit=10_000)

    _, parameters = client.reads[0]
    assert parameters["limit"] == ReadStore.MAX_VERIFICATIONS
