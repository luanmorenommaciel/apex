"""Deterministic Commander recommendations and preview loop."""

from apex.commander.fix_preview import build_fix_preview

RULE_SET = "apex.commander.recommendations.v1"

RECOMMENDATION_RULES = {
    "shuffle_skew_candidate": {
        "title": "Review skew-safe join mitigation",
        "action": "validate_aqe_then_consider_salting_or_repartition",
        "summary": (
            "Validate AQE skew join settings and the join key distribution before "
            "previewing salting or repartition changes."
        ),
        "guardrails": [
            "Confirm the hot key and join side before changing code.",
            "Prefer previewing a minimal code diff before any apply step.",
            "Re-run the job and compare skew ratio before accepting the fix.",
        ],
    },
    "shuffle_spill_candidate": {
        "title": "Review shuffle spill reduction",
        "action": "reduce_shuffle_volume_or_repartition",
        "summary": (
            "Inspect partition sizing and shuffle volume before increasing cluster resources."
        ),
        "guardrails": [
            "Avoid scaling executors before validating data layout.",
            "Preview repartition or projection changes before applying them.",
            "Compare spilled bytes after the next run.",
        ],
    },
    "gc_pressure_candidate": {
        "title": "Review GC pressure mitigation",
        "action": "reduce_object_pressure_or_adjust_partition_size",
        "summary": (
            "Review cache usage, partition size, and object pressure before changing memory settings."
        ),
        "guardrails": [
            "Check whether cache/persist is retaining unnecessary data.",
            "Preview code-level reductions before changing executor memory.",
            "Compare JVM GC ratio after the next run.",
        ],
    },
    "oom_candidate": {
        "title": "Review OOM recovery plan",
        "action": "reduce_partition_memory_pressure_before_rerun",
        "summary": (
            "Reduce per-task memory pressure and inspect joins before rerunning a failed job."
        ),
        "guardrails": [
            "Do not blindly retry with more memory without checking partition volume.",
            "Preview join or repartition changes first.",
            "Require human approval before applying any change.",
        ],
    },
    "plan_aqe_replan_candidate": {
        "title": "Review AQE plan instability",
        "action": "inspect_adaptive_plan_changes",
        "summary": (
            "Inspect adaptive execution updates to understand join, shuffle, or coalescing changes."
        ),
        "guardrails": [
            "Use the SQL plan evidence before changing Spark settings.",
            "Preview configuration or code changes before applying them.",
            "Compare plan update count after the next run.",
        ],
    },
}


def recommend_fix(finding_store, job_id):
    """Build deterministic recommendations from persisted validated findings."""
    if finding_store is None:
        return _empty_response(job_id, "not_configured")
    if not hasattr(finding_store, "query_by_job_id"):
        raise ValueError("finding_store_not_queryable")

    records = finding_store.query_by_job_id(job_id)
    if not records:
        return _empty_response(job_id, "not_found")

    recommendations = _recommendations_from_records(records, job_id)
    return {
        "job_id": job_id,
        "status": "found" if recommendations else "no_recommendation",
        "rule_set": RULE_SET,
        "count": len(recommendations),
        "skipped_count": len(records) - len(recommendations),
        "recommendations": recommendations,
    }


def preview_recommendation(finding_store, job_id, recommendation_id, path, replacement):
    """Preview a recommendation-backed replacement without modifying the target file."""
    response = recommend_fix(finding_store, job_id)
    if response["status"] != "found":
        return {
            "job_id": job_id,
            "status": response["status"],
            "mode": "preview",
            "recommendation_id": recommendation_id,
            "target": str(path),
            "diff": "",
        }

    recommendation = _find_recommendation(response["recommendations"], recommendation_id)
    if recommendation is None:
        return {
            "job_id": job_id,
            "status": "recommendation_not_found",
            "mode": "preview",
            "recommendation_id": recommendation_id,
            "target": str(path),
            "diff": "",
        }

    preview = build_fix_preview(
        path,
        recommendation["summary"],
        replacement=replacement,
    )
    preview.update(
        {
            "status": "preview_ready",
            "job_id": job_id,
            "recommendation_id": recommendation_id,
            "recommendation_record": recommendation,
            "requires_approval": True,
        }
    )
    return preview


def _recommendations_from_records(records, job_id):
    recommendations = []
    for index, record in enumerate(records):
        validation = record.get("validation") or {}
        if validation.get("accepted") is not True:
            continue

        finding = record.get("finding") or {}
        kind = finding.get("kind") or finding.get("title", "unknown_finding")
        rule = RECOMMENDATION_RULES.get(kind, _fallback_rule(kind))
        evidence = finding.get("evidence") or {}
        recommendations.append(
            {
                "id": _recommendation_id(job_id, kind, evidence, index),
                "job_id": job_id,
                "finding_kind": kind,
                "severity": finding.get("severity", ""),
                "confidence": finding.get("confidence", ""),
                "title": rule["title"],
                "action": rule["action"],
                "summary": rule["summary"],
                "evidence": _evidence_summary(evidence),
                "guardrails": list(rule["guardrails"]),
                "preview": {
                    "mode": "manual_replacement",
                    "tool": "preview_recommendation",
                    "requires_approval_before_apply": True,
                },
                "rule_set": RULE_SET,
            }
        )
    return recommendations


def _recommendation_id(job_id, kind, evidence, index):
    stage_id = evidence.get("stage_id")
    scope = f"stage-{stage_id}" if stage_id is not None else "job"
    return f"{job_id}:{kind}:{scope}:{index}"


def _evidence_summary(evidence):
    keys = (
        "app_id",
        "stage_id",
        "ratio",
        "hot_records",
        "median_cold_records",
        "spilled_bytes",
        "gc_ratio",
        "jvm_gc_time_ms",
        "executor_run_time_ms",
        "adaptive_execution_updates",
        "failure_reasons",
    )
    return {key: evidence[key] for key in keys if key in evidence}


def _fallback_rule(kind):
    return {
        "title": f"Review {kind}",
        "action": "manual_review",
        "summary": "Review the persisted finding evidence before proposing a code change.",
        "guardrails": [
            "Do not apply changes without human approval.",
            "Preview a minimal diff before any apply step.",
            "Re-run the job and compare evidence after the change.",
        ],
    }


def _find_recommendation(recommendations, recommendation_id):
    for recommendation in recommendations:
        if recommendation["id"] == recommendation_id:
            return recommendation
    return None


def _empty_response(job_id, status):
    return {
        "job_id": job_id,
        "status": status,
        "rule_set": RULE_SET,
        "count": 0,
        "skipped_count": 0,
        "recommendations": [],
    }
