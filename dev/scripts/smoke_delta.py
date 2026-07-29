"""Apex dev-env smoke probe — proves Delta write/read on MinIO + event-log emission.

This is NOT a pathology job; it is the health check that `make verify` runs to prove the
cluster works end to end. The real reusable SparkSession factory is common/session.py (T5);
this stays deliberately minimal and self-contained so verify has no dependency on job code.
"""
import sys
from pyspark.sql import SparkSession

APP_NAME = "apex-smoke"
SMOKE_PATH = "s3a://warehouse/_smoke"


def main() -> int:
    # master + Delta/S3A/eventlog config come from spark-submit + spark-defaults.conf.
    spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
    sc = spark.sparkContext
    print(f"APEX_SMOKE app_id={sc.applicationId}", flush=True)

    df = spark.range(0, 100).withColumnRenamed("id", "n")
    df.write.format("delta").mode("overwrite").save(SMOKE_PATH)
    count = spark.read.format("delta").load(SMOKE_PATH).count()
    print(f"APEX_SMOKE delta_roundtrip_count={count}", flush=True)
    if count != 100:
        print(f"APEX_SMOKE FAILED expected=100 got={count}", flush=True)
        spark.stop()
        return 1

    # stop() finalizes the event log (drops .inprogress) so the History Server lists it.
    spark.stop()
    print("APEX_SMOKE ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
