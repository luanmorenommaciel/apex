"""T8 — deterministic skewed data generator (shared by the pathology jobs).

One hot join key = ~50% of fact rows, fully seeded → byte-identical across runs.
numPartitions is PINNED so rand() assignment is stable regardless of cluster size
(rand(seed) is deterministic per (partitionIndex, rowIndex) — a varying partition
count would otherwise change the output).
"""
from __future__ import annotations

import os
import pyspark.sql.functions as F

HOT_KEY = 7
NUM_KEYS = 10_000
SEED = 42
GEN_PARTITIONS = 16          # pinned → reproducible across 2-core or N-core clusters
FACT_PATH = "s3a://warehouse/fact"
DIM_PATH = "s3a://warehouse/dim"


def default_rows() -> int:
    return int(os.environ.get("APEX_ROWS", "5000000"))


def generate_data(spark, rows: int | None = None) -> None:
    rows = rows or default_rows()
    fact = (spark.range(0, rows, step=1, numPartitions=GEN_PARTITIONS)
            .withColumn("join_key",
                        F.when(F.rand(SEED) < 0.5, F.lit(HOT_KEY))              # ~50% hot
                         .otherwise((F.rand(SEED + 1) * NUM_KEYS).cast("int")))
            .withColumn("amount", (F.rand(SEED + 2) * 1000)))
    fact.write.format("delta").mode("overwrite").save(FACT_PATH)

    dim = (spark.range(0, NUM_KEYS, step=1, numPartitions=GEN_PARTITIONS)
           .withColumnRenamed("id", "join_key")
           .withColumn("attr", F.concat(F.lit("k_"), F.col("join_key").cast("string"))))
    dim.write.format("delta").mode("overwrite").save(DIM_PATH)


def _exists(spark, path: str) -> bool:
    """Return whether a committed Delta log exists without starting a Spark job.

    ``limit(1).collect()`` looks harmless but plans and executes a distributed
    read for every pathology. The lab already has S3A available in the driver,
    so checking for a committed JSON transaction is enough to decide whether
    deterministic input must be generated again.
    """
    try:
        hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(path)
        filesystem = hadoop_path.getFileSystem(spark._jsc.hadoopConfiguration())
        committed_log = spark._jvm.org.apache.hadoop.fs.Path(
            f"{path.rstrip('/')}/_delta_log/[0-9]*.json"
        )
        matches = filesystem.globStatus(committed_log)
        return bool(matches and len(matches) > 0)
    except Exception:
        return False


def ensure_data(spark, rows: int | None = None) -> None:
    """Generate fact+dim only if missing — so pathology jobs are self-sufficient
    but don't pay the regeneration cost on every run."""
    if _exists(spark, FACT_PATH) and _exists(spark, DIM_PATH):
        return
    generate_data(spark, rows)
