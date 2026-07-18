from apex.commander.clickhouse_adapter import ClickHouseTelemetryStore
from apex.commander.clickstack_mvp import append_envelope
from apex.commander.telemetry_compare import compare_job_telemetry


class FakeQueryResult:
    def __init__(self, result_rows):
        self.result_rows = result_rows


class FakeClickHouseClient:
    def __init__(self):
        self.rows = []

    def command(self, sql):
        pass

    def insert(self, table, rows, column_names):
        for row in rows:
            self.rows.append(dict(zip(column_names, row)))

    def query(self, sql, parameters):
        job_id = parameters["job_id"]
        return FakeQueryResult(
            [[row["envelope_json"]] for row in self.rows if row["job_id"] == job_id]
        )


def telemetry_envelope(
    job_id,
    *,
    ratio=1.0,
    disk_spill=0,
    memory_spill=0,
    gc_time=0,
    run_time=10000,
    aqe_updates=0,
    failure_reasons=None,
    shuffle_read_bytes=0,
):
    if not shuffle_read_bytes and (disk_spill or memory_spill):
        shuffle_read_bytes = 300 * 1024 * 1024
    stage = {
        "stage_id": 2,
        "task_count": 8,
        "records": [1000, 1000, 1000, 1000],
        "total_records": 4000,
        "max_records": 1000,
        "median_cold_records": 1000,
        "ratio": ratio,
        "evidence_status": "valid",
        "quality_issues": [],
        "disk_bytes_spilled": disk_spill,
        "memory_bytes_spilled": memory_spill,
        "shuffle_read_bytes": shuffle_read_bytes,
        "shuffle_read_records": 4000,
        "jvm_gc_time_ms": gc_time,
        "executor_run_time_ms": run_time,
        "failure_reasons": failure_reasons or [],
    }
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": job_id,
        "app_id": "app-compare",
        "event_counts": {
            "SparkListenerTaskEnd": 8,
            "SparkListenerSQLAdaptiveExecutionUpdate": aqe_updates,
        },
        "stages": [stage],
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


def test_compare_job_telemetry_reports_improved_after_rerun(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(
        store,
        telemetry_envelope(
            "before-job",
            ratio=29.5,
            disk_spill=2 * 1024 * 1024,
            gc_time=4000,
            run_time=10000,
            aqe_updates=4,
        ),
    )
    append_envelope(store, telemetry_envelope("after-job", ratio=1.0))

    result = compare_job_telemetry(store, "before-job", "after-job")

    assert result["status"] == "improved"
    assert result["summary"]["resolved_findings"] == [
        "gc_pressure_candidate",
        "plan_aqe_replan_candidate",
        "shuffle_skew_candidate",
        "shuffle_spill_candidate",
    ]
    assert result["before"]["finding_count"] == 4
    assert result["after"]["finding_count"] == 0
    assert _comparison(result, "max_skew_ratio")["status"] == "improved"


def test_compare_job_telemetry_reports_regression(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=1.0))
    append_envelope(
        store,
        telemetry_envelope(
            "after-job",
            ratio=29.5,
            disk_spill=2 * 1024 * 1024,
        ),
    )

    result = compare_job_telemetry(store, "before-job", "after-job")

    assert result["status"] == "regressed"
    assert result["summary"]["new_findings"] == [
        "shuffle_skew_candidate",
        "shuffle_spill_candidate",
    ]
    assert _comparison(result, "finding_count")["status"] == "regressed"


def test_compare_job_telemetry_reports_not_comparable_when_after_missing(tmp_path):
    store = tmp_path / "store.ndjson"
    append_envelope(store, telemetry_envelope("before-job", ratio=1.0))

    result = compare_job_telemetry(store, "before-job", "missing-after")

    assert result["status"] == "not_comparable"
    assert result["missing_job_ids"] == ["missing-after"]
    assert result["comparisons"] == []


def test_compare_job_telemetry_reads_from_clickhouse_adapter_fake():
    store = ClickHouseTelemetryStore(FakeClickHouseClient())
    store.append_envelope(telemetry_envelope("before-job", ratio=29.5))
    store.append_envelope(telemetry_envelope("after-job", ratio=1.0))

    result = compare_job_telemetry(store, "before-job", "after-job")

    assert result["status"] == "improved"
    assert result["before"]["metrics"]["max_skew_ratio"] == 29.5
    assert result["after"]["metrics"]["max_skew_ratio"] == 1.0


def test_compare_job_telemetry_ignores_invalid_skew_ratio_stages(tmp_path):
    store = tmp_path / "store.ndjson"
    before = telemetry_envelope("before-job", ratio=29.5)
    before["stages"].append(
        {
            **before["stages"][0],
            "stage_id": 3,
            "ratio": float("inf"),
            "evidence_status": "invalid",
            "quality_issues": ["median_cold_records_zero"],
        }
    )
    append_envelope(store, before)
    append_envelope(store, telemetry_envelope("after-job", ratio=1.0))

    result = compare_job_telemetry(store, "before-job", "after-job")

    assert result["before"]["metrics"]["max_skew_ratio"] == 29.5
    assert _comparison(result, "max_skew_ratio")["status"] == "improved"


def _comparison(result, metric):
    return next(item for item in result["comparisons"] if item["metric"] == metric)
