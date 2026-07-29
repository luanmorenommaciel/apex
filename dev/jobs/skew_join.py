"""T9 — SKEW ON JOIN. fact(2 hot keys, ~25% each) ⋈ dim on join_key.

Default (pathology): AQE OFF + autoBroadcastJoinThreshold=-1 → a real sort-merge
shuffle join where the two hot keys' partitions hold ~50% of rows → those reduce
tasks run far longer → p99 ≫ p50. With broadcast allowed or AQE on it self-heals.

  APEX_AQE=on  → AQE enabled: Spark's adaptive skew-join SPLITS the hot partitions.
                 Runs the SAME query so the jar's AQE differentiator (skew-split
                 capture) has a real re-plan to observe.  (make run-pathology JOB=skew_join AQE=on)

Calibration (2026-07-28): the aggregation carries the `amount` payload
(sum + count) and the action consumes it — a bare .count() lets the optimizer
drop sum(amount) as unused and the join exchange degenerates to bare int keys
(measured: 2.1 B/row, hot partition below the AQE skew threshold). Two hot keys
instead of one: percentile statistics (Spark taskSummary AND the plugin's p99 in
spark_events) interpolate/nearest-rank p99 to a COLD task when a single task in
a hundred is hot (measured: plugin p99/p50 = 12.46× on a stage whose max task
was 53× the median); two hot tasks put the skew above the p99 rank. Each hot
partition is ~28 MB > the 16m skewedPartitionThresholdInBytes, so the AQE split
is data volume, not luck. See common/data.py for the full calibration note.
"""
import os
import sys

sys.path.insert(0, "/opt/apex")

import pyspark.sql.functions as F                            # noqa: E402
from common.session import build_session, stop_session      # noqa: E402
from common.data import ensure_data, FACT_PATH, DIM_PATH     # noqa: E402


def main() -> int:
    aqe = os.environ.get("APEX_AQE", "off").lower() == "on"
    conf = {
        "spark.sql.adaptive.enabled": "true" if aqe else "false",
        "spark.sql.autoBroadcastJoinThreshold": "-1",   # force a shuffle join, never broadcast
        # 100 reduce partitions (not the 200 default): percentile statistics only
        # see hot tasks that sit above the p99 rank — with the 200-task default
        # the two hot tasks were ranks 199/200 and p99 (~rank 198) stayed cold.
        # verify's closed form — a stage is tail-bound iff p99/p50 >
        # (n-1)/(slots-1) — is evaluated against the plugin's p99 in spark_events.
        "spark.sql.shuffle.partitions": os.environ.get("APEX_SHUFFLE_PARTITIONS", "100"),
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
    # sum(amount) forces the join exchange to carry the payload column, so the
    # shuffled volume (and the hot partition) is real data, not pruned ints.
    joined = (fact.join(dim, "join_key")
              .groupBy("attr")
              .agg(F.sum("amount").alias("total_amount"), F.count("*").alias("rows")))

    # The action must CONSUME the aggregates: a bare joined.count() lets the
    # optimizer drop sum(amount) as unused and the join exchange degenerates
    # back to the bare int key (measured 2026-07-28: 2.1 B/row, hot partition
    # below the AQE skew threshold). Summing the aggregates downstream pins
    # every column into the plan.
    total = joined.agg(F.sum("rows").alias("joined_rows"),
                       F.sum("total_amount").alias("grand_total")).collect()[0]
    print(f"APEX_JOB skew_join aqe={aqe} app_id={app_id} "
          f"joined_rows={total['joined_rows']} grand_total={total['grand_total']:.1f}",
          flush=True)

    stop_session(spark)
    return 0


if __name__ == "__main__":
    sys.exit(main())
