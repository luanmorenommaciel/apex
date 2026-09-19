"""Offline routing contract for the public tail-outlier package command.

These source-level checks deliberately do not invoke PowerShell, Docker, Spark,
or ClickHouse.  They prove routing and fail-closed guards, not runtime success.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "dev" / "scripts" / "e2e_canonical.ps1"
PACKAGE = ROOT / "scripts" / "apex.ps1"
WORKLOAD = ROOT / "dev" / "jobs" / "tail_outlier.py"


def _tail_outlier_gate(source: str) -> str:
    start = source.index("function Invoke-TailOutlierGate {")
    end = source.index("\nfunction Show-Help", start)
    return source[start:end]


def test_canonical_runner_accepts_and_maps_tail_outlier():
    source = CANONICAL.read_text(encoding="utf-8")

    assert WORKLOAD.is_file()
    assert "[ValidateSet('skew_join', 'tail_outlier', 'spill', 'bad_shuffle', 'driver_oom')]" in source
    assert "tail_outlier = 'tail_outlier.py'" in source
    assert "$result = Invoke-SparkJob -Name $name -Job $jobs[$name] -Aqe 'off'" in source


def test_public_gate_reaches_canonical_tail_outlier():
    source = PACKAGE.read_text(encoding="utf-8")
    gate = _tail_outlier_gate(source)

    assert "scenario are not available in this repo yet" not in gate
    assert "Invoke-TailOutlierGate" in source.split("switch ($Action)", 1)[1]
    assert "'-Scenario', 'tail_outlier'" in gate
    assert "dev/scripts/e2e_canonical.ps1" in gate


def test_public_gate_remains_fail_closed_and_llm_free():
    gate = _tail_outlier_gate(PACKAGE.read_text(encoding="utf-8"))

    assert "Tail-outlier job_id missing" in gate
    assert "$engineExitCode -ne 0" in gate
    assert "Tail-outlier ENGINE analysis failed" in gate
    assert "tail_outlier_watcher" in gate
    assert "--no-crew" in gate
    assert "APEX_TAIL_OUTLIER_GATE=passed" in gate
    assert "llm_calls=0" in gate
