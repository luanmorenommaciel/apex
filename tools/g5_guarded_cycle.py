"""G5 guarded detect -> fix -> rerun helpers."""

import argparse
import json
import math
import tempfile
from pathlib import Path

from apex import apexlib
from apex.commander.apply_verify import apply_recommendation
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.diagnostic_mvp import diagnose_findings
from apex.commander.evidence_validator import validate_finding
from apex.commander.recommendations import preview_recommendation, recommend_fix
from apex.commander.telemetry import build_telemetry


class InMemoryFindingStore:
    def __init__(self, records):
        self.records = records

    def query_by_job_id(self, job_id):
        return self.records.get(job_id, [])


def load_g4_record(path):
    text = Path(path).read_text(encoding="utf-8")
    start = text.index("{")
    end_marker = "\n\n# no-LLM"
    end = text.index(end_marker, start) if end_marker in text[start:] else text.rindex("}") + 1
    payload = json.loads(text[start:end])
    if not payload["findings"] or not payload["validations"]:
        raise ValueError("g4_log_without_finding_or_validation")
    return {
        "job_id": payload["job_id"],
        "finding": payload["findings"][0],
        "validation": payload["validations"][0],
    }


def build_skew_fix_replacement(path):
    source = Path(path).read_text(encoding="utf-8")
    source = source.replace(
        "from pyspark.sql.functions import col, rand, when, collect_list",
        "from pyspark.sql.functions import broadcast, col, rand, when, collect_list",
    )
    source = source.replace(
        '    .config("spark.sql.adaptive.enabled", "false")\n'
        '    .config("spark.sql.adaptive.skewJoin.enabled", "false")\n'
        '    .config("spark.sql.shuffle.partitions", "8")\n'
        '    .config("spark.sql.adaptive.coalescePartitions.enabled", "false")\n'
        '    .config("spark.sql.adaptive.autoBroadcastJoinThreshold", "-1")\n',
        '    .config("spark.sql.adaptive.enabled", "true")\n'
        '    .config("spark.sql.adaptive.skewJoin.enabled", "true")\n'
        '    .config("spark.sql.shuffle.partitions", "8")\n'
        '    .config("spark.sql.adaptive.coalescePartitions.enabled", "false")\n'
        '    .config("spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760")\n',
    )
    source = source.replace(
        'result = orders.join(customers.hint("shuffle_merge"), "customer_id", "inner")  # APEX::ANTIPATTERN',
        'result = orders.join(broadcast(customers), "customer_id", "inner")  # APEX::FIXED_BY_G5',
    )
    return source


def preview(args):
    record = load_g4_record(args.g4_log)
    job_id = record["job_id"]
    store = InMemoryFindingStore({job_id: [record]})
    recommendations = recommend_fix(store, job_id)
    if recommendations["status"] != "found" or not recommendations["recommendations"]:
        raise RuntimeError(f"recommendation_not_found: {recommendations}")

    recommendation_id = recommendations["recommendations"][0]["id"]
    replacement = build_skew_fix_replacement(args.job)
    result = preview_recommendation(store, job_id, recommendation_id, args.job, replacement)
    output = {
        "mode": "preview",
        "source_finding_log": args.g4_log,
        "target_job": args.job,
        "recommendations": recommendations,
        "preview": result,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def apply(args):
    record = load_g4_record(args.g4_log)
    job_id = record["job_id"]
    store = InMemoryFindingStore({job_id: [record]})
    recommendation_id = f"{job_id}:shuffle_skew_candidate:stage-2:0"
    replacement = build_skew_fix_replacement(args.job)
    result = apply_recommendation(
        store,
        job_id,
        recommendation_id,
        args.job,
        replacement,
        args.approval_token,
        apply_root=args.apply_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "applied" else 1


def diagnose(args):
    events = apexlib.read_events(args.event_log)
    envelope = build_telemetry(events, job_id=args.job_id)
    with tempfile.TemporaryDirectory() as tempdir:
        store = Path(tempdir) / "clickstack.ndjson"
        append_envelope(store, envelope)
        findings = diagnose_findings(store, args.job_id)
    validations = [validate_finding(finding) for finding in findings]
    stages = envelope.get("stages", [])
    valid_stages = [stage for stage in stages if stage.get("evidence_status") == "valid"]
    valid_ratios = [
        stage.get("ratio", 0)
        for stage in valid_stages
        if isinstance(stage.get("ratio", 0), (int, float))
        and math.isfinite(stage.get("ratio", 0))
    ]
    output = {
        "event_log": args.event_log,
        "job_id": args.job_id,
        "app_id": envelope.get("app_id"),
        "finding_count": len(findings),
        "findings": findings,
        "validations": validations,
        "shuffle_read_bytes_total": sum(stage.get("shuffle_read_bytes", 0) for stage in stages),
        "shuffle_read_records_total": sum(stage.get("shuffle_read_records", 0) for stage in stages),
        "max_valid_skew_ratio": max(valid_ratios) if valid_ratios else 0,
        "valid_shuffle_stage_count": len(valid_stages),
        "stages": stages,
    }
    print(json.dumps(_json_safe(output), indent=2, sort_keys=True, allow_nan=False))
    return 0


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument("--g4-log", required=True)
    preview_parser.add_argument("--job", required=True)
    preview_parser.set_defaults(func=preview)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--g4-log", required=True)
    apply_parser.add_argument("--job", required=True)
    apply_parser.add_argument("--approval-token", required=True)
    apply_parser.add_argument("--apply-root", required=True)
    apply_parser.set_defaults(func=apply)

    diagnose_parser = subparsers.add_parser("diagnose")
    diagnose_parser.add_argument("--event-log", required=True)
    diagnose_parser.add_argument("--job-id", required=True)
    diagnose_parser.set_defaults(func=diagnose)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
