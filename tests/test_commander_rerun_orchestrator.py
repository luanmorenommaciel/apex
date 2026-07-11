from apex.commander.clickstack_mvp import append_envelope
from apex.commander.rerun_orchestrator import (
    execute_rerun_and_compare,
    plan_rerun,
)


class FakeRunner:
    def __init__(self, *, on_run=None, result=None):
        self.calls = []
        self.on_run = on_run
        self.result = result or {
            "status": "succeeded",
            "exit_code": 0,
            "timed_out": False,
            "stdout": "ok",
            "stderr": "",
        }

    def run(self, command, cwd, timeout_seconds):
        self.calls.append(
            {
                "command": command,
                "cwd": str(cwd),
                "timeout_seconds": timeout_seconds,
            }
        )
        if self.on_run:
            self.on_run()
        return self.result


def telemetry_envelope(job_id, *, ratio=1.0):
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-rerun",
        "event_counts": {"SparkListenerTaskEnd": 8},
        "stages": [
            {
                "stage_id": 2,
                "task_count": 8,
                "records": [1000, 1000, 1000, 1000],
                "total_records": 4000,
                "max_records": 1000,
                "median_cold_records": 1000,
                "ratio": ratio,
                "evidence_status": "valid",
                "quality_issues": [],
                "disk_bytes_spilled": 0,
                "memory_bytes_spilled": 0,
                "jvm_gc_time_ms": 0,
                "executor_run_time_ms": 10000,
                "failure_reasons": [],
            }
        ],
        "skew_candidates": [
            {
                "kind": "shuffle_skew_candidate",
                "stage_id": 2,
                "ratio": ratio,
                "hot_records": 1000,
                "median_cold_records": 100,
                "task_count": 8,
            }
        ]
        if ratio >= 10
        else [],
    }


def test_plan_rerun_returns_token_for_allowed_command(tmp_path):
    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
    )

    assert plan["status"] == "planned"
    assert plan["runnable"] is True
    assert len(plan["approval"]["token"]) == 64
    assert plan["command_sha256"]


def test_plan_rerun_blocks_without_rerun_root():
    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        allowed_command_prefixes=[["spark-submit"]],
    )

    assert plan["status"] == "rerun_root_not_configured"
    assert plan["runnable"] is False


def test_plan_rerun_blocks_unapproved_command(tmp_path):
    plan = plan_rerun(
        "before-job",
        "after-job",
        ["powershell", "-Command", "Remove-Item"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
    )

    assert plan["status"] == "command_not_allowed"


def test_plan_rerun_blocks_cwd_outside_root(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()

    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        cwd=outside,
        rerun_root=root,
        allowed_command_prefixes=[["spark-submit"]],
    )

    assert plan["status"] == "outside_rerun_root"


def test_execute_rerun_rejects_invalid_token_without_runner_call(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=29.5))
    runner = FakeRunner()

    result = execute_rerun_and_compare(
        store,
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        "wrong-token",
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
        runner=runner,
    )

    assert result["status"] == "invalid_approval_token"
    assert result["runner"]["status"] == "not_run"
    assert runner.calls == []


def test_execute_rerun_runs_fake_runner_and_compares_telemetry(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=29.5))

    def collect_after_telemetry():
        append_envelope(store, telemetry_envelope("after-job", ratio=1.0))

    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
    )
    runner = FakeRunner(on_run=collect_after_telemetry)

    result = execute_rerun_and_compare(
        store,
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        plan["approval"]["token"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
        runner=runner,
    )

    assert result["status"] == "rerun_completed"
    assert result["runner"]["status"] == "succeeded"
    assert result["comparison"]["status"] == "improved"
    assert len(runner.calls) == 1


def test_execute_rerun_returns_failed_without_comparison(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=29.5))
    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
    )
    runner = FakeRunner(
        result={
            "status": "failed",
            "exit_code": 2,
            "timed_out": False,
            "stdout": "",
            "stderr": "failed",
        }
    )

    result = execute_rerun_and_compare(
        store,
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        plan["approval"]["token"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
        runner=runner,
    )

    assert result["status"] == "rerun_failed"
    assert result["comparison"]["status"] == "not_run"
