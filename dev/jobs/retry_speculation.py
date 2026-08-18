"""Phase A baseline: induce one retry or one speculative task without changing APEX.

The job deliberately prints only the effective Spark settings needed to interpret
the run. It never prints credentials or the complete SparkConf.
"""

from __future__ import annotations

import json
import os
import sys
import time

from pyspark import TaskContext

sys.path.insert(0, "/opt/apex")

from common.session import build_session  # noqa: E402


MODE = os.environ.get("APEX_PHASE_A_MODE", "").strip().lower()
PARTITIONS = int(os.environ.get("APEX_PHASE_A_PARTITIONS", "8"))
SLOW_PARTITION = int(os.environ.get("APEX_PHASE_A_SLOW_PARTITION", "0"))
SLEEP_SECONDS = float(os.environ.get("APEX_PHASE_A_SLEEP_SECONDS", "30"))
POST_ACTION_SLEEP_SECONDS = float(
    os.environ.get("APEX_PHASE_A_POST_ACTION_SLEEP_SECONDS", "10")
)

EFFECTIVE_CONF_KEYS = (
    "spark.speculation",
    "spark.speculation.interval",
    "spark.speculation.multiplier",
    "spark.speculation.quantile",
    "spark.speculation.minTaskRuntime",
    "spark.speculation.efficiency.enabled",
    "spark.task.maxFailures",
    "spark.executor.cores",
    "spark.default.parallelism",
)


def retry_once(partition_id, values):
    context = TaskContext.get()
    if partition_id == SLOW_PARTITION and context.attemptNumber() == 0:
        raise RuntimeError("apex_phase_a_induced_retry")
    yield from values


def speculative_straggler(partition_id, values):
    context = TaskContext.get()
    if partition_id == SLOW_PARTITION and context.attemptNumber() == 0:
        time.sleep(SLEEP_SECONDS)
    yield from values


def main() -> int:
    if MODE not in {"retry", "speculation"}:
        raise ValueError("APEX_PHASE_A_MODE must be retry or speculation")
    if PARTITIONS < 4:
        raise ValueError("APEX_PHASE_A_PARTITIONS must be at least 4")
    if not 0 <= SLOW_PARTITION < PARTITIONS:
        raise ValueError("APEX_PHASE_A_SLOW_PARTITION is outside the partition range")

    extra_conf = {
        "spark.sql.adaptive.enabled": "false",
        "spark.default.parallelism": str(PARTITIONS),
        "spark.task.maxFailures": "4",
        "spark.speculation": "true" if MODE == "speculation" else "false",
    }
    if MODE == "speculation":
        extra_conf.update(
            {
                "spark.speculation.interval": "100ms",
                "spark.speculation.multiplier": "1.5",
                "spark.speculation.quantile": "0.5",
                "spark.speculation.minTaskRuntime": "100ms",
                "spark.speculation.efficiency.enabled": "false",
            }
        )

    spark, job_id, app_id, app_name = build_session(
        f"apex-phase-a-{MODE}", extra_conf
    )
    effective_conf = {
        key: spark.sparkContext.getConf().get(key, "<unset>")
        for key in EFFECTIVE_CONF_KEYS
    }
    print(
        "APEX_PHASE_A_EFFECTIVE_CONF "
        + json.dumps(effective_conf, sort_keys=True),
        flush=True,
    )

    transform = retry_once if MODE == "retry" else speculative_straggler
    count = (
        spark.sparkContext
        .parallelize(range(PARTITIONS), PARTITIONS)
        .mapPartitionsWithIndex(transform)
        .count()
    )
    # Let Spark publish the loser TaskEnd before the driver closes its event log.
    # This is test harness timing only; it does not alter listener behavior.
    if MODE == "speculation" and POST_ACTION_SLEEP_SECONDS > 0:
        time.sleep(POST_ACTION_SLEEP_SECONDS)
    print(
        "APEX_PHASE_A_RESULT "
        + json.dumps(
            {
                "app_id": app_id,
                "job_id": job_id,
                "mode": MODE,
                "partitions": PARTITIONS,
                "rows": count,
                "slow_partition": SLOW_PARTITION,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
