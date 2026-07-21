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
from common.listener import attach, set_plan      # noqa: E402
from common.data import ensure_data, FACT_PATH, DIM_PATH  # noqa: E402


def main() -> int:
    aqe = os.environ.get("APEX_AQE", "off").lower() == "on"
    conf = {
        "spark.sql.adaptive.enabled": "true" if aqe else "false",
        "spark.sql.autoBroadcastJoinThreshold": "-1",   # force a shuffle join, never broadcast
    }
    if aqe:
        # Lower the skew thresholds so AQE's skew-join split actually FIRES on this
        # lab's modest data volume (defaults expect >256MB partitions) — that runtime
        # re-plan is exactly what the jar's AQE differentiator captures.
        conf.update({
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "16m",
            "spark.sql.adaptive.advisoryPartitionSizeInBytes": "8m",
        })
    spark, job_id, app_id, app_name = build_session(
        f"apex-skew_join{'-aqe' if aqe else ''}", conf)
    listener = attach(spark, job_id, app_id, app_name)
    ensure_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)
    dim = spark.read.format("delta").load(DIM_PATH)
    joined = fact.join(dim, "join_key").groupBy("attr").count()

    set_plan(listener, joined)
    n = joined.count()
    print(f"APEX_JOB skew_join aqe={aqe} app_id={app_id} out_groups={n}", flush=True)

    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
