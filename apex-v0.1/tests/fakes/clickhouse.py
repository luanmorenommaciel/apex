from typing import Any


class FakeCHClient:
    """In-memory CHClient double keyed by exact SQL text.

    Mirrors tests/fakes/spark.py: detector and store tests validate query
    dispatch and row handling without a running ClickHouse.
    """

    def __init__(self, rows_by_sql: dict[str, list[dict[str, Any]]] | None = None):
        self.rows_by_sql = rows_by_sql or {}
        self.queries: list[tuple[str, dict[str, Any]]] = []
        self.inserted: list[tuple[str, list[dict[str, Any]]]] = []

    def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self.queries.append((sql, params or {}))
        if sql not in self.rows_by_sql:
            raise AssertionError(f"Unexpected SQL in FakeCHClient:\n{sql}")
        return self.rows_by_sql[sql]

    def insert(self, table: str, rows: list[dict[str, Any]]) -> None:
        self.inserted.append((table, rows))
