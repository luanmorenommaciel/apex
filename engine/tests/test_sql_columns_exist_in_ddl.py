"""Every column the engine's SQL reads must be declared by the contract DDL.

CI has no ClickHouse, so the engine's queries are never executed there — the
integration tests that would run them skip. A column that exists only in the
query and in nobody's DDL therefore reaches a reviewer green, and fails for the
first person who runs it against a real store, with a raw

    Code: 47. DB::Exception: Unknown expression or function identifier '<col>'

that points inside the SQL rather than at the schema. This closes that gap
statically: it is text analysis, no database, so it runs wherever pytest runs.

Scope, stated plainly: this proves the SQL only names columns the repository
declares somewhere. It does **not** prove any particular deployment has them —
an existing ClickHouse volume only receives migrations on first init, so a
schema can satisfy this test and still be missing columns at runtime. That is
a deployment question, not a repository one.
"""

from __future__ import annotations

import re
from pathlib import Path

from apex_engine.clickhouse import STAGE_AGGREGATES_SQL, STAGE_EVENTS_SQL

ROOT = Path(__file__).resolve().parents[2]

# Every place spark_events columns are declared: the frozen contract, the infra
# base DDL, and the additive migrations that widen it.
DDL_SOURCES = (
    ROOT / "contract" / "spark_events.ddl.sql",
    ROOT / "infra" / "sql" / "002_spark_events.sql",
    *sorted((ROOT / "infra" / "sql").glob("0[23][0-9]_*additive*.sql")),
)

# Identifiers that appear in the SQL but are not spark_events columns.
NOT_COLUMNS = {
    "argMax", "any", "max", "sum", "count", "if", "toInt64OrZero", "nullIf",
    "toStartOfMinute", "round", "attributes", "apex", "spark_events",
    "job_id", "SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "AS", "String",
}


def _declared_columns() -> set[str]:
    declared: set[str] = set()
    for path in DDL_SOURCES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # Base DDL: "  column_name  Type," at the start of a line.
        declared |= set(re.findall(r"^\s{2,}([a-z][a-z0-9_]*)\s+\w", text, re.MULTILINE))
        # Migrations: "ADD COLUMN IF NOT EXISTS column_name Type".
        declared |= set(re.findall(r"ADD COLUMN(?:\s+IF NOT EXISTS)?\s+([a-z][a-z0-9_]*)", text))
    return declared


def _strip_comments(sql: str) -> str:
    """`-- ...` prose is not part of the query. Leaving it in makes every English
    word in an explanatory comment look like a column name."""
    return "\n".join(line.split("--", 1)[0] for line in sql.splitlines())


def _columns_read_by(sql: str) -> set[str]:
    """Bare identifiers the query reads, minus SQL keywords and functions."""
    cleaned = _strip_comments(sql)
    # Quoted map keys and string literals are values, not column identifiers.
    cleaned = re.sub(r"'(?:''|[^'])*'", "''", cleaned)
    # Remove only the output declaration, not every occurrence of the alias.
    # In particular, ``argMax(fake, ts) AS fake`` still reads ``fake`` and must
    # fail when no DDL declares it. Subtracting aliases from a set of tokens
    # erased both occurrences and let that invalid query pass.
    inputs_only = re.sub(
        r"\bAS\s+[a-z][a-z0-9_]*",
        "AS",
        cleaned,
        flags=re.IGNORECASE,
    )
    read = set(re.findall(r"\b([a-z][a-z0-9_]*)\b", inputs_only))
    read -= {token.lower() for token in NOT_COLUMNS}
    read -= NOT_COLUMNS
    return read


def test_ddl_sources_are_present():
    """A moved or renamed DDL file must fail loudly, not silently weaken the
    check below into asserting against an empty set."""
    missing = [p.relative_to(ROOT) for p in DDL_SOURCES[:2] if not p.exists()]
    assert not missing, f"DDL source(s) not found: {missing}"
    assert len(_declared_columns()) > 20, "column extraction produced implausibly few columns"


def test_stage_aggregates_sql_reads_only_declared_columns():
    undeclared = _columns_read_by(STAGE_AGGREGATES_SQL) - _declared_columns()
    assert not undeclared, (
        f"STAGE_AGGREGATES_SQL reads column(s) no DDL declares: {sorted(undeclared)}. "
        "Add the column to contract/ + infra/sql/, or stop reading it."
    )


def test_stage_events_sql_reads_only_declared_columns():
    undeclared = _columns_read_by(STAGE_EVENTS_SQL) - _declared_columns()
    assert not undeclared, (
        f"STAGE_EVENTS_SQL reads column(s) no DDL declares: {sorted(undeclared)}. "
        "Add the column to contract/ + infra/sql/, or stop reading it."
    )


def test_same_name_alias_cannot_hide_an_undeclared_input_column():
    sql = "SELECT argMax(fake, ts) AS fake FROM apex.spark_events"

    undeclared = _columns_read_by(sql) - _declared_columns()

    assert undeclared == {"fake"}


def test_short_undeclared_identifier_cannot_escape_column_validation():
    sql = "SELECT id FROM apex.spark_events"

    undeclared = _columns_read_by(sql) - _declared_columns()

    assert undeclared == {"id"}
