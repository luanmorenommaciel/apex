"""Exercise the live gate's actual ordering assertion without running its I/O."""

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


def _assert_gate_order(listed):
    source = Path(__file__).resolve().parents[1] / "tools/read_only_gate.py"
    assertions = [
        node for node in ast.walk(ast.parse(source.read_text()))
        if isinstance(node, ast.Assert)
        and isinstance(node.msg, ast.Constant)
        and str(node.msg.value).startswith("runs are not ordered")
    ]
    assert len(assertions) == 1, "exercise the actual gate assertion, never a copy"
    code = compile(ast.Module(body=assertions, type_ignores=[]), str(source), "exec")
    exec(code, {"listed": listed})


@pytest.fixture
def overlapping_runs():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    return [
        {"job_id": "new-short", "first_ts": start + timedelta(hours=1),
         "last_ts": start + timedelta(hours=2)},
        {"job_id": "old-long", "first_ts": start,
         "last_ts": start + timedelta(hours=3)},
    ]


def test_gate_accepts_start_order_when_overlapping_runs_end_in_opposite_order(overlapping_runs):
    assert overlapping_runs[0]["last_ts"] < overlapping_runs[1]["last_ts"]
    _assert_gate_order(overlapping_runs)


def test_gate_rejects_end_order_for_overlapping_runs(overlapping_runs):
    with pytest.raises(AssertionError, match="runs are not ordered"):
        _assert_gate_order(list(reversed(overlapping_runs)))


def test_gate_uses_ascending_job_id_to_break_equal_start_times(overlapping_runs):
    first = {**overlapping_runs[0], "job_id": "job-a"}
    second = {**overlapping_runs[1], "job_id": "job-z", "first_ts": first["first_ts"]}
    _assert_gate_order([first, second])
    with pytest.raises(AssertionError, match="runs are not ordered"):
        _assert_gate_order([second, first])
