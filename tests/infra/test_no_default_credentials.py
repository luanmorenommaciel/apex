"""T-20261103-infra-no-default-credentials — no default password, no world-facing ports.

docker compose config fails without CLICKHOUSE_PASSWORD; every published port binds to
127.0.0.1 unless BIND_HOST overrides; preflight.sh refuses empty/default credentials and
accepts generated ones; the four infra scripts carry no default password and fail by name;
make up runs preflight before compose.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from _live import REPO

INFRA = REPO / "infra"
SCRIPTS = [INFRA / "scripts" / n for n in ("apply_ddl.sh", "seed.sh", "verify.sh", "verify_ddl.py")]
GOOD_PW = "3f9c1a7e5b2d4c6a8e0f1b3d5a7c9e2b"
GOOD_KEY = "ab" * 32
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI required")


def compose_config(extra_env: dict | None = None, drop: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env.update({"HYPERDX_API_KEY": GOOD_KEY, "CLICKHOUSE_PASSWORD": GOOD_PW})
    for k in drop:
        env.pop(k, None)
    env.update(extra_env or {})
    return subprocess.run(
        ["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env.example", "config", "--format", "json"],
        cwd=INFRA, capture_output=True, text=True, env=env,
    )


def preflight(env_text: str | None) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        env_file = Path(tmp) / "env"
        if env_text is not None:
            env_file.write_text(env_text)
        clean = {k: v for k, v in os.environ.items() if k not in ("CLICKHOUSE_PASSWORD", "HYPERDX_API_KEY")}
        return subprocess.run([str(INFRA / "scripts" / "preflight.sh")], env=dict(clean, INFRA_ENV_FILE=str(env_file)),
                              capture_output=True, text=True)


@needs_docker
def test_compose_refuses_missing_password():
    proc = compose_config(drop=("CLICKHOUSE_PASSWORD",))
    assert proc.returncode != 0
    assert "CLICKHOUSE_PASSWORD" in proc.stderr
    assert compose_config().returncode == 0, compose_config().stderr[-500:]


@needs_docker
def test_ports_bind_loopback():
    services = json.loads(compose_config().stdout)["services"]
    published = [(name, p) for name, svc in services.items() for p in svc.get("ports", [])]
    assert len(published) >= 9
    for name, port in published:
        assert port.get("host_ip") == "127.0.0.1", (name, port)
    services = json.loads(compose_config({"BIND_HOST": "0.0.0.0"}).stdout)["services"]
    for name, svc in services.items():
        for port in svc.get("ports", []):
            assert port.get("host_ip") == "0.0.0.0", (name, port)


def test_preflight_rejects_defaults():
    cases = {
        f"CLICKHOUSE_PASSWORD=apex_local_dev\nHYPERDX_API_KEY={GOOD_KEY}\n": "CLICKHOUSE_PASSWORD",
        f"CLICKHOUSE_PASSWORD=\nHYPERDX_API_KEY={GOOD_KEY}\n": "CLICKHOUSE_PASSWORD",
        f"CLICKHOUSE_PASSWORD=short\nHYPERDX_API_KEY={GOOD_KEY}\n": "CLICKHOUSE_PASSWORD",
        f"CLICKHOUSE_PASSWORD={GOOD_PW}\nHYPERDX_API_KEY=change-me-openssl-rand-hex-32\n": "HYPERDX_API_KEY",
        f"CLICKHOUSE_PASSWORD={GOOD_PW}\nHYPERDX_API_KEY=abcdef0123\n": "HYPERDX_API_KEY",
        f"CLICKHOUSE_PASSWORD={GOOD_PW}\n": "HYPERDX_API_KEY",
    }
    for text, variable in cases.items():
        proc = preflight(text)
        assert proc.returncode == 1, (text, proc.stdout, proc.stderr)
        assert variable in proc.stdout + proc.stderr, (text, proc.stdout)
    missing = preflight(None)
    assert missing.returncode == 1 and "cp .env.example" in missing.stdout


def test_preflight_accepts_generated():
    proc = preflight(f"CLICKHOUSE_PASSWORD={GOOD_PW}\nHYPERDX_API_KEY={GOOD_KEY}\n")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "preflight ok" in proc.stdout


def test_scripts_have_no_default_password():
    clean = {k: v for k, v in os.environ.items() if k != "CLICKHOUSE_PASSWORD"}
    clean["INFRA_ENV_FILE"] = "/nonexistent/apex-infra.env"
    for script in SCRIPTS:
        assert "apex_local_dev" not in script.read_text(), script.name
        cmd = ["python3", str(script)] if script.suffix == ".py" else [str(script)]
        proc = subprocess.run(cmd, env=clean, capture_output=True, text=True, cwd=INFRA)
        assert proc.returncode != 0, script.name
        assert "CLICKHOUSE_PASSWORD" in proc.stdout + proc.stderr, (script.name, proc.stdout, proc.stderr)


def test_make_up_runs_preflight_first():
    proc = subprocess.run(["make", "-n", "up"], cwd=INFRA, capture_output=True, text=True, check=True)
    lines = [l for l in proc.stdout.splitlines() if l.strip()]
    assert "preflight.sh" in lines[0], lines
    assert any("docker compose up" in l for l in lines[1:]), lines
    assert (INFRA / ".env.example").read_text().count("CLICKHOUSE_PASSWORD=\n") == 1
    assert re.search(r"^HYPERDX_API_KEY=$", (INFRA / ".env.example").read_text(), re.M)
