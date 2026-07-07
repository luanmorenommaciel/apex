from typing import Any, Protocol

from apex_diagnostics.config import ClickHouseSettings, load_clickhouse_settings


class CHClient(Protocol):
    """Read/write access used by detectors and the report store.

    Production wraps clickhouse-connect; tests substitute
    tests/fakes/clickhouse.py, so detector code never needs a running stack.
    """

    def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...

    def insert(self, table: str, rows: list[dict[str, Any]]) -> None: ...


class ClickHouseConnectClient:
    def __init__(self, settings: ClickHouseSettings | None = None):
        import clickhouse_connect

        resolved = settings or load_clickhouse_settings()
        self._client = clickhouse_connect.get_client(
            host=resolved.host,
            port=resolved.port,
            database=resolved.database,
            username=resolved.user,
            password=resolved.password,
        )

    def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        result = self._client.query(sql, parameters=params or {})
        columns = result.column_names
        return [dict(zip(columns, row)) for row in result.result_rows]

    def insert(self, table: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        columns = list(rows[0].keys())
        data = [[row[column] for column in columns] for row in rows]
        self._client.insert(table, data, column_names=columns)
