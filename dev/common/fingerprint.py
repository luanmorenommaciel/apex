"""T7 — contract plan_fingerprint over the NORMALIZED LOGICAL plan.

`optimizedPlan.canonicalized` alone is NOT enough: it does not normalize literal
VALUES, so `id > 100` and `id > 900` would hash differently — breaking the
contract's "same query, different literals -> same fingerprint" rule (verified
empirically by the jar lane, CONTRACT.md). We therefore delegate to the JVM helper
`apexdev.PlanFingerprint`, which runs the SAME Catalyst operations as the Scala jar
(literal-null + canonicalized + toString + SHA-256), guaranteeing an identical
64-hex fingerprint across the Python (dev) and Scala (jar) listeners.
"""
from __future__ import annotations


def _optimized_logical_plan(df):
    # LOGICAL, post-Catalyst — never executedPlan/sparkPlan (physical churns under AQE).
    return df._jdf.queryExecution().optimizedPlan()


def _helper(df):
    helper = df.sparkSession._jvm.apexdev.PlanFingerprint
    if helper is None:  # pragma: no cover - defensive
        raise RuntimeError("apexdev.PlanFingerprint not on the driver classpath "
                           "(spark.driver.extraClassPath -> /opt/apex/lib/apex-devfp.jar)")
    return helper


def plan_fingerprint(df) -> str:
    """64 lowercase hex chars; matches the jar's apex.ApexPlanFingerprint."""
    return _helper(df).fingerprint(_optimized_logical_plan(df))


def redacted_plan_json(df) -> str:
    """Redacted, literal-free logical-plan text for the contract `plan_json`."""
    return _helper(df).redactedPlan(_optimized_logical_plan(df))
