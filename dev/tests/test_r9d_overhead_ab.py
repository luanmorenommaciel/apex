from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

DEV = Path(__file__).resolve().parents[1]
SCRIPT = DEV / "scripts" / "r9d_overhead_ab.py"
SPEC = importlib.util.spec_from_file_location("r9d_overhead_ab", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_evidence_manifest_lives_under_dev_out_and_no_dead_doc_reference_remains() -> None:
    assert MODULE.EVIDENCE.parent == MODULE.OUT == DEV / "out"
    source = SCRIPT.read_text(encoding="utf-8")
    assert "docs/convergence" not in source
    assert 'ROOT / "evidence"' not in source
    assert "out/r9d-*.json" in (DEV / ".gitignore").read_text(encoding="utf-8")


def test_summarize_reports_n_median_min_max_and_iqr() -> None:
    out = MODULE.summarize([10.0, 12.0, 11.0, 20.0, 13.0, 14.0, 15.0, 16.0])
    assert out["n"] == 8
    assert out["median_s"] == 13.5
    assert out["min_s"] == 10.0
    assert out["max_s"] == 20.0
    assert out["iqr_s"] == pytest.approx(4.0, abs=1.0)


def test_summarize_handles_empty_and_short_samples() -> None:
    assert MODULE.summarize([]) == {"n": 0}
    short = MODULE.summarize([3.0, 5.0])
    assert short["n"] == 2
    assert short["median_s"] == 4.0
    assert short["iqr_s"] is None


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (dict(functional_failures=["skew_join"], measurement_missing=[], overhead_pct=1.0, accept_bands=True), "rejected"),
        (dict(functional_failures=[], measurement_missing=["soak"], overhead_pct=1.0, accept_bands=True), "inconclusive"),
        (dict(functional_failures=[], measurement_missing=[], overhead_pct=None, accept_bands=True), "inconclusive"),
        (dict(functional_failures=[], measurement_missing=[], overhead_pct=5.0, accept_bands=False),
         "measurement_complete_pending_operator_threshold_approval"),
        (dict(functional_failures=[], measurement_missing=[], overhead_pct=10.0, accept_bands=True), "approved"),
        (dict(functional_failures=[], measurement_missing=[], overhead_pct=15.0, accept_bands=True), "inconclusive"),
        (dict(functional_failures=[], measurement_missing=[], overhead_pct=20.0, accept_bands=True), "inconclusive"),
        (dict(functional_failures=[], measurement_missing=[], overhead_pct=20.1, accept_bands=True), "rejected"),
    ],
)
def test_classify_follows_the_predeclared_decision_rule(kwargs, expected) -> None:
    assert MODULE.classify(**kwargs) == expected


def test_load_env_file_ignores_comments_blanks_and_strips_quotes(tmp_path: Path) -> None:
    env = tmp_path / "x.env"
    env.write_text('# c\n\nA=1\nB="two"\nC=\'three\'\nNOEQUALS\n D = 4 \n', encoding="utf-8")
    assert MODULE.load_env_file(env) == {"A": "1", "B": "two", "C": "three", "D": "4"}


def test_parse_soak_reads_the_last_soak_result_and_the_inner_elapsed(tmp_path: Path) -> None:
    inner = MODULE.DEV / "out" / "test-r9d-inner-soak.log"
    inner.parent.mkdir(exist_ok=True)
    inner.write_text("APEX_SOAK cycle=1\nAPEX_SOAK_COMPLETE elapsed_ms=4321 cycles=1\n", encoding="utf-8")
    try:
        unit_log = tmp_path / "unit.log"
        unit_log.write_text(
            "noise\n"
            "SOAK_RESULT status=failed plugin=on reason=first\n"
            f"SOAK_RESULT status=passed plugin=on job_id=app-1 completed_cycles=1 log=out/{inner.name}\n",
            encoding="utf-8",
        )
        fields = MODULE.parse_soak(unit_log)
    finally:
        inner.unlink()
    assert fields["status"] == "passed"
    assert fields["job_id"] == "app-1"
    assert fields["job_elapsed_ms"] == "4321"


def test_parse_soak_without_result_line_returns_empty(tmp_path: Path) -> None:
    unit_log = tmp_path / "unit.log"
    unit_log.write_text("nothing here\n", encoding="utf-8")
    assert MODULE.parse_soak(unit_log) == {}


# ── #167: every argument the harness sends must exist on the runner it targets ──

_PARAM_BLOCK = re.compile(r"^param\((.*?)^\)", re.DOTALL | re.MULTILINE)
_PARAM_NAME = re.compile(r"\$(\w+)\s*(?:=|,|\s*$)", re.MULTILINE)


def declared_parameters(ps1_source: str) -> set[str]:
    """Names declared in the leading `param(...)` block of a PowerShell script."""
    block = _PARAM_BLOCK.search(ps1_source)
    assert block, "runner has no param( ... ) block"
    return set(_PARAM_NAME.findall(block.group(1)))


def sent_flags(command: list[str]) -> list[str]:
    """`-Flag` tokens the harness passes after `-File <script>`."""
    tail = command[command.index("-File") + 2:]
    return [tok[1:] for tok in tail if tok.startswith("-")]


def _runner_for(arm: str) -> Path:
    command = MODULE.e2e_command(arm)
    return Path(command[command.index("-File") + 1])


@pytest.mark.parametrize("arm", ["on", "off"])
def test_every_flag_the_harness_sends_is_declared_by_that_arm_runner(arm: str) -> None:
    runner = _runner_for(arm)
    declared = declared_parameters(runner.read_text(encoding="utf-8"))
    for flag in sent_flags(MODULE.e2e_command(arm)):
        assert flag in declared, f"{runner.name} does not declare -{flag}"


def test_both_arms_receive_the_same_environment_and_overlay_arguments() -> None:
    on, off = MODULE.e2e_command("on"), MODULE.e2e_command("off")
    assert sent_flags(on) == sent_flags(off) == ["EnvFile", "AdditionalComposeFile"]
    assert on[on.index("-EnvFile") + 1] == off[off.index("-EnvFile") + 1]
    assert (
        on[on.index("-AdditionalComposeFile") + 1]
        == off[off.index("-AdditionalComposeFile") + 1]
    )


def test_arm_runners_differ_only_where_the_plugin_switches_are() -> None:
    # Intentional asymmetry: the ON runner carries the inner-loop knobs the
    # control arm never needs; the control arm never grows a plugin endpoint.
    on = declared_parameters(_runner_for("on").read_text(encoding="utf-8"))
    off = declared_parameters(_runner_for("off").read_text(encoding="utf-8"))
    assert off <= on
    assert on - off == {"ReuseDev", "Build", "DriverHost"}


def test_negative_control_a_removed_runner_parameter_is_detected() -> None:
    source = _runner_for("on").read_text(encoding="utf-8")
    without_env_file = source.replace("[string]$EnvFile = '.env',\n", "")
    assert "EnvFile" in declared_parameters(source)
    assert "EnvFile" not in declared_parameters(without_env_file)
