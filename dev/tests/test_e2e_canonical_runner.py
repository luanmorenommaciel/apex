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


# ── Runner parity (T-20261019-dev-canonical-runners-parity) ────────────────

SH = (DEV / "scripts" / "e2e_canonical.sh").read_text(encoding="utf-8")
PS1 = (DEV / "scripts" / "e2e_canonical.ps1").read_text(encoding="utf-8")
R9D = (DEV / "scripts" / "r9d_e2e_canonical_noplugin.ps1").read_text(encoding="utf-8")
GENERATOR = (DEV / "jobs" / "generate_data.py").read_text(encoding="utf-8")


def test_bash_runner_never_builds_the_image_implicitly() -> None:
    assert "up -d --build" not in SH
    assert 'E2E_CANONICAL_BUILD:-0' in SH
    assert "dev image is missing - run 'make build' or set E2E_CANONICAL_BUILD=1" in SH
    # the explicit build path exists and is separate from the default path
    assert '"${COMPOSE[@]}" build && "${COMPOSE[@]}" up -d --wait' in SH


def test_powershell_runner_never_builds_the_image_implicitly() -> None:
    assert "'--build'" not in PS1
    assert "[switch]$Build" in PS1
    assert "Invoke-Compose @('build')" in PS1
    assert "dev image is missing - run 'make build' or pass -Build." in PS1


def test_powershell_runner_exposes_the_bash_knobs() -> None:
    for parameter in (
        "[switch]$StartDev",
        "[switch]$ReuseDev",
        "[switch]$SkipGenerate",
        "[switch]$Build",
        "[string]$DriverHost = 'spark-master'",
        "[string]$EnvFile = '.env'",
        "[string[]]$AdditionalComposeFile = @()",
    ):
        assert parameter in PS1, parameter
    for knob in (
        "E2E_CANONICAL_REUSE_DEV",
        "E2E_CANONICAL_SKIP_GENERATE",
        "E2E_CANONICAL_BUILD",
        "APEX_CANONICAL_DRIVER_HOST",
        "E2E_CANONICAL_COMPOSE_FILES",
    ):
        assert knob in SH, knob


def test_both_runners_honour_the_driver_host_override() -> None:
    assert 'DRIVER_HOST="${APEX_CANONICAL_DRIVER_HOST:-spark-master}"' in SH
    assert "spark.driver.host=spark-master" not in PS1
    assert PS1.count('"spark.driver.host=$DriverHost"') == 2  # scenario submit + generate
    assert "spark.driver.bindAddress=0.0.0.0" in SH and "spark.driver.bindAddress=0.0.0.0" in PS1


def test_both_runners_accept_additional_compose_files_like_the_r9d_arm() -> None:
    assert 'for extra in ${E2E_CANONICAL_COMPOSE_FILES:-}; do COMPOSE+=(-f "$extra"); done' in SH
    loop = "foreach ($composeFile in $AdditionalComposeFile) {\n    $compose += @('-f', $composeFile)\n}"
    assert loop in PS1
    assert loop in R9D


def test_all_three_runners_expect_the_marker_the_generator_prints() -> None:
    marker = "hot_keys_~50pct="
    assert marker in GENERATOR
    assert "hot_keys_~50pct=PASS" in SH
    assert "hot_keys_~50pct=PASS" in PS1
    assert "hot_keys_~50pct=PASS" in R9D
    assert "hot_key_~50pct" not in R9D


def test_default_scenario_list_is_unchanged_in_both_runners() -> None:
    assert "REQUESTED_SCENARIOS=(skew_join spill bad_shuffle driver_oom)" in SH
    assert "[string[]]$Scenario = @('skew_join', 'spill', 'bad_shuffle', 'driver_oom')" in PS1
    assert "[ValidateSet('skew_join', 'tail_outlier', 'spill', 'bad_shuffle', 'driver_oom')]" in PS1


def test_start_dev_and_reuse_dev_are_mutually_exclusive_in_powershell() -> None:
    assert "-StartDev and -ReuseDev are mutually exclusive." in PS1


def test_both_runners_accept_the_aliased_infra_collector() -> None:
    sh = (DEV / "scripts" / "e2e_canonical.sh").read_text(encoding="utf-8")
    ps1 = (DEV / "scripts" / "e2e_canonical.ps1").read_text(encoding="utf-8")
    for source in (sh, ps1):
        assert "apex-infra-otel-collector" in source
        assert "{{range .Containers}}{{.Name}} {{end}}" in source
    assert "collector_available ||" in sh
    assert "Test-CollectorAvailable" in ps1


def test_bash_runner_is_executable_in_git() -> None:
    import subprocess
    mode = subprocess.run(
        ["git", "ls-files", "-s", "scripts/e2e_canonical.sh"], cwd=DEV, capture_output=True, text=True
    ).stdout.split()
    assert mode and mode[0] == "100755", mode
