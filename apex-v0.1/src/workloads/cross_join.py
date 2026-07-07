"""
Synthetic plan-antipattern workload: an explicit cartesian product, so the
physical plan contains `CartesianProduct` (ground truth for the plans detector's
code-analysis rules).

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/cross_join.py

Execution sequence:
1. Load configuration and cross_join parameters from the catalog.
2. Create a Spark session (broadcast disabled, AQE off so the plan text is stable)
   with app name `workload-crossjoin`.
3. crossJoin two small ranges (3k x 3k = 9M combinations — cheap to execute, but
   the plan carries the CartesianProduct operator the detector flags).
4. Aggregate the combinations and materialize through the `noop` sink.
5. Stop the Spark session.

Tuning lives in workloads/catalog.py (env overrides: WORKLOAD_LEFT_ROWS,
WORKLOAD_RIGHT_ROWS, ...).
"""

from pyspark.sql import functions as F

from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger
from workloads.catalog import CrossJoinParams, describe, load_params

APP_NAME = "workload-crossjoin"
WORKLOAD_NAME = "cross_join"


def build_cartesian(spark, params: CrossJoinParams):
    """Step 3: explicit cross join between two small generated ranges."""
    left = spark.range(0, params.left_rows, 1, params.input_partitions).alias("l")
    right = spark.range(0, params.right_rows, 1, params.input_partitions).alias("r")
    return left.crossJoin(right).select(
        (F.col("l.id") * F.col("r.id")).alias("product")
    )


def build_aggregate(dataframe):
    """Step 4: aggregate so the cartesian product is fully executed."""
    return dataframe.agg(F.count(F.lit(1)).alias("combinations"), F.sum("product").alias("product_sum"))


def main() -> int:
    """Run the cartesian-product workload (see module docstring for the sequence)."""
    params = load_params(WORKLOAD_NAME)
    logger.info(f"Starting {APP_NAME} with parameters: {describe(params)}")
    logger.info(f"{APP_NAME} extra_conf: {params.spark_conf()}")

    def body(spark, _config) -> int:
        build_aggregate(build_cartesian(spark, params)).write.format("noop").mode("overwrite").save()
        logger.info(f"Completed {APP_NAME}: cartesian product materialized via noop sink")
        return 0

    return run_spark_app(APP_NAME, body, extra_conf=params.spark_conf())


if __name__ == "__main__":
    raise SystemExit(main())
