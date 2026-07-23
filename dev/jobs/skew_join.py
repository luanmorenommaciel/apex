"""T9 — SKEW ON JOIN. fact(~50% hot key) ⋈ dim on join_key.

Default (pathology): AQE OFF + autoBroadcastJoinThreshold=-1 → a real sort-merge
shuffle join where the hot key's partition holds ~50% of rows → one reduce task
runs far longer → p99 ≫ p50. With broadcast allowed or AQE on it self-heals.

  APEX_AQE=on  → AQE enabled: Spark's adaptive skew-join SPLITS the hot partition.
                 Runs the SAME query so the jar's AQE differentiator (skew-split
                 capture) has a real re-plan to observe.  (make run-pathology JOB=skew_join AQE=on)
"""
import os
import sys

sys.path.insert(0, "/opt/apex")

from common.session import build_session          # noqa: E402
from common.data import ensure_data, FACT_PATH, DIM_PATH  # noqa: E402


def main() -> int:
    aqe = os.environ.get("APEX_AQE", "off").lower() == "on"
    conf = {
        "spark.sql.adaptive.enabled": "true" if aqe else "false",
        "spark.sql.autoBroadcastJoinThreshold": "-1",   # force a shuffle join, never broadcast
    }
    if aqe:
        # The default C4 cell stays conservative. Dedicated calibration cells pass
        # stricter values through the environment, so the reproducible pathology is
        # not silently changed while we investigate an actual skew_split transition.
        conf.update({
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": os.environ.get(
                "APEX_AQE_SKEW_THRESHOLD", "16m"),
            "spark.sql.adaptive.advisoryPartitionSizeInBytes": os.environ.get(
                "APEX_AQE_ADVISORY_PARTITION", "8m"),
            "spark.sql.adaptive.skewJoin.skewedPartitionFactor": os.environ.get(
                "APEX_AQE_SKEW_FACTOR", "5"),
            "spark.sql.adaptive.coalescePartitions.enabled": os.environ.get(
                "APEX_AQE_COALESCE", "true"),
            "spark.sql.adaptive.forceOptimizeSkewedJoin": os.environ.get(
                "APEX_AQE_FORCE_OPTIMIZE_SKEW", "false"),
        })
    spark, job_id, app_id, app_name = build_session(
        f"apex-skew_join{'-aqe' if aqe else ''}", conf)
    ensure_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)
    dim = spark.read.format("delta").load(DIM_PATH)
    joined = fact.join(dim, "join_key").groupBy("attr").count()

    n = joined.count()
    print(f"APEX_JOB skew_join aqe={aqe} app_id={app_id} out_groups={n}", flush=True)

    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
