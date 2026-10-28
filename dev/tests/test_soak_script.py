from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

DEV = Path(__file__).resolve().parents[1]
SCRIPT = DEV / "scripts" / "soak_driver_listener.sh"


def _source() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_soak_script_parses() -> None:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash not available")
    result = subprocess.run([bash, "-n", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_sampler_discovers_containers_from_compose_instead_of_literal_names() -> None:
    source = _source()
    assert "apex-dev-spark-master-1" not in source
    assert "apex-dev-spark-worker-1" not in source
    assert re.search(r'"\$\{COMPOSE\[@\]\}" ps -q spark-master spark-worker', source)
    assert '"${SAMPLE_CONTAINERS[@]}"' in source


def test_discovery_runs_after_the_stack_is_up_and_before_sampling() -> None:
    source = _source()
    up = source.index('"${COMPOSE[@]}" up -d --wait --no-recreate')
    discover = source.index("\ndiscover_containers\n")
    first_sample = source.index('sampler "$submit_pid" &')
    assert up < discover < first_sample


def test_discovery_fails_fast_when_no_spark_container_is_found() -> None:
    source = _source()
    assert "compose ps found no spark-master/spark-worker containers" in source


def test_collector_is_still_sampled_by_its_stable_alias() -> None:
    # The collector is owned by collect/infra and reached by its stable
    # container name on apex-collect-net; it is not part of the dev project.
    assert "SAMPLE_CONTAINERS+=(apex-otel-collector)" in _source()


def test_off_arm_still_overrides_the_mounted_plugin_conf() -> None:
    assert "--conf spark.plugins=" in _source()
