"""T8 — generate the deterministic skewed fact + dim Delta tables, and verify the
hot key is ~50%. Run: make gen-data
"""
import sys

sys.path.insert(0, "/opt/apex")

import pyspark.sql.functions as F                       # noqa: E402
from common.session import build_session                # noqa: E402
from common.data import generate_data, HOT_KEY, FACT_PATH  # noqa: E402


def main() -> int:
    spark, job_id, app_id, app_name = build_session("apex-generate-data")
    generate_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)
    total = fact.count()
    hot = fact.filter(F.col("join_key") == HOT_KEY).count()
    frac = hot / total if total else 0.0
    print(f"APEX_GEN rows={total} hot_key={HOT_KEY} hot_rows={hot} hot_frac={frac:.4f}", flush=True)
    ok = 0.45 <= frac <= 0.55
    print(f"APEX_GEN hot_key_~50pct={'PASS' if ok else 'FAIL'}", flush=True)

    spark.stop()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
