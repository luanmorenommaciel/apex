"""
Synthetic data-skew workload: hot-key sort-merge join (ground truth for the skew detector).

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/skew_join.py

Execution sequence:
1. Load lakehouse configuration from YAML and skew_join parameters from the catalog.
2. Create a Spark session with skew-exhibiting extra_conf (AQE off, broadcast off,
   fixed shuffle partitions) and app name `workload-skew`.
3. Generate a fact table where one hot key owns ~90% of the rows (hash-based,
   fully deterministic) and a dimension too large to broadcast.
4. Sort-merge join fact with dimension: the hot key hashes into a single shuffle
   partition, producing one straggler task among the fixed 24.
5. Materialize through the `noop` sink (full computation, no storage side effects).
6. Stop the Spark session.

Tuning lives in workloads/catalog.py (env overrides: WORKLOAD_ROWS,
WORKLOAD_HOT_KEY_RATIO, WORKLOAD_SHUFFLE_PARTITIONS, ...).
"""

from pyspark.sql import functions as F

from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger
from workloads.catalog import SkewJoinParams, describe, load_params

APP_NAME = "workload-skew"
WORKLOAD_NAME = "skew_join"


def build_fact(spark, params: SkewJoinParams):
    """Step 3a: fact rows where the hot key owns ~hot_key_ratio of all rows.

    Key assignment is a pure function of the row id (no randomness):
    - rows with `id % 100 < hot_key_ratio * 100` get the hot key;
    - the remainder are spread evenly over the other dimension keys.
    A 32-char payload per repeat gives the shuffled rows enough weight for
    the hot task to run multiple seconds even at local scale.
    """
    hot_pct = int(round(params.hot_key_ratio * 100))
    join_key = (
        F.when(F.pmod(F.col("id"), F.lit(100)) < F.lit(hot_pct), F.lit(params.hot_key))
        .otherwise(F.lit(1) + F.pmod(F.col("id"), F.lit(params.dim_rows - 1)))
        .cast("long")
        .alias("join_key")
    )
    payload = F.repeat(F.md5(F.col("id").cast("string")), params.payload_repeat).alias("payload")
    return spark.range(0, params.rows, 1, params.input_partitions).select(
        F.col("id"), join_key, payload
    )


def build_dim(spark, params: SkewJoinParams):
    """Step 3b: dimension with one row per join key (ids 0..dim_rows-1).

    dim_rows is large enough that broadcasting would be unreasonable even if
    autoBroadcastJoinThreshold were not already disabled, so the join stays a
    shuffle (sort-merge) join on both sides.
    """
    return spark.range(0, params.dim_rows, 1, params.input_partitions).select(
        F.col("id").alias("join_key"),
        F.md5(F.col("id").cast("string")).alias("dim_attr"),
    )


def build_skewed_join(spark, params: SkewJoinParams):
    """Step 4: inner join whose hot shuffle partition dominates the stage."""
    return build_fact(spark, params).join(build_dim(spark, params), "join_key", "inner")


def main() -> int:
    """
    Run the skew workload.

    1. Load lakehouse configuration and skew_join catalog parameters.
    2. Create a Spark session with skew-exhibiting extra_conf.
    3. Build the hot-key fact and non-broadcastable dimension.
    4. Sort-merge join them (one straggler task among 24).
    5. Materialize through the `noop` sink.
    6. Stop the Spark session.
    """
    params = load_params(WORKLOAD_NAME)
    logger.info(f"Starting {APP_NAME} with parameters: {describe(params)}")
    logger.info(f"{APP_NAME} extra_conf: {params.spark_conf()}")

    def body(spark, _config) -> int:
        joined = build_skewed_join(spark, params)
        joined.write.format("noop").mode("overwrite").save()
        logger.info(f"Completed {APP_NAME}: skewed join materialized via noop sink")
        return 0

    return run_spark_app(APP_NAME, body, extra_conf=params.spark_conf())


# Run only when this file is executed directly by spark-submit.
# SystemExit propagates main() as the process exit code, so Make/CI can
# fail correctly if a future main() returns a non-zero status.
if __name__ == "__main__":
    raise SystemExit(main())
