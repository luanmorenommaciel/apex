"""Local telemetry contract for the Commander V0.1 harness."""

from collections import Counter

from apex import apexlib
from apex.commander.diagnostics_config import load_diagnostics_config

SCHEMA_VERSION = "apex.commander.telemetry.v1"
DIAGNOSTICS = load_diagnostics_config()
SKEW_RATIO_MIN = DIAGNOSTICS["skew"]["ratio_min"]
SKEW_MIN_TASKS = DIAGNOSTICS["skew"]["min_tasks"]


def infer_job_id(events):
    """Return a stable local job id from Spark events when the caller did not provide one."""
    app_id = _infer_app_id(events)
    if app_id:
        return app_id
    for event in events:
        job_id = event.get("Job ID")
        if job_id is not None:
            return f"spark-job-{job_id}"
    return "local-job"


def build_telemetry(events, job_id=None):
    """Normalize Spark events into the V0.1 Commander telemetry envelope."""
    event_list = list(events)
    selected_job_id = job_id or infer_job_id(event_list)
    stages = stage_summaries(event_list)
    return {
        "schema_version": SCHEMA_VERSION,
        "job_id": selected_job_id,
        "app_id": _infer_app_id(event_list),
        "event_counts": dict(Counter(event.get("Event", "unknown") for event in event_list)),
        "physical_plans": _physical_plans(event_list),
        "stages": stages,
        "skew_candidates": [
            _candidate_from_stage(stage)
            for stage in stages
            if stage["evidence_status"] == "valid"
            and stage["task_count"] >= SKEW_MIN_TASKS
            and stage["ratio"] >= SKEW_RATIO_MIN
        ],
    }


def stage_summaries(events):
    """Summarize effective shuffle-read records by stage."""
    summaries = []
    extra_by_stage = _task_metric_by_stage(events)
    for stage_id, records in sorted(apexlib.shuffle_read_by_stage(events).items()):
        metrics = apexlib.skew_metrics(records)
        summary = {
            "stage_id": stage_id,
            "task_count": metrics["n_tasks"],
            "records": records,
            "total_records": sum(records),
            "max_records": metrics["hot"],
            "median_cold_records": metrics["median_cold"],
            "ratio": metrics["ratio"],
            "evidence_status": metrics["evidence_status"],
            "quality_issues": metrics["quality_issues"],
        }
        summary.update(
            extra_by_stage.get(
                stage_id,
                {
                    "disk_bytes_spilled": 0,
                    "memory_bytes_spilled": 0,
                    "shuffle_read_bytes": 0,
                    "shuffle_read_records": 0,
                    "jvm_gc_time_ms": 0,
                    "executor_run_time_ms": 0,
                    "failure_reasons": [],
                },
            )
        )
        summaries.append(summary)
    return summaries


def _task_metric_by_stage(events):
    by_stage = {}
    for event in events:
        if event.get("Event") != "SparkListenerTaskEnd":
            continue
        stage_id = event.get("Stage ID")
        if stage_id is None:
            continue
        metrics = event.get("Task Metrics") or {}
        stage = by_stage.setdefault(
            stage_id,
            {
                "disk_bytes_spilled": 0,
                "memory_bytes_spilled": 0,
                "shuffle_read_bytes": 0,
                "shuffle_read_records": 0,
                "jvm_gc_time_ms": 0,
                "executor_run_time_ms": 0,
                "failure_reasons": [],
            },
        )
        stage["disk_bytes_spilled"] += int(metrics.get("Disk Bytes Spilled") or 0)
        stage["memory_bytes_spilled"] += int(metrics.get("Memory Bytes Spilled") or 0)
        shuffle = metrics.get("Shuffle Read Metrics") or {}
        stage["shuffle_read_bytes"] += _shuffle_read_bytes(shuffle)
        stage["shuffle_read_records"] += int(shuffle.get("Total Records Read") or 0)
        stage["jvm_gc_time_ms"] += int(metrics.get("JVM GC Time") or 0)
        stage["executor_run_time_ms"] += int(metrics.get("Executor Run Time") or 0)
        reason = _failure_reason(event.get("Task End Reason") or {})
        if reason and reason != "Success":
            stage["failure_reasons"].append(reason)
    return by_stage


def _shuffle_read_bytes(shuffle):
    total = int(shuffle.get("Total Bytes Read") or 0)
    if total:
        return total
    return int(shuffle.get("Remote Bytes Read") or 0) + int(
        shuffle.get("Local Bytes Read") or 0
    )


def _failure_reason(task_end_reason):
    parts = [
        task_end_reason.get("Reason"),
        task_end_reason.get("Class Name"),
        task_end_reason.get("Description"),
        task_end_reason.get("Full Stack Trace"),
    ]
    return " | ".join(str(part) for part in parts if part)


def _physical_plans(events):
    plans = []
    for event in events:
        plan = event.get("physicalPlanDescription") or event.get(
            "Physical Plan Description"
        )
        if not plan:
            continue
        plans.append(
            {
                "event": event.get("Event"),
                "execution_id": event.get("executionId")
                or event.get("SQL Execution ID")
                or event.get("sqlExecutionId"),
                "plan": plan,
            }
        )
    return plans


def _candidate_from_stage(stage):
    return {
        "kind": "shuffle_skew_candidate",
        "stage_id": stage["stage_id"],
        "ratio": stage["ratio"],
        "hot_records": stage["max_records"],
        "median_cold_records": stage["median_cold_records"],
        "task_count": stage["task_count"],
    }


def _infer_app_id(events):
    for event in events:
        app_id = event.get("App ID") or event.get("App ID ")
        if app_id:
            return app_id
    return None
