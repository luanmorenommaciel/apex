"""Testes dos detectores deterministicos (G2 / ISSUE-A01) — portados do spike."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from apex import apexlib, detectors  # noqa: E402


def synth(scenario_name, tmp_path):
    scen = str(ROOT / "scenarios" / scenario_name)
    log = str(tmp_path / "log.ndjson")
    r = subprocess.run([sys.executable, str(ROOT / "generators/plan_generator.py"), scen, log],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return apexlib.read_events(log), scen, log


def run_watcher(scen, log):
    return subprocess.run([sys.executable, str(ROOT / "watchers/pattern_watcher.py"), scen, log],
                          capture_output=True, text=True)


def test_gc_detector_critical(tmp_path):
    events, scen, log = synth("gc_pressure_25pct.yaml", tmp_path)
    hits = detectors.detect_gc(events, detectors.load_thresholds())
    assert hits and hits[0]["severity"] == "critical"
    assert abs(hits[0]["evidence"]["gc_ratio"] - 0.25) < 0.02
    assert "GATE VERDE" in run_watcher(scen, log).stdout


def test_shuffle_detector_disk_spill_critical(tmp_path):
    events, scen, log = synth("shuffle_spill_disk.yaml", tmp_path)
    hits = detectors.detect_shuffle(events, detectors.load_thresholds())
    assert hits and hits[0]["severity"] == "critical"
    assert hits[0]["evidence"]["disk_bytes_spilled"] > 0
    assert "GATE VERDE" in run_watcher(scen, log).stdout


def test_oom_detector_critical(tmp_path):
    events, scen, log = synth("oom_on_aggregation.yaml", tmp_path)
    hits = detectors.detect_oom(events)
    assert hits and hits[0]["evidence"]["oom_tasks"] == 2
    assert "OutOfMemoryError" in hits[0]["title"]
    assert "GATE VERDE" in run_watcher(scen, log).stdout


def test_plans_detector_cartesian_critical(tmp_path):
    events, scen, log = synth("cartesian_product.yaml", tmp_path)
    hits = detectors.detect_plans(events, detectors.load_thresholds())
    assert any(f["severity"] == "critical" and "CartesianProduct" in f["title"] for f in hits)
    assert "GATE VERDE" in run_watcher(scen, log).stdout


def test_baseline_fires_no_detector(tmp_path):
    events, scen, log = synth("no_skew_baseline.yaml", tmp_path)
    findings = detectors.run_all(events)
    bad = [f for f in findings if f["severity"] in ("warning", "critical")]
    assert not bad, f"falso positivo: {bad}"
    r = run_watcher(scen, log)
    assert r.returncode == 0 and "Baseline limpo em todos os detectores" in r.stdout


def test_skew_scenario_does_not_trip_other_detectors(tmp_path):
    # o cenario de skew nao pode disparar gc/shuffle/oom por acidente
    events, _, _ = synth("skew_on_join_30x.yaml", tmp_path)
    findings = detectors.run_all(events)
    bad = [f for f in findings if f["severity"] in ("warning", "critical")]
    assert not bad, f"cross-fire indevido: {bad}"
