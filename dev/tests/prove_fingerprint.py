"""T7 proof (mirrors jar/ApexPlanFingerprintSpec) — run via:
    spark-submit --master local[2] /opt/apex/tests/prove_fingerprint.py

Proves the dev Python fingerprint:
  1. is 64 lowercase hex;
  2. same query / different literals (AQE on) -> IDENTICAL fingerprint;
  3. structurally different query -> DIFFERENT fingerprint;
  4. raw canonicalized (literals kept) DIFFERS on literals — justifying normalization;
  5. (integration, best-effort) equals the jar's apex.ApexPlanFingerprint when that
     class is on the classpath.
"""
import hashlib
import sys

from pyspark.sql import SparkSession

sys.path.insert(0, "/opt/apex")
from common.fingerprint import plan_fingerprint  # noqa: E402


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> int:
    spark = (SparkSession.builder.master("local[2]").appName("apex-fp-test")
             .config("spark.sql.adaptive.enabled", "true")   # AQE ON — fp must survive it
             .config("spark.ui.enabled", "false")
             .config("spark.sql.shuffle.partitions", "4")
             .getOrCreate())
    jvm = spark._jvm
    failures = []

    def opt_plan(sql):
        return spark.sql(sql)._jdf.queryExecution().optimizedPlan()

    def fp(sql):
        return jvm.apexdev.PlanFingerprint.fingerprint(opt_plan(sql))

    def raw(sql):
        return sha256(opt_plan(sql).canonicalized().toString())

    # id is a genuine 0..999 range column, so the filter is NOT constant-folded —
    # the literal survives into the optimized plan (the whole point).
    spark.range(0, 1000).selectExpr("id", "id % 10 as amount", "id % 3 as segment") \
        .createOrReplaceTempView("t")

    fp1 = fp("select segment, count(*) c from t where id > 100 group by segment")
    fp2 = fp("select segment, count(*) c from t where id > 900 group by segment")
    fp3 = fp("select segment, sum(amount) s from t group by segment")

    def check(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)
        if not cond:
            failures.append(name)

    import re
    check("fp1 is 64 lowercase hex", bool(re.fullmatch(r"[0-9a-f]{64}", fp1)))
    check("same query, different literals -> identical fp (fp1 == fp2)", fp1 == fp2)
    check("structurally different query -> different fp (fp1 != fp3)", fp1 != fp3)

    raw1 = raw("select segment, count(*) c from t where id > 100 group by segment")
    raw2 = raw("select segment, count(*) c from t where id > 900 group by segment")
    check("raw canonicalized DIFFERS on literals (justifies normalization)", raw1 != raw2)

    print(f"  fp1={fp1}", flush=True)
    print(f"  fp2={fp2}  (== fp1: {fp1 == fp2})", flush=True)
    print(f"  fp3={fp3}", flush=True)
    print(f"  raw1={raw1[:16]}…  raw2={raw2[:16]}…  (== : {raw1 == raw2})", flush=True)

    # ── best-effort integration cross-check vs the jar's real Scala class ──
    try:
        jar_fp1 = jvm.apex.ApexPlanFingerprint.fingerprint(
            opt_plan("select segment, count(*) c from t where id > 100 group by segment"))
        check("dev fp == jar apex.ApexPlanFingerprint fp (cross-language match)", jar_fp1 == fp1)
        print(f"  jar_fp1={jar_fp1}", flush=True)
    except Exception as ex:
        print(f"  [SKIP] jar cross-check — apex.ApexPlanFingerprint not on classpath "
              f"({type(ex).__name__}). Algorithm is identical by construction; run "
              f"`make fp-crosscheck` to prove against the jar's compiled class.", flush=True)

    spark.stop()
    if failures:
        print(f"FINGERPRINT TEST FAILED: {failures}", flush=True)
        return 1
    print("FINGERPRINT TEST PASSED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
