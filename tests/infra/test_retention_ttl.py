"""T-20261103-infra-retention-ttl — every table has a deliberate retention.

Offline: each MergeTree-family CREATE in infra/sql declares a TTL; findings and
fix_verifications at 365 DAY, the three raw landing tables at 14 DAY. Live
(APEX_INFRA_LIVE=1): a fresh volume shows those TTLs, and a volume whose TTLs are
rolled back to the pre-leaf state converges after 042.
"""
from __future__ import annotations

import re

from _live import SQL_DIR, DisposableClickHouse, live_only, normalize_sql, sql_files

EXPECTED_DAYS = {
    "findings": 365, "fix_verifications": 365,
    "otel_traces": 14, "otel_traces_trace_id_ts": 14, "otel_logs": 14,
    "spark_events": 90, "plan_transitions": 90, "job_conf": 90, "spark_jobs_1m": 90,
    "plan_memory": 365, "run_outcomes": 365,
}
# the live state every pre-leaf volume has: no TTL on the two, 90 days on the raw three
PRE_LEAF = [
    "ALTER TABLE apex.findings REMOVE TTL",
    "ALTER TABLE apex.fix_verifications REMOVE TTL",
    "ALTER TABLE apex.otel_traces MODIFY TTL toDateTime(Timestamp) + INTERVAL 90 DAY",
    "ALTER TABLE apex.otel_traces_trace_id_ts MODIFY TTL Start + INTERVAL 90 DAY",
    "ALTER TABLE apex.otel_logs MODIFY TTL toDateTime(Timestamp) + INTERVAL 90 DAY",
]


def creates() -> dict[str, str]:
    """table -> normalised CREATE TABLE statement across infra/sql."""
    out = {}
    for path in sql_files():
        text = normalize_sql(path.read_text())
        for m in re.finditer(r"CREATE TABLE (?:IF NOT EXISTS )?apex\.(\w+) \(.*?ENGINE = \w+.*?(?=;| CREATE |$)", text):
            out[m.group(1)] = m.group(0)
    return out


# -- offline ---------------------------------------------------------------------


def test_every_table_has_ttl():
    stmts = creates()
    assert set(stmts) == set(EXPECTED_DAYS), sorted(set(stmts) ^ set(EXPECTED_DAYS))
    for table, days in EXPECTED_DAYS.items():
        m = re.search(r"TTL .*? \+ INTERVAL (\d+) DAY", stmts[table])
        assert m, f"{table} declares no TTL"
        assert int(m.group(1)) == days, (table, m.group(1))


def test_042_covers_exactly_the_changed_tables():
    text = normalize_sql((SQL_DIR / "042_retention_additive.sql").read_text())
    changed = dict(re.findall(r"ALTER TABLE apex\.(\w+) MODIFY TTL .*? \+ INTERVAL (\d+) DAY", text))
    assert changed == {"findings": "365", "fix_verifications": "365", "otel_traces": "14", "otel_traces_trace_id_ts": "14", "otel_logs": "14"}


# -- live ------------------------------------------------------------------------

LIVE_TABLES = ("findings", "fix_verifications", "otel_traces", "otel_traces_trace_id_ts", "otel_logs")


def live_days(ch, table) -> int:
    m = re.search(r"TTL .*?toIntervalDay\((\d+)\)", ch.create_table_query(table))
    assert m, (table, ch.create_table_query(table))
    return int(m.group(1))


@live_only
def test_retention_fresh_volume():
    with DisposableClickHouse(sql_files()) as ch:
        for table in LIVE_TABLES:
            assert live_days(ch, table) == EXPECTED_DAYS[table], table


@live_only
def test_retention_upgrade_converges():
    with DisposableClickHouse(sql_files()) as ch:
        expected = {t: normalize_sql(ch.create_table_query(t)) for t in LIVE_TABLES}
        for stmt in PRE_LEAF:                      # roll the live TTLs back to the pre-leaf state
            ch.query(stmt, fmt=None)
        assert "TTL" not in ch.create_table_query("findings")
        assert live_days(ch, "otel_traces") == 90
        ch.apply(sql_files(lambda n: n == 42))
        for table, want in expected.items():
            assert normalize_sql(ch.create_table_query(table)) == want, table
