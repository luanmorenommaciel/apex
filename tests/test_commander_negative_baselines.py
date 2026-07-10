from apex.commander.baselines import evaluate_negative_baseline
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.telemetry import build_telemetry


def app_start(app_id="app-healthy"):
    return {
        "Event": "SparkListenerApplicationStart",
        "App ID": app_id,
        "App Name": "apex-negative-baseline",
    }


def task_end(
    stage,
    partition,
    records,
    *,
    app_id="app-healthy",
    disk_spill=0,
    memory_spill=0,
    gc_time=0,
    duration=1000,
    reason="Success",
):
    return {
        "Event": "SparkListenerTaskEnd",
        "App ID": app_id,
        "Stage ID": stage,
        "Task End Reason": {"Reason": reason},
        "Task Info": {
            "Task ID": partition,
            "Index": partition,
            "Duration": duration,
        },
        "Task Metrics": {
            "Executor Run Time": duration,
            "JVM GC Time": gc_time,
            "Disk Bytes Spilled": disk_spill,
            "Memory Bytes Spilled": memory_spill,
            "Shuffle Read Metrics": {
                "Total Records Read": records,
            },
        },
    }


def aqe_update(app_id="app-healthy"):
    return {
        "Event": "SparkListenerSQLAdaptiveExecutionUpdate",
        "App ID": app_id,
    }


def store_envelope(tmp_path, events, job_id):
    store = tmp_path / "clickstack.ndjson"
    append_envelope(store, build_telemetry(events, job_id=job_id))
    return store


def healthy_events():
    return [
        app_start(),
        task_end(2, 0, 10000, disk_spill=128 * 1024, gc_time=50),
        task_end(2, 1, 10200, disk_spill=128 * 1024, gc_time=50),
        task_end(2, 2, 9900, disk_spill=128 * 1024, gc_time=50),
        task_end(2, 3, 10100, disk_spill=128 * 1024, gc_time=50),
        aqe_update(),
        aqe_update(),
    ]


def test_negative_baseline_passes_for_healthy_job(tmp_path):
    store = store_envelope(tmp_path, healthy_events(), "healthy-job")

    result = evaluate_negative_baseline(store, "healthy-job")

    assert result == {
        "job_id": "healthy-job",
        "status": "passed",
        "unexpected_findings": [],
        "unexpected_finding_count": 0,
    }


def spill_events():
    return [
        app_start("app-spill"),
        task_end(3, 0, 10000, app_id="app-spill", disk_spill=1024 * 1024),
        task_end(3, 1, 10200, app_id="app-spill"),
    ]


def test_negative_baseline_fails_when_detector_fires(tmp_path):
    store = store_envelope(tmp_path, spill_events(), "spill-job")

    result = evaluate_negative_baseline(store, "spill-job")

    assert result["job_id"] == "spill-job"
    assert result["status"] == "failed"
    assert result["unexpected_finding_count"] == 1
    assert result["unexpected_findings"][0]["kind"] == "shuffle_spill_candidate"
