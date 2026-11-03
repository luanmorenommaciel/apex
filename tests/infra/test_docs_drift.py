"""T-20261103-infra-docs-drift — the infra documents match the files.

infra/README.md describes every sql/ file; CONTRACT.md's spark_events ORDER BY equals the
DDL's; HYPERDX_SETUP.md and the lane brief carry no stale host or port; the comments in
001 and the compose header name the current files; CHANGELOG.md and CONTRACT.md's changelog
record the new operator requirements.
"""
from __future__ import annotations

import re

from _live import REPO, SQL_DIR, sql_files

INFRA = REPO / "infra"
README = INFRA / "README.md"
SETUP = INFRA / "HYPERDX_SETUP.md"
CONTRACT = REPO / "CONTRACT.md"
CHANGELOG = REPO / "CHANGELOG.md"
BRIEF = REPO / "docs" / "lanes" / "INFRA.md"


def test_readme_lists_every_sql_file():
    text = README.read_text()
    section = text.split("### `sql/`")[1].split("> **First-boot")[0]
    for path in sql_files():
        number = path.name[:3]
        in_range = "034" <= number <= "039" and "`034`–`039`" in section
        assert in_range or f"`{number}`" in section, f"sql/{path.name} is not described"
    assert "sql/001..032" not in text
    assert f"sql/001..{sql_files()[-1].name[:3]}" in text


def test_contract_order_by_matches_ddl():
    ddl = (REPO / "contract" / "spark_events.ddl.sql").read_text()
    order = re.search(r"^ORDER BY (\(.*?\))", ddl, re.M).group(1)
    assert f"`ORDER BY {order}`" in CONTRACT.read_text()


def test_no_stale_hosts_or_ports():
    assert "http://clickhouse:8123" not in SETUP.read_text()
    assert "apex-infra-clickhouse:8123" in SETUP.read_text()
    assert "sql/005" not in SETUP.read_text() and "sql/050" in SETUP.read_text()
    brief = BRIEF.read_text()
    assert ":8080" not in brief.replace("8090:8080", "")
    assert "hdx-oss-v2`." not in brief
    assert "050" in (SQL_DIR / "001_database.sql").read_text() and "ddl_manifest.txt" in (SQL_DIR / "001_database.sql").read_text()
    header = (INFRA / "docker-compose.yml").read_text().split("\nname:")[0]
    assert "ddl-migrate" in header and "queue-init" in header and "Four services:" not in header
    for path in list(SQL_DIR.glob("*.sql")) + [INFRA / "scripts" / "verify.sh", REPO / "tests" / "e2e" / "run.sh", INFRA / "dashboards" / "skew_dashboard.json"]:
        assert "sql/005" not in path.read_text(), path.name


def test_changelog_flags_operator_requirements():
    section = CHANGELOG.read_text().split("## [Unreleased]")[1].split("### Changed\n")[0]
    for needle in ("make -C infra up", "preflight.sh", "hyperdx_bootstrap.sh", "secrets/", "apex_hdx", "BIND_HOST",
                   "APEX_INFRA_CLICKHOUSE_PASSWORD", "APEX_CLUSTER_SLOTS", "050_skew.sql", "14 days", "365-day",
                   "ddl-migrate", "ddl_manifest.txt", "pinned by digest", "make -C infra backup"):
        assert needle in section, needle
    contract_log = CONTRACT.read_text().split("**Changelog:**")[1].split("- **v0.6**")[0]
    assert "non_replicated_deduplication_window = 100" in contract_log and "plan_transitions" in contract_log
    assert "14 days" in contract_log
