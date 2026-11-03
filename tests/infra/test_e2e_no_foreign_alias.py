"""T-20261103-infra-e2e-no-foreign-alias — the e2e runner never aliases a foreign name.

infra/docker-compose.yml rule 3 forbids `docker network connect --alias <other lane's
name>`; tests/e2e/run.sh used to do exactly that. Now it joins under the container
name only and resolves one OTLP host for both the probe and the spark-submit line.
"""
from __future__ import annotations

import re

from _live import REPO

RUN_SH = REPO / "tests" / "e2e" / "run.sh"
DEV_README = REPO / "dev" / "README.md"


def test_e2e_runner_never_aliases():
    for line in RUN_SH.read_text().splitlines():
        if "docker network connect" in line and not line.lstrip().startswith("#"):
            assert "--alias" not in line, line


def test_e2e_runner_resolves_host_once():
    text = RUN_SH.read_text()
    assert re.search(r"^\s*OTLP_HOST=apex-otel-collector$", text, re.M)
    assert re.search(r"^\s*OTLP_HOST=apex-infra-otel-collector$", text, re.M)
    assert 'OTLP_ENDPOINT="http://${OTLP_HOST}:4318"' in text
    assert 'spark.apex.otlp.endpoint="${OTLP_ENDPOINT}"' in text
    assert "${OTLP_ENDPOINT}/v1/traces" in text
    live = [l for l in text.splitlines() if not l.lstrip().startswith("#")]
    assert not any("http://apex-otel-collector:4318" in l for l in live), "a literal collector host survived"


def test_dev_readme_no_longer_calls_the_fix_pending():
    text = DEV_README.read_text()
    assert "a file-level fix belongs to infra/" not in text
    assert "no longer sets it" in text
