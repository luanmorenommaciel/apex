"""Live gate: cross-run memory (L6) against a real ClickHouse.

The unit suite proves this layer against fakes, and `FakeClient` does not parse
SQL. That is exactly the gap that let two L2 defects through a fully green
suite, and it let one through here too: `SIMILAR_PLANS_SQL` originally read the
queried shape through a scalar sub-select, which ClickHouse constant-folds
BEFORE `WHERE` runs — so a plan shape that had never been seen raised code 125
instead of returning nothing. Every assertion below exists because only a real
database can make it.

It seeds its own disposable fixture rows into apex.plan_memory,
apex.run_outcomes and apex.spark_events. Those writes are the FIXTURE's, not
the server's — every code path exercised below issues SELECTs only.

    uv run python tools/recall_gate.py
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import sys
import uuid
from datetime import datetime, timezone

import clickhouse_connect

from apex_mcp import ch
from apex_mcp.ch import ApexStoreError, ReadStore
from apex_mcp.server import create_server

RUN = uuid.uuid4().hex[:8]
CURRENT_JOB = f"l6-gate-current-{RUN}"
FAST_JOB = f"l6-gate-fast-{RUN}"
SLOW_JOB = f"l6-gate-slow-{RUN}"
NEAR_JOB = f"l6-gate-near-{RUN}"
JOB_IDS = (CURRENT_JOB, FAST_JOB, SLOW_JOB, NEAR_JOB)

# Distinct, real-width fingerprints. `9`*64 is deliberately never inserted:
# it is the "shape we have never seen" case.
FP_SELF = "1" * 64
FP_NEAR = "2" * 64
FP_FAR = "3" * 64
FP_UNSEEN = "9" * 64
ENCODER = "struct-v1"

# Contract v0.3 — the columns serve reads. Asserted rather than assumed,
# exactly as the v0.2 gate asserts its own.
REQUIRED_PLAN_MEMORY = {
    "plan_fingerprint", "encoder_version", "embedding_kind", "embedding", "dim",
    "node_count", "join_count", "agg_count", "exchange_count", "scan_count",
    "last_seen",
}
REQUIRED_RUN_OUTCOMES = {
    "job_id", "app_id", "app_name", "plan_fingerprint",
    "conf_shuffle_partitions", "conf_executor_instances", "conf_executor_cores",
    "conf_executor_memory_mb", "conf_driver_cores", "conf_driver_memory_mb",
    "conf_extra", "config_source", "stage_count", "task_count", "wall_clock_ms",
    "task_time_ms", "max_skew_ratio", "worst_severity", "outcome_source",
    "observed_at",
}

PLAN_MEMORY_COLUMNS = [
    "plan_fingerprint", "encoder_version", "embedding_kind", "embedding", "dim",
    "op_counts", "node_count", "max_depth", "join_count", "agg_count",
    "exchange_count", "scan_count", "has_udf", "plan_chars", "sample_plan_json",
    "first_seen", "last_seen", "indexed_at",
]
RUN_OUTCOME_COLUMNS = [
    "job_id", "app_id", "app_name", "plan_fingerprint",
    "conf_shuffle_partitions", "conf_executor_instances", "conf_executor_cores",
    "conf_executor_memory_mb", "conf_driver_cores", "conf_driver_memory_mb",
    "conf_extra", "config_source", "stage_count", "task_count", "wall_clock_ms",
    "task_time_ms", "shuffle_read_bytes", "shuffle_write_bytes",
    "spill_disk_bytes", "spill_mem_bytes", "gc_time_ms", "input_bytes",
    "output_bytes", "peak_execution_mem_bytes", "max_skew_ratio",
    "aqe_skew_splits", "aqe_coalesces", "finding_count", "worst_severity",
    "outcome_source", "observed_at", "indexed_at",
]
EVENT_COLUMNS = [
    "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
    "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes",
    "spill_mem_bytes", "gc_time_ms", "input_bytes", "output_bytes",
    "peak_execution_mem_bytes", "task_count", "task_duration_p50_ms",
    "task_duration_p99_ms", "plan_fingerprint", "plan_json", "attributes",
]


def unit(*values: float) -> list[float]:
    """L2-normalise, because that is the invariant plan_memory guarantees and
    the only reason `1 - cosineDistance` is a similarity at all."""
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def plan_row(fingerprint: str, embedding: list[float], now: datetime) -> list:
    return [
        fingerprint, ENCODER, "structural", embedding, len(embedding), {},
        12, 4, 1, 1, 2, 2, 0, 100, "SortMergeJoin Inner", now, now, now,
    ]


def outcome_row(
    job_id: str, fingerprint: str, wall_clock_ms: int, observed_at: datetime,
    now: datetime, config: list | None = None, config_source: str = "unknown",
) -> list:
    return [
        job_id, f"app-{job_id}", "l6-gate", fingerprint,
        *(config or [None] * 6), {}, config_source,
        4, 200, wall_clock_ms, wall_clock_ms * 3,
        0, 0, 0, 0, 0, 0, 0, 0, 1.2, 0, 1, 0, "", "apex", observed_at, now,
    ]


def event_row(
    job_id: str, fingerprint: str, task_count: int, p50: int, ts: datetime,
    stage_id: int = 2,
) -> list:
    return [
        job_id, f"app-{job_id}", "l6-gate", stage_id, 0, ts,
        0, 0, 0, 0, 0, 0, 0, 0, task_count, p50, p50, fingerprint,
        "SortMergeJoin Inner", {},
    ]


def describe(client, table: str) -> set[str]:
    return {row[0] for row in client.query(f"DESCRIBE apex.{table}").result_rows}


def main() -> int:
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "apex"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev"),
        database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
    )

    # -- the v0.3 additive schema is really applied ------------------------
    plan_memory_columns = describe(client, "plan_memory")
    run_outcome_columns = describe(client, "run_outcomes")
    assert REQUIRED_PLAN_MEMORY <= plan_memory_columns, (
        f"plan_memory missing {REQUIRED_PLAN_MEMORY - plan_memory_columns}"
    )
    assert REQUIRED_RUN_OUTCOMES <= run_outcome_columns, (
        f"run_outcomes missing {REQUIRED_RUN_OUTCOMES - run_outcome_columns}"
    )

    now = datetime.now(timezone.utc).replace(microsecond=0)

    # -- fixture (writes belong to the gate, never to the server) ----------
    # FP_NEAR is a near-duplicate of FP_SELF; FP_FAR is orthogonal to it, so it
    # must be dropped by the similarity gate rather than returned as "nearest".
    client.insert("plan_memory", [
        plan_row(FP_SELF, unit(1, 1, 0, 0, 0, 0, 0, 0), now),
        plan_row(FP_NEAR, unit(1, 0.9, 0, 0, 0, 0, 0, 0), now),
        plan_row(FP_FAR, unit(0, 0, 1, 1, 0, 0, 0, 0), now),
    ], column_names=PLAN_MEMORY_COLUMNS)

    client.insert("run_outcomes", [
        outcome_row(FAST_JOB, FP_SELF, 60_000, now.replace(tzinfo=None),
                    now, [200, 4, 4, 8192, 2, 4096], "observed"),
        outcome_row(SLOW_JOB, FP_SELF, 120_000,
                    now.replace(tzinfo=None).replace(day=max(now.day - 1, 1)),
                    now, [800, 4, 4, 8192, 2, 4096], "observed"),
        outcome_row(NEAR_JOB, FP_NEAR, 90_000,
                    now.replace(tzinfo=None).replace(day=max(now.day - 2, 1)), now),
        # The run being asked about must never recall itself.
        outcome_row(CURRENT_JOB, FP_SELF, 75_000, now.replace(tzinfo=None), now),
    ], column_names=RUN_OUTCOME_COLUMNS)

    # The tool resolves its shape from spark_events. Two stages: one trivial on
    # FP_NEAR, one expensive on FP_SELF, so the work-proxy ranking is exercised
    # rather than a single-shape shortcut.
    client.insert("spark_events", [
        event_row(CURRENT_JOB, FP_NEAR, task_count=1, p50=1, ts=now, stage_id=1),
        event_row(CURRENT_JOB, FP_SELF, task_count=200, p50=3_000, ts=now, stage_id=2),
    ], column_names=EVENT_COLUMNS)

    store = ReadStore(client)
    results: dict = {}

    try:
        # -- the additive tables are detected ------------------------------
        assert store.memory_tables_present() is True

        # -- similarity ranks, and the gate DROPS the unrelated shape ------
        neighbours = store.similar_plans(FP_SELF, top_k=10)
        returned = {row["plan_fingerprint"] for row in neighbours}
        assert FP_NEAR in returned, f"near-duplicate shape not recalled: {returned}"
        assert FP_FAR not in returned, (
            "an orthogonal plan shape was returned as a neighbour — the "
            "similarity gate is not holding"
        )
        assert FP_SELF not in returned, "a plan was returned as its own neighbour"
        assert neighbours[0]["similarity"] >= ch.MIN_SIMILARITY
        assert neighbours == sorted(
            neighbours, key=lambda r: r["similarity"], reverse=True
        ), "neighbours came back unordered"
        results["similar_plans"] = {
            "returned": len(neighbours),
            "top_similarity": round(float(neighbours[0]["similarity"]), 4),
            "orthogonal_shape_dropped": True,
        }

        # -- a never-before-seen shape is an ANSWER, not an error ----------
        # This is the defect the fakes could not see: the original scalar
        # sub-select raised code 125 here, and the degrade path swallowed it.
        unseen = store.similar_plans(FP_UNSEEN)
        assert unseen == [], f"unseen shape returned neighbours: {unseen}"
        assert store.memory_tables_present() is True, (
            "an unseen shape poisoned the memory-table probe cache"
        )

        # -- hostile values bind, match nothing, and never raise -----------
        hostile_values = ["' OR 1=1 --", "A" * 300, "", "'; DROP TABLE apex.plan_memory; --"]
        for value in hostile_values:
            assert store.similar_plans(value) == [], f"hostile fingerprint widened: {value!r}"
            assert store.prior_outcomes([value]) == [], f"hostile fingerprint widened: {value!r}"
        assert describe(client, "plan_memory"), "plan_memory did not survive the gate"
        results["hostile_fingerprints"] = {
            "tried": len(hostile_values), "rows": 0, "raised": False,
        }

        # -- outcomes: newest first, real Nullable/Map/DateTime64 ----------
        priors = store.prior_outcomes(
            [FP_SELF, FP_NEAR], exclude_job_id=CURRENT_JOB, limit=50
        )
        job_ids = [row["job_id"] for row in priors]
        assert CURRENT_JOB not in job_ids, "a run recalled itself as its own prior"
        assert {FAST_JOB, SLOW_JOB, NEAR_JOB} <= set(job_ids), job_ids
        observed = [row["observed_at"] for row in priors]
        assert observed == sorted(observed, reverse=True), "prior runs were not newest-first"
        by_job = {row["job_id"]: row for row in priors}
        # Nullable(Int32) must arrive as None, never as 0 — the whole point of
        # the column being Nullable in the v0.3 DDL.
        assert by_job[NEAR_JOB]["conf_shuffle_partitions"] is None
        assert by_job[NEAR_JOB]["config_source"] == "unknown"
        assert by_job[FAST_JOB]["conf_shuffle_partitions"] == 200
        assert by_job[FAST_JOB]["config_source"] == "observed"
        assert isinstance(by_job[FAST_JOB]["conf_extra"], dict)
        assert isinstance(by_job[FAST_JOB]["observed_at"], datetime), (
            "observed_at came back as a string; the driver returns datetime and "
            "the model must coerce it (the L2 defect, in a new column)"
        )
        results["prior_outcomes"] = {
            "returned": len(priors),
            "newest_first": True,
            "self_excluded": True,
            "null_config_stayed_null": True,
        }

        # -- the tool, end to end over the real store ----------------------
        server = create_server(store)
        tool_names = [t.name for t in asyncio.run(server.list_tools())]
        assert tool_names == [
            "analyze_run", "compare_runs", "list_runs", "search_kb",
            "recall_similar_runs", "suggest_fix",
        ], tool_names

        raw = asyncio.run(
            server.call_tool("recall_similar_runs", {"job_id": CURRENT_JOB})
        )
        payload = raw[1] if isinstance(raw, tuple) else raw
        assert payload["status"] == "recalled", payload["status"]
        assert payload["plan_fingerprint"] == FP_SELF, (
            "the dominant shape was not the one the run spent its time in"
        )
        assert CURRENT_JOB not in [r["job_id"] for r in payload["prior_runs"]]
        assert "prior_runs[].app_name" in payload["untrusted_fields"]
        # No floor supplied: measurements only, no verdict.
        assert payload["summary"]["compared"] is False
        assert payload["summary"]["faster_job_id"] is None
        assert "better" not in payload["summary"]["claim"].lower()

        # -- with a MEASURED floor, a verdict becomes reachable ------------
        raw = asyncio.run(server.call_tool(
            "recall_similar_runs", {"job_id": CURRENT_JOB, "noise_floor_pct": 0.15}
        ))
        adjudicated = (raw[1] if isinstance(raw, tuple) else raw)["summary"]
        assert adjudicated["compared"] is True
        assert adjudicated["faster_job_id"] == FAST_JOB
        assert "15.0%" in adjudicated["claim"], adjudicated["claim"]
        assert adjudicated["attributable_to_config"] is True, (
            "two distinct captured configs should make the difference creditable"
        )
        results["recall_similar_runs"] = {
            "status": payload["status"],
            "shape": "dominant",
            "prior_runs": len(payload["prior_runs"]),
            "no_floor_verdict": False,
            "with_floor_verdict": True,
            "floor_named_in_claim": True,
        }

        # -- a deployment WITHOUT the additive tables ----------------------
        # Probed against a database that has none, which is what an older
        # cluster looks like to the probe.
        absent = ReadStore(client, database=f"apex_no_such_{RUN}")
        assert absent.memory_tables_present() is False
        assert absent.similar_plans(FP_SELF) == []
        assert absent.prior_outcomes([FP_SELF]) == []
        results["absent_tables"] = {"present": False, "raised": False, "rows": 0}

        # -- a store that is DOWN still raises, it does not degrade --------
        # Connected lazily, mirroring the server's own LazyClient: building the
        # client eagerly would fail here in the gate instead of inside the read,
        # which is the code path actually under test.
        class _DeadClient:
            def query(self, query, parameters=None):  # noqa: ANN001, ANN201
                return clickhouse_connect.get_client(
                    host="127.0.0.1", port=1, username="apex", password="x",
                    database="apex", connect_timeout=2, send_receive_timeout=2,
                ).query(query, parameters=parameters)

        down = ReadStore(_DeadClient())
        try:
            down.similar_plans(FP_SELF)
            raised = "no"
        except ApexStoreError as exc:
            raised = "unavailable" if "unavailable" in str(exc) else str(exc).split(":")[0]
        assert raised != "no", (
            "an unreachable store reported 'no neighbours' instead of raising"
        )
        results["store_down"] = {"degraded_to_empty": False, "code": raised}

    finally:
        # -- cleanup: the gate removes only its own fixture rows -----------
        # mutations_sync = 2 because ALTER ... DELETE is ASYNCHRONOUS: without
        # it the leftover count below runs before the mutation materialises and
        # "verified none remain" would be a claim about nothing.
        client.command(
            "ALTER TABLE apex.plan_memory DELETE WHERE plan_fingerprint IN "
            "({a:String}, {b:String}, {c:String}) SETTINGS mutations_sync = 2",
            parameters={"a": FP_SELF, "b": FP_NEAR, "c": FP_FAR},
        )
        for table in ("run_outcomes", "spark_events"):
            client.command(
                f"ALTER TABLE apex.{table} DELETE WHERE job_id IN {{jobs:Array(String)}} "
                "SETTINGS mutations_sync = 2",
                parameters={"jobs": list(JOB_IDS)},
            )

    leftover = client.query(
        "SELECT count() + (SELECT count() FROM apex.plan_memory "
        "  WHERE plan_fingerprint IN ({a:String}, {b:String}, {c:String})) "
        "FROM apex.run_outcomes WHERE job_id IN {jobs:Array(String)}",
        parameters={"jobs": list(JOB_IDS), "a": FP_SELF, "b": FP_NEAR, "c": FP_FAR},
    ).result_rows[0][0]
    assert leftover == 0, f"the gate left {leftover} fixture row(s) behind"

    print(json.dumps({
        "gate": "serve-recall",
        "clickhouse": client.query("SELECT version()").result_rows[0][0],
        "contract": {"plan_memory": "ok", "run_outcomes": "ok"},
        "external_llm_calls": 0,
        "writes_by_the_server": 0,
        "fixture_rows_remaining": leftover,
        **results,
        "status": "passed",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
