"""T-20261103-infra-compose-resilience-pins — the stack is self-healing, bounded, pinned.

Rendered-compose assertions (docker compose config against .env.example): every
long-running service restarts unless-stopped with a memory limit; one-shot services are
gated by a service_completed_successfully consumer; hyperdx waits for a HEALTHY mongodb;
every image is repo:tag@sha256 and the digest is what the registry serves for that tag.
The mongo healthcheck is run against a fake mongosh to prove it fails on anything but 1.
"""
from __future__ import annotations

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
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI required")
PINNED = re.compile(r"^(?P<repo>[\w./-]+):(?P<tag>[\w.-]+)@(?P<digest>sha256:[0-9a-f]{64})$")
EXPECTED_TAGS = {
    "clickhouse": ("clickhouse/clickhouse-server", "24.8.14.39"),
    "mongodb": ("mongo", "5.0.32-focal"),
    "hyperdx": ("hyperdx/hyperdx", "2.43.1"),
    "otel-collector": ("otel/opentelemetry-collector-contrib", "0.156.0"),
    "queue-init": ("busybox", "1.36"),
}


def rendered_compose() -> dict:
    out = subprocess.run(
        ["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env.example", "config", "--format", "json"],
        cwd=INFRA, capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def one_shot_services(services: dict) -> set[str]:
    gated = set()
    for svc in services.values():
        for dep, spec in (svc.get("depends_on") or {}).items():
            if spec.get("condition") == "service_completed_successfully":
                gated.add(dep)
    return gated


@needs_docker
def test_every_service_restarts_and_is_bounded():
    services = rendered_compose()["services"]
    one_shot = one_shot_services(services)
    for name, svc in services.items():
        limit = svc.get("deploy", {}).get("resources", {}).get("limits", {}).get("memory")
        assert limit, f"{name} has no memory limit"
        if name in one_shot:
            assert svc.get("restart", "no") == "no", f"{name} is one-shot and must not restart"
        else:
            assert svc.get("restart") == "unless-stopped", f"{name} restart={svc.get('restart')}"


@needs_docker
def test_hyperdx_waits_for_healthy_mongo():
    services = rendered_compose()["services"]
    assert services["hyperdx"]["depends_on"]["mongodb"]["condition"] == "service_healthy"
    assert services["hyperdx"]["depends_on"]["clickhouse"]["condition"] == "service_healthy"
    assert "healthcheck" in services["mongodb"]


@needs_docker
def test_images_pinned_by_digest():
    services = rendered_compose()["services"]
    assert set(services) >= set(EXPECTED_TAGS)
    for name, (repo, tag) in EXPECTED_TAGS.items():
        m = PINNED.match(services[name]["image"])
        assert m, f"{name}: {services[name]['image']} is not repo:tag@sha256"
        assert (m["repo"], m["tag"]) == (repo, tag), name
        inspect = subprocess.run(["docker", "buildx", "imagetools", "inspect", f"{repo}:{tag}"],
                                 capture_output=True, text=True)
        assert inspect.returncode == 0, inspect.stderr[-500:]
        served = re.search(r"^Digest:\s+(sha256:[0-9a-f]{64})", inspect.stdout, re.M).group(1)
        assert served == m["digest"], f"{name}: registry serves {served} for {repo}:{tag}"


@needs_docker
def test_mongo_healthcheck_discriminates():
    test = rendered_compose()["services"]["mongodb"]["healthcheck"]["test"]
    assert test[0] == "CMD-SHELL", test
    command = test[1]
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "mongosh"
        fake.write_text('#!/bin/sh\ncase "$FAKE_PING" in\n  fail) echo "MongoNetworkError: connect ECONNREFUSED" >&2; exit 1;;\n  *) echo "$FAKE_PING";;\nesac\n')
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ, PATH=f"{tmp}:{os.environ['PATH']}")
        def run(ping):
            return subprocess.run(["sh", "-c", command], env=dict(env, FAKE_PING=ping), capture_output=True).returncode
        assert run("1") == 0
        assert run("0") != 0, "a false ping passed"
        assert run("fail") != 0, "a connection error passed"
        assert run("10") != 0, "a non-exact match passed"
