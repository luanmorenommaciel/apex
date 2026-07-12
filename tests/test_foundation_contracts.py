from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_clickhouse_ddl_is_published_under_docs_specs():
    expected = ROOT / "pacote-comum" / "apex_telemetry_v1.sql"
    published = ROOT / "docs" / "specs" / "apex_telemetry_v1.sql"

    assert published.read_text(encoding="utf-8") == expected.read_text(
        encoding="utf-8"
    )


def test_canonical_clickhouse_ddl_contains_required_contract_tables():
    ddl = (ROOT / "docs" / "specs" / "apex_telemetry_v1.sql").read_text(
        encoding="utf-8"
    )

    for table in (
        "apex.task_metrics",
        "apex.stage_metrics",
        "apex.sql_plans",
        "apex.findings",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in ddl

    assert "DEFAULT 'apex.telemetry.v1'" in ddl
    assert "shuffle_read_records" in ddl
    assert "ReplacingMergeTree(ingested_at)" in ddl
    assert "ORDER BY (app_id, stage_id, stage_attempt_id, task_id, task_attempt)" in ddl


def test_compose_uses_named_volume_for_clickhouse_and_publishes_canonical_schema():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))

    clickhouse = compose["services"]["clickhouse"]
    volumes = clickhouse["volumes"]

    assert "apex_clickhouse_data:/var/lib/clickhouse" in volumes
    assert (
        "./docs/specs/apex_telemetry_v1.sql:/docker-entrypoint-initdb.d/001-apex-telemetry-v1.sql:ro"
        in volumes
    )
    assert "apex_clickhouse_data" in compose["volumes"]

    forbidden_bind_mounts = [
        volume
        for volume in volumes
        if volume.endswith(":/var/lib/clickhouse")
        and not volume.startswith("apex_clickhouse_data:")
    ]
    assert forbidden_bind_mounts == []


def test_compose_declares_spark_master_worker_and_event_log_volume():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]

    assert {"clickhouse", "spark-master", "spark-worker"}.issubset(services)
    assert "apex_spark_event_logs" in compose["volumes"]
    assert "apex_spark_event_logs:/tmp/spark-events" in services["spark-master"][
        "volumes"
    ]
    assert "apex_spark_event_logs:/tmp/spark-events" in services["spark-worker"][
        "volumes"
    ]
    assert "SPARK_MASTER_URL=spark://spark-master:7077" in services["spark-worker"][
        "environment"
    ]


def test_compose_aligns_g3_environment_with_plat_v0_contract():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]

    assert {"minio", "minio-init"}.issubset(services)
    assert "28123:8123" in services["clickhouse"]["ports"]
    assert "CLICKHOUSE_USER=spv0" in services["clickhouse"]["environment"]
    assert "CLICKHOUSE_PASSWORD=spv0" in services["clickhouse"]["environment"]
    assert "29000:9000" in services["minio"]["ports"]
    assert "MINIO_ROOT_USER=spv0" in services["minio"]["environment"]
    assert "MINIO_ROOT_PASSWORD=spv0spv0" in services["minio"]["environment"]
    assert "apex_minio_data" in compose["volumes"]

    minio_init_command = services["minio-init"]["entrypoint"]
    assert "mc mb --ignore-existing local/spark-logs" in minio_init_command
    assert "local/spark-logs/events/.keep" in minio_init_command

    worker_env = services["spark-worker"]["environment"]
    assert "SPARK_WORKER_CORES=8" in worker_env
    assert "SPARK_WORKER_MEMORY=4G" in worker_env

    spark_defaults = (ROOT / "docker" / "spark" / "spark-defaults.conf").read_text(
        encoding="utf-8"
    )
    assert "spark.eventLog.dir s3a://spark-logs/events" in spark_defaults
    assert "spark.hadoop.fs.s3a.endpoint http://minio:9000" in spark_defaults
