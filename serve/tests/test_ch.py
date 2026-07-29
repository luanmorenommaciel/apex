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
