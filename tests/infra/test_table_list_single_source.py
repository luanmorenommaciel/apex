"""T-20261103-infra-table-list-single-source — one manifest feeds every table list.

Offline: verify.sh, run.sh and apex.ps1 carry no literal IN-list of table names and each
reads infra/scripts/ddl_manifest.txt; apex.ps1 keeps balanced braces (pwsh is not on this
host; CI parses it). Live (APEX_INFRA_LIVE=1): verify.sh's check_schema counts N of N on a
fresh disposable store and fails after a table is dropped.
"""
from __future__ import annotations

import os
import re
import subprocess

from _live import REPO, DisposableClickHouse, live_only, sql_files

INFRA = REPO / "infra"
SCRIPTS = {
    "verify.sh": INFRA / "scripts" / "verify.sh",
    "run.sh": REPO / "tests" / "e2e" / "run.sh",
    "apex.ps1": REPO / "scripts" / "apex.ps1",
}
MANIFEST = INFRA / "scripts" / "ddl_manifest.txt"
LITERAL_LIST = re.compile(r"IN \(\s*'(spark_events|findings|plan_transitions)'", re.I)
LITERAL_LOOP = re.compile(r"^for t in spark_events", re.M)


def manifest_objects() -> list[str]:
    return [ln.split()[0].split(".", 1)[1] for ln in MANIFEST.read_text().splitlines() if ln.strip() and not ln.startswith("#")]


def test_no_literal_table_lists():
    for name, path in SCRIPTS.items():
        text = path.read_text()
        assert not LITERAL_LIST.search(text), f"{name} still carries a literal table list"
        assert not LITERAL_LOOP.search(text), f"{name} still loops over a literal table list"
        assert not re.search(r"/\s*[37]\b.*schema|schema=3/3", text), f"{name} hardcodes an expected count"


def test_scripts_reference_manifest():
    for name, path in SCRIPTS.items():
        assert "ddl_manifest.txt" in path.read_text(), name
    ps1 = SCRIPTS["apex.ps1"].read_text()
    assert ps1.count("{") == ps1.count("}"), "apex.ps1 braces are unbalanced"
    assert "/run/secrets/clickhouse_password" in ps1, "apex.ps1 must read the password file, not a container env var"
    assert "Get-InfraDdlObjects" in ps1 and "preflight.sh" in ps1


# -- live ------------------------------------------------------------------------


def check_schema(ch: DisposableClickHouse) -> subprocess.CompletedProcess:
    env = dict(os.environ, INFRA_ENV_FILE="/nonexistent", CLICKHOUSE_HTTP_HOST_PORT=str(ch.port),
               CLICKHOUSE_USER=ch.user, CLICKHOUSE_PASSWORD=ch.password)
    return subprocess.run(["bash", "-c", "source ./verify.sh; resolve_creds; check_schema"],
                          cwd=INFRA / "scripts", env=env, capture_output=True, text=True)


@live_only
def test_verify_step2_counts_manifest():
    n = len(manifest_objects())
    assert n >= 16
    with DisposableClickHouse(sql_files()) as ch:
        proc = check_schema(ch)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert f"{n}/{n}" in proc.stdout
        ch.query("DROP TABLE apex.mv_job_conf", fmt=None)
        proc = check_schema(ch)
        assert proc.returncode == 1, proc.stdout
        assert f"{n - 1}/{n}" in proc.stdout and "mv_job_conf" in proc.stdout, proc.stdout
