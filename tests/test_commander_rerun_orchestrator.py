from apex.commander.clickstack_mvp import append_envelope
from apex.commander.rerun_orchestrator import (
    execute_rerun_and_compare,
    execute_rerun_poll_and_compare,
    plan_rerun,
)
from apex.commander.spark_rerun_template import build_spark_submit_rerun_command
from apex.commander.telemetry_polling import poll_for_telemetry


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


def test_build_spark_submit_rerun_command_includes_listener_and_job_id(tmp_path):
    source = tmp_path / "jobs" / "skew_job.py"
    source.parent.mkdir()
    source.write_text("print('spark job')\n", encoding="utf-8")

    result = build_spark_submit_rerun_command(
        app_path="jobs/skew_job.py",
        after_job_id="after-job",
        app_args=["--tenant", "apex"],
        conf={"spark.sql.shuffle.partitions": "32"},
        rerun_root=tmp_path,
    )

    assert result["status"] == "planned"
    assert result["command"][0] == "spark-submit"
    assert "--jars" in result["command"]
    assert (
        "listener-jvm/build/libs/apex-spark-listener-0.1.0.jar"
        in result["command"]
    )
    assert "--conf" in result["command"]
    assert "spark.apex.jobId=after-job" in result["command"]
    assert "spark.apex.listener.output=/tmp/apex-listener-events.ndjson" in result[
        "command"
    ]
    assert "spark.apex.listener.failMode=false" in result["command"]
    assert (
        "spark.extraListeners=apex.commander.spark.ApexSparkListener"
        in result["command"]
    )
    assert "spark.sql.shuffle.partitions=32" in result["command"]
    assert result["command"][-3:] == [str(source.resolve()), "--tenant", "apex"]


def test_build_spark_submit_rerun_command_blocks_path_outside_root(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    source = outside / "job.py"
    source.write_text("print('outside')\n", encoding="utf-8")

    result = build_spark_submit_rerun_command(
        app_path=str(source),
        after_job_id="after-job",
        rerun_root=root,
    )

    assert result["status"] == "app_path_outside_rerun_root"


def test_poll_for_telemetry_waits_until_after_job_is_visible(tmp_path):
    store = tmp_path / "store.ndjson"
    sleeps = []

    def collect_after_telemetry(interval_seconds):
        sleeps.append(interval_seconds)
        append_envelope(store, telemetry_envelope("after-job", ratio=1.0))

    result = poll_for_telemetry(
        store,
        "after-job",
        attempts=3,
        interval_seconds=0.25,
        sleeper=collect_after_telemetry,
    )

    assert result["status"] == "found"
    assert result["attempt"] == 2
    assert sleeps == [0.25]


def test_execute_rerun_poll_and_compare_waits_for_after_telemetry(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=29.5))

    def collect_after_telemetry(interval_seconds):
        assert interval_seconds == 0.1
        append_envelope(store, telemetry_envelope("after-job", ratio=1.0))

    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
    )
    runner = FakeRunner()

    result = execute_rerun_poll_and_compare(
        store,
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        plan["approval"]["token"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
        runner=runner,
        poll_attempts=3,
        poll_interval_seconds=0.1,
        poll_sleeper=collect_after_telemetry,
    )

    assert result["status"] == "rerun_completed"
    assert result["telemetry"]["status"] == "found"
    assert result["telemetry"]["attempt"] == 2
    assert result["comparison"]["status"] == "improved"
    assert len(runner.calls) == 1


def test_execute_rerun_poll_and_compare_reports_missing_after_telemetry(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=29.5))
    plan = plan_rerun(
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
    )

    result = execute_rerun_poll_and_compare(
        store,
        "before-job",
        "after-job",
        ["spark-submit", "job.py"],
        plan["approval"]["token"],
        rerun_root=tmp_path,
        allowed_command_prefixes=[["spark-submit"]],
        runner=FakeRunner(),
        poll_attempts=2,
        poll_interval_seconds=0,
    )

    assert result["status"] == "telemetry_not_available"
    assert result["telemetry"]["status"] == "not_found"
    assert result["comparison"]["status"] == "not_run"


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
