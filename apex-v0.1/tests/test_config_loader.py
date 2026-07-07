from pathlib import Path

from spark_platform.config import get_read_config, get_write_config, load_config


def test_load_config_merges_environment_and_expands_env_vars(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
default:
  lakehouse:
    bucket: "${MINIO_LAKEHOUSE_BUCKET:-lakehouse}"
  entities:
    customer:
      landing:
        read:
          format: json
          path: "s3a://${MINIO_LAKEHOUSE_BUCKET:-lakehouse}/landing/customer"
        write:
          format: json
          path: "s3a://${MINIO_LAKEHOUSE_BUCKET:-lakehouse}/landing/customer"
          mode: overwrite
      bronze:
        read:
          format: delta
          path: "s3a://${MINIO_LAKEHOUSE_BUCKET:-lakehouse}/bronze/customer"
        write:
          format: delta
          path: "s3a://${MINIO_LAKEHOUSE_BUCKET:-lakehouse}/bronze/customer"
          mode: overwrite
local:
  app:
    log_level: DEBUG
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("MINIO_LAKEHOUSE_BUCKET", "unit-lakehouse")

    config = load_config(env="local", config_path=Path(config_path))

    assert config["app"]["log_level"] == "DEBUG"
    assert config["lakehouse"]["bucket"] == "unit-lakehouse"
    assert get_read_config(config, "customer", "landing")["path"] == "s3a://unit-lakehouse/landing/customer"
    assert get_read_config(config, "customer", "bronze")["path"] == "s3a://unit-lakehouse/bronze/customer"
    assert get_write_config(config, "customer", "landing")["format"] == "json"
    assert get_write_config(config, "customer", "bronze")["mode"] == "overwrite"
