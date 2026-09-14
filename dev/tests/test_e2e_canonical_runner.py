from pathlib import Path


DEV = Path(__file__).resolve().parents[1]


def test_canonical_runner_never_copies_s3_values_to_arguments_or_spark_conf() -> None:
    source = (DEV / "scripts" / "e2e_canonical.ps1").read_text(encoding="utf-8")

    forbidden = (
        "APEX_S3_ACCESS_KEY",
        "APEX_S3_SECRET_KEY",
        "spark.executorEnv.AWS_ACCESS_KEY_ID",
        "spark.executorEnv.AWS_SECRET_ACCESS_KEY",
        '"AWS_ACCESS_KEY_ID=$',
        '"AWS_SECRET_ACCESS_KEY=$',
        "spark.hadoop.fs.s3a.access.key",
        "spark.hadoop.fs.s3a.secret.key",
    )
    for value in forbidden:
        assert value not in source
