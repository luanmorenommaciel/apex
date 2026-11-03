"""T-20261103-infra-verify-ddl-full — verify-ddl compares whole objects, MVs included.

Offline: the manifest names every CREATE in infra/sql and every file it points at exists;
--list-tables prints the manifest's objects without a server. Live (APEX_INFRA_LIVE=1):
the script passes on a fresh store and reports every object, fails naming apex.findings
and TTL after a TTL change, fails naming apex.mv_spark_events after a query change, and
leaves no apex_verify_ database behind either way.
"""
from __future__ import annotations

import os
import re
import subprocess

from _live import REPO, SQL_DIR, DisposableClickHouse, live_only, normalize_sql, sql_files

INFRA = REPO / "infra"
SCRIPT = INFRA / "scripts" / "verify_ddl.py"
MANIFEST = INFRA / "scripts" / "ddl_manifest.txt"


def manifest_rows() -> list[list[str]]:
    return [ln.split() for ln in MANIFEST.read_text().splitlines() if ln.strip() and not ln.startswith("#")]


# -- offline ---------------------------------------------------------------------


def test_manifest_covers_every_object():
    rows = manifest_rows()
    objects = {r[0] for r in rows}
    declared = set()
    for path in sql_files():
        text = normalize_sql(path.read_text())
        declared.update("apex." + n for n in re.findall(r"CREATE (?:TABLE|MATERIALIZED VIEW) (?:IF NOT EXISTS )?apex\.(\w+)", text))
    assert objects == declared, sorted(objects ^ declared)
    for obj, kind, lane, infra in rows:
        assert kind in ("table", "mv"), obj
        assert (REPO / lane).exists(), lane
        assert (REPO / infra).exists() and infra.startswith("infra/sql/"), infra
        assert obj.split(".")[1] in normalize_sql((REPO / lane).read_text()), f"{lane} does not create {obj}"


def test_list_tables_is_offline():
    env = dict(os.environ, INFRA_CLICKHOUSE_CONTAINER="apex-nonexistent", INFRA_ENV_FILE="/nonexistent", INFRA_SECRETS_DIR="/nonexistent", PATH="/usr/bin:/bin")
    proc = subprocess.run(["python3", str(SCRIPT), "--list-tables"], env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.split() == [r[0].split(".")[1] for r in manifest_rows()]


# -- live ------------------------------------------------------------------------


def run_verify(ch: DisposableClickHouse) -> subprocess.CompletedProcess:
    env = dict(os.environ, INFRA_CLICKHOUSE_CONTAINER=ch.name, CLICKHOUSE_USER=ch.user, CLICKHOUSE_PASSWORD=ch.password, INFRA_ENV_FILE="/nonexistent")
    return subprocess.run(["python3", str(SCRIPT)], env=env, capture_output=True, text=True, cwd=INFRA)


def scratch_count(ch: DisposableClickHouse) -> str:
    return ch.query("SELECT count() FROM system.databases WHERE name LIKE 'apex_verify_%'").strip()


@live_only
def test_verify_ddl_passes_fresh():
    with DisposableClickHouse(sql_files()) as ch:
        proc = run_verify(ch)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        for obj in ("apex.mv_spark_events", "apex.spark_jobs_1m_mv", "apex.otel_traces", "apex.otel_logs", "apex.fix_verifications"):
            assert f"✅ {obj}" in proc.stdout, obj
        assert "16 objects match" in proc.stdout
        assert scratch_count(ch) == "0"


@live_only
def test_verify_ddl_catches_ttl_drift():
    with DisposableClickHouse(sql_files()) as ch:
        ch.query("ALTER TABLE apex.findings MODIFY TTL toDateTime(ts) + INTERVAL 30 DAY", fmt=None)
        proc = run_verify(ch)
        assert proc.returncode == 1
        assert "❌ apex.findings" in proc.stdout and "TTL drift" in proc.stdout, proc.stdout
        assert "✅ apex.spark_events" in proc.stdout
        assert scratch_count(ch) == "0"


@live_only
def test_verify_ddl_catches_mv_drift():
    body = normalize_sql((REPO / "collect" / "ddl" / "30_mv_spark_events.sql").read_text()).split(" AS SELECT ", 1)[1]
    drifted = re.sub(r"toInt64OrZero\(SpanAttributes\['executor_run_time_ms'\]\) AS executor_run_time_ms, ", "", body)
    assert drifted != body
    with DisposableClickHouse(sql_files()) as ch:
        ch.query(f"ALTER TABLE apex.mv_spark_events MODIFY QUERY SELECT {drifted}", fmt=None)
        proc = run_verify(ch)
        assert proc.returncode == 1
        assert "❌ apex.mv_spark_events" in proc.stdout and "QUERY drift" in proc.stdout, proc.stdout
        assert scratch_count(ch) == "0"


@live_only
def test_verify_ddl_drops_scratch():
    with DisposableClickHouse(sql_files()) as ch:
        ch.query("DROP TABLE apex.job_conf", fmt=None)   # a missing object must not leave scratch behind
        proc = run_verify(ch)
        assert proc.returncode == 1 and "❌ apex.job_conf" in proc.stdout and "missing on the live server" in proc.stdout
        assert scratch_count(ch) == "0"
