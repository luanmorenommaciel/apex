"""Check a built Serve wheel in a clean venv, without starting either service.

Usage: python tools/check_wheel.py /path/to/apex_mcp-<version>-py3-none-any.whl
Build the artifact first with `uv build --wheel`. Dependencies must already be
cached: downloads require explicit --allow-download. Nothing is uploaded.
"""

from __future__ import annotations

import argparse
import configparser
from email.parser import Parser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile


ENTRYPOINTS = {"apex-mcp": "apex_mcp.server:main", "apex-api": "apex_api.app:main"}
REQUIRED = {"apex_mcp/server.py", "apex_mcp/diagnose.py", "apex_api/app.py",
            "apex_api/routes/diagnostics.py"}


class WheelCheckError(RuntimeError):
    pass


def inspect_wheel(path: Path) -> str:
    """Check artifact contents before installation; do not import the checkout."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if not REQUIRED <= names:
                raise WheelCheckError("wheel_missing_package_modules")
            metadata = [n for n in names if n.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                raise WheelCheckError("wheel_metadata_count")
            info = Parser().parsestr(archive.read(metadata[0]).decode("utf-8"))
            if info.get("Name", "").replace("_", "-").lower() != "apex-mcp":
                raise WheelCheckError("wheel_distribution_name")
            version = info.get("Version")
            if not version:
                raise WheelCheckError("wheel_version_missing")
            entry_file = metadata[0].rsplit("/", 1)[0] + "/entry_points.txt"
            entries = configparser.ConfigParser(interpolation=None)
            entries.read_string(archive.read(entry_file).decode("utf-8"))
            for name, target in ENTRYPOINTS.items():
                if entries.get("console_scripts", name, fallback=None) != target:
                    raise WheelCheckError("wheel_entrypoint_mismatch")
            return version
    except (OSError, zipfile.BadZipFile, KeyError, UnicodeError, configparser.Error) as exc:
        raise WheelCheckError("wheel_unreadable") from None


# -I and a temporary cwd keep the checkout off sys.path. The installed modules
# must live inside the new venv. Entry points are invoked with their service
# runners intercepted, so no listening socket, stdio loop or store call starts.
PROBE = r'''
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import socket
import sys
from unittest.mock import patch

os.environ.clear()
os.environ['APEX_API_TOKENS'] = 'wheel-smoke-placeholder'
dist = metadata.distribution('apex-mcp')
assert dist.version == sys.argv[1], 'installed_version_mismatch'
expected = {'apex-mcp': 'apex_mcp.server:main', 'apex-api': 'apex_api.app:main'}
entries = {e.name: e for e in dist.entry_points if e.group == 'console_scripts'}
origins = {}
with patch.object(socket.socket, 'connect', side_effect=AssertionError('network_forbidden')), \
     patch.object(socket.socket, 'connect_ex', side_effect=AssertionError('network_forbidden')), \
     patch.object(socket, 'create_connection', side_effect=AssertionError('network_forbidden')):
    for name, value in expected.items():
        assert entries[name].value == value, 'installed_entrypoint_mismatch'
        entry = entries[name].load()
        assert callable(entry), 'entrypoint_not_callable'
        origin = Path(sys.modules[entry.__module__].__file__).resolve()
        assert origin.is_relative_to(Path(sys.prefix).resolve()), 'checkout_import_leak'
        command = Path(sys.executable).parent / (name + ('.exe' if os.name == 'nt' else ''))
        assert command.is_file(), 'console_script_not_installed'
        origins[name] = origin.relative_to(Path(sys.prefix).resolve()).as_posix()
        if name == 'apex-mcp':
            with patch('mcp.server.fastmcp.FastMCP.run') as run:
                entry()
                run.assert_called_once_with(transport='stdio')
        else:
            with patch('uvicorn.run') as run:
                entry()
                run.assert_called_once()
                app = run.call_args.args[0]
                assert any(r.path == '/v1/health' for r in app.routes), 'api_routes_missing'
print(json.dumps({'version': dist.version, 'entrypoints': sorted(expected),
                  'origins': origins, 'service_runners_intercepted': True}))
'''


def _run(command: list[str], cwd: Path, env: dict[str, str], phase: str) -> str:
    try:
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                text=True, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise WheelCheckError(f"{phase}_unavailable_or_timeout") from None
    if result.returncode:
        # Installer output can carry private index URLs. Keep the public result
        # opaque; offline install failure is never converted into a skip/PASS.
        raise WheelCheckError(f"{phase}_failed")
    return result.stdout


def check_wheel(path: Path, *, allow_download: bool = False) -> dict:
    path = path.resolve()
    version = inspect_wheel(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    uv = shutil.which("uv")
    if not uv:
        raise WheelCheckError("uv_required")
    with tempfile.TemporaryDirectory(prefix="apex-wheel-check-") as tmp:
        work = Path(tmp)
        target = work / "venv"
        venv.EnvBuilder(with_pip=False).create(target)
        python = target / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = {k: v for k, v in os.environ.items()
               if k not in {"PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"}}
        env["UV_NO_CONFIG"] = "1"
        # A caller's UV_LINK_MODE=symlink must not make installed modules point
        # back into the cache: the probe verifies their resolved venv origins.
        command = [uv, "pip", "install", "--python", str(python), "--link-mode", "copy"]
        if not allow_download:
            command.append("--offline")
        command.append(str(path))
        _run(command, work, env, "install")
        probe = work / "probe.py"
        probe.write_text(PROBE, encoding="utf-8")
        output = _run([str(python), "-I", str(probe), version], work, env, "probe")
        try:
            report = json.loads(output)
            if (report["version"] != version or report["entrypoints"] != sorted(ENTRYPOINTS)
                    or report["service_runners_intercepted"] is not True):
                raise WheelCheckError("probe_result_mismatch")
        except (ValueError, KeyError, TypeError):
            raise WheelCheckError("probe_invalid_result") from None
    return {"status": "passed", "distribution": "apex-mcp", **report,
            "wheel_sha256": digest, "downloads_allowed": allow_download}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--allow-download", action="store_true",
                        help="allow the installer to fetch dependencies; default is offline")
    args = parser.parse_args()
    try:
        report = check_wheel(args.wheel, allow_download=args.allow_download)
    except WheelCheckError as exc:
        print(json.dumps({"status": "failed", "code": str(exc)}))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
