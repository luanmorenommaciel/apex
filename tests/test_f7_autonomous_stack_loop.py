from pathlib import Path

import pytest

from scripts import f7_autonomous_stack_loop as loop


def test_build_spark_submit_command_targets_autonomous_master():
    command = loop.build_spark_submit_command("/tmp/job.py")

    assert command == [
        "docker",
        "exec",
        "apex-autonomous-spark-master",
        "/opt/spark/bin/spark-submit",
        "--master",
        "spark://spark-master:7077",
        "/tmp/job.py",
    ]


def test_build_fetch_eventlog_command_uses_minio_bucket_and_network():
    command = loop.build_fetch_eventlog_command("app-1", "before_eventlog.zstd")

    assert command[:4] == ["docker", "run", "--rm", "--network"]
    assert "apex-autonomous_default" in command
    assert "quay.io/minio/mc:RELEASE.2025-08-13T08-35-41Z" in command
    assert "local/spark-logs/events/eventlog_v2_app-1/events_1_*" in command[-1]
    assert "/out/before_eventlog.zstd" in command[-1]


def test_write_after_job_applies_official_skew_safe_join(tmp_path):
    before = tmp_path / "before.py"
    after = tmp_path / "after.py"
    before.write_text(
        "\n".join(
            [
                "from pyspark.sql.functions import col, rand, when, collect_list",
                '(SparkSession.builder.appName("x")',
                '    .config("spark.sql.adaptive.coalescePartitions.enabled", "false")',
                "    .getOrCreate())",
                'result = orders.join(customers, "customer_id", "inner")',
            ]
        ),
        encoding="utf-8",
    )

    loop.write_after_job(before, after)

    text = after.read_text(encoding="utf-8")
    assert "from pyspark.sql.functions import broadcast, col, rand, when, collect_list" in text
    assert 'spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760"' in text
    assert 'orders.join(broadcast(customers), "customer_id", "inner")' in text
    assert "APEX::FIXED_BY_F7_LOOP" in text


def test_assert_gate_accepts_clean_improved_comparison():
    loop.assert_gate(
        {
            "status": "improved",
            "before": {
                "metrics": {
                    "finding_count": 1,
                    "max_skew_ratio": 29.4,
                    "total_spilled_bytes": 1157481,
                }
            },
            "after": {
                "metrics": {
                    "finding_count": 0,
                    "max_skew_ratio": 0.0,
                    "total_spilled_bytes": 0,
                }
            },
        }
    )


def test_assert_gate_rejects_dirty_after_job():
    with pytest.raises(RuntimeError, match="after job must be clean"):
        loop.assert_gate(
            {
                "status": "improved",
                "before": {
                    "metrics": {
                        "finding_count": 1,
                        "max_skew_ratio": 29.4,
                        "total_spilled_bytes": 1157481,
                    }
                },
                "after": {
                    "metrics": {
                        "finding_count": 1,
                        "max_skew_ratio": 0.0,
                        "total_spilled_bytes": 0,
                    }
                },
            }
        )


def test_make_paths_keeps_evidence_under_generated_loop_dir():
    paths = loop.make_paths("unit")

    assert paths.run_dir == Path(loop.ROOT, "evidence", "generated", "f7-autonomous-loop", "unit")
    assert paths.evidence_log == Path(loop.ROOT, "evidence", "f7-autonomous-stack-loop-unit.log")
