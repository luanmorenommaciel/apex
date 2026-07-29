"""Real data, not invented data.

Every number here was read out of the live stack on the feat/base-project-e2e
branch and is reproducible:

  * findings / spark_events  -> apex ClickHouse (infra lane, :8123)
  * effective SparkConf      -> Spark History Server REST
                                /api/v1/applications/app-20260724160310-0000/environment
                                (captured pre-v0.4; the primary source is now
                                apex.job_conf — see apex_verify.config_source)
  * slots                    -> dev/.env SPARK_WORKER_CORES=2, one worker

The sibling runs `…161143-0001` and `…163620-0002` are byte-identical replays of
`…160310-0000` (same query, same conf, `sum(shuffle_read_bytes)` equal to the
byte across all three), which is what makes them a legitimate noise sample.
"""

from __future__ import annotations

from apex_verify.models import FindingRef, StageObservation

# ── the exit-criterion finding, verbatim from apex.findings ─────────────────
FINDING_SKEW_STAGE4 = FindingRef(
    finding_id="189e3495-585f-4295-a29c-6853c53897d7",
    job_id="app-20260724160310-0000",
    app_id="app-20260724160310-0000",
    stage_id=4,
    type="SKEW_ON_JOIN",
    severity="critical",
    evidence="p99/p50 = 21.62x on stage 4 (p99=454ms, p50=21ms, 50 tasks)",
    fix=(
        "Enable AQE skew join (spark.sql.adaptive.skewJoin.enabled=true); if the "
        "hot key survives that, salt it or broadcast the small side."
    ),
    confidence_score=0.88,
    detected_by="skew_watcher",
)

# The config `engine`'s fix text proposes.
PROPOSED_CONFIG_SKEW = {"spark.sql.adaptive.skewJoin.enabled": "true"}

# Stage 4 as stored. plan_json is the redacted Catalyst tree-string: a Delta
# transaction-log aggregate over a LogicalRDD — note there is no Join node.
STAGE4_OBSERVED = StageObservation(
    stage_id=4,
    task_count=50,
    task_duration_p50_ms=21,
    task_duration_p99_ms=454,
    shuffle_read_bytes=0,
    shuffle_write_bytes=4750,
    input_bytes=9163,
    spill_disk_bytes=0,
    plan_fingerprint="6b4fb76dc1eee8d66b3a2b060811694c7c28cdef196405d2ca693079ee3212f6",
    plan_json=(
        "!Aggregate [collect_set(none#5, 0, 0) AS #0, null AS #1, "
        "collect_set(none#0, 0, 0) AS #2, count(none#4) AS #4L]\n"
        "+- Project [none#0, none#1, none#2, none#3, none#4, none#8]\n"
        "   +- LogicalRDD [none#0, none#1, none#2, none#3, none#4], false\n"
    ),
)

# The same stage in the two sibling runs — the noise sample.
STAGE4_SIBLINGS = [
    STAGE4_OBSERVED,
    STAGE4_OBSERVED.model_copy(update={"task_duration_p50_ms": 17, "task_duration_p99_ms": 420}),
    STAGE4_OBSERVED.model_copy(update={"task_duration_p50_ms": 15, "task_duration_p99_ms": 368}),
]

# max(ts) - min(ts) over stage_attempt=0 rows, per run.
JOB_RUNTIMES_MS = [9277.0, 8262.0, 8832.0]
JOB_RUNTIME_MS = 9277.0

# ── stage 26: where the ACTUAL join lives ('Join Inner in the plan) ─────────
# 1335/733 = 1.82x, under engine's 5x threshold, so it was never flagged — while
# stages 2 and 4 (Delta metadata) were flagged critical.
STAGE26_REAL_JOIN = StageObservation(
    stage_id=26,
    task_count=2,
    task_duration_p50_ms=733,
    task_duration_p99_ms=1335,
    shuffle_read_bytes=10752890,
    shuffle_write_bytes=99820,
    input_bytes=0,
    spill_disk_bytes=390465,
    plan_fingerprint="9c5f738025347939555b8bd7820d68b293ad1a7dde24ef18144ab1255310783a",
    plan_json=(
        "'Aggregate [count(null) AS #0L]\n+- 'Aggregate [none#0]\n"
        "   +- 'Project [none#2]\n      +- 'Join Inner, (none#1L = cast(none#0 as bigint))\n"
    ),
)

# ── effective SparkConf of the observed run, from the History Server ────────
OBSERVED_CONFIG = {
    "spark.sql.adaptive.advisoryPartitionSizeInBytes": "8m",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.forceOptimizeSkewedJoin": "false",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "16m",
    "spark.sql.autoBroadcastJoinThreshold": "-1",
}

SLOTS = 2  # dev/.env SPARK_WORKER_CORES=2, single worker

# ── a synthetic stage where the mechanism IS plausible ─────────────────────
# Needed to exercise the branches that sit *after* the mechanism check. No real
# stage in the current lab qualifies — which is itself the dev-lane calibration
# finding: at 5M rows the join stages are either KB-scale metadata work or
# AQE-coalesced down to 2 tasks. 50 tasks x 10 MiB with a Join node is the shape
# a genuine skew finding would need.
PLAUSIBLE_REDUCE_STAGE = StageObservation(
    stage_id=104,
    task_count=50,
    task_duration_p50_ms=800,
    task_duration_p99_ms=17_000,
    shuffle_read_bytes=50 * (10 << 20),
    shuffle_write_bytes=0,
    input_bytes=0,
    spill_disk_bytes=64 << 20,
    plan_fingerprint="f" * 64,
    plan_json="'Aggregate [count(1)]\n+- 'Join Inner, (none#1L = none#0L)\n",
)
