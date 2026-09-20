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


def test_posix_canonical_runner_exposes_opt_in_tail_outlier_without_changing_defaults() -> None:
    source = (DEV / "scripts" / "e2e_canonical.sh").read_text(encoding="utf-8")

    assert "REQUESTED_SCENARIOS=(skew_join spill bad_shuffle driver_oom)" in source
    assert "skew_join|tail_outlier|spill|bad_shuffle|driver_oom" in source
    assert "should_run tail_outlier && run_success tail_outlier tail_outlier.py off off" in source
