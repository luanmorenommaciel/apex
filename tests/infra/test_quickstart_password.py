"""T-20261103-infra-quickstart-password — no quick-start path exports the old default.

The root README reads infra's rendered secret; the collect C3 overlay refuses to render
without CLICKHOUSE_PASSWORD; no operator-facing path that points at infra's store still
carries apex_local_dev (the client-library defaults in other lanes are follow-up D-12).
"""
from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from _live import REPO

README = REPO / "README.md"
COLLECT = REPO / "collect"
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI required")
SWEEP_PATHS = ["README.md", "infra", "collect/docker-compose.c3-infra.yml", "tests/e2e", "scripts/apex.ps1", "dev"]
SWEEP_EXCLUDES = [":!infra/scripts/preflight.sh"]   # rejects the literal on purpose
# collect/README.md documents its own throwaway store with the base default; only its C3
# section points at infra's store, and that section is checked on its own below.


def test_quickstart_reads_secret():
    text = README.read_text()
    assert "apex_local_dev" not in text
    assert 'APEX_CANONICAL_CH_PASSWORD="$(cat ../infra/secrets/clickhouse_password)"' in text
    assert 'APEX_INFRA_CLICKHOUSE_PASSWORD="$(cat ../infra/secrets/clickhouse_password)"' in text
    assert "make up" in text.split("## Quick start")[1].split("### Prove it")[0]


@needs_docker
def test_collect_overlay_requires_password():
    env = {k: v for k, v in os.environ.items() if k not in ("CLICKHOUSE_PASSWORD", "APEX_INFRA_CLICKHOUSE_PASSWORD")}
    cmd = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.c3-infra.yml",
           "--env-file", ".env.example", "--env-file", ".env.c3-infra.example", "config", "--quiet"]
    refused = subprocess.run(cmd, cwd=COLLECT, capture_output=True, text=True, env=env)
    assert refused.returncode != 0 and "APEX_INFRA_CLICKHOUSE_PASSWORD" in refused.stderr, refused.stderr[-400:]
    ok = subprocess.run(cmd, cwd=COLLECT, capture_output=True, text=True, env=dict(env, APEX_INFRA_CLICKHOUSE_PASSWORD="x" * 20))
    assert ok.returncode == 0, ok.stderr[-400:]
    # the base compose alone still renders: the throwaway store keeps its own default
    base = subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env.example", "config", "--quiet"],
                          cwd=COLLECT, capture_output=True, text=True, env=env)
    assert base.returncode == 0, base.stderr[-400:]


def test_no_default_password_in_repo():
    proc = subprocess.run(["git", "grep", "-n", "apex_local_dev", "--", *SWEEP_PATHS, *SWEEP_EXCLUDES],
                          cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 1, "apex_local_dev survives on an operator-facing path:\n" + proc.stdout
    c3 = (COLLECT / "README.md").read_text().split("## C3 canonical integration")[1].split("## Lane boundaries")[0]
    assert "apex_local_dev" not in c3 and "APEX_INFRA_CLICKHOUSE_PASSWORD" in c3
