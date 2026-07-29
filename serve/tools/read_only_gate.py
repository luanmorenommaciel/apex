"""Live gate: contract conformance + all four tools against a real ClickHouse.

Complements the unit suite (which uses fakes) by proving the parts only a real
database can prove: that the contract DDL is actually applied, that server-side
binding works against the real parser, and that `argMax` really does pick the
latest attempt when a stage has more than one.

It seeds its own disposable fixture rows. Those writes are the FIXTURE's, not
the server's — every MCP code path exercised below issues SELECTs only.

    uv run python tools/read_only_gate.py
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone

import clickhouse_connect

from apex_mcp import ch, diagnose
from apex_mcp.ch import ReadStore

RUN = uuid.uuid4().hex[:8]
BEFORE_JOB_ID = f"serve-gate-before-{RUN}"
AFTER_JOB_ID = f"serve-gate-after-{RUN}"
FINGERPRINT_A = "a" * 64
FINGERPRINT_B = "b" * 64

# Contract v0.2 — the columns serve depends on. The additive ones are checked
# separately because a cluster may not have had the ALTER applied yet.
REQUIRED_SPARK_EVENTS = {
    "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
    "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes",
    "spill_mem_bytes", "gc_time_ms", "input_bytes", "output_bytes",
    "peak_execution_mem_bytes", "task_count", "task_duration_p50_ms",
    "task_duration_p99_ms", "plan_fingerprint", "plan_json",
}
REQUIRED_FINDINGS = {
    "finding_id", "job_id", "stage_id", "type", "severity", "evidence",
    "hot_key", "impact", "fix", "confidence", "detected_by", "ts",
}
ADDITIVE_FINDINGS = {"app_id", "confidence_score"}
REQUIRED_PLAN_TRANSITIONS = {
    "job_id", "execution_id", "update_seq", "transition_type", "detail",
    "before", "after", "confidence", "ts",
}

EVENT_COLUMNS = [
    "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
    "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes",
    "spill_mem_bytes", "gc_time_ms", "input_bytes", "output_bytes",
    "peak_execution_mem_bytes", "task_count", "task_duration_p50_ms",
    "task_duration_p99_ms", "plan_fingerprint", "plan_json", "attributes",
]


def event_row(
    job_id, *, stage_id=2, attempt=0, p50=100, p99=100, spill_disk=0,
    spill_mem=0, fingerprint=FINGERPRINT_A, plan="SortMergeJoin Inner", ts=None,
):
    return [
        job_id, f"app-{job_id}", "serve-gate", stage_id, attempt,
        ts or datetime.now(timezone.utc),
        1_000_000, 1_000_000, spill_disk, spill_mem, 0, 1_000_000, 0, 0, 50,
        p50, p99, fingerprint, plan, {},
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

    # -- T2: the contract schema is really applied -------------------------
    events_columns = describe(client, "spark_events")
    findings_columns = describe(client, "findings")
    transitions_columns = describe(client, "plan_transitions")
    assert REQUIRED_SPARK_EVENTS <= events_columns, (
        f"spark_events missing {REQUIRED_SPARK_EVENTS - events_columns}"
    )
    assert REQUIRED_FINDINGS <= findings_columns, (
        f"findings missing {REQUIRED_FINDINGS - findings_columns}"
    )
    assert REQUIRED_PLAN_TRANSITIONS <= transitions_columns, (
        f"plan_transitions missing {REQUIRED_PLAN_TRANSITIONS - transitions_columns}"
    )
    additive_present = sorted(ADDITIVE_FINDINGS & findings_columns)

    # -- fixture (writes belong to the gate, never to the server) ----------
    now = datetime.now(timezone.utc)
    older = now.replace(microsecond=0)
    client.insert(
        "spark_events",
        [
            # Baseline: clean. TWO attempts of stage 2 — attempt 1 is newer and
            # is the one argMax must win with; attempt 0 carries poison values.
            event_row(BEFORE_JOB_ID, attempt=0, p50=100, p99=9_999,
                      spill_disk=999_999_999, ts=older),
            event_row(BEFORE_JOB_ID, attempt=1, p50=100, p99=110, ts=now),
            event_row(BEFORE_JOB_ID, stage_id=7, fingerprint=FINGERPRINT_B, ts=now),
            # Current: stage 2 now spills badly and the tail blows out.
            event_row(AFTER_JOB_ID, p50=100, p99=5_000, ts=now,
                      spill_disk=512 * 1024 * 1024, spill_mem=1024 * 1024 * 1024),
            event_row(AFTER_JOB_ID, stage_id=7, fingerprint="c" * 64, ts=now),
        ],
        column_names=EVENT_COLUMNS,
    )

    finding_columns = [
        "finding_id", "job_id", "stage_id", "type", "severity", "evidence",
        "hot_key", "impact", "fix", "confidence", "detected_by", "ts",
    ]
    finding_values = [
        f"serve-gate-finding-{RUN}", AFTER_JOB_ID, 2, "SPILL", "critical",
        "shuffle spill of 512MiB on stage 2", "",
        "stage runtime dominated by disk I/O",
        "raise spark.sql.adaptive.advisoryPartitionSizeInBytes", "HIGH",
        "spill_watcher", now,
    ]
    if "confidence_score" in findings_columns:
        finding_columns.append("confidence_score")
        finding_values.append(0.91)
    if "app_id" in findings_columns:
        finding_columns.append("app_id")
        finding_values.append(f"app-{AFTER_JOB_ID}")
    client.insert("findings", [finding_values], column_names=finding_columns)

    client.insert(
        "plan_transitions",
        [[AFTER_JOB_ID, 1, 0, "skew_split", "AQEShuffleRead skewed x4",
          "1 skewed", "4 skewed", "HIGH", now]],
        column_names=["job_id", "execution_id", "update_seq", "transition_type",
                      "detail", "before", "after", "confidence", "ts"],
    )

    store = ReadStore(client)

    # -- T3: argMax really picks the latest attempt ------------------------
    baseline_stages = {row["stage_id"]: row for row in store.stages(BEFORE_JOB_ID)}
    stage_2 = baseline_stages[2]
    assert stage_2["stage_attempt"] == 1, "argMax did not pick the latest attempt"
    assert stage_2["p99_ms"] == 110, f"mixed attempts: p99={stage_2['p99_ms']}"
    assert stage_2["spill_disk_bytes"] == 0, "spill leaked from the older attempt"

    # a job_id carrying a quote must bind, not break
    assert store.stages("' OR 1=1 --") == []

    # -- the four tools ----------------------------------------------------
    diagnosis = diagnose.analyze(
        AFTER_JOB_ID, store.stages(AFTER_JOB_ID), store.findings(AFTER_JOB_ID),
        store.plan_transitions(AFTER_JOB_ID),
    )
    assert diagnosis.status == "degraded"
    assert diagnosis.worst_stage_id == 2
    assert any(s.ground_truth for s in diagnosis.symptoms), "skew_split not applied"

    self_comparison = diagnose.compare(
        BEFORE_JOB_ID, BEFORE_JOB_ID,
        store.stages(BEFORE_JOB_ID), store.stages(BEFORE_JOB_ID),
        store.findings(BEFORE_JOB_ID), store.findings(BEFORE_JOB_ID),
    )
    assert self_comparison.status == "unchanged"
    assert self_comparison.regressions == []

    comparison = diagnose.compare(
        BEFORE_JOB_ID, AFTER_JOB_ID,
        store.stages(BEFORE_JOB_ID), store.stages(AFTER_JOB_ID),
        store.findings(BEFORE_JOB_ID), store.findings(AFTER_JOB_ID),
    )
    assert comparison.status == "regressed"
    assert any("spill_introduced" in r for r in comparison.regressions)
    assert any("plan_fingerprint_changed" in r for r in comparison.regressions)
    assert any("finding_introduced" in r for r in comparison.regressions)

    tokens = ch.tokenize("shuffle spill")
    hits = diagnose.build_hits("shuffle spill", tokens, store.search(tokens, 5), 5)
    assert hits.total >= 1, "seeded spill remediation note not found"

    suggestion = diagnose.suggest_fix(
        AFTER_JOB_ID, None, 0.75, store.findings(AFTER_JOB_ID),
        store.stages(AFTER_JOB_ID), store.plan_transitions(AFTER_JOB_ID),
    )
    assert suggestion.applied is False
    assert suggestion.requires_human_approval is True
    assert suggestion.source == "findings_table"
    assert suggestion.proposed_diff

    gated = diagnose.suggest_fix(
        AFTER_JOB_ID, None, 0.999, store.findings(AFTER_JOB_ID),
        store.stages(AFTER_JOB_ID), store.plan_transitions(AFTER_JOB_ID),
    )
    assert gated.gated is True and gated.proposed_diff == ""

    # -- cleanup: the gate removes only its own fixture rows ---------------
    for table in ("spark_events", "findings", "plan_transitions"):
        client.command(
            f"ALTER TABLE apex.{table} DELETE WHERE job_id IN "
            "({before:String}, {after:String})",
            parameters={"before": BEFORE_JOB_ID, "after": AFTER_JOB_ID},
        )

    print(json.dumps({
        "gate": "serve-read-only",
        "contract": {
            "spark_events": "ok",
            "findings": "ok",
            "plan_transitions": "ok",
            "findings_additive_columns_present": additive_present,
        },
        "latest_attempt_per_stage": {
            "attempts_seeded": 2,
            "attempt_selected": stage_2["stage_attempt"],
            "p99_ms": stage_2["p99_ms"],
            "argMax": "ok",
        },
        "external_llm_calls": 0,
        "tools": {
            "analyze_run": {
                "status": diagnosis.status,
                "worst_stage_id": diagnosis.worst_stage_id,
                "primary_symptom": diagnosis.primary_symptom,
                "aqe_ground_truth": len(diagnosis.aqe_ground_truth),
            },
            "compare_runs": {
                "self_vs_self": self_comparison.status,
                "before_vs_after": comparison.status,
                "regressions": len(comparison.regressions),
                "finding_deltas": len(comparison.findings),
            },
            "search_kb": {"query": "shuffle spill", "hits": hits.total},
            "suggest_fix": {
                "source": suggestion.source,
                "confidence": suggestion.confidence,
                "applied": suggestion.applied,
                "requires_human_approval": suggestion.requires_human_approval,
                "gated_at_0_999": gated.gated,
            },
        },
        "status": "passed",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
