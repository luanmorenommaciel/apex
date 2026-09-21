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


def test_powershell_canonical_runner_resolves_python_before_docker_work() -> None:
    source = (DEV / "scripts" / "e2e_canonical.ps1").read_text(encoding="utf-8")

    resolver = source[source.index("function Get-PythonApplication {"):]
    resolver = resolver[: resolver.index("\n}\n")]
    assert "@('python', 'python3')" in resolver
    assert "@('python3', 'python')" in resolver
    assert "Get-Command $name -CommandType Application" in resolver
    assert "sys.version_info[0] == 3" in resolver
    assert "throw 'Python 3 is required on PATH" in resolver

    preflight = source.index("$pythonExe = Get-PythonApplication")
    first_docker_work = min(
        source.index(marker)
        for marker in ("$compose = @(", "docker network inspect", "Invoke-Compose @(", "& docker ")
    )
    assert preflight < first_docker_work
    assert "New-Item -ItemType Directory" not in source[:preflight]


def test_package_overlay_sources_dev_s3_secrets_from_wrapper_exported_paths() -> None:
    source = (DEV / "docker-compose.package.yml").read_text(encoding="utf-8")

    secrets = source[source.index("\nsecrets:\n") :]
    secrets = secrets[: secrets.index("\nservices:\n") + 1]
    assert (
        "  apex_s3_access_key:\n"
        "    file: ${APEX_S3_ACCESS_KEY_FILE:?set APEX_S3_ACCESS_KEY_FILE}\n"
    ) in secrets
    assert (
        "  apex_s3_secret_key:\n"
        "    file: ${APEX_S3_SECRET_KEY_FILE:?set APEX_S3_SECRET_KEY_FILE}\n"
    ) in secrets

    active = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )
    assert "dev/secrets" not in active
    assert "./secrets/apex_s3_" not in active
    assert "secrets/apex_s3_" not in active


def test_powershell_canonical_runner_never_invokes_bare_python() -> None:
    source = (DEV / "scripts" / "e2e_canonical.ps1").read_text(encoding="utf-8")

    assert "& $pythonExe scripts/canonical_e2e_assert.py" in source
    for line in source.splitlines():
        assert not line.lstrip().startswith("python "), line
