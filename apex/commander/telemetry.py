"""Local telemetry contract for the Commander V0.1 harness."""

from collections import Counter

from apex import apexlib

SCHEMA_VERSION = "apex.commander.telemetry.v1"
SKEW_RATIO_MIN = 10


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
        "stages": stages,
        "skew_candidates": [
            _candidate_from_stage(stage)
            for stage in stages
            if stage["evidence_status"] == "valid" and stage["ratio"] >= SKEW_RATIO_MIN
        ],
    }


def stage_summaries(events):
    """Summarize effective shuffle-read records by stage."""
    summaries = []
    for stage_id, records in sorted(apexlib.shuffle_read_by_stage(events).items()):
        metrics = apexlib.skew_metrics(records)
        summaries.append(
            {
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
        )
    return summaries


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
