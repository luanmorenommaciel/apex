"""
Synthetic shuffle-spill workload: wide-payload aggregation into starved memory
(ground truth for the shuffle/spill detector).

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/shuffle_heavy.py

Execution sequence:
1. Load lakehouse configuration from YAML and shuffle_heavy parameters from the catalog.
2. Create a Spark session with spill-forcing extra_conf (memory.fraction=0.2, only 4
   shuffle partitions, AQE off) and app name `workload-shuffle`.
3. Generate rows with a wide (~224-char) deterministic payload and near-unique group
   keys, so map-side partial aggregation cannot shrink the shuffle.
4. groupBy-aggregate into 4 fat reduce partitions, then sort within partitions: each
   task holds far more data than the starved execution memory pool allows, forcing
   memory and disk spill, with stage shuffle bytes in the hundreds of MiB.
5. Materialize through the `noop` sink (full computation, no storage side effects).
6. Stop the Spark session.

Tuning lives in workloads/catalog.py (env overrides: WORKLOAD_ROWS,
WORKLOAD_PAYLOAD_REPEAT, WORKLOAD_MEMORY_FRACTION, ...).
"""

from pyspark.sql import functions as F

from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger
from workloads.catalog import ShuffleHeavyParams, describe, load_params

APP_NAME = "workload-shuffle"
WORKLOAD_NAME = "shuffle_heavy"


def build_wide_rows(spark, params: ShuffleHeavyParams):
    """Step 3: rows with a wide deterministic payload and near-unique group keys.

    - payload: md5(id) repeated `payload_repeat` times (32 chars per repeat);
      pure function of the row id, no randomness.
    - group_key: id modulo distinct_keys; with the default distinct_key_ratio
      of 1.0 every key is unique, so the shuffle carries the full payload and
      the reduce-side hash aggregation must keep one entry per row.
    """
    payload = F.repeat(F.md5(F.col("id").cast("string")), params.payload_repeat).alias("payload")
    group_key = F.pmod(F.col("id"), F.lit(params.distinct_keys)).cast("long").alias("group_key")
    return spark.range(0, params.rows, 1, params.input_partitions).select(group_key, payload)


def build_shuffle_aggregate(dataframe):
    """Step 4: wide aggregation plus an in-partition sort, both sized to spill.

    min/max keep the wide payload flowing through the aggregation buffers, and
    sortWithinPartitions adds an external sort over the still-wide result in
    the same stage — two independent spill triggers per reduce task.
    """
    aggregated = dataframe.groupBy("group_key").agg(
        F.count(F.lit(1)).alias("row_count"),
        F.min("payload").alias("payload_min"),
        F.max("payload").alias("payload_max"),
    )
    return aggregated.sortWithinPartitions("payload_max")


def main() -> int:
    """
    Run the shuffle-spill workload.

    1. Load lakehouse configuration and shuffle_heavy catalog parameters.
    2. Create a Spark session with spill-forcing extra_conf.
    3. Generate wide-payload rows with near-unique group keys.
    4. Aggregate + sort into 4 fat reduce partitions (memory/disk spill).
    5. Materialize through the `noop` sink.
    6. Stop the Spark session.
    """
    params = load_params(WORKLOAD_NAME)
    logger.info(f"Starting {APP_NAME} with parameters: {describe(params)}")
    logger.info(f"{APP_NAME} extra_conf: {params.spark_conf()}")

    def body(spark, _config) -> int:
        result = build_shuffle_aggregate(build_wide_rows(spark, params))
        result.write.format("noop").mode("overwrite").save()
        logger.info(f"Completed {APP_NAME}: spilling aggregation materialized via noop sink")
        return 0

    return run_spark_app(APP_NAME, body, extra_conf=params.spark_conf())


# Run only when this file is executed directly by spark-submit.
# SystemExit propagates main() as the process exit code, so Make/CI can
# fail correctly if a future main() returns a non-zero status.
if __name__ == "__main__":
    raise SystemExit(main())
