"""T12 — DRIVER OOM. Pull a multi-GB result to a 512m driver via collect().

spark.driver.memory MUST be set at SUBMIT time (--driver-memory 512m): the driver
JVM heap is fixed when spark-submit launches it, so setting it in-code is too late.
`make run-pathology JOB=driver_oom` passes it automatically.

Pre-collect telemetry survives: a real shuffle stage runs and COMPLETES before the
fatal collect(), and the JVM StageListener writes each stage record to
out/spark_events.jsonl the instant the stage completes — so the OOM never loses the
telemetry for stages that already ran. spark.stop() never runs (driver crashes), so
the event log stays `.inprogress` and the History Server entry is INCOMPLETE — that
is the correct, expected outcome for a driver OOM.

  APEX_SAFE=on → collect only a small sample instead of OOMing.
                 (make run-pathology JOB=driver_oom SAFE=on)
"""
import os
import sys

sys.path.insert(0, "/opt/apex")

from common.session import build_session          # noqa: E402
from common.listener import attach, set_plan      # noqa: E402
from common.data import ensure_data, FACT_PATH     # noqa: E402


def main() -> int:
    safe = os.environ.get("APEX_SAFE", "off").lower() == "on"
    # NOTE: driver.memory is NOT set here (too late) — it comes from --driver-memory.
    # maxResultSize=0 (unlimited) so collect() truly materializes the result and the
    # 512m driver OOMs, rather than Spark's result-size guard aborting with a different error.
    spark, job_id, app_id, app_name = build_session(
        f"apex-driver_oom{'-safe' if safe else ''}",
        {"spark.sql.adaptive.enabled": "false", "spark.driver.maxResultSize": "0"})
    listener = attach(spark, job_id, app_id, app_name)
    ensure_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)

    # (1) A real shuffle stage that COMPLETES before the fatal collect — its listener
    #     record is flushed to disk, proving pre-OOM telemetry is not lost.
    pre = fact.groupBy("join_key").count()
    set_plan(listener, pre)
    ngroups = len(pre.collect())               # small result (~10k keys) — safe
    print(f"APEX_JOB driver_oom precollect_stage_done groups={ngroups}", flush=True)

    # (2) Inflate each row and spread across many partitions so each task result is
    #     small enough to deserialize, but the driver accumulates the multi-GB total
    #     into its 512m heap → a clean OutOfMemoryError (Java heap space) on collect.
    big = fact.repartition(200).selectExpr("*", "repeat('x', 512) as payload")
    if safe:
        sample = big.limit(1000).collect()
        print(f"APEX_JOB driver_oom SAFE sampled_rows={len(sample)}", flush=True)
        spark.stop()
        return 0

    print("APEX_JOB driver_oom collecting multi-GB to a 512m driver (expect OOM)...", flush=True)
    rows = big.collect()                       # OOM here
    print(f"APEX_JOB driver_oom collected={len(rows)} (did NOT OOM — raise payload/rows)", flush=True)
    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
