from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "phase_a_eventlog_report.py"
SPEC = importlib.util.spec_from_file_location("phase_a_eventlog_report", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
task_reason_kind = MODULE.task_reason_kind


def test_task_reason_kind_reads_spark_reason_shape() -> None:
    assert task_reason_kind({"Reason": "TaskKilled"}) == "TaskKilled"
    assert task_reason_kind({"Class Name": "ExceptionFailure"}) == "ExceptionFailure"
    assert task_reason_kind("Success") == "Success"
    assert task_reason_kind(None) == "unknown"
