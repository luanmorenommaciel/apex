"""
Synthetic GC-pressure workload: allocation churn on a deliberately small heap
(ground truth for the gc detector: gc_time / task_time >= 15%).

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/gc_churn.py

Execution sequence:
1. Load configuration and gc_churn parameters from the catalog.
2. Create a Spark session with a 512m executor heap and app name `workload-gc`.
3. Explode each base row into `explode_factor` short-lived rows and derive several
   churny string columns per row — every row allocates and immediately discards
   objects, keeping the young generation under constant pressure.
4. Aggregate the churned rows so the whole pipeline actually executes.
5. Materialize through the `noop` sink.
6. Stop the Spark session.

Tuning lives in workloads/catalog.py (env overrides: WORKLOAD_ROWS,
WORKLOAD_EXPLODE_FACTOR, WORKLOAD_EXECUTOR_MEMORY, ...).
"""

from pyspark.sql import functions as F

from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger
from workloads.catalog import GcChurnParams, describe, load_params

APP_NAME = "workload-gc"
WORKLOAD_NAME = "gc_churn"


def build_churned_rows(spark, params: GcChurnParams):
    """Steps 3: explode + string churn — many short-lived objects per input row."""
    base = spark.range(0, params.rows, 1, params.input_partitions)
    exploded = base.select(
        F.col("id"),
        F.explode(F.sequence(F.lit(1), F.lit(params.explode_factor))).alias("copy"),
    )
    churn = F.md5(F.concat_ws("-", F.col("id"), F.col("copy")))
    return exploded.select(
        F.col("id"),
        F.repeat(churn, params.payload_repeat).alias("payload"),
        F.substring(F.reverse(churn), 1, 8).alias("bucket"),
    )


def build_aggregate(dataframe):
    """Step 4: object-based aggregation so the churn hits the JVM heap.

    collect_list is executed by ObjectHashAggregate (real JVM objects per
    value), unlike Tungsten's off-heap codegen paths — this is what turns the
    allocation churn into measurable GC time on a small heap.
    """
    return dataframe.groupBy("bucket").agg(
        F.count(F.lit(1)).alias("row_count"),
        F.size(F.collect_list("payload")).alias("payload_count"),
    )


def main() -> int:
    """Run the GC-churn workload (see module docstring for the sequence)."""
    params = load_params(WORKLOAD_NAME)
    logger.info(f"Starting {APP_NAME} with parameters: {describe(params)}")
    logger.info(f"{APP_NAME} extra_conf: {params.spark_conf()}")

    def body(spark, _config) -> int:
        result = build_aggregate(build_churned_rows(spark, params))
        result.write.format("noop").mode("overwrite").save()
        logger.info(f"Completed {APP_NAME}: churned aggregation materialized via noop sink")
        return 0

    return run_spark_app(APP_NAME, body, extra_conf=params.spark_conf())


if __name__ == "__main__":
    raise SystemExit(main())
