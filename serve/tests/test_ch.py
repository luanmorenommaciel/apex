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

