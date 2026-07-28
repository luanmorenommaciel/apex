#!/usr/bin/env python3
"""Two-arm replay on the calibrated dev bench, with the positive control.

Runs dev's `skew_join` job in two configurations — BASELINE (AQE off, the
observed pathology) and TREATMENT (AQE on, the proposed skew fix) — interleaved
`REPS` times per arm, and reduces the two arms with `apex_verify.replay`.

THE COMPARISON LEVEL IS THE STAGE, NOT THE JOB (contract rule 2). The skew fix
acts on one stage; the job carries ~25s of scans, aggregates and startup the
fix cannot touch, so a job-level comparison dilutes the fix's ceiling (~1s) to
~4% — inside ANY job-level floor, unresolvable by construction. The metric is
therefore the wall duration of the heaviest shuffle-read stage, and the noise
floor is measured from the baseline arm's stage durations — never inherited
from another level or scale (the 5.8% / 9.2% / 37.7% lesson). Job-level
durations are still printed, as context, with their own floor.

This bench is the contract-rule-1 bench: n=100 tasks, 8 slots, p99/p50 =
17.7–20.6 against a closed-form tail-bound threshold of 99/7 = 14.14, with
`skew_split` firing 3/3 under AQE. A skew fix genuinely CAN matter here — which
is exactly what makes the run a POSITIVE CONTROL: if this harness cannot
resolve a fix known to act on this exact shape, its "no measurable change"
verdicts are unproven. The control is evaluated on every invocation and is
non-negotiable: it fails, the exit code fails.

A caveat the control itself surfaced on its first live run: the closed form
being satisfied (p99/p50 > threshold) means the fix CAN matter; it does not
guarantee the effect clears the measured floor. But the deeper finding was a
MIS-SPECIFIED CONTROL (contract rule 4 corollary): the first control ran full
AQE, which coalesced 100→17 partitions and raised the median task 61–92ms →
508–792ms — W was NOT conserved, so it tested a repartitioning that the
makespan model explicitly refuses to model (see predict.classify_fix). The
RE-SPECIFIED control holds the partition count constant: treatment is AQE on
with `spark.sql.adaptive.coalescePartitions.enabled=false`, a PURE tail
redistribution — the fix class the model covers.

Verdicts are emitted as the rule-4 PAIR: `mechanism_confirmed` (the skew_split
transition fired and/or the tail ratio collapsed beyond its own measured
floor) plus `runtime_certified` or `runtime_unresolved` (|delta| vs the
measured stage-level CV). If even this W-conserving control cannot clear the
runtime floor, that is the honest limit of laptop scale — reported, not tuned
away.

Usage (host, from verify/):  python3 scripts/run_replay.py [--reps 3]
Exit 0 iff the positive control passes. Stdlib + apex_verify only.
Set APEX_CANONICAL_CH_PASSWORD (+ optional _USER/_URL) to also assert that
`skew_split` fired in apex.plan_transitions on every treatment run — the
mechanism check behind the timing check.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from apex_verify.guardrails import runtime_cv_pct  # noqa: E402
from apex_verify.replay import (  # noqa: E402
    Arm,
    MechanismEvidence,
    analyse_replay,
    evaluate_positive_control,
)

DEV_DIR = Path(__file__).resolve().parent.parent.parent / "dev"
OUT_DIR = DEV_DIR / "out"
HISTORY_URL = os.environ.get("APEX_HISTORY_URL", "http://localhost:18080")
MASTER_URL = os.environ.get("APEX_MASTER_URL", "http://localhost:8080")

APP_ID_RE = re.compile(r"APEX_SESSION job_id=(app-\d{14}-\d{4})")
_TS_FMT = "%Y-%m-%dT%H:%M:%S.%fGMT"

# The conf overlay each arm actually runs with — this is also what the
# attributability rule (contract rule 3) counts. Two distinct configs, which
# is the entire point of the two-arm design.
BASELINE_CONFIG = {
    "spark.sql.adaptive.enabled": "false",
    "spark.sql.autoBroadcastJoinThreshold": "-1",
    "spark.sql.shuffle.partitions": "100",
}
TREATMENT_CONFIG = {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "16m",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
    # Re-specified control (rule 4 corollary): coalesce OFF holds the partition
    # count constant, so the split is a pure tail redistribution with W
    # conserved — the fix class the makespan model covers. With coalesce on
    # (the first control) 100 partitions became 17 and W grew 10-30%.
    "spark.sql.adaptive.coalescePartitions.enabled": "false",
    "spark.sql.autoBroadcastJoinThreshold": "-1",
    "spark.sql.shuffle.partitions": "100",
}


def submit_one(arm: str, rep: int) -> str:
    """Submit one skew_join run; return its app_id. arm: baseline|treatment."""
    aqe = "on" if arm == "treatment" else "off"
    cmd = (["docker", "compose", "-f", "docker-compose.yml", "exec", "-T",
            "-e", f"APEX_AQE={aqe}", "-e", "APEX_FIX=off", "-e", "APEX_SAFE=off",
            # Coalesce OFF in the treatment arm: the control is a pure tail
            # redistribution at constant partition count (rule 4 corollary).
            "-e", "APEX_AQE_COALESCE=false",
            "spark-master", "/opt/spark/bin/spark-submit",
            "--master", "spark://spark-master:7077",
            "/opt/apex/jobs/skew_join.py"])
    proc = subprocess.run(cmd, cwd=DEV_DIR, capture_output=True, text=True, timeout=3600)
    log = proc.stdout + proc.stderr
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / f"replay-{arm}-{rep}.log").write_text(log)
    if proc.returncode != 0:
        raise RuntimeError(f"{arm} rep {rep} exited {proc.returncode}; see out/replay-{arm}-{rep}.log")
    m = APP_ID_RE.search(log)
    if not m:
        raise RuntimeError(f"{arm} rep {rep}: no APEX_SESSION app id in log")
    return m.group(1)


def _get_json(url: str):
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def alive_slots() -> int:
    try:
        data = _get_json(f"{MASTER_URL}/json/")
        return int(sum(w["cores"] for w in data.get("workers", []) if w.get("state") == "ALIVE"))
    except Exception:
        return 0


def run_metrics(app_id: str, timeout_s: int = 240) -> dict:
    """Per-run metrics from the History Server, at both comparison levels.

    Returns the STAGE-level comparison metric (wall duration of the heaviest
    shuffle-read stage — the level the skew fix acts on), the job-level app
    duration (context only), and the stage's p99/p50 (the mechanism evidence:
    a working skew fix collapses the tail ratio).
    """
    deadline = time.monotonic() + timeout_s
    while True:
        try:
            app = _get_json(f"{HISTORY_URL}/api/v1/applications/{app_id}")
            attempts = app.get("attempts") or []
            stages = _get_json(f"{HISTORY_URL}/api/v1/applications/{app_id}/stages")
            done = [s for s in stages if s.get("status") == "COMPLETE"]
            if attempts and attempts[-1].get("completed") and done:
                break
        except Exception:
            pass
        if time.monotonic() >= deadline:
            raise TimeoutError(f"history server did not index {app_id} within {timeout_s}s")
        time.sleep(5)

    job_ms = float(attempts[-1]["duration"])
    read_stages = [s for s in done if float(s.get("shuffleReadBytes", 0)) > 0]
    sig = max(read_stages, key=lambda s: float(s["shuffleReadBytes"]))
    t0 = datetime.strptime(sig["submissionTime"], _TS_FMT)
    t1 = datetime.strptime(sig["completionTime"], _TS_FMT)
    stage_ms = (t1 - t0).total_seconds() * 1000.0
    summary = _get_json(
        f"{HISTORY_URL}/api/v1/applications/{app_id}"
        f"/stages/{sig['stageId']}/{sig['attemptId']}/taskSummary?quantiles=0.5,0.99"
    )
    p50, p99 = (float(v) for v in summary["duration"])
    return {
        "job_ms": job_ms,
        "stage_ms": stage_ms,
        "stage_id": sig["stageId"],
        "tasks": int(sig["numTasks"]),
        "p99_p50": p99 / p50 if p50 > 0 else 0.0,
    }


def ch_skew_split_fired(app_id: str, wait_seconds: int = 90) -> bool | None:
    """Did AQE's skew_split reach apex.plan_transitions? None if unconfigured."""
    password = os.environ.get("APEX_CANONICAL_CH_PASSWORD")
    if not password:
        return None
    user = os.environ.get("APEX_CANONICAL_CH_USER", "apex")
    url = os.environ.get("APEX_CANONICAL_CH_URL", "http://127.0.0.1:8123").rstrip("/")
    sql = (f"SELECT count() FROM apex.plan_transitions "
           f"WHERE job_id = '{app_id}' AND transition_type = 'skew_split' FORMAT TSV")
    deadline = time.monotonic() + wait_seconds
    while True:
        req = urllib.request.Request(
            url, data=sql.encode("utf-8"), method="POST",
            headers={"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return int(resp.read().decode("utf-8").strip() or "0") > 0
        except Exception:
            pass
        if time.monotonic() >= deadline:
            return False
        time.sleep(5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reps", type=int, default=3, help="repetitions PER ARM (>=3 measures the floor)")
    args = parser.parse_args()

    slots = alive_slots()
    if slots > 1:
        print(f"alive worker slots: {slots} (bench calibrated for 8; closed-form threshold "
              f"(n-1)/(slots-1) at n=100 = {99 / (slots - 1):.2f})")
    else:
        print(f"alive worker slots: {slots} — cannot compute the tail-bound threshold")

    baseline = Arm(name="baseline_aqe_off", config=BASELINE_CONFIG)
    treatment = Arm(name="treatment_aqe_on", config=TREATMENT_CONFIG)
    context: dict[str, list] = {"baseline": [], "treatment": []}
    skew_split_ok: list[bool] = []

    # Interleave the arms so slow bench drift lands on both sides equally.
    for rep in range(args.reps):
        for arm_name, arm in (("baseline", baseline), ("treatment", treatment)):
            app_id = submit_one(arm_name, rep)
            m = run_metrics(app_id)
            arm.samples_ms.append(m["stage_ms"])
            context[arm_name].append(m)
            extra = ""
            if arm_name == "treatment":
                fired = ch_skew_split_fired(app_id)
                if fired is not None:
                    skew_split_ok.append(fired)
                    extra = f" skew_split={'fired' if fired else 'MISSING'}"
            print(f"  {arm_name:<10} rep {rep}: {app_id} stage={m['stage_ms']:.0f}ms "
                  f"(stage {m['stage_id']}, {m['tasks']} tasks, p99/p50={m['p99_p50']:.1f}x) "
                  f"job={m['job_ms']:.0f}ms{extra}", flush=True)

    mechanism = MechanismEvidence(
        transition_fired=all(skew_split_ok) if skew_split_ok else None,
        transition_detail=(
            f"skew_split in apex.plan_transitions on {sum(skew_split_ok)}/{len(skew_split_ok)} "
            "treatment runs" if skew_split_ok else ""
        ),
        baseline_ratios=[m["p99_p50"] for m in context["baseline"]],
        treatment_ratios=[m["p99_p50"] for m in context["treatment"]],
    )
    measurement = analyse_replay(
        bench="dev:skew_join",
        baseline=baseline,
        treatment=treatment,
        # The control's fidelity is 1.0 by construction: the bench IS the shape
        # the control fix is known to act on. Fidelity scoring applies when
        # replaying an observed finding, not when proving the harness.
        shape_fidelity=1.0,
        level="stage",
        mechanism=mechanism,
    )
    control = evaluate_positive_control(measurement)

    print(f"\nSTAGE level (the comparison — the fix acts on one stage):")
    print(f"  baseline  samples (ms): {[round(s) for s in baseline.samples_ms]}  median {measurement.baseline_ms:,.0f}")
    print(f"  treatment samples (ms): {[round(s) for s in treatment.samples_ms]}  median {measurement.treatment_ms:,.0f}")
    print(f"  delta {measurement.delta_pct:+.1f}%  |  floor ±{measurement.noise_floor_pct:.1f}%"
          "  (measured from the baseline arm at stage level)"
          f"{'  — floor UNMEASURED' if not measurement.floor_measured else ''}")
    print(f"  attributable: {measurement.attributable} — {measurement.attribution_detail}")

    # Job level is context, not the comparison: the fix's ceiling there is the
    # stage's recoverable tail (~1s of a ~25s job), inside any job-level floor.
    job_base = [m["job_ms"] for m in context["baseline"]]
    job_treat = [m["job_ms"] for m in context["treatment"]]
    job_floor = runtime_cv_pct(job_base)
    job_delta = (100.0 * (statistics.median(job_treat) - statistics.median(job_base))
                 / statistics.median(job_base) if statistics.median(job_base) > 0 else 0.0)
    print(f"\nJOB level (context only — NOT the comparison):")
    print(f"  baseline {[round(s) for s in job_base]} vs treatment {[round(s) for s in job_treat]}"
          f"  delta {job_delta:+.1f}%"
          + (f" vs job-level floor ±{job_floor:.1f}% — unresolvable at this level by construction"
             if job_floor is not None else "  (floor unmeasured)"))

    ratios_base = [f"{m['p99_p50']:.1f}x" for m in context["baseline"]]
    ratios_treat = [f"{m['p99_p50']:.1f}x" for m in context["treatment"]]
    print(f"\nmechanism: tail ratio p99/p50 baseline {ratios_base} -> treatment {ratios_treat}")
    if skew_split_ok:
        print(f"skew_split fired on {sum(skew_split_ok)}/{len(skew_split_ok)} treatment runs"
              + ("  ⚠ mechanism did not fire on every run" if not all(skew_split_ok) else ""))
    print(f"rule-4 verdicts: {' + '.join(v.value for v in measurement.verdicts) or 'none'}")
    print(f"\n{control.detail}")
    return 0 if control.passed else 1


if __name__ == "__main__":
    sys.exit(main())
