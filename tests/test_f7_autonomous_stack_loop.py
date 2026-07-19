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
    assert "local/spark-logs/events/eventlog_v2_app-1/events_1_app-1.zstd" in command[-1]
    assert "/out/before_eventlog.zstd" in command[-1]


class _MemoryLogger:
    def __init__(self):
        self.lines = []

    def line(self, text: str) -> None:
        self.lines.append(text)


def test_build_listener_jar_command_compiles_with_spark_image():
    output_jar = Path(loop.ROOT, "evidence", "generated", "unit", "listener.jar")
    command = loop.build_listener_jar_command(output_jar)

    assert command[:3] == ["docker", "run", "--rm"]
    assert "--user" in command
    assert "root" in command
    assert "spark-plat-v0-spark:4.1.2" in command
    assert "/work" in command
    assert f"{output_jar.parent.resolve()}:/out" in command
    assert "javac -cp '/opt/spark/jars/*'" in command[-1]
    assert "/tmp/apex-listener-build/classes" in command[-1]
    assert "mkdir -p /tmp/apex-listener-build/classes build/libs" not in command[-1]
    assert "rm -rf /out/apex-spark-listener-0.1.0.jar" in command[-1]
    assert "cp /tmp/apex-listener-build/apex-spark-listener-0.1.0.jar" in command[-1]
    assert "/out/apex-spark-listener-0.1.0.jar" in command[-1]


def test_prepare_listener_build_dir_recreates_clean_host_paths(tmp_path):
    build_dir = tmp_path / "listener-jvm" / "build"
    (build_dir / "libs").mkdir(parents=True)
    (build_dir / "libs" / "stale.jar").write_text("old", encoding="utf-8")
    logger = _MemoryLogger()

    loop.prepare_listener_build_dir(logger, build_dir=build_dir, workspace_root=tmp_path)

    assert (build_dir / "classes" / "java" / "main").is_dir()
    assert (build_dir / "libs").is_dir()
    assert not (build_dir / "libs" / "stale.jar").exists()
    assert logger.lines == [f"listener_build_dir_prepared={build_dir}"]


def test_prepare_listener_build_dir_replaces_file_at_build_path(tmp_path):
    build_dir = tmp_path / "listener-jvm" / "build"
    build_dir.parent.mkdir(parents=True)
    build_dir.write_text("not a directory", encoding="utf-8")

    loop.prepare_listener_build_dir(_MemoryLogger(), build_dir=build_dir, workspace_root=tmp_path)

    assert (build_dir / "classes" / "java" / "main").is_dir()
    assert (build_dir / "libs").is_dir()


def test_prepare_listener_build_dir_rejects_path_outside_workspace(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside" / "build"

    with pytest.raises(RuntimeError, match="outside workspace"):
        loop.prepare_listener_build_dir(_MemoryLogger(), build_dir=outside, workspace_root=tmp_path)


def test_write_after_job_applies_official_skew_safe_join(tmp_path):
    before = tmp_path / "before.py"
    after = tmp_path / "after.py"
    before.write_text(
        "\n".join(
            [
                "from pyspark.sql.functions import col, rand, when, collect_list",
                '(SparkSession.builder.appName("x")',
                '    .config("spark.sql.adaptive.enabled", "false")',
                '    .config("spark.sql.adaptive.skewJoin.enabled", "false")',
                '    .config("spark.sql.adaptive.coalescePartitions.enabled", "false")',
                '    .config("spark.sql.adaptive.autoBroadcastJoinThreshold", "-1")',
                "    .getOrCreate())",
                'result = orders.join(customers.hint("shuffle_merge"), "customer_id", "inner")  # APEX::ANTIPATTERN',
            ]
        ),
        encoding="utf-8",
    )

    loop.write_after_job(before, after)

    text = after.read_text(encoding="utf-8")
    assert "from pyspark.sql.functions import broadcast, col, rand, when, collect_list" in text
    assert 'spark.sql.adaptive.enabled", "true"' in text
    assert 'spark.sql.adaptive.skewJoin.enabled", "true"' in text
    assert 'spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760"' in text
    assert 'orders.join(broadcast(customers), "customer_id", "inner")' in text
    assert "APEX::FIXED_BY_F7_LOOP" in text
    assert "APEX::ANTIPATTERN" not in text
    assert "shuffle_merge" not in text


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
    assert paths.listener_jar == paths.run_dir / "listener" / "apex-spark-listener-0.1.0.jar"


def test_prepend_pythonpath_keeps_repo_root_first():
    assert loop._prepend_pythonpath("existing", Path("repo")) == f"repo{loop.os.pathsep}existing"
    assert loop._prepend_pythonpath(None, Path("repo")) == "repo"


def test_extract_app_id_prefers_real_spark_app_id_over_application_name():
    output = "\n".join(
        [
            "INFO SparkContext: Submitted application: skew_on_join_30x",
            "INFO StandaloneSchedulerBackend: Connected to Spark cluster with app ID app-20260718201021-0000",
        ]
    )

    assert loop.extract_app_id(output) == "app-20260718201021-0000"
