"""T-20261103-infra-collector-file-storage — infra's collector persists its sending queue.

The config validates with the real contrib image and wires sending_queue.storage to a
file_storage extension; the compose mounts a named queue volume at that directory and
chowns it first (the contrib image runs as uid 10001). Both checks need the docker CLI
and skip without it.
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
# the compose refuses to render without credentials; these are render-only values
RENDER_ENV = dict(os.environ, CLICKHOUSE_PASSWORD="render-only-not-a-real-password", HYPERDX_API_KEY="0" * 64)
COLLECTOR_IMAGE = "otel/opentelemetry-collector-contrib:0.156.0"
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI required")


def rendered_compose() -> dict:
    out = subprocess.run(
        ["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env.example", "config", "--format", "json"],
        cwd=INFRA, capture_output=True, text=True, check=True, env=RENDER_ENV,
    ).stdout
    return json.loads(out)


@needs_docker
def test_collector_config_validates():
    text = "\n".join(re.sub(r"\s+#.*$", "", l) for l in (INFRA / "otel-collector-config.yaml").read_text().splitlines())
    assert re.search(r"^  file_storage:\n    directory: /var/lib/otelcol/queue\n    create_directory: true$", text, re.M)
    assert re.search(r"^    sending_queue:\n(?:      .*\n)*?      storage: file_storage$", text, re.M)
    assert re.search(r"^  extensions: \[health_check, file_storage\]$", text, re.M)
    with tempfile.TemporaryDirectory() as tmp:   # the config reads the password from a compose secret file
        secret = Path(tmp) / "clickhouse_password"
        secret.write_text("validate-only-password")
        secret.chmod(0o644)
        proc = subprocess.run(
            ["docker", "run", "--rm", "-e", "CLICKHOUSE_USER=apex",
             "-v", f"{INFRA / 'otel-collector-config.yaml'}:/c.yaml:ro",
             "-v", f"{secret}:/run/secrets/clickhouse_password:ro", COLLECTOR_IMAGE, "validate", "--config", "/c.yaml"],
            capture_output=True, text=True,
        )
    assert proc.returncode == 0, proc.stderr[-2000:]


@needs_docker
def test_collector_queue_persisted():
    services = rendered_compose()["services"]
    collector = services["otel-collector"]
    mounts = {v["target"]: v for v in collector["volumes"]}
    assert mounts["/var/lib/otelcol/queue"]["type"] == "volume"
    volume = mounts["/var/lib/otelcol/queue"]["source"]
    init = services["queue-init"]
    assert any(v["source"] == volume for v in init["volumes"]), "queue-init must chown the same volume"
    assert "chown -R 10001:10001" in " ".join(init["command"])
    assert collector["depends_on"]["queue-init"]["condition"] == "service_completed_successfully"
