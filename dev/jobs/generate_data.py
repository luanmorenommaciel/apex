"""T8 — generate the deterministic skewed fact + dim Delta tables, and verify the
hot key is ~50%. Run: make gen-data
"""
import sys

sys.path.insert(0, "/opt/apex")

import pyspark.sql.functions as F                       # noqa: E402
from common.session import build_session, stop_session  # noqa: E402
from common.data import generate_data, HOT_KEYS, FACT_PATH  # noqa: E402


def main() -> int:
    spark, job_id, app_id, app_name = build_session("apex-generate-data")
    generate_data(spark)

    fact = spark.read.format("delta").load(FACT_PATH)
    total = fact.count()
    shares = {k: fact.filter(F.col("join_key") == k).count() / total for k in HOT_KEYS}
    hot = sum(shares.values())
    per_key = " ".join(f"key_{k}={shares[k]:.4f}" for k in HOT_KEYS)
    print(f"APEX_GEN rows={total} {per_key} hot_frac={hot:.4f}", flush=True)
    ok = 0.45 <= hot <= 0.55 and all(0.20 <= s <= 0.30 for s in shares.values())
    print(f"APEX_GEN hot_keys_~50pct={'PASS' if ok else 'FAIL'}", flush=True)

    stop_session(spark)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
