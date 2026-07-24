"""T10 — SPILL. Global sort of the large fact table under a starved execution-memory
pool and few shuffle partitions → the external sorter spills to disk → spill_disk_bytes>0.

Default (pathology): AQE OFF, shuffle.partitions=8, executor.memory=1g, and a tiny
memory.fraction so the sort cannot stay in RAM.
  APEX_FIX=on → healthy config (more memory + partitions) → no spill.
"""
import os
import sys

sys.path.insert(0, "/opt/apex")

from common.session import build_session          # noqa: E402
from common.data import ensure_data, FACT_PATH     # noqa: E402


def main() -> int:
    fix = os.environ.get("APEX_FIX", "off").lower() == "on"
    conf = {
        "spark.sql.adaptive.enabled": "false",
        "spark.executor.memory": "2g" if fix else "1g",
        "spark.sql.shuffle.partitions": "200" if fix else "8",
        "spark.memory.fraction": "0.6" if fix else "0.1",   # starve execution memory → spill
    }
    spark, job_id, app_id, app_name = build_session(
        f"apex-spill{'-fix' if fix else ''}", conf)
    ensure_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)
    # Global sort forces a shuffle + external sort; the constrained pool spills to disk.
    sorted_df = fact.orderBy("amount")

    sorted_df.write.format("noop").mode("overwrite").save()   # materialize the full sort
    print(f"APEX_JOB spill fix={fix} app_id={app_id}", flush=True)

    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
