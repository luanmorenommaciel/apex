from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

DEV = Path(__file__).resolve().parents[1]
SCRIPT = DEV / "scripts" / "verify.sh"


def _source() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_verify_script_parses() -> None:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash not available")
    result = subprocess.run([bash, "-n", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_volume_destruction_is_gated_behind_verify_fresh() -> None:
    source = _source()
    # Every `down -v` must live inside the VERIFY_FRESH conditional helper.
    occurrences = [m.start() for m in re.finditer(r"down -v", source)]
    assert len(occurrences) == 1
    helper = source[source.index("down_args() {"):]
    helper = helper[: helper.index("\n")]
    assert "down -v" in helper
    assert 'if [ "$VERIFY_FRESH" = "1" ]' in helper
    assert 'VERIFY_FRESH="${VERIFY_FRESH:-0}"' in source


def test_both_teardowns_use_the_gated_helper() -> None:
    source = _source()
    assert source.count("$COMPOSE $(down_args)") == 2
    assert 'teardown() { [ "$KEEP_UP" = "1" ] ||' in source


def _evaluate_down_args(fresh: str) -> str:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash not available")
    source = _source()
    helper = source[source.index("down_args() {"):]
    helper = helper[: helper.index("\n")]
    script = f'VERIFY_FRESH="{fresh}"\n{helper}\ndown_args\n'
    result = subprocess.run([bash, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_default_keeps_the_volume() -> None:
    assert _evaluate_down_args("0") == "down --remove-orphans"


def test_fresh_run_destroys_the_volume() -> None:
    assert _evaluate_down_args("1") == "down -v --remove-orphans"


def test_keep_up_still_skips_teardown() -> None:
    assert 'KEEP_UP="${KEEP_UP:-0}"' in _source()
