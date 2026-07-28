"""T5 — SparkSession factory + contract job_id.

Delta / S3A / event-log config live in conf/spark-defaults.conf (mounted into every
Spark service), so this factory stays thin: it names the app, applies any per-job
overrides (pathology jobs turn AQE off here, never in the base conf), mints the
contract trace key `job_id`, and stashes it in `spark.apex.job_id` for downstream.
"""
from __future__ import annotations

import os
import time
from typing import Optional
from pyspark.sql import SparkSession

JOB_ID_KEY = "spark.apex.job_id"

# Measured 2026-07-28: without a pre-stop drain, fast lab apps (~20 s) lose their
# whole OTLP export ~2/3 of the time (zero spark_events rows in ClickHouse,
# collector error-free) — the plugin's bounded queue is still draining when the
# driver JVM exits. A short sleep before spark.stop() makes delivery reliable.
# Root fix belongs to the jar lane's shutdown flush; this keeps the lab honest.
OTLP_DRAIN_SECONDS = float(os.environ.get("APEX_OTLP_DRAIN_SECONDS", "5"))


def stop_session(spark: SparkSession) -> None:
    """spark.stop() with a pre-stop OTLP drain window (see OTLP_DRAIN_SECONDS)."""
    time.sleep(OTLP_DRAIN_SECONDS)
    spark.stop()


def build_session(app_name: str = "apex-dev-job",
                  extra_conf: Optional[dict] = None) -> tuple[SparkSession, str, str, str]:
    """Return (spark, job_id, app_id, app_name).

    job_id = `spark.apex.job_id` if provided at submit (stable id when the
    applicationId isn't), else the Spark applicationId — the contract trace key,
    constant for the whole run. It is stashed back into `spark.apex.job_id`.
    """
    builder = SparkSession.builder.appName(app_name)
    for k, v in (extra_conf or {}).items():
        builder = builder.config(k, v)
    spark = builder.getOrCreate()

    app_id = spark.sparkContext.applicationId
    # override wins; otherwise the applicationId is the trace key.
    job_id = spark.conf.get(JOB_ID_KEY, None) or app_id
    spark.conf.set(JOB_ID_KEY, job_id)

    print(f"APEX_SESSION job_id={job_id} app_id={app_id} app_name={app_name}", flush=True)
    return spark, job_id, app_id, app_name
