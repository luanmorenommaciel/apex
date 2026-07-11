"""Compare Commander telemetry before and after a guarded apply."""

from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.telemetry_store import query_envelopes

RULE_SET = "apex.commander.telemetry_compare.v1"

METRICS = (
    ("finding_count", "lower_is_better"),
    ("max_skew_ratio", "lower_is_better"),
    ("total_spilled_bytes", "lower_is_better"),
    ("max_gc_ratio", "lower_is_better"),
    ("oom_failure_count", "lower_is_better"),
    ("adaptive_execution_updates", "lower_is_better"),
)


def compare_job_telemetry(store, before_job_id, after_job_id):
    """Compare latest telemetry evidence for two job ids."""
    before_envelope = _latest_envelope(store, before_job_id)
    after_envelope = _latest_envelope(store, after_job_id)
    missing = [
        job_id
        for job_id, envelope in (
            (before_job_id, before_envelope),
            (after_job_id, after_envelope),
        )
        if envelope is None
    ]
    if missing:
        return {
            "rule_set": RULE_SET,
            "status": "not_comparable",
            "before_job_id": before_job_id,
            "after_job_id": after_job_id,
            "missing_job_ids": missing,
            "summary": {
                "resolved_findings": [],
                "new_findings": [],
                "improved_metric_count": 0,
                "regressed_metric_count": 0,
            },
            "comparisons": [],
        }

    before_findings = diagnose_findings(store, before_job_id)
    after_findings = diagnose_findings(store, after_job_id)
    before = _snapshot(before_job_id, before_envelope, before_findings)
    after = _snapshot(after_job_id, after_envelope, after_findings)
    comparisons = [
        _compare_metric(name, direction, before["metrics"][name], after["metrics"][name])
        for name, direction in METRICS
    ]
    resolved = sorted(set(before["finding_kinds"]) - set(after["finding_kinds"]))
    new = sorted(set(after["finding_kinds"]) - set(before["finding_kinds"]))
    improved_count = sum(1 for item in comparisons if item["status"] == "improved")
    regressed_count = sum(1 for item in comparisons if item["status"] == "regressed")

    return {
        "rule_set": RULE_SET,
        "status": _overall_status(improved_count, regressed_count, resolved, new),
        "before_job_id": before_job_id,
        "after_job_id": after_job_id,
        "before": before,
        "after": after,
        "summary": {
            "resolved_findings": resolved,
            "new_findings": new,
            "improved_metric_count": improved_count,
            "regressed_metric_count": regressed_count,
        },
        "comparisons": comparisons,
    }


def _latest_envelope(store, job_id):
    matches = query_envelopes(store, job_id)
    if not matches:
        return None
    return matches[-1]


def _snapshot(job_id, envelope, findings):
    finding_kinds = sorted(
        finding.get("kind") or finding.get("title", "")
        for finding in findings
    )
    metrics = _metrics_from_envelope(envelope)
    metrics["finding_count"] = len(findings)
    return {
        "job_id": job_id,
        "app_id": envelope.get("app_id"),
        "finding_count": len(findings),
        "finding_kinds": finding_kinds,
        "metrics": metrics,
    }


def _metrics_from_envelope(envelope):
    stages = envelope.get("stages") or []
    return {
        "max_skew_ratio": max(
            [_float(stage.get("ratio")) for stage in stages] or [0.0]
        ),
        "total_spilled_bytes": sum(
            _int(stage.get("disk_bytes_spilled"))
            + _int(stage.get("memory_bytes_spilled"))
            for stage in stages
        ),
        "max_gc_ratio": max([_gc_ratio(stage) for stage in stages] or [0.0]),
        "oom_failure_count": sum(_oom_failure_count(stage) for stage in stages),
        "adaptive_execution_updates": _int(
            (envelope.get("event_counts") or {}).get(
                "SparkListenerSQLAdaptiveExecutionUpdate"
            )
        ),
    }


def _compare_metric(name, direction, before, after):
    if before == after:
        status = "unchanged"
    elif direction == "lower_is_better":
        status = "improved" if after < before else "regressed"
    else:
        status = "improved" if after > before else "regressed"
    return {
        "metric": name,
        "direction": direction,
        "before": before,
        "after": after,
        "delta": after - before,
        "status": status,
    }


def _overall_status(improved_count, regressed_count, resolved, new):
    improvement_score = improved_count + len(resolved)
    regression_score = regressed_count + len(new)
    if improvement_score and regression_score:
        return "mixed"
    if improvement_score:
        return "improved"
    if regression_score:
        return "regressed"
    return "unchanged"


def _gc_ratio(stage):
    run_time = _int(stage.get("executor_run_time_ms"))
    if run_time == 0:
        return 0.0
    return _int(stage.get("jvm_gc_time_ms")) / run_time


def _oom_failure_count(stage):
    reasons = stage.get("failure_reasons") or []
    return sum(
        1
        for reason in reasons
        if "memory" in reason.lower() or "oom" in reason.lower()
    )


def _float(value):
    if value in (None, ""):
        return 0.0
    return float(value)


def _int(value):
    if value in (None, ""):
        return 0
    return int(value)
