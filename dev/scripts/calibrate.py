#!/usr/bin/env python3
"""Calibration harness — prove each pathology is a MECHANISM, not noise.

Runs each pathology job N times against the local cluster, pulls the real stage
metrics from the Spark History Server REST API after every run, extracts the
per-pathology signal, and reports the coefficient of variation (CV = sample
std / mean) across runs. A signal whose CV is comparable to the measured noise
floor is not a pathology — the report says so explicitly.

Noise floor: the `control` scenario (bad_shuffle with FIX=on — a balanced
200-partition reduce over the same data) measures pure run-to-run jitter of
task durations at the current scale. Pathology signals are judged against it.

Tail-bound acceptance (verify-lane closed form): the skew stage is genuinely
tail-bound iff p99/p50 > (n_tasks - 1)/(slots - 1), with slots = total alive
worker cores from the Spark master API. Volume cancels out of that ratio, so
the only levers are slots and n — skew_join pins n=100 so p99 (nearest-rank)
reaches the single hot task.

Usage (host, from dev/):  python3 scripts/calibrate.py --runs 3
                          make calibrate RUNS=3
Stdlib only. Writes out/calibration-<UTC ts>.json and prints a markdown table.
Set APEX_CANONICAL_CH_PASSWORD (+ optional _USER/_URL) to also assert the
skew_split plan_transition per AQE run against canonical ClickHouse.
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
from datetime import datetime, timezone
from pathlib import Path

DEV_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = DEV_DIR / "out"
HISTORY_URL = os.environ.get("APEX_HISTORY_URL", "http://localhost:18080")
MASTER_URL = os.environ.get("APEX_MASTER_URL", "http://localhost:8080")
QUANTILES = "0.0,0.5,0.99,1.0"          # indices: 0=min 1=p50 2=p99 3=max

# scenario -> (job file, env toggles, extra submit args, expect_failure)
SCENARIOS: dict[str, dict] = {
    "skew_join":     {"job": "skew_join.py",  "env": {"APEX_AQE": "off"}, "args": []},
    "skew_join_aqe": {"job": "skew_join.py",  "env": {"APEX_AQE": "on"},  "args": []},
    "spill":         {"job": "spill.py",      "env": {"APEX_FIX": "off"}, "args": []},
    "bad_shuffle":   {"job": "bad_shuffle.py", "env": {"APEX_FIX": "off"}, "args": []},
    "control":       {"job": "bad_shuffle.py", "env": {"APEX_FIX": "on"},  "args": []},
    "driver_oom":    {"job": "driver_oom.py", "env": {"APEX_SAFE": "off"},
                      "args": ["--driver-memory", "512m"], "expect_failure": True},
}
DEFAULT_SCENARIOS = ["skew_join", "skew_join_aqe", "spill", "bad_shuffle", "control", "driver_oom"]

APP_ID_RE = re.compile(r"APEX_SESSION job_id=(app-\d{14}-\d{4})")


def submit(scenario: str, run_idx: int) -> tuple[int, str, float]:
    """Run one job via docker compose exec; return (exit_code, log_text, wall_s)."""
    spec = SCENARIOS[scenario]
    env_flags = []
    for key, val in {"APEX_AQE": "off", "APEX_FIX": "off", "APEX_SAFE": "off", **spec["env"]}.items():
        env_flags += ["-e", f"{key}={val}"]
    cmd = (["docker", "compose", "-f", "docker-compose.yml", "exec", "-T", *env_flags,
            "spark-master", "/opt/spark/bin/spark-submit",
            "--master", "spark://spark-master:7077", *spec["args"],
            f"/opt/apex/jobs/{spec['job']}"])
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=DEV_DIR, capture_output=True, text=True, timeout=3600)
    wall = time.monotonic() - start
    log = proc.stdout + proc.stderr
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / f"calibrate-{scenario}-{run_idx}.log").write_text(log)
    return proc.returncode, log, wall


def _get_json(url: str):
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def alive_slots() -> int:
    """Total cores of ALIVE workers — the lab's true slot count (closed-form input)."""
    try:
        data = _get_json(f"{MASTER_URL}/json/")
        return int(sum(w["cores"] for w in data.get("workers", []) if w.get("state") == "ALIVE"))
    except Exception:
        return 0


def wait_stages(app_id: str, timeout_s: int = 240) -> list[dict]:
    """Poll the History Server until the app is indexed with completed stages."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            stages = _get_json(f"{HISTORY_URL}/api/v1/applications/{app_id}/stages")
            done = [s for s in stages if s.get("status") == "COMPLETE"]
            if done:
                return done
        except Exception:
            pass
        time.sleep(5)
    raise TimeoutError(f"history server did not index {app_id} within {timeout_s}s")


def task_summary(app_id: str, stage_id: int, attempt: int) -> dict:
    return _get_json(f"{HISTORY_URL}/api/v1/applications/{app_id}"
                     f"/stages/{stage_id}/{attempt}/taskSummary?quantiles={QUANTILES}")


def ch_transitions(app_id: str, wait_seconds: int = 90) -> list[str] | None:
    """transition_type list from canonical ClickHouse, or None if not configured.

    Polls: OTLP ingestion is asynchronous (collector queue + async_insert), so a
    query fired the second the job exits can legitimately miss rows that land a
    few seconds later.
    """
    password = os.environ.get("APEX_CANONICAL_CH_PASSWORD")
    if not password:
        return None
    user = os.environ.get("APEX_CANONICAL_CH_USER", "apex")
    url = os.environ.get("APEX_CANONICAL_CH_URL", "http://127.0.0.1:8123").rstrip("/")
    sql = (f"SELECT transition_type FROM apex.plan_transitions "
           f"WHERE job_id = '{app_id}' ORDER BY update_seq FORMAT TSV")
    deadline = time.monotonic() + wait_seconds
    while True:
        req = urllib.request.Request(
            url, data=sql.encode("utf-8"), method="POST",
            headers={"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                rows = [line for line in resp.read().decode("utf-8").splitlines() if line]
            if rows:
                return rows
        except Exception:
            pass
        if time.monotonic() >= deadline:
            return []
        time.sleep(5)


def ch_stage_p99(app_id: str, wait_seconds: int = 90) -> dict | None:
    """The plugin's own p50/p99 for the heaviest shuffle stage — the exact
    statistic verify's closed form consumes (from apex.spark_events)."""
    password = os.environ.get("APEX_CANONICAL_CH_PASSWORD")
    if not password:
        return None
    user = os.environ.get("APEX_CANONICAL_CH_USER", "apex")
    url = os.environ.get("APEX_CANONICAL_CH_URL", "http://127.0.0.1:8123").rstrip("/")
    sql = (f"SELECT stage_id, task_count, task_duration_p50_ms, task_duration_p99_ms "
           f"FROM apex.spark_events WHERE job_id = '{app_id}' "
           f"ORDER BY shuffle_read_bytes DESC LIMIT 1 FORMAT JSONEachRow")
    deadline = time.monotonic() + wait_seconds
    while True:
        req = urllib.request.Request(
            url, data=sql.encode("utf-8"), method="POST",
            headers={"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                rows = [json.loads(line) for line in resp.read().decode("utf-8").splitlines() if line]
            if rows:
                return rows[0]
        except Exception:
            pass
        if time.monotonic() >= deadline:
            return None
        time.sleep(5)


def q(metrics: dict, field: str, idx: int) -> float:
    vals = metrics.get(field)
    return float(vals[idx]) if vals else 0.0


def extract_signal(scenario: str, app_id: str, log: str, exit_code: int,
                   wall_s: float, slots: int) -> dict:
    """Per-pathology signal from real stage metrics."""
    base = {"app_id": app_id, "exit_code": exit_code, "wall_s": round(wall_s, 1)}

    if scenario == "driver_oom":
        oom = "OutOfMemoryError" in log or "java heap space" in log.lower()
        return {**base, "oom_in_log": oom, "failed_as_expected": exit_code != 0 and oom}

    stages = wait_stages(app_id)
    total_spill = sum(float(s.get("diskBytesSpilled", 0)) for s in stages)

    if scenario == "spill":
        fat = max(stages, key=lambda s: float(s.get("diskBytesSpilled", 0)))
        ts = task_summary(app_id, fat["stageId"], fat["attemptId"])
        return {**base, "spill_disk_bytes": int(total_spill),
                "signal_stage": fat["stageId"],
                "stage_duration_max_ms": q(ts, "duration", 3)}

    # skew_join / bad_shuffle / control: the signal stage is the heaviest
    # shuffle-read stage (for skew_join AQE=off that is the sort-merge join read).
    read_stages = [s for s in stages if float(s.get("shuffleReadBytes", 0)) > 0]
    if not read_stages:
        return {**base, "error": "no shuffle-read stage found", "stage_count": len(stages)}
    sig = max(read_stages, key=lambda s: float(s.get("shuffleReadBytes", 0)))
    ts = task_summary(app_id, sig["stageId"], sig["attemptId"])
    dur_med, dur_p99, dur_max = q(ts, "duration", 1), q(ts, "duration", 2), q(ts, "duration", 3)
    hot_bytes = q(ts.get("shuffleReadMetrics", {}), "readBytes", 3)
    n_tasks = int(sig["numTasks"])
    out = {**base,
           "signal_stage": sig["stageId"],
           "stage_tasks": n_tasks,
           "slots": slots,
           "stage_shuffle_read_bytes": int(float(sig.get("shuffleReadBytes", 0))),
           "hot_partition_bytes": int(hot_bytes),
           "task_dur_med_ms": dur_med,
           "task_dur_p99_ms": dur_p99,
           "task_dur_max_ms": dur_max,
           "p99_p50": round(dur_p99 / dur_med, 2) if dur_med > 0 else None,
           "skew_ratio": round(dur_max / dur_med, 2) if dur_med > 0 else None,
           "stage_spill_bytes": int(float(sig.get("diskBytesSpilled", 0)))}
    # verify-lane closed form: tail-bound iff p99/p50 > (n-1)/(slots-1)
    if slots > 1 and dur_med > 0:
        threshold = (n_tasks - 1) / (slots - 1)
        out["tail_threshold"] = round(threshold, 2)
        out["tail_bound"] = bool(out["p99_p50"] and out["p99_p50"] > threshold)
    if scenario in ("skew_join", "skew_join_aqe"):
        # The plugin's own p50/p99 from apex.spark_events — the statistic the
        # closed form is actually evaluated on downstream.
        plugin = ch_stage_p99(app_id) if scenario == "skew_join" else None
        if plugin:
            p50, p99 = float(plugin["task_duration_p50_ms"]), float(plugin["task_duration_p99_ms"])
            out["plugin_p50_ms"], out["plugin_p99_ms"] = p50, p99
            out["plugin_p99_p50"] = round(p99 / p50, 2) if p50 > 0 else None
            if slots > 1 and p50 > 0:
                out["plugin_tail_bound"] = bool(out["plugin_p99_p50"]
                                                and out["plugin_p99_p50"] > (n_tasks - 1) / (slots - 1))
    if scenario == "skew_join_aqe":
        transitions = ch_transitions(app_id)
        if transitions is not None:
            out["plan_transitions"] = transitions
            out["skew_split_fired"] = "skew_split" in transitions
    return out


def cv(values: list[float]) -> float | None:
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    mean = statistics.mean(vals)
    if mean == 0:
        return 0.0 if all(v == 0 for v in vals) else None
    return statistics.stdev(vals) / mean   # sample std (ddof=1)


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--scenarios", default=",".join(DEFAULT_SCENARIOS))
    args = parser.parse_args()
    scenarios = [s for s in args.scenarios.split(",") if s in SCENARIOS]
    if not scenarios:
        print(f"no valid scenarios in {args.scenarios!r}; choices: {sorted(SCENARIOS)}")
        return 2

    slots = alive_slots()
    print(f"alive worker slots: {slots}")
    report: dict = {"started_utc": datetime.now(timezone.utc).isoformat(),
                    "slots": slots, "runs": args.runs, "scenarios": {}}
    for scenario in scenarios:
        print(f"\n=== {scenario}: {args.runs} runs ===", flush=True)
        runs = []
        for i in range(args.runs):
            exit_code, log, wall = submit(scenario, i)
            m = APP_ID_RE.search(log)
            app_id = m.group(1) if m else None
            print(f"  run {i}: exit={exit_code} wall={wall:.0f}s app={app_id}", flush=True)
            if app_id is None:
                runs.append({"exit_code": exit_code, "error": "no APEX_SESSION app id in log"})
                continue
            try:
                runs.append(extract_signal(scenario, app_id, log, exit_code, wall, slots))
            except Exception as exc:
                runs.append({"app_id": app_id, "exit_code": exit_code,
                             "error": f"{type(exc).__name__}: {exc}"})
            print(f"        {json.dumps(runs[-1], sort_keys=True)}", flush=True)
        report["scenarios"][scenario] = runs

    # ── CV summary ──────────────────────────────────────────────────────────
    summary: dict[str, dict] = {}
    for scenario, runs in report["scenarios"].items():
        good = [r for r in runs if "error" not in r]
        entry: dict = {"runs_ok": len(good)}
        if scenario == "driver_oom":
            entry["oom_every_run"] = bool(good) and all(r.get("failed_as_expected") for r in good)
        else:
            for field, label in [("skew_ratio", "skew_ratio_cv"),
                                 ("p99_p50", "p99_p50_cv"),
                                 ("task_dur_max_ms", "hot_task_dur_cv"),
                                 ("spill_disk_bytes", "spill_bytes_cv"),
                                 ("hot_partition_bytes", "hot_partition_bytes_cv")]:
                vals = [r.get(field) for r in good if r.get(field) is not None]
                if vals:
                    entry[label] = None if len(vals) < 2 else round(cv(vals), 4)
                    entry[f"{field}_values"] = vals
            if any("tail_bound" in r for r in good):
                entry["tail_bound_every_run"] = all(r.get("tail_bound") for r in good)
                entry["tail_threshold"] = good[0].get("tail_threshold")
            if any("plugin_tail_bound" in r for r in good):
                entry["plugin_tail_bound_every_run"] = all(r.get("plugin_tail_bound") for r in good)
                vals = [r["plugin_p99_p50"] for r in good if r.get("plugin_p99_p50") is not None]
                entry["plugin_p99_p50_values"] = vals
            if any("skew_split_fired" in r for r in good):
                entry["skew_split_every_run"] = all(r.get("skew_split_fired") for r in good)
        summary[scenario] = entry
    report["summary"] = summary

    noise = summary.get("control", {}).get("hot_task_dur_cv")
    report["noise_floor_cv"] = noise

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / f"calibration-{ts}.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True))

    def first_not_none(*vals):
        return next((v for v in vals if v is not None), None)

    print(f"\n{'scenario':<16} {'ok':>2}  {'signal CV':>10}  verdict")
    print("-" * 78)
    for scenario, entry in summary.items():
        if scenario == "driver_oom":
            verdict = "MECHANICAL (binary OOM)" if entry.get("oom_every_run") else "NOT REPRODUCIBLE"
            print(f"{scenario:<16} {entry['runs_ok']:>2}  {'binary':>10}  {verdict}")
            continue
        if scenario == "control":
            main_cv = entry.get("hot_task_dur_cv")
            print(f"{scenario:<16} {entry['runs_ok']:>2}  {pct(main_cv):>10}  noise floor = {pct(main_cv)}")
            continue
        if scenario == "skew_join_aqe":
            fired = entry.get("skew_split_every_run")
            verdict = {True: "SKEW_SPLIT FIRED every run", False: "skew_split MISSING",
                       None: "no ClickHouse creds — check plan_transitions manually"}[fired]
            print(f"{scenario:<16} {entry['runs_ok']:>2}  {pct(entry.get('hot_task_dur_cv')):>10}  {verdict}")
            continue
        main_cv = first_not_none(entry.get("skew_ratio_cv"), entry.get("spill_bytes_cv"),
                                 entry.get("hot_task_dur_cv"))
        parts = []
        if "tail_bound_every_run" in entry:
            parts.append(f"tail-bound(REST) {'✓' if entry['tail_bound_every_run'] else '✗'} "
                         f"(threshold {entry.get('tail_threshold')})")
        if "plugin_tail_bound_every_run" in entry:
            parts.append(f"tail-bound(plugin) {'✓' if entry['plugin_tail_bound_every_run'] else '✗'} "
                         f"{entry.get('plugin_p99_p50_values')}")
        if noise is not None and main_cv is not None:
            parts.append("MECHANISM (signal stable vs floor)"
                         if main_cv <= max(0.15, 2 * noise) else
                         f"WEAK (CV {pct(main_cv)} vs floor {pct(noise)})")
        print(f"{scenario:<16} {entry['runs_ok']:>2}  {pct(main_cv):>10}  {'; '.join(parts)}")
    print(f"\nfull report: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
