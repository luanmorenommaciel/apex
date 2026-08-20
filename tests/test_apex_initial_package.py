from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apex.ps1"
MAC_SCRIPT = ROOT / "scripts" / "apex.sh"
PACKAGE_MAKEFILE = ROOT / "Makefile"


def _powershell() -> str:
    executable = shutil.which("pwsh")
    if not executable:
        pytest.skip("PowerShell 7 is required for the package contract test")
    return executable


@pytest.mark.parametrize(
    "action",
    ["bootstrap", "doctor", "smoke", "e2e", "tail-outlier", "pilot-clean", "status", "down"],
)
def test_every_command_has_a_non_mutating_dry_run(action: str) -> None:
    completed = subprocess.run(
        [_powershell(), "-NoProfile", "-File", str(SCRIPT), action, "-DryRun"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    assert f"APEX_DRY_RUN=passed action={action}" in completed.stdout
    assert "mutations=0 external_calls=0" in completed.stdout


def test_package_uses_generated_local_secrets() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "RandomNumberGenerator" in source
    assert "Get-ExistingContainerEnvValue" in source
    assert "'-ExecutionPolicy', 'Bypass'" in source
    assert "$script:PowerShellExe" in source
    assert "spark-defaults.conf" in source
    assert "Set-S3SecretEnvironment" in source
    assert "S3AccessKeyFile" in source
    assert "S3SecretKeyFile" in source
    assert "spark.hadoop.fs.s3a.access.key" not in source
    assert "spark.hadoop.fs.s3a.secret.key" not in source
    assert "MINIO_ROOT_PASSWORD" in source
    assert "ANTHROPIC_API_KEY" not in source
    assert "OPENAI_API_KEY" not in source
    assert "down', '-v" not in source
    assert "docker volume rm" not in source
    assert "docker network rm" not in source
    assert "docker rm" not in source
    assert "applied=false" not in source


def test_package_requires_powershell_7_without_legacy_fallback() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert source.startswith("#Requires -Version 7.0\n")
    assert "$script:PowerShellExe = 'pwsh'" in source
    assert "'powershell'" not in source


def test_package_runtime_directory_is_ignored() -> None:
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".apex/" in ignored


def test_macos_entry_point_installs_prerequisites_then_delegates_to_shared_bootstrap() -> None:
    source = MAC_SCRIPT.read_text(encoding="utf-8")

    assert 'ACTION="${1:-help}"' in source
    assert '"$ACTION" == "install"' in source
    assert "brew install powershell" in source
    assert "brew install uv" in source
    assert "brew fetch --cask docker-desktop" in source
    assert 'ditto "$mount_dir/Docker.app" /Applications/Docker.app' in source
    assert "DOCKER_APP_BIN" in source
    assert "uv python install 3.11" in source
    assert 'exec pwsh -NoProfile -ExecutionPolicy Bypass -File' in source


def test_root_makefile_delegates_package_actions_to_platform_launchers() -> None:
    source = PACKAGE_MAKEFILE.read_text(encoding="utf-8")

    assert "PACKAGE_RUN := pwsh" in source
    assert "PACKAGE_RUN := ./scripts/apex.sh" in source
    for action in ("bootstrap", "doctor", "smoke", "e2e", "tail-outlier", "pilot-clean", "status", "down"):
        assert f"{action}: ##" in source
        assert f"$(PACKAGE_RUN) {action}" in source


def test_clean_pilot_is_fail_closed_and_sanitized() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "Assert-CleanPilotEnvironment" in source
    assert "APEX_CLEAN_PILOT=refused" in source
    assert "APEX_CLEAN_PILOT=passed" in source
    assert "apex.clean_pilot.v1" in source
    assert "secret_values_in_report = $false" in source
    assert "external_llm_called = $false" in source
    assert "automatic_fix_applied = $false" in source
