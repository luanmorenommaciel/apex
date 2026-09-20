from __future__ import annotations

import hashlib
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
        pytest.fail("PowerShell 7 is required for the package contract test")
    return executable


ACTION_HANDLERS = {
    "bootstrap": "Start-Package",
    "doctor": "Assert-Prerequisites+Invoke-Doctor",
    "smoke": "Assert-Prerequisites+Invoke-ProductGate",
    "e2e": "Assert-Prerequisites+Invoke-ProductGate-Full",
    "tail-outlier": "Assert-Prerequisites+Invoke-TailOutlierGate",
    "pilot-clean": "Invoke-CleanPilot",
    "status": "Show-Status",
    "down": "Stop-Package",
}


def _runtime_snapshot() -> tuple[bool, tuple[tuple[str, str], ...]]:
    """Record runtime contents without changing a possibly user-owned directory."""
    runtime_dir = ROOT / ".apex"
    if not runtime_dir.exists():
        return False, ()

    entries: list[tuple[str, str]] = []
    for path in sorted(runtime_dir.rglob("*")):
        relative = path.relative_to(runtime_dir).as_posix()
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append((relative, f"file:{digest}"))
        elif path.is_dir():
            entries.append((relative, "directory"))
        else:
            entries.append((relative, f"other:{path.is_symlink()}"))
    return True, tuple(entries)


@pytest.mark.parametrize(
    ("action", "handler"),
    ACTION_HANDLERS.items(),
)
def test_every_command_has_a_non_mutating_dry_run(action: str, handler: str) -> None:
    completed = subprocess.run(
        [_powershell(), "-NoProfile", "-File", str(SCRIPT), action, "-DryRun"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    summary = f"APEX_DRY_RUN=passed action={action} handler={handler} mutations=0 external_calls=0"
    assert summary in completed.stdout.splitlines()


def test_help_dispatches_to_safe_handler_without_runtime_state() -> None:
    before = _runtime_snapshot()
    completed = subprocess.run(
        [_powershell(), "-NoProfile", "-File", str(SCRIPT), "help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Apex initial package" in completed.stdout
    assert _runtime_snapshot() == before


def test_invalid_action_is_rejected_by_validateset_without_runtime_state() -> None:
    before = _runtime_snapshot()
    completed = subprocess.run(
        [_powershell(), "-NoProfile", "-File", str(SCRIPT), "not-a-package-action"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode != 0
    assert "ValidateSet" in completed.stderr
    assert _runtime_snapshot() == before


def test_representative_dry_runs_leave_runtime_directory_unchanged() -> None:
    before = _runtime_snapshot()
    for action in ("bootstrap", "doctor", "pilot-clean", "status", "down"):
        completed = subprocess.run(
            [_powershell(), "-NoProfile", "-File", str(SCRIPT), action, "-DryRun"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr

    assert _runtime_snapshot() == before


def test_missing_powershell_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _name: None)

    with pytest.raises(pytest.fail.Exception, match="PowerShell 7 is required"):
        _powershell()


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
