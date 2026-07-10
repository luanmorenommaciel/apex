from apex.commander.findings import build_finding
from apex.commander.telemetry import build_telemetry
from apex.commander.detectors import detect_findings


def test_build_finding_keeps_legacy_title_and_new_kind():
    finding = build_finding(
        kind="shuffle_spill_candidate",
        job_id="job-42",
        severity="warning",
        confidence="medium",
        evidence={"stage_id": 3},
        recommendations=["Reduce shuffle spill."],
    )

    assert finding["status"] == "finding"
    assert finding["kind"] == "shuffle_spill_candidate"
    assert finding["title"] == "shuffle_spill_candidate"
    assert finding["job_id"] == "job-42"
    assert finding["evidence"]["stage_id"] == 3


def task_end(
    stage,
    partition,
    records,
    *,
    disk_spill=0,
    memory_spill=0,
    gc_time=0,
    duration=1000,
    reason="Success",
):
    return {
        "Event": "SparkListenerTaskEnd",
        "App ID": "app-detectors",
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


def test_build_telemetry_captures_extended_stage_metrics():
    envelope = build_telemetry(
        [
            task_end(3, 0, 1000, disk_spill=2048, memory_spill=1024, gc_time=200, duration=1000),
            task_end(3, 1, 1000, disk_spill=0, memory_spill=0, gc_time=100, duration=1000),
        ],
        job_id="job-42",
    )

    stage = envelope["stages"][0]
    assert stage["disk_bytes_spilled"] == 2048
    assert stage["memory_bytes_spilled"] == 1024
    assert stage["jvm_gc_time_ms"] == 300
    assert stage["executor_run_time_ms"] == 2000


def envelope_with_stage(stage):
    return {
        "job_id": "job-42",
        "app_id": "app-detectors",
        "stages": [stage],
        "skew_candidates": [],
    }


def base_stage(**overrides):
    stage = {
        "stage_id": 1,
        "task_count": 8,
        "ratio": 1.0,
        "max_records": 1000,
        "median_cold_records": 1000,
        "disk_bytes_spilled": 0,
        "memory_bytes_spilled": 0,
        "jvm_gc_time_ms": 0,
        "executor_run_time_ms": 10000,
        "failure_reasons": [],
    }
    stage.update(overrides)
    return stage


def test_detects_shuffle_spill_candidate():
    findings = detect_findings(envelope_with_stage(base_stage(disk_bytes_spilled=1024 * 1024)))
    assert findings[0]["kind"] == "shuffle_spill_candidate"


def test_detects_gc_pressure_candidate():
    findings = detect_findings(envelope_with_stage(base_stage(jvm_gc_time_ms=3000, executor_run_time_ms=10000)))
    assert findings[0]["kind"] == "gc_pressure_candidate"


def test_detects_oom_candidate():
    findings = detect_findings(
        envelope_with_stage(
            base_stage(
                failure_reasons=[
                    "ExecutorLostFailure: Container killed by YARN for exceeding memory limits"
                ]
            )
        )
    )
    assert findings[0]["kind"] == "oom_candidate"


def test_detects_plan_aqe_candidate_from_event_counts():
    envelope = envelope_with_stage(base_stage())
    envelope["event_counts"] = {"SparkListenerSQLAdaptiveExecutionUpdate": 4}
    findings = detect_findings(envelope)
    assert findings[0]["kind"] == "plan_aqe_replan_candidate"


def test_balanced_stage_has_no_detector_findings():
    assert detect_findings(envelope_with_stage(base_stage())) == []
