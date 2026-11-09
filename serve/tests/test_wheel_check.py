"""Negative artifact controls for the standalone wheel check; no installation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest


TOOL = Path(__file__).resolve().parents[1] / "tools" / "check_wheel.py"
spec = importlib.util.spec_from_file_location("wheel_check", TOOL)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def wheel(tmp_path, *, missing=None, name="apex-mcp", version="0.2.0", entries=None):
    path = tmp_path / "apex_mcp-0.2.0-py3-none-any.whl"
    files = {name: "# inert artifact fixture\n" for name in check.REQUIRED}
    files["apex_mcp-0.2.0.dist-info/METADATA"] = f"Name: {name}\nVersion: {version}\n"
    files["apex_mcp-0.2.0.dist-info/entry_points.txt"] = (
        "[console_scripts]\n" + (entries if entries is not None else
        "apex-mcp = apex_mcp.server:main\napex-api = apex_api.app:main\n"))
    if missing:
        files.pop(missing)
    with zipfile.ZipFile(path, "w") as archive:
        for key, value in files.items():
            archive.writestr(key, value)
    return path


def test_current_declared_surface_is_read_without_importing(tmp_path):
    assert check.inspect_wheel(wheel(tmp_path)) == "0.2.0"


@pytest.mark.parametrize("missing", sorted(check.REQUIRED))
def test_missing_package_module_fails_before_install(tmp_path, monkeypatch, missing):
    def forbidden(*_a, **_k):
        raise AssertionError("installer must not run for an invalid artifact")
    monkeypatch.setattr(check, "_run", forbidden)
    with pytest.raises(check.WheelCheckError, match="wheel_missing_package_modules"):
        check.check_wheel(wheel(tmp_path, missing=missing))


@pytest.mark.parametrize("entries", [
    "apex-mcp = apex_mcp.server:main\n",
    "apex-mcp = apex_mcp.server:main\napex-api = apex_mcp.server:main\n",
])
def test_missing_or_misrouted_entrypoint_is_rejected(tmp_path, entries):
    with pytest.raises(check.WheelCheckError, match="wheel_entrypoint_mismatch"):
        check.inspect_wheel(wheel(tmp_path, entries=entries))


def test_another_distribution_is_not_accepted(tmp_path):
    with pytest.raises(check.WheelCheckError, match="wheel_distribution_name"):
        check.inspect_wheel(wheel(tmp_path, name="another-package"))


def test_corrupt_archive_returns_failed_json_not_pass(tmp_path):
    path = tmp_path / "broken.whl"
    path.write_text("not a zip")
    result = subprocess.run([sys.executable, str(TOOL), str(path)],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {"status": "failed", "code": "wheel_unreadable"}


def test_installer_error_is_not_skipped_or_leaked(tmp_path):
    with pytest.raises(check.WheelCheckError, match="install_failed") as error:
        check._run([sys.executable, "-c",
                    "import sys; print('private-index-token', file=sys.stderr); sys.exit(3)"],
                   tmp_path, {}, "install")
    assert "private-index-token" not in str(error.value)


@pytest.mark.parametrize("allow_download", [False, True])
def test_downloads_require_explicit_opt_in(tmp_path, monkeypatch, allow_download):
    calls = []
    monkeypatch.setattr(check.shutil, "which", lambda _name: "/fake-uv")

    def record(command, _cwd, _env, phase):
        calls.append((phase, command))
        return json.dumps({"version": "0.2.0", "entrypoints": sorted(check.ENTRYPOINTS),
                           "service_runners_intercepted": True})

    monkeypatch.setattr(check, "_run", record)
    result = check.check_wheel(wheel(tmp_path), allow_download=allow_download)
    assert ("--offline" in calls[0][1]) is not allow_download
    assert result["downloads_allowed"] is allow_download
    assert len(result["wheel_sha256"]) == 64


def test_inherited_symlink_mode_is_overridden(tmp_path, monkeypatch):
    monkeypatch.setenv("UV_LINK_MODE", "symlink")
    monkeypatch.setattr(check.shutil, "which", lambda _name: "/fake-uv")

    def inspect_install(command, _cwd, env, phase):
        if phase == "install":
            assert env["UV_LINK_MODE"] == "symlink"
            assert command[command.index("--link-mode") + 1] == "copy"
        return json.dumps({"version": "0.2.0", "entrypoints": sorted(check.ENTRYPOINTS),
                           "service_runners_intercepted": True})

    monkeypatch.setattr(check, "_run", inspect_install)
    assert check.check_wheel(wheel(tmp_path))["status"] == "passed"
