"""Small ClickHouse HTTP client for Commander local validation."""

import base64
import json
from urllib import parse, request


class ClickHouseQueryResult:
    def __init__(self, result_rows):
        self.result_rows = result_rows


class ClickHouseHttpClient:
    def __init__(self, base_url, *, user=None, password=None, timeout=10, opener=None):
        self.base_url = base_url.rstrip("/")
        self.user = user
        self.password = password
        self.timeout = timeout
        self.opener = opener or request.urlopen

    def command(self, sql):
        self._request(sql)

    def insert(self, table, rows, column_names):
        sql = f"INSERT INTO {table} ({', '.join(column_names)}) FORMAT JSONEachRow"
        lines = [
            json.dumps(dict(zip(column_names, row)), sort_keys=True) for row in rows
        ]
        body = ("\n".join(lines) + "\n").encode("utf-8")
        self._request(sql, body=body)

    def query(self, sql, parameters=None):
        query_sql = _ensure_json_each_row(sql)
        response = self._request(query_sql, parameters=parameters or {})
        rows = []
        for line in response.decode("utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            rows.append(list(item.values()))
        return ClickHouseQueryResult(rows)

    def _request(self, sql, *, body=None, parameters=None):
        query = {"query": sql}
        for key, value in (parameters or {}).items():
            query[f"param_{key}"] = value
        url = f"{self.base_url}/?{parse.urlencode(query)}"
        req = request.Request(url, data=body, method="POST")
        if self.user is not None:
            token = base64.b64encode(
                f"{self.user}:{self.password or ''}".encode("utf-8")
            ).decode("ascii")
            req.add_header("Authorization", f"Basic {token}")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        with self.opener(req, timeout=self.timeout) as response:
            return response.read()


def _ensure_json_each_row(sql):
    normalized = sql.strip()
    if normalized.upper().endswith("FORMAT JSONEACHROW"):
        return normalized
    return f"{normalized} FORMAT JSONEachRow"
