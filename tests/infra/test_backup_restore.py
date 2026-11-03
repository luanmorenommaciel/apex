"""T-20261103-infra-backup-restore — the single node is recoverable.

Live (APEX_INFRA_LIVE=1): on a disposable server with infra/config.d mounted, backup.sh
snapshots a seeded findings table to the host and restore.sh brings it back into a
scratch database with the same rows; restore refuses to overwrite without --force.
Rendered compose: the backups disk config and volume are mounted. The Makefile wires
both and refuses restore without FILE.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from _live import REPO, DisposableClickHouse, live_only, sql_files

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
def test_backups_disk_mounted():
    clickhouse = rendered_compose()["services"]["clickhouse"]
    mounts = {v["target"]: v for v in clickhouse["volumes"]}
    assert mounts["/etc/clickhouse-server/config.d/backups.xml"]["source"].endswith("infra/config.d/backups.xml")
    assert mounts["/var/lib/clickhouse/backups"]["type"] == "volume"
    text = (INFRA / "config.d" / "backups.xml").read_text()
    assert "<allowed_disk>backups</allowed_disk>" in text and "/var/lib/clickhouse/backups/" in text
    make = (INFRA / "Makefile").read_text()
    assert "backup.sh" in make and "restore.sh" in make
    dry = subprocess.run(["make", "-n", "restore"], cwd=INFRA, capture_output=True, text=True)
    assert "usage: make restore FILE=" in dry.stdout
    assert subprocess.run(["git", "check-ignore", "-q", "infra/backups/x.zip"], cwd=REPO).returncode == 0


def script_env(ch: DisposableClickHouse, backup_dir: Path) -> dict:
    return dict(os.environ, INFRA_ENV_FILE="/nonexistent", INFRA_CLICKHOUSE_CONTAINER=ch.name,
                CLICKHOUSE_USER=ch.user, CLICKHOUSE_PASSWORD=ch.password, BACKUP_DIR=str(backup_dir), SKIP_MONGO="1")


@live_only
def test_backup_restore_roundtrip():
    now_ms = int(time.time() * 1000)
    rows = ", ".join(f"('f{i}', 'job-{now_ms}', {i}, 'SKEW_ON_JOIN', 'critical', 'e', '', 'i', 'fix', 'HIGH', 'seed', fromUnixTimestamp64Milli({now_ms}))" for i in range(5))
    with DisposableClickHouse(sql_files(), config_d=INFRA / "config.d") as ch, tempfile.TemporaryDirectory() as tmp:
        ch.query(f"INSERT INTO apex.findings (finding_id, job_id, stage_id, type, severity, evidence, hot_key, impact, fix, confidence, detected_by, ts) VALUES {rows}", fmt=None)
        assert ch.query("SELECT count() FROM apex.findings").strip() == "5"
        env = script_env(ch, Path(tmp))
        backup = subprocess.run([str(INFRA / "scripts" / "backup.sh")], env=env, capture_output=True, text=True, cwd=INFRA)
        assert backup.returncode == 0, backup.stdout + backup.stderr
        archives = sorted(Path(tmp).glob("*-clickhouse.zip"))
        assert len(archives) == 1 and archives[0].stat().st_size > 0
        refused = subprocess.run([str(INFRA / "scripts" / "restore.sh"), str(archives[0])], env=env, capture_output=True, text=True, cwd=INFRA)
        assert refused.returncode == 1 and "--force" in refused.stdout, refused.stdout
        ch.query("TRUNCATE TABLE apex.findings", fmt=None)
        restored = subprocess.run([str(INFRA / "scripts" / "restore.sh"), str(archives[0]), "--into", "apex_restore_test"], env=env, capture_output=True, text=True, cwd=INFRA)
        assert restored.returncode == 0, restored.stdout + restored.stderr
        assert ch.query("SELECT count() FROM apex_restore_test.findings").strip() == "5"
        assert ch.query("SELECT count() FROM apex.findings").strip() == "0", "restore --into must not touch apex"
        assert ch.query("SELECT count() FROM system.tables WHERE database = 'apex_restore_test'").strip() == ch.query("SELECT count() FROM system.tables WHERE database = 'apex'").strip()
        ch.query("DROP DATABASE apex_restore_test", fmt=None)
