"""T6 proof — run via:
    spark-submit --master spark://spark-master:7077 /opt/apex/tests/listener_probe.py

Builds a session (T5), attaches the ApexStageListener (T6), sets the plan context
(T7 fingerprint), runs a small multi-stage query (groupBy -> shuffle -> ≥2 stages),
and stops. The listener writes one contract record per completed stage to
out/spark_events.jsonl, which the harness then validates.
"""
import sys

sys.path.insert(0, "/opt/apex")

from common.session import build_session          # noqa: E402
from common.listener import attach, set_plan       # noqa: E402


def main() -> int:
    spark, job_id, app_id, app_name = build_session("apex-listener-probe")
    listener = attach(spark, job_id, app_id, app_name)

    # A genuine shuffle: range -> groupBy -> agg. Forces a stage boundary so we get
    # more than one completed stage (map + reduce).
    df = (spark.range(0, 100000)
          .selectExpr("id", "id % 7 as k")
          .where("id > 5")
          .groupBy("k").count())

    set_plan(listener, df)    # fingerprint + redacted plan for the current query
    rows = df.collect()
    print(f"APEX_PROBE job_id={job_id} groups={len(rows)}", flush=True)

    spark.stop()              # flush the bus / finalize the event log
    print("APEX_PROBE done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
