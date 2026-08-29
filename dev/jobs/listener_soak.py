"""Controlled, non-production soak workload for one long-lived Spark driver.

It deliberately uses small repeated shuffle jobs.  The driver stays alive for
all cycles, which makes listener cleanup observable without changing the plugin
or the production pathology workloads.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, "/opt/apex")

from common.session import build_session  # noqa: E402


def positive_int(name: str, default: int) -> int:
    value = int(os.environ.get(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def main() -> int:
    cycles = positive_int("APEX_SOAK_CYCLES", 60)
    records = positive_int("APEX_SOAK_RECORDS", 20000)
    partitions = positive_int("APEX_SOAK_PARTITIONS", 8)
    spark, job_id, app_id, _ = build_session(
        "apex-driver-listener-soak",
        {"spark.sql.adaptive.enabled": "false", "spark.sql.shuffle.partitions": str(partitions)},
    )
    sc = spark.sparkContext
    started = time.monotonic()
    try:
        for cycle in range(1, cycles + 1):
            total = (
                sc.parallelize(range(records), partitions)
                .map(lambda value: (value % 97, value))
                .reduceByKey(lambda left, right: left + right)
                .values()
                .sum()
            )
            # Only progress metadata; never credentials, plans or input rows.
            print(f"APEX_SOAK cycle={cycle}/{cycles} aggregate={int(total)}", flush=True)
    finally:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        print(
            f"APEX_SOAK_COMPLETE cycles={cycles} elapsed_ms={elapsed_ms} "
            f"job_id={job_id} app_id={app_id}",
            flush=True,
        )
        spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
