"""P1 probe: one extreme task in a real 200-task Spark stage.

This is deliberately not a root-cause simulation. It isolates the telemetry
question that a hot-key join cannot guarantee on every machine: nearest-rank
p99 may stay healthy while one task holds the stage open.
"""

import os
import sys
import time

sys.path.insert(0, "/opt/apex")

from common.session import build_session  # noqa: E402


def slow_one_partition(partition_index, values):
    if partition_index == 0:
        time.sleep(float(os.environ.get("APEX_TAIL_SLEEP_SECONDS", "20")))
    yield from values


def main() -> int:
    partitions = int(os.environ.get("APEX_TAIL_PARTITIONS", "200"))
    spark, job_id, app_id, app_name = build_session(
        "apex-tail-outlier",
        {
            "spark.sql.adaptive.enabled": "false",
            "spark.default.parallelism": str(partitions),
        },
    )

    count = (
        spark.sparkContext
        .parallelize(range(partitions), partitions)
        .mapPartitionsWithIndex(slow_one_partition)
        .count()
    )
    print(
        f"APEX_JOB tail_outlier app_id={app_id} partitions={partitions} rows={count}",
        flush=True,
    )
    spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
