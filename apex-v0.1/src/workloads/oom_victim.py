"""
Synthetic OOM workload: per-task allocations that cannot spill, sized past the
executor heap (ground truth for the oom detector and the Error Handling tab).

THIS WORKLOAD IS EXPECTED TO FAIL: the job aborts after `task_max_failures`
attempts with java.lang.OutOfMemoryError (or the executor is lost). main()
treats that failure as success and returns 0 so Make targets stay green.

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/oom_victim.py

Execution sequence:
1. Load configuration and oom_victim parameters from the catalog.
2. Create a Spark session with a 512m executor heap, task retries lowered to 2,
   and app name `workload-oom`.
3. Each task materializes sequence(1, array_cells) — a single in-memory array of
   ~60M longs (~480MB) that execution memory cannot spill.
4. The allocation exceeds the heap: tasks die with OutOfMemoryError, the executor
   may be lost, and the job aborts. The exception is caught and logged.
5. Stop the Spark session.

Tuning lives in workloads/catalog.py (env overrides: WORKLOAD_ARRAY_CELLS,
WORKLOAD_EXECUTOR_MEMORY, WORKLOAD_TASK_MAX_FAILURES, ...).
"""

from pyspark.sql import functions as F

from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger
from workloads.catalog import OomVictimParams, describe, load_params

APP_NAME = "workload-oom"
WORKLOAD_NAME = "oom_victim"


def build_oom_projection(spark, params: OomVictimParams):
    """Step 3: one giant, unspillable array allocation per task.

    reverse() forces the sequence to be materialized as a real in-memory array
    (a bare size(sequence(...)) is computed by Catalyst without allocating).
    """
    giant = F.sequence(F.lit(1), F.col("id") + F.lit(params.array_cells))
    return spark.range(0, params.rows, 1, params.input_partitions).select(
        F.element_at(F.reverse(giant), 1).alias("first_of_reversed")
    )


def main() -> int:
    """Run the OOM workload; the job failing with OOM is the expected outcome."""
    params = load_params(WORKLOAD_NAME)
    logger.info(f"Starting {APP_NAME} with parameters: {describe(params)}")
    logger.info(f"{APP_NAME} extra_conf: {params.spark_conf()}")

    def body(spark, _config) -> int:
        try:
            build_oom_projection(spark, params).write.format("noop").mode("overwrite").save()
            logger.warning(
                f"{APP_NAME} finished WITHOUT failing — increase WORKLOAD_ARRAY_CELLS "
                "or lower WORKLOAD_EXECUTOR_MEMORY to guarantee the OOM"
            )
        except Exception as exc:
            logger.info(f"Completed {APP_NAME}: falha esperada capturada ({type(exc).__name__})")
        return 0

    return run_spark_app(APP_NAME, body, extra_conf=params.spark_conf())


if __name__ == "__main__":
    raise SystemExit(main())
