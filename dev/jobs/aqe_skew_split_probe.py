"""C4 calibration probe matching the JAR's AQE transition test shape.

This is deliberately independent from the Delta business job: it answers one
narrow runtime question, namely whether Spark 4.1.2 emits an observable AQE
skew-split transition through ``apex.ApexPlugin``.
"""
import sys

from pyspark.sql import SparkSession


def main() -> int:
    spark = (SparkSession.builder
        .appName("apex-aqe-skew-split-probe")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.adaptive.skewJoin.enabled", "true")
        .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "16")
        .config("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2")
        .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64")
        .config("spark.sql.autoBroadcastJoinThreshold", "-1")
        .config("spark.sql.shuffle.partitions", "16")
        .getOrCreate())
    try:
        app_id = spark.sparkContext.applicationId
        spark.conf.set("spark.apex.job_id", app_id)
        left = spark.range(0, 100000).selectExpr(
            "CASE WHEN id < 90000 THEN 1 ELSE id END AS k", "id AS v1")
        right = spark.range(0, 100000).selectExpr("id AS k", "id AS v2")
        rows = left.join(right, "k").count()
        print(f"APEX_AQE_PROBE app_id={app_id} rows={rows}", flush=True)
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
