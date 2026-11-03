"""T-20261103-infra-console-ro-scope — apex_ro reads the console's tables and nothing else.

Offline: front/contract/01-readonly-user.sql grants SELECT per named table (never on
apex.*) and the list covers every apex.* table front/src references. Live
(APEX_INFRA_LIVE=1): on a fresh store with the user applied, apex_ro reads
spark_events and is refused otel_traces.
"""
from __future__ import annotations

import re
import subprocess
import urllib.error
import urllib.request

from _live import REPO, DisposableClickHouse, live_only, sql_files

USER_SQL = REPO / "front" / "contract" / "01-readonly-user.sql"
FRONT_SRC = REPO / "front" / "src"


def granted_tables() -> list[str]:
    return re.findall(r"GRANT SELECT ON apex\.(\w+)\s+TO apex_ro", USER_SQL.read_text())


def console_tables() -> set[str]:
    names = set()
    for path in FRONT_SRC.rglob("*.ts*"):
        names.update(re.findall(r"apex\.([a-z_0-9]+)", path.read_text()))
    return names


# -- offline ---------------------------------------------------------------------


def test_console_user_grants_explicit():
    live = "\n".join(l for l in USER_SQL.read_text().splitlines() if not l.lstrip().startswith("--"))
    assert not re.search(r"GRANT SELECT ON apex\.\* ", live), "a wildcard SELECT grant survived"
    assert len(granted_tables()) == len(set(granted_tables())) >= 7
    assert "otel_traces" not in granted_tables()
    assert "REVOKE ALL ON apex.* FROM apex_ro" in live, "re-running must converge from an older apex.* grant"


def test_console_user_covers_queries():
    missing = console_tables() - set(granted_tables())
    assert not missing, sorted(missing)


# -- live ------------------------------------------------------------------------


def as_apex_ro(ch, sql: str) -> tuple[int, str]:
    req = urllib.request.Request(f"http://127.0.0.1:{ch.port}/?user=apex_ro", data=sql.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


@live_only
def test_console_user_cannot_read_raw_traces():
    with DisposableClickHouse(sql_files()) as ch:
        ch.apply([USER_SQL])
        ch.apply([USER_SQL])  # converges on a second run
        status, body = as_apex_ro(ch, "SELECT count() FROM apex.spark_events")
        assert (status, body.strip()) == (200, "0"), body
        for table in ("otel_traces", "otel_logs"):
            status, body = as_apex_ro(ch, f"SELECT count() FROM apex.{table}")
            assert status != 200 and "ACCESS_DENIED" in body, (table, status, body[:200])
        for table in granted_tables():
            status, body = as_apex_ro(ch, f"SELECT count() FROM apex.{table}")
            assert status == 200, (table, body[:200])
