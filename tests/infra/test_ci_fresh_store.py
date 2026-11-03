"""T-20261103-infra-ci-fresh-store — CI provisions and verifies a fresh store.

ci.yml gains an infra job that runs the live infra tests (APEX_INFRA_LIVE=1, from the
engine environment), validates the collector config with the contrib image and a mounted
secret, and renders the infra compose. The pre-existing jobs are byte-identical to main.
"""
from __future__ import annotations

import re
import subprocess

import pytest

from _live import REPO

CI = REPO / ".github" / "workflows" / "ci.yml"


def job_block(text: str, name: str) -> str:
    m = re.search(rf"^  {re.escape(name)}:\n(.*?)(?=^  \w[\w-]*:\n|\Z)", text, re.S | re.M)
    assert m, f"job {name} not found"
    return m.group(0)


def test_ci_has_infra_job():
    text = CI.read_text()
    job = job_block(text, "infra")
    assert "runs-on: ubuntu-latest" in job and "timeout-minutes:" in job
    assert "astral-sh/setup-uv" in job
    assert re.search(r"working-directory: engine\n\s+run: APEX_INFRA_LIVE=1 uv run --extra dev pytest \.\./tests/infra", job)
    assert "otel/opentelemetry-collector-contrib:0.156.0 validate --config" in job
    assert "/run/secrets/clickhouse_password" in job
    assert re.search(r"docker compose -f docker-compose\.yml --env-file \.env\.example config", job)
    assert "continue-on-error" not in job
    assert "infra" in text.split("jobs:")[0], "the header must name the infra job"


def test_ci_other_jobs_unchanged():
    base = None
    for ref in ("main", "origin/main"):
        if subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], cwd=REPO, capture_output=True).returncode == 0:
            base = ref
            break
    if base is None:
        pytest.skip("no main ref available to compare against (shallow checkout)")
    merge_base = subprocess.run(["git", "merge-base", "HEAD", base], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    before = subprocess.run(["git", "show", f"{merge_base}:.github/workflows/ci.yml"], cwd=REPO, capture_output=True, text=True, check=True).stdout
    after = CI.read_text()
    for name in ("front", "python", "repo-checks"):
        assert job_block(before, name).rstrip() == job_block(after, name).rstrip(), f"job {name} changed"
    assert before.split("jobs:")[1].count("\n  ") <= after.split("jobs:")[1].count("\n  ")
