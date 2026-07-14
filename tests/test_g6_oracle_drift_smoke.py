import json
from pathlib import Path

from tools.g6_oracle_drift_smoke import main


def _event(event_name, **extra):
    payload = {"Event": event_name}
    payload.update(extra)
    return payload


def _sql_start(join_op="SortMergeJoin"):
    return _event(
        "org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart",
        executionId=1,
        physicalPlanDescription=f"*(5) {join_op} [id#1], [id#2]",
    )


def _stage_submitted(stage_id=4):
    return _event(
        "org.apache.spark.scheduler.SparkListenerStageSubmitted",
        **{
            "Stage Info": {
                "Stage ID": stage_id,
                "Stage Name": "reduce at SortMergeJoin",
            }
        },
    )


def _task_end(stage_id, partition, records):
    return _event(
        "org.apache.spark.scheduler.SparkListenerTaskEnd",
        **{
            "Stage ID": stage_id,
            "Task Type": "ShuffleMapTask",
            "Task Info": {
                "Index": partition,
                "Task ID": partition,
                "Attempt": 0,
                "Failed": False,
            },
            "Task End Reason": {"Reason": "Success"},
            "Task Metrics": {
                "Shuffle Read Metrics": {
                    "Remote Blocks Fetched": 1,
                    "Local Blocks Fetched": 1,
                    "Remote Bytes Read": records,
                    "Local Bytes Read": 0,
                    "Total Records Read": records,
                }
            },
        },
    )


def _write_real_log(path: Path, *, join_op="SortMergeJoin"):
    events = [
        _sql_start(join_op),
        _stage_submitted(4),
        *[
            _task_end(4, i, 160000 if i == 0 else 5400 + i * 10)
            for i in range(8)
        ],
    ]
    path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")


def test_g6_oracle_drift_smoke_passes_with_realistic_log(tmp_path):
    real_log = tmp_path / "real.ndjson"
    summary = tmp_path / "summary.json"
    work_dir = tmp_path / "generated"
    _write_real_log(real_log)

    rc = main(
        [
            "--real-log",
            str(real_log),
            "--work-dir",
            str(work_dir),
            "--summary",
            str(summary),
        ]
    )

    result = json.loads(summary.read_text(encoding="utf-8"))
    assert rc == 0
    assert result["status"] == "passed"
    assert result["oracle_compare"]["returncode"] == 0
    assert "fiel ao Spark real" in result["oracle_compare"]["stdout"]


def test_g6_oracle_drift_smoke_fails_on_join_drift(tmp_path):
    real_log = tmp_path / "real.ndjson"
    summary = tmp_path / "summary.json"
    work_dir = tmp_path / "generated"
    _write_real_log(real_log, join_op="BroadcastHashJoin")

    rc = main(
        [
            "--real-log",
            str(real_log),
            "--work-dir",
            str(work_dir),
            "--summary",
            str(summary),
        ]
    )

    result = json.loads(summary.read_text(encoding="utf-8"))
    assert rc == 1
    assert result["status"] == "failed"
    assert result["oracle_compare"]["returncode"] != 0
    assert "join operator divergiu" in result["oracle_compare"]["stdout"]
