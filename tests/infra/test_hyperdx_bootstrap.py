"""T-20261103-infra-hyperdx-bootstrap — the first HyperDX user comes from the API.

The script is driven against a local fake of GET /installation and POST /register/password
that records every request: it registers exactly once with email, password and
confirmPassword, does nothing when a team exists or on 409, refuses missing credentials
without a request, and run.sh step 6 calls it instead of skipping.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from _live import REPO

SCRIPT = REPO / "infra" / "scripts" / "hyperdx_bootstrap.sh"
RUN_SH = REPO / "tests" / "e2e" / "run.sh"


class FakeHyperDX:
    def __init__(self, team_exists: bool, register_status: int = 200):
        self.requests: list[tuple[str, str, dict | None]] = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def _send(self, status, payload):
                body = json.dumps(payload).encode()
                self.send_response(status); self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            def do_GET(self):
                fake.requests.append(("GET", self.path, None))
                if self.path == "/installation":
                    return self._send(200, {"isTeamExisting": team_exists})
                self._send(404, {"error": "not found"})
            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                fake.requests.append(("POST", self.path, json.loads(raw or b"{}")))
                if self.path == "/register/password":
                    return self._send(register_status, {"error": "teamAlreadyExists"} if register_status == 409 else {"ok": True})
                self._send(404, {"error": "not found"})

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start(); return self

    def __exit__(self, *exc):
        self.server.shutdown(); self.server.server_close()


def run(api_url: str, email="ops@example.com", password="correct-horse-battery") -> subprocess.CompletedProcess:
    clean = {k: v for k, v in os.environ.items() if not k.startswith("HYPERDX_")}
    with tempfile.TemporaryDirectory() as tmp:
        env_file = Path(tmp) / "env"
        lines = [f"HYPERDX_API_URL={api_url}"]
        if email is not None:
            lines.append(f"HYPERDX_ADMIN_EMAIL={email}")
        if password is not None:
            lines.append(f"HYPERDX_ADMIN_PASSWORD={password}")
        env_file.write_text("\n".join(lines) + "\n")
        return subprocess.run([str(SCRIPT)], env=dict(clean, INFRA_ENV_FILE=str(env_file)), capture_output=True, text=True)


def test_hyperdx_bootstrap_registers_once():
    with FakeHyperDX(team_exists=False) as api:
        proc = run(api.url)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        posts = [r for r in api.requests if r[0] == "POST"]
        assert len(posts) == 1 and posts[0][1] == "/register/password"
        assert posts[0][2] == {"email": "ops@example.com", "password": "correct-horse-battery", "confirmPassword": "correct-horse-battery"}
        assert "registered ops@example.com" in proc.stdout


def test_hyperdx_bootstrap_idempotent():
    with FakeHyperDX(team_exists=True) as api:
        proc = run(api.url)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert not [r for r in api.requests if r[0] == "POST"], "registered although a team exists"
    with FakeHyperDX(team_exists=False, register_status=409) as api:
        proc = run(api.url)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert len([r for r in api.requests if r[0] == "POST"]) == 1, "a 409 must not be retried"


def test_hyperdx_bootstrap_refuses_missing():
    with FakeHyperDX(team_exists=False) as api:
        for email, password, variable in ((None, "x" * 16, "HYPERDX_ADMIN_EMAIL"), ("a@b.c", None, "HYPERDX_ADMIN_PASSWORD")):
            proc = run(api.url, email=email, password=password)
            assert proc.returncode == 1 and variable in proc.stdout, (variable, proc.stdout, proc.stderr)
        assert api.requests == [], "no request may leave without credentials"
    unreachable = run("http://127.0.0.1:9")
    assert unreachable.returncode == 1 and "not answering" in unreachable.stdout


def test_e2e_runner_bootstraps_hyperdx():
    text = RUN_SH.read_text()
    assert 'hyperdx_bootstrap.sh"' in text
    assert "SKIP — no team registered yet" not in text
    assert "best-effort" not in text.split('step "6/6')[1]
