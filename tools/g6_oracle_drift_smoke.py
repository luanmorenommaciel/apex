"""Run the G6 oracle drift smoke for one scenario and one real Spark event log.

This does not change thresholds. It generates the official synthetic log for the
scenario, runs the existing oracle comparison, and writes an auditable JSON
summary that can later be scheduled by CI.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Apex G6 oracle drift smoke.")
    parser.add_argument(
        "--scenario",
        default="scenarios/skew_on_join_30x.yaml",
        help="Scenario YAML used to generate the synthetic log.",
    )
    parser.add_argument(
        "--real-log",
        default="real_log.ndjson",
        help="Real Spark event log (.ndjson, .zstd, or rolling-log directory).",
    )
    parser.add_argument(
        "--work-dir",
        default="evidence/generated/g6-oracle-drift",
        help="Directory where generated synthetic evidence is written.",
    )
    parser.add_argument(
        "--summary",
        default="evidence/g6-oracle-drift-summary.json",
        help="JSON summary output path.",
    )
    args = parser.parse_args(argv)

    scenario = Path(args.scenario)
    real_log = Path(args.real_log)
    work_dir = Path(args.work_dir)
    summary_path = Path(args.summary)
    synthetic_log = work_dir / "synthetic.ndjson"

    work_dir.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    generated_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    plan_cmd = [
        sys.executable,
        "generators/plan_generator.py",
        str(scenario),
        str(synthetic_log),
    ]
    oracle_cmd = [
        sys.executable,
        "oracle/compare.py",
        str(scenario),
        str(synthetic_log),
        str(real_log),
    ]

    plan = run_command(plan_cmd)
    oracle = None
    status = "failed"
    if plan.returncode == 0:
        oracle = run_command(oracle_cmd)
        status = "passed" if oracle.returncode == 0 else "failed"

    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    summary = {
        "gate": "G6",
        "name": "oracle_drift_smoke",
        "status": status,
        "generated_at": generated_at,
        "elapsed_ms": elapsed_ms,
        "scenario": str(scenario),
        "real_log": str(real_log),
        "synthetic_log": str(synthetic_log),
        "commands": {
            "plan_generator": plan_cmd,
            "oracle_compare": oracle_cmd,
        },
        "plan_generator": {
            "returncode": plan.returncode,
            "stdout": plan.stdout,
            "stderr": plan.stderr,
        },
        "oracle_compare": None
        if oracle is None
        else {
            "returncode": oracle.returncode,
            "stdout": oracle.stdout,
            "stderr": oracle.stderr,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
