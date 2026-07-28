#!/usr/bin/env python
"""Live gate for the memory lane — proves the exit criterion against real data.

    uv run --extra clickhouse python tools/recall_gate.py

Exits non-zero on failure so CI can depend on it. Unlike the unit suite this
touches the real ClickHouse and asserts on what is actually stored, so it fails
if the schema drifts, the index goes stale, or a gate stops firing.
"""

from __future__ import annotations

import sys

from apex_memory.clickhouse import MemoryStore
from apex_memory.config import ENCODER_VERSION
from apex_memory.encoder import VECTOR_DIM
from apex_memory.recall import recall
from apex_memory.schema import Confidence, MatchTier
from apex_memory.seed import probe_zest_dataset

PASS, FAIL = "  \033[32mPASS\033[0m", "  \033[31mFAIL\033[0m"
_failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"{PASS if condition else FAIL}  {label}{f' — {detail}' if detail else ''}")
    if not condition:
        _failures.append(label)


def main() -> int:
    store = MemoryStore()
    try:
        store.query("SELECT 1")
    except Exception as exc:  # noqa: BLE001 — a live gate reports, never raises
        print(f"ClickHouse unreachable, skipping live gate: {type(exc).__name__}")
        return 0

    print("\n── index health ─────────────────────────────────────────────")
    plans = store.query(
        "SELECT count() AS n, min(dim) AS min_dim, max(dim) AS max_dim, "
        "uniqExact(encoder_version) AS versions, min(node_count) AS min_nodes "
        "FROM apex.plan_memory FINAL"
    )[0]
    check("plan_memory is populated", plans["n"] > 0, f"{plans['n']} plans")
    check(
        "every embedding matches the current encoder",
        plans["min_dim"] == plans["max_dim"] == VECTOR_DIM,
        f"dim={plans['min_dim']} expected {VECTOR_DIM}",
    )
    check("one encoder version indexed", plans["versions"] == 1, ENCODER_VERSION)
    check(
        "no degenerate plan reached the fuzzy index",
        plans["min_nodes"] >= 2,
        f"min node_count={plans['min_nodes']}",
    )

    zero = store.query(
        "SELECT count() AS n FROM apex.plan_memory FINAL WHERE length(embedding) = 0"
    )[0]["n"]
    check("no zero vectors (cosineDistance would return NaN)", zero == 0)

    outcomes = store.query(
        "SELECT count() AS n, uniqExact(job_id) AS jobs, "
        "countIf(config_source = 'observed') AS with_conf FROM apex.run_outcomes FINAL"
    )[0]
    check("run_outcomes is populated", outcomes["n"] > 0, f"{outcomes['n']} rows")
    check(
        "config is captured for some runs (contract v0.4)",
        outcomes["with_conf"] > 0,
        f"{outcomes['with_conf']}/{outcomes['n']} rows",
    )

    print("\n── the exit criterion ───────────────────────────────────────")
    # Pick the most widely-shared plan shape and one job that ran it. Selecting
    # by "job with the most shapes" instead would happily pick a fixture job
    # whose fingerprints are unique to itself -- correctly yielding zero
    # history, and testing nothing.
    # `AS sample_job`, not `AS job_id`: an alias shadowing the source column
    # makes the sibling uniqExact(job_id) resolve to the aggregate, and
    # ClickHouse rejects it (ILLEGAL_AGGREGATION).
    candidates = store.query(
        "SELECT toString(plan_fingerprint) AS fp, any(job_id) AS sample_job, "
        "uniqExact(job_id) AS jobs FROM apex.run_outcomes FINAL "
        "GROUP BY plan_fingerprint ORDER BY jobs DESC LIMIT 1"
    )
    check("a shape with cross-job history exists", bool(candidates) and candidates[0]["jobs"] > 1)
    if not candidates:
        return _finish()

    job_id, fingerprint = candidates[0]["sample_job"], candidates[0]["fp"]
    result = recall(store, job_id=job_id, plan_fingerprint=fingerprint)
    print(f"       recall(job_id={job_id}, plan_fingerprint={fingerprint[:16]}…)")
    print(f"       {candidates[0]['jobs']} jobs ran this shape")

    check("similar historical runs returned", bool(result.similar_runs),
          f"{len(result.similar_runs)} runs")
    check(
        "every returned run cites a real evidence row",
        all(r.citation and r.outcome.job_id for r in result.similar_runs),
    )
    check("a run is never evidence about itself",
          all(r.job_id != job_id for r in result.similar_runs))
    tiers = [r.tier for r in result.similar_runs]
    check(
        "exact matches rank above structural ones",
        # No structural match may precede an exact one. Comparing the tier list
        # to a sorted list of run OBJECTS (an easy mistake) is always False and
        # would make this check silently useless.
        all(
            MatchTier.EXACT not in tiers[i:]
            for i, tier in enumerate(tiers)
            if tier is MatchTier.STRUCTURAL
        ),
        f"{tiers.count(MatchTier.EXACT)} exact, {tiers.count(MatchTier.STRUCTURAL)} structural",
    )
    check("a confidence tier is reported", result.confidence in set(Confidence))
    check("confidence is explained", bool(result.confidence_reasons))
    check("untrusted fields are declared", bool(result.untrusted_fields))

    print("\n── honesty gates ────────────────────────────────────────────")
    delta = result.predicted_delta
    if delta:
        print(f"       delta={delta.delta_pct}%  meaningful={delta.meaningful}  "
              f"floor={delta.noise_floor_pct:.1f}%")
        check("a delta always carries a stated reason", bool(delta.reason))
        check(
            "a meaningful delta clears its own measured noise floor",
            (not delta.meaningful) or delta.delta_pct > delta.noise_floor_pct,
        )
        check(
            "a meaningful delta requires >=2 configurations (v0.4 rule 3)",
            (not delta.meaningful) or result.n_config_variants >= 2,
        )

    rec = result.best_known_config
    check(
        "no configuration is invented when none was captured",
        rec.available or (rec.config == {} and "config_unavailable" in rec.reason),
    )
    if rec.available:
        check("a recommendation names its contributing jobs", bool(rec.derived_from_jobs))
        check("a recommendation reports per-key support", bool(rec.key_support))

    print("\n── the honest negative ──────────────────────────────────────")
    # A job whose shapes nothing else shares must return nothing and say so,
    # rather than reaching for a loose neighbour to look useful.
    orphan = store.query(
        "SELECT any(job_id) AS sample_job FROM apex.run_outcomes FINAL "
        "GROUP BY plan_fingerprint HAVING uniqExact(job_id) = 1 LIMIT 1"
    )
    if orphan:
        empty = recall(store, job_id=orphan[0]["sample_job"])
        check(
            "a job with no shared history returns no runs",
            not empty.similar_runs,
            f"{orphan[0]['sample_job']} -> {len(empty.similar_runs)} runs",
        )
        check("...and reads as LOW", empty.confidence is Confidence.LOW)
        check(
            "...and says why",
            any("nothing to recall" in r for r in empty.confidence_reasons),
        )

    print("\n── thin history must read as LOW ────────────────────────────")
    thin = store.query(
        "SELECT toString(plan_fingerprint) AS fp, uniqExact(job_id) AS jobs "
        "FROM apex.run_outcomes FINAL GROUP BY fp HAVING jobs <= 2 "
        "ORDER BY jobs DESC LIMIT 1"
    )
    if thin:
        thin_result = recall(store, plan_fingerprint=thin[0]["fp"])
        check(
            "a shape seen in <=2 jobs is LOW confidence",
            thin_result.confidence is Confidence.LOW,
            f"{thin[0]['jobs']} job(s) -> {thin_result.confidence.value}",
        )
    else:
        print("       (no thin-history shape in the store to test)")

    print("\n── cold start (the ZEST case) ───────────────────────────────")
    sample = store.query(
        "SELECT sample_plan_json FROM apex.plan_memory FINAL "
        "WHERE node_count >= 4 ORDER BY node_count DESC LIMIT 1"
    )
    if sample:
        cold = recall(store, plan_json=sample[0]["sample_plan_json"])
        check("a never-executed plan still recalls neighbours",
              bool(cold.similar_runs), f"{len(cold.similar_runs)} structural")
        check("cold start needs no fingerprint", cold.query_plan_fingerprint is None)

    print("\n── ZEST seed provenance ─────────────────────────────────────")
    seeded = store.query(
        "SELECT count() AS n FROM apex.run_outcomes FINAL WHERE outcome_source = 'zest-seed'"
    )[0]["n"]
    print(f"       {probe_zest_dataset()}")
    check("Apex does not claim to be ZEST-seeded", seeded == 0, f"{seeded} seeded rows")

    return _finish()


def _finish() -> int:
    print()
    if _failures:
        print(f"\033[31m{len(_failures)} check(s) failed:\033[0m " + "; ".join(_failures))
        return 1
    print("\033[32mAll checks passed.\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
