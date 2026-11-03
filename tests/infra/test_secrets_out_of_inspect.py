"""T-20261103-infra-secrets-out-of-inspect — no container environment holds the admin password.

The rendered compose carries no CLICKHOUSE_PASSWORD value: clickhouse reads a compose
secret through CLICKHOUSE_PASSWORD_FILE, the collector through ${file:...} (validated with
the contrib image, present and absent), HyperDX connects as the read-only apex_hdx user
from a rendered env file, preflight renders every file with the apex_hdx password hashed,
the generated paths are gitignored, and the scripts fall back to the secret file.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

import pytest

from _live import REPO

INFRA = REPO / "infra"
ADMIN_PW = "9d2b7c4e1f6a3b8c5d0e2f7a4b9c6d1e"
GOOD_KEY = "cd" * 32
RENDER_ENV = dict(os.environ, CLICKHOUSE_PASSWORD=ADMIN_PW, HYPERDX_API_KEY=GOOD_KEY)
COLLECTOR_IMAGE = "otel/opentelemetry-collector-contrib:0.156.0"
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI required")


def rendered_compose() -> dict:
    out = subprocess.run(
        ["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env.example", "config", "--format", "json"],
        cwd=INFRA, capture_output=True, text=True, check=True, env=RENDER_ENV,
    ).stdout
    return json.loads(out)


def run_preflight(tmp: Path, env_text: str | None = None) -> subprocess.CompletedProcess:
    env_file = tmp / "env"
    env_file.write_text(env_text or f"CLICKHOUSE_PASSWORD={ADMIN_PW}\nHYPERDX_API_KEY={GOOD_KEY}\n")
    clean = {k: v for k, v in os.environ.items() if k not in ("CLICKHOUSE_PASSWORD", "HYPERDX_API_KEY")}
    env = dict(clean, INFRA_ENV_FILE=str(env_file), INFRA_SECRETS_DIR=str(tmp / "secrets"), INFRA_LOCAL_DIR=str(tmp / "local"))
    return subprocess.run([str(INFRA / "scripts" / "preflight.sh")], env=env, capture_output=True, text=True)


@needs_docker
def test_no_admin_password_in_environment():
    cfg = rendered_compose()
    services = cfg["services"]
    for name, svc in services.items():
        for key, value in (svc.get("environment") or {}).items():
            assert ADMIN_PW not in str(value), f"{name}.environment.{key} carries the admin password"
            assert key != "CLICKHOUSE_PASSWORD", f"{name} still has a CLICKHOUSE_PASSWORD variable"
    assert services["clickhouse"]["environment"]["CLICKHOUSE_PASSWORD_FILE"] == "/run/secrets/clickhouse_password"
    for name in ("clickhouse", "otel-collector"):
        assert any(s["source"] == "clickhouse_password" for s in services[name]["secrets"]), name
    assert cfg["secrets"]["clickhouse_password"]["file"].endswith("infra/secrets/clickhouse_password")
    assert "$(cat /run/secrets/clickhouse_password)" in services["clickhouse"]["healthcheck"]["test"][1]
    text = "\n".join(l for l in (INFRA / "otel-collector-config.yaml").read_text().splitlines() if not l.lstrip().startswith("#"))
    assert "password: ${file:/run/secrets/clickhouse_password}" in text
    assert "${env:CLICKHOUSE_PASSWORD}" not in text


@needs_docker
def test_collector_reads_secret_file():
    config = INFRA / "otel-collector-config.yaml"
    with tempfile.TemporaryDirectory() as tmp:
        secret = Path(tmp) / "clickhouse_password"
        secret.write_text(ADMIN_PW)
        secret.chmod(0o644)  # the collector runs as uid 10001; a compose secret is world-readable too
        base = ["docker", "run", "--rm", "-e", "CLICKHOUSE_USER=apex", "-v", f"{config}:/c.yaml:ro"]
        ok = subprocess.run(base + ["-v", f"{secret}:/run/secrets/clickhouse_password:ro", COLLECTOR_IMAGE, "validate", "--config", "/c.yaml"],
                            capture_output=True, text=True)
        assert ok.returncode == 0, ok.stderr[-1500:]
        absent = subprocess.run(base + [COLLECTOR_IMAGE, "validate", "--config", "/c.yaml"], capture_output=True, text=True)
        assert absent.returncode != 0
        assert "/run/secrets/clickhouse_password" in absent.stderr


@needs_docker
def test_hyperdx_uses_readonly_user():
    hyperdx = rendered_compose()["services"]["hyperdx"]
    assert "DEFAULT_CONNECTIONS" not in (hyperdx.get("environment") or {})
    # `config` folds env_file into environment (and drops an absent required:false file),
    # so the declaration is checked in the source compose.
    source = (INFRA / "docker-compose.yml").read_text()
    assert "env_file:\n      - path: ./.local/hyperdx.env\n        required: false" in source
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        assert run_preflight(tmp).returncode == 0
        line = next(l for l in (tmp / "local" / "hyperdx.env").read_text().splitlines() if l.startswith("DEFAULT_CONNECTIONS="))
        conn = json.loads(line.split("=", 1)[1])[0]
        hdx_pw = (tmp / "secrets" / "hyperdx_clickhouse_password").read_text().strip()
        assert conn["username"] == "apex_hdx"
        assert conn["password"] == hdx_pw and hdx_pw != ADMIN_PW
        assert conn["host"] == "http://apex-infra-clickhouse:8123"


def test_preflight_generates_secrets():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        first = run_preflight(tmp)
        assert first.returncode == 0, first.stdout + first.stderr
        admin = tmp / "secrets" / "clickhouse_password"
        hdx = tmp / "secrets" / "hyperdx_clickhouse_password"
        xml = tmp / "local" / "users.d" / "apex-hyperdx.xml"
        assert admin.read_text() == ADMIN_PW
        assert re.fullmatch(r"[0-9a-f]{48}\n?", hdx.read_text())
        for f in (admin, hdx, xml):
            assert stat.S_IMODE(f.stat().st_mode) == 0o600, f
        text = xml.read_text()
        assert hashlib.sha256(hdx.read_text().strip().encode()).hexdigest() in text
        assert hdx.read_text().strip() not in text and ADMIN_PW not in text, "plaintext password in users.d"
        assert "<readonly>2</readonly>" in text and "GRANT SELECT ON apex.spark_events" in text
        assert "GRANT SELECT ON apex.otel_traces" not in text and "apex.*</query>" not in text.replace("SHOW TABLES ON apex.*", "")
        second = run_preflight(tmp)
        assert second.returncode == 0
        assert hdx.read_text() == (tmp / "secrets" / "hyperdx_clickhouse_password").read_text(), "apex_hdx password must persist across runs"


def test_generated_paths_gitignored():
    for path in ("infra/secrets/clickhouse_password", "infra/secrets/hyperdx_clickhouse_password",
                 "infra/.local/hyperdx.env", "infra/.local/users.d/apex-hyperdx.xml"):
        proc = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO)
        assert proc.returncode == 0, f"{path} is not gitignored"


def test_scripts_read_secret_file():
    with tempfile.TemporaryDirectory() as tmp:
        secrets = Path(tmp) / "secrets"
        secrets.mkdir()
        (secrets / "clickhouse_password").write_text(ADMIN_PW)
        clean = {k: v for k, v in os.environ.items() if k != "CLICKHOUSE_PASSWORD"}
        env = dict(clean, INFRA_ENV_FILE="/nonexistent/apex-infra.env", INFRA_SECRETS_DIR=str(secrets),
                   INFRA_CLICKHOUSE_CONTAINER="apex-nonexistent-container", OTLP_HTTP_HOST_PORT="1", CLICKHOUSE_HTTP_HOST_PORT="1")
        for name in ("apply_ddl.sh", "seed.sh", "verify.sh", "verify_ddl.py"):
            script = INFRA / "scripts" / name
            cmd = ["python3", str(script)] if name.endswith(".py") else [str(script)]
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=INFRA)
            out = proc.stdout + proc.stderr
            assert "CLICKHOUSE_PASSWORD" not in out, (name, out[-400:])   # it got past credentials
            assert proc.returncode != 0, name                                # ...and failed later, on the absent stack
        env.pop("INFRA_SECRETS_DIR")
        env["INFRA_SECRETS_DIR"] = "/nonexistent/secrets"
        proc = subprocess.run(["python3", str(INFRA / "scripts" / "verify_ddl.py")], env=env, capture_output=True, text=True, cwd=INFRA)
        assert "CLICKHOUSE_PASSWORD" in proc.stdout and proc.returncode == 2
