"""
Synthetic cache-tracking workload: persists a dataset larger than the storage
pool so cached blocks overflow to disk, with block updates written to the event
log (`spark.eventLog.logBlockUpdates.enabled=true` via extra_conf). Blocks are
then visible in ClickHouse through the `spark_cache_blocks` view.

Manual submit command, assuming the Compose stack is already running:
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/workloads/cache_heavy.py

Execution sequence:
1. Load configuration and cache_heavy parameters from the catalog.
2. Create a Spark session with block-update logging on and a shrunken storage
   pool (memory.fraction=0.3), app name `workload-cache`.
3. Build a wide-payload dataset (~270MB) and persist it MEMORY_AND_DISK — bigger
   than the storage pool, so part of the blocks land on the disk tier.
4. Run two actions over the cached data (count + aggregation): the first
   populates the cache, the second reads from it.
5. Unpersist (emits SparkListenerUnpersistRDD) and stop the session.

Tuning lives in workloads/catalog.py (env overrides: WORKLOAD_ROWS,
WORKLOAD_MEMORY_FRACTION, ...).
"""

from pyspark import StorageLevel
from pyspark.sql import functions as F

from spark_platform.runner import run_spark_app
from spark_platform.utils.logger import logger
from workloads.catalog import CacheHeavyParams, describe, load_params

APP_NAME = "workload-cache"
WORKLOAD_NAME = "cache_heavy"


def build_cacheable_rows(spark, params: CacheHeavyParams):
    """Step 3: wide, incompressible payload sized past the shrunken storage pool.

    Distinct md5 segments (not a repeated one) defeat the columnar cache
    compression, so the cached size stays close to the raw size and the
    storage pool genuinely overflows to the disk tier.
    """
    segments = [
        F.md5(F.concat(F.col("id").cast("string"), F.lit(f"-{i}")))
        for i in range(params.payload_repeat)
    ]
    return spark.range(0, params.rows, 1, params.input_partitions).select(
        F.col("id"), F.concat(*segments).alias("payload")
    )


def main() -> int:
    """Run the cache-tracking workload (see module docstring for the sequence)."""
    params = load_params(WORKLOAD_NAME)
    logger.info(f"Starting {APP_NAME} with parameters: {describe(params)}")
    logger.info(f"{APP_NAME} extra_conf: {params.spark_conf()}")

    def body(spark, _config) -> int:
        cached = build_cacheable_rows(spark, params).persist(StorageLevel.MEMORY_AND_DISK)
        populated = cached.count()
        digest = cached.agg(F.max("payload").alias("payload_max")).collect()[0]["payload_max"]
        logger.info(f"{APP_NAME}: cached {populated} rows; digest sample {digest[:16]}...")
        cached.unpersist(blocking=True)
        logger.info(f"Completed {APP_NAME}: cache populated, re-read, and unpersisted")
        return 0

    return run_spark_app(APP_NAME, body, extra_conf=params.spark_conf())


if __name__ == "__main__":
    raise SystemExit(main())
