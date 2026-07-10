import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def task_end(stage, partition, records, *, app_id="app-1", finish_time=1000):
    return {
        "Event": "SparkListenerTaskEnd",
        "App ID": app_id,
        "Stage ID": stage,
        "Stage Attempt ID": 0,
        "Task End Reason": {"Reason": "Success"},
        "Task Type": "ShuffleMapTask",
        "Task Info": {
            "Task ID": partition,
            "Index": partition,
            "Attempt": 0,
            "Failed": False,
            "Finish Time": finish_time + partition,
        },
        "Task Metrics": {
            "Shuffle Read Metrics": {
                "Total Records Read": records,
            }
        },
    }


def app_start(app_id="app-1"):
    return {
        "Event": "SparkListenerApplicationStart",
        "App ID": app_id,
        "App Name": "apex-v01-demo",
    }


def skew_events():
    return [
        app_start("app-skew"),
        task_end(4, 0, 160000, app_id="app-skew"),
        task_end(4, 1, 5000, app_id="app-skew"),
        task_end(4, 2, 5200, app_id="app-skew"),
        task_end(4, 3, 5400, app_id="app-skew"),
    ]


def no_skew_events():
    return [
        app_start("app-balanced"),
        task_end(2, 0, 10000, app_id="app-balanced"),
        task_end(2, 1, 10500, app_id="app-balanced"),
        task_end(2, 2, 9800, app_id="app-balanced"),
        task_end(2, 3, 10100, app_id="app-balanced"),
    ]


def write_events(path, events):
    path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
    return path


def test_build_telemetry_envelope_summarizes_spark_events():
    from apex.commander.telemetry import build_telemetry

    envelope = build_telemetry(skew_events(), job_id="job-42")

    assert envelope["schema_version"] == "apex.commander.telemetry.v1"
    assert envelope["job_id"] == "job-42"
    assert envelope["app_id"] == "app-skew"
    assert envelope["event_counts"]["SparkListenerTaskEnd"] == 4
    assert envelope["stages"][0]["stage_id"] == 4
    assert envelope["stages"][0]["task_count"] == 4
    assert envelope["stages"][0]["max_records"] == 160000
    assert envelope["skew_candidates"][0]["stage_id"] == 4
    assert envelope["skew_candidates"][0]["ratio"] > 10


def test_clickstack_mvp_appends_and_queries_by_job_id(tmp_path):
    from apex.commander.clickstack_mvp import append_envelope, query_by_job_id
    from apex.commander.telemetry import build_telemetry

    store = tmp_path / "clickstack.ndjson"
    envelope = build_telemetry(skew_events(), job_id="job-42")

    append_envelope(store, envelope)

    assert query_by_job_id(store, "job-42") == [envelope]
    assert query_by_job_id(store, "missing-job") == []


def test_diagnose_job_returns_skew_finding(tmp_path):
    from apex.commander.clickstack_mvp import append_envelope
    from apex.commander.diagnostic_mvp import diagnose_job
    from apex.commander.telemetry import build_telemetry

    store = tmp_path / "clickstack.ndjson"
    append_envelope(store, build_telemetry(skew_events(), job_id="job-42"))

    finding = diagnose_job(store, "job-42")

    assert finding["status"] == "finding"
    assert finding["title"] == "shuffle_skew_candidate"
    assert finding["confidence"] == "medium"
    assert finding["job_id"] == "job-42"
    assert finding["evidence"]["stage_id"] == 4
    assert finding["evidence"]["ratio"] > 10
    assert "spark.sql.adaptive.skewJoin.enabled" in finding["recommendations"][0]


def test_diagnose_job_does_not_flag_balanced_baseline(tmp_path):
    from apex.commander.clickstack_mvp import append_envelope
    from apex.commander.diagnostic_mvp import diagnose_job
    from apex.commander.telemetry import build_telemetry

    store = tmp_path / "clickstack.ndjson"
    append_envelope(store, build_telemetry(no_skew_events(), job_id="balanced-job"))

    finding = diagnose_job(store, "balanced-job")

    assert finding["status"] == "no_finding"
    assert finding["title"] == "no_commander_v01_finding"


def test_commander_v01_demo_cli_outputs_json_finding(tmp_path):
    input_log = write_events(tmp_path / "events.ndjson", skew_events())
    store = tmp_path / "clickstack.ndjson"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "commander_v01_demo.py"),
            str(input_log),
            str(store),
            "--job-id",
            "job-42",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["title"] == "shuffle_skew_candidate"
    assert payload["job_id"] == "job-42"
