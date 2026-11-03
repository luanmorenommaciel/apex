"""T-20261103-infra-migrate-on-up — every compose up converges the schema.

Rendered compose: a one-shot ddl-migrate service waits for a healthy clickhouse and gates
hyperdx and otel-collector. Live (APEX_INFRA_LIVE=1): apply_ddl.sh in container mode,
run in a container sharing a disposable server's network namespace, converges a volume
initialised from 001–033 onto the fresh-volume schema and is a no-op the second time.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

import pytest

from _live import IMAGE, REPO, SQL_DIR, DisposableClickHouse, live_only, normalize_sql, sql_files

INFRA = REPO / "infra"
RENDER_ENV = dict(os.environ, CLICKHOUSE_PASSWORD="render-only-not-a-real-password", HYPERDX_API_KEY="0" * 64)
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI required")


def rendered_compose() -> dict:
    out = subprocess.run(
        ["docker", "compose", "-f", "docker-compose.yml", "--env-file", ".env.example", "config", "--format", "json"],
        cwd=INFRA, capture_output=True, text=True, check=True, env=RENDER_ENV,
    ).stdout
    return json.loads(out)


@needs_docker
def test_migrate_service_gates_consumers():
    services = rendered_compose()["services"]
    migrate = services["ddl-migrate"]
    assert migrate["depends_on"]["clickhouse"]["condition"] == "service_healthy"
    assert migrate.get("restart", "no") == "no"
    assert migrate["environment"]["APPLY_DDL_MODE"] == "container"
    assert migrate["image"] == services["clickhouse"]["image"], "the client comes from the pinned server image"
    assert any(s["source"] == "clickhouse_password" for s in migrate["secrets"])
    targets = {v["target"] for v in migrate["volumes"]}
    assert {"/sql", "/apply_ddl.sh"} <= targets
    for consumer in ("hyperdx", "otel-collector"):
        assert services[consumer]["depends_on"]["ddl-migrate"]["condition"] == "service_completed_successfully", consumer


def apply_in_container(ch: DisposableClickHouse) -> subprocess.CompletedProcess:
    """Run apply_ddl.sh exactly as ddl-migrate does, inside the disposable's network namespace."""
    return subprocess.run(
        ["docker", "run", "--rm", f"--network=container:{ch.name}",
         "-e", "APPLY_DDL_MODE=container", "-e", "CLICKHOUSE_HOST=127.0.0.1", "-e", f"CLICKHOUSE_USER={ch.user}",
         "-e", f"CLICKHOUSE_PASSWORD={ch.password}", "-e", "INFRA_ENV_FILE=/nonexistent", "-e", "SQL_DIR=/sql",
         "-v", f"{SQL_DIR}:/sql:ro", "-v", f"{INFRA / 'scripts' / 'apply_ddl.sh'}:/apply_ddl.sh:ro",
         "--entrypoint", "/bin/bash", IMAGE, "/apply_ddl.sh"],
        capture_output=True, text=True,
    )


def schema(ch: DisposableClickHouse) -> dict[str, str]:
    names = ch.query("SELECT name FROM system.tables WHERE database = 'apex' ORDER BY name").split()
    return {n: normalize_sql(ch.create_table_query(n)) for n in names}


@live_only
def test_apply_ddl_converges_old_volume():
    with DisposableClickHouse(sql_files()) as fresh:
        expected = schema(fresh)
    with DisposableClickHouse(sql_files(lambda n: n < 30)) as old:   # no memory/verify tables, no additive migrations
        assert set(schema(old)) < set(expected), "fixture is not older than the repo"
        proc = apply_in_container(old)
        assert proc.returncode == 0, proc.stdout[-1500:] + proc.stderr[-1500:]
        assert "fully applied (container mode)" in proc.stdout
        got = schema(old)
        assert set(got) == set(expected), sorted(set(got) ^ set(expected))
        for name, want in expected.items():
            assert got[name] == want, name


@live_only
def test_apply_ddl_second_run_is_noop():
    with DisposableClickHouse(sql_files()) as ch:
        before = schema(ch)
        for _ in range(2):
            proc = apply_in_container(ch)
            assert proc.returncode == 0, proc.stdout[-1500:] + proc.stderr[-1500:]
        assert schema(ch) == before
