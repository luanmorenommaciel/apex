"""T8 — deterministic skewed data generator (shared by the pathology jobs).

Two hot join keys = ~25% of fact rows each (~50% combined), fully seeded →
byte-identical across runs. numPartitions is PINNED so rand() assignment is
stable regardless of cluster size (rand(seed) is deterministic per
(partitionIndex, rowIndex) — a varying partition count would otherwise change
the output).

Why TWO hot keys (2026-07-28, second calibration pass): a single hot key makes
exactly ONE hot reduce task, and every percentile statistic in the pipeline
(Spark's taskSummary, the ApexPlugin's p99 in spark_events) interpolates or
nearest-ranks p99 to a *cold* task when only one task in a hundred is hot —
measured: plugin p99/p50 = 12.46× on a stage whose max task was 53× the median.
Two hot keys put two tasks above the p99 rank, so the statistic the engine
consumes actually sees the skew. Each hot partition stays ~28 MB > the 16m
spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes, so AQE still has a
byte-volume reason to split — and now splits TWO partitions.

Calibration (2026-07-28): default scale raised 5M → 10M rows. The 2026-07-24
verify-lane analysis proved the old jobs produced measurement noise, not
pathologies: the skew_join query pruned every column except the INT join key,
so the whole join shuffle was ~10 MB and the hot partition (~5 MB) sat BELOW
the AQE skew threshold — and every duration-based signal was JVM/scheduler
jitter. At 10M rows with the payload-carrying query (sum(amount)) each hot
shuffle partition is ~28 MB ≈ 1.75× the 16m threshold → the split is mechanical.

Generation marker: `ensure_data` used to skip regeneration whenever ANY fact
table existed, so a stale table generated at a different row count silently
poisoned every later run. A marker dataset (s3a://warehouse/_gen_meta) now
records (version, rows, seed, keys, partitions); any mismatch forces a full
deterministic regeneration.
"""
from __future__ import annotations

import os
import pyspark.sql.functions as F

HOT_KEYS = (7, 8)            # two heavy keys ~25% each (~50% combined) — see header
HOT_FRAC = 0.25
HOT_KEY = HOT_KEYS[0]        # legacy single-key alias (hot-band checks)
NUM_KEYS = 10_000
SEED = 42
GEN_PARTITIONS = 16          # pinned → reproducible across 2-core or N-core clusters
GEN_VERSION = 4              # bump when generation logic changes → forces regen
FACT_PATH = "s3a://warehouse/fact"
DIM_PATH = "s3a://warehouse/dim"
META_PATH = "s3a://warehouse/_gen_meta"   # one-row JSON dataset written by Spark


def default_rows() -> int:
    return int(os.environ.get("APEX_ROWS", "10000000"))


def _marker(rows: int) -> dict:
    return {"v": GEN_VERSION, "rows": rows, "seed": SEED,
            "num_keys": NUM_KEYS, "partitions": GEN_PARTITIONS}


def _read_marker(spark) -> dict | None:
    try:
        found = spark.read.json(META_PATH).collect()
    except Exception:
        return None
    if len(found) != 1:
        return None
    try:
        return {k: int(found[0][k]) for k in ("v", "rows", "seed", "num_keys", "partitions")}
    except Exception:
        return None


def _write_marker(spark, rows: int) -> None:
    spark.createDataFrame([_marker(rows)]).coalesce(1).write.mode("overwrite").json(META_PATH)


def generate_data(spark, rows: int | None = None) -> None:
    rows = rows or default_rows()
    # rand() is nondeterministic → Catalyst will NOT common-subexpression-eliminate
    # two references in a when() chain (measured: key_8 came out 37.5%, not 25%).
    # Materialize the draw as a column so both band tests see the SAME value.
    fact = (spark.range(0, rows, step=1, numPartitions=GEN_PARTITIONS)
            .withColumn("_r", F.rand(SEED))
            .withColumn("join_key",
                        F.when(F.col("_r") < HOT_FRAC, F.lit(HOT_KEYS[0]))          # ~25% hot key A
                         .when(F.col("_r") < 2 * HOT_FRAC, F.lit(HOT_KEYS[1]))      # ~25% hot key B
                         .otherwise((F.rand(SEED + 1) * NUM_KEYS).cast("int")))
            .withColumn("amount", (F.rand(SEED + 2) * 1000))
            .drop("_r"))
    fact.write.format("delta").mode("overwrite").save(FACT_PATH)

    dim = (spark.range(0, NUM_KEYS, step=1, numPartitions=GEN_PARTITIONS)
           .withColumnRenamed("id", "join_key")
           .withColumn("attr", F.concat(F.lit("k_"), F.col("join_key").cast("string"))))
    dim.write.format("delta").mode("overwrite").save(DIM_PATH)

    _write_marker(spark, rows)


def _exists(spark, path: str) -> bool:
    try:
        spark.read.format("delta").load(path).limit(1).collect()
        return True
    except Exception:
        return False


def ensure_data(spark, rows: int | None = None) -> None:
    """Generate fact+dim unless the on-disk data matches the expected generation.

    The marker check is what makes scale changes actually take effect: data
    generated at a different row count / seed / generator version is treated as
    absent and regenerated deterministically (mode=overwrite).
    """
    rows = rows or default_rows()
    if _read_marker(spark) == _marker(rows) and _exists(spark, FACT_PATH) and _exists(spark, DIM_PATH):
        return
    generate_data(spark, rows)
