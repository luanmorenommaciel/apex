"""T6 — SparkListener → one contract record per completed stage (the 19 fields).

The record-building runs JVM-side (jvm/StageListener.java), attached from here. A
pure-Python py4j SparkListener is unreliable under Spark 4.0's py4j ClientServer
gateway — JVM→Python callbacks on the async listener bus refuse ("Error while
obtaining a new communication channel / Connection refused"). A JVM listener is
invoked in-process by Spark, so it is robust; Python only makes Python→JVM calls
(construct, register, setPlan), which always work. Mirrors the jar's ApexStageListener.

Each completed stage → one line in out/spark_events.jsonl (host-visible; what
`make logs-check` reads), with plan_fingerprint/plan_json from set_plan().
"""
from __future__ import annotations

# The 19 contract fields, in contract order — used by the harness to validate records.
CONTRACT_FIELDS = (
    "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
    "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes", "spill_mem_bytes",
    "gc_time_ms", "input_bytes", "output_bytes", "peak_execution_mem_bytes",
    "task_count", "task_duration_p50_ms", "task_duration_p99_ms",
    "plan_fingerprint", "plan_json",
)

DEFAULT_OUT = "/opt/apex/out/spark_events.jsonl"


def attach(spark, job_id, app_id, app_name, out_path: str = DEFAULT_OUT):
    """Construct + register the JVM apexdev.StageListener; return it (call setPlan on it)."""
    jl = spark._jvm.apexdev.StageListener(job_id, app_id, app_name, out_path)
    spark.sparkContext._jsc.sc().addSparkListener(jl)
    return jl


def set_plan(listener, df) -> None:
    """Compute the current query's fingerprint + redacted plan_json and hand them to
    the listener, which attaches them to every stage record it emits next."""
    from common.fingerprint import plan_fingerprint, redacted_plan_json
    listener.setPlan(plan_fingerprint(df), redacted_plan_json(df))
