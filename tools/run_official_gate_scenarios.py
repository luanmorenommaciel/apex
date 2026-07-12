#!/usr/bin/env python3
"""Run official G1/G2 scenarios through the Codex deterministic path."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.clickstack_mvp import append_envelope
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.telemetry import build_telemetry


SCENARIO_DIR = ROOT / "pacote-comum" / "scenarios"
PLAN_GENERATOR = ROOT / "pacote-comum" / "generators" / "plan_generator.py"
GENERATED_DIR = ROOT / "evidence" / "generated" / "official-scenarios"
STORE_PATH = GENERATED_DIR / "telemetry-store.ndjson"

G1_SCENARIOS = ["no_skew_baseline.yaml"]
G2_SCENARIOS = [
    "skew_on_join_30x.yaml",
    "gc_pressure_25pct.yaml",
    "shuffle_spill_disk.yaml",
    "oom_on_aggregation.yaml",
    "cartesian_product.yaml",
]

SEVERITY_ORDER = {
    "none": 0,
    "info": 1,
    "warning": 2,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

EXPECTED_KIND_BY_CLASS = {
    "data_skew_on_join_key": "shuffle_skew_candidate",
    "gc_pressure": "gc_pressure_candidate",
    "shuffle_spill": "shuffle_spill_candidate",
    "oom_task_failure": "oom_candidate",
    "cartesian_product": "cartesian_product_candidate",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", choices=["g1", "g2", "all"])
    args = parser.parse_args()

    scenarios = []
    if args.gate in ("g1", "all"):
        scenarios.extend(G1_SCENARIOS)
    if args.gate in ("g2", "all"):
        scenarios.extend(G2_SCENARIOS)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    if STORE_PATH.exists():
        STORE_PATH.unlink()

    results = []
    print(f"official_gate_runner_version=1")
    print(f"gate={args.gate}")
    print(f"plan_generator={PLAN_GENERATOR}")
    print(f"generated_dir={GENERATED_DIR}")
    print("")

    for scenario_name in scenarios:
        result = run_scenario(scenario_name)
        results.append(result)

    if STORE_PATH.exists():
        STORE_PATH.unlink()

    print("### summary")
    print(json.dumps(results, indent=2, sort_keys=True))
    passed = all(result["passed"] for result in results)
    print(f"OVERALL_STATUS={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


def run_scenario(scenario_name):
    scenario_path = SCENARIO_DIR / scenario_name
    output_path = GENERATED_DIR / scenario_name.replace(".yaml", ".ndjson")

    print(f"### scenario {scenario_name}")
    print(f"scenario_path={scenario_path}")
    print(f"output_path={output_path}")

    command = [sys.executable, str(PLAN_GENERATOR), str(scenario_path), str(output_path)]
    print("plan_generator_command=" + " ".join(command))
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    completed = subprocess.run(
        command, capture_output=True, text=True, check=False, env=env
    )
    print(f"plan_generator_exit_code={completed.returncode}")
    print("plan_generator_stdout_begin")
    print(completed.stdout.rstrip())
    print("plan_generator_stdout_end")
    print("plan_generator_stderr_begin")
    print(completed.stderr.rstrip())
    print("plan_generator_stderr_end")
    if completed.returncode != 0:
        result = {
            "scenario": scenario_name,
            "passed": False,
            "reason": "plan_generator_failed",
        }
        print("assessment=" + json.dumps(result, sort_keys=True))
        print("")
        return result

    config = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    events = load_ndjson(output_path)
    envelope = build_telemetry(events)
    append_envelope(STORE_PATH, envelope)
    findings = diagnose_findings(STORE_PATH, envelope["job_id"])
    assessment = assess(config, findings)

    print("telemetry_envelope_begin")
    print(json.dumps(envelope, indent=2, sort_keys=True))
    print("telemetry_envelope_end")
    print("findings_begin")
    print(json.dumps(findings, indent=2, sort_keys=True))
    print("findings_end")
    print("assessment=" + json.dumps(assessment, sort_keys=True))
    print("")
    return {
        "scenario": scenario_name,
        "passed": assessment["passed"],
        "reason": assessment["reason"],
    }


def load_ndjson(path):
    events = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def assess(config, findings):
    scenario_id = config["scenario_id"]
    klass = config.get("anti_pattern", {}).get("class", "none")

    if klass == "none":
        warning_or_higher = [
            finding
            for finding in findings
            if severity_rank(finding.get("severity")) >= severity_rank("warning")
        ]
        return {
            "scenario_id": scenario_id,
            "passed": not warning_or_higher,
            "reason": "baseline_clean" if not warning_or_higher else "false_positive",
            "unexpected_findings": warning_or_higher,
        }

    expected_kind = EXPECTED_KIND_BY_CLASS.get(klass)
    acceptance = config.get("acceptance") or {}
    min_severity = acceptance.get("min_severity") or config.get("anti_pattern", {}).get(
        "severity", "warning"
    )
    matching = [finding for finding in findings if finding.get("kind") == expected_kind]
    if not matching:
        return {
            "scenario_id": scenario_id,
            "passed": False,
            "reason": "expected_detector_not_triggered",
            "expected_kind": expected_kind,
            "min_severity": min_severity,
            "actual_kinds": [finding.get("kind") for finding in findings],
        }

    best = max(matching, key=lambda finding: severity_rank(finding.get("severity")))
    severity_ok = severity_rank(best.get("severity")) >= severity_rank(min_severity)
    return {
        "scenario_id": scenario_id,
        "passed": severity_ok,
        "reason": "detected" if severity_ok else "severity_below_expected",
        "expected_kind": expected_kind,
        "min_severity": min_severity,
        "actual_severity": best.get("severity"),
        "finding": best,
    }


def severity_rank(value):
    return SEVERITY_ORDER.get(str(value or "none").lower(), 0)


if __name__ == "__main__":
    raise SystemExit(main())
