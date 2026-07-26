from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apex.ps1"


def _powershell() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        pytest.skip("PowerShell is required for the package contract test")
    return executable


@pytest.mark.parametrize(
    "action", ["bootstrap", "doctor", "smoke", "e2e", "status", "down"]
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
    assert "MINIO_ROOT_PASSWORD" in source
    assert "ANTHROPIC_API_KEY" not in source
    assert "OPENAI_API_KEY" not in source
    assert "down', '-v" not in source
    assert "applied=false" not in source


def test_package_is_explicitly_ignored() -> None:
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".apex/" in ignored
