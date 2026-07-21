"""T11 — BAD SHUFFLE. A shuffle-heavy aggregation forced through far too few
partitions (shuffle.partitions=2) → 2 enormous reduce tasks + long wall time.

Default (pathology): AQE OFF, shuffle.partitions=2.
  APEX_FIX=on → shuffle.partitions=200 (and AQE could coalesce) → balanced tasks.
"""
import os
import sys

sys.path.insert(0, "/opt/apex")

from common.session import build_session          # noqa: E402
from common.listener import attach, set_plan      # noqa: E402
from common.data import ensure_data, FACT_PATH     # noqa: E402


def main() -> int:
    fix = os.environ.get("APEX_FIX", "off").lower() == "on"
    conf = {
        "spark.sql.adaptive.enabled": "false",
        "spark.sql.shuffle.partitions": "200" if fix else "2",   # far too few → huge tasks
    }
    spark, job_id, app_id, app_name = build_session(
        f"apex-bad_shuffle{'-fix' if fix else ''}", conf)
    listener = attach(spark, job_id, app_id, app_name)
    ensure_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)
    # High-cardinality shuffle: repartition all rows by id across only 2 partitions.
    agg = fact.groupBy("id").agg({"amount": "sum"})

    set_plan(listener, agg)
    agg.write.format("noop").mode("overwrite").save()
    print(f"APEX_JOB bad_shuffle fix={fix} app_id={app_id}", flush=True)

    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
