"""The API's boundary contract: what it serves, what it refuses, what it never says.

Every test here builds the REAL app against a fake client, the way
tests/conftest.py already builds the real MCP server. Nothing is mocked at the
route layer, because the route layer is what is under test.
"""

from __future__ import annotations

import ast
import importlib
import pathlib
import sys
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import ConfigError, Settings, TOKENS_VAR, load_settings
from apex_mcp.ch import ReadStore
from tests.conftest import FakeClient, FakeResult

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}

# A realistic connection string, carrying the two things that must never be
# echoed: the host and the password.
DSN = "clickhouse://apex:sup3rs3cr3t@db.internal.example:8123/apex"

API_PACKAGE = pathlib.Path(__file__).resolve().parents[1] / "src" / "apex_api"


class HealthClient:
    """Answers the health query with a known row."""

    def __init__(self, row: dict[str, Any] | None = None) -> None:
        self.row = row or {"row_count": 412, "job_count": 7, "latest_ts": "2026-09-20 10:00:00"}
        self.calls: list[str] = []

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        self.calls.append(query)
        return FakeResult([self.row])


class ExplodingClient:
    """Raises with the DSN in the message, the way a real driver does."""

    def __init__(self, exc: Exception | None = None) -> None:
        self.exc = exc or RuntimeError(f"could not connect to {DSN}: auth failed")
        self.calls: list[str] = []

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        self.calls.append(query)
        raise self.exc


def build(client: Any) -> TestClient:
    return TestClient(create_app(store=ReadStore(client), settings=SETTINGS))


# -- what it serves ---------------------------------------------------------


def test_health_reports_store_health():
    client = HealthClient()
    body = build(client).get("/v1/health").json()
    assert body["status"] == "ok"
    assert body["store"] == "ok"
    # The store's own numbers, not a synthesised placeholder.
    assert body["row_count"] == 412
    assert body["job_count"] == 7


def test_app_accepts_an_injected_store():
    """No live ClickHouse, and no global store to leak between apps."""
    first, second = HealthClient({"row_count": 1, "job_count": 1, "latest_ts": None}), HealthClient(
        {"row_count": 2, "job_count": 2, "latest_ts": None}
    )
    app_one = create_app(store=ReadStore(first), settings=SETTINGS)
    app_two = create_app(store=ReadStore(second), settings=SETTINGS)
    assert TestClient(app_one).get("/v1/health").json()["row_count"] == 1
    assert TestClient(app_two).get("/v1/health").json()["row_count"] == 2
    # Each app kept its own store rather than sharing one.
    assert app_one.state.store is not app_two.state.store


# -- what it never says -----------------------------------------------------


def test_dsn_never_appears_in_a_response():
    response = build(ExplodingClient()).get("/v1/health")
    body = response.text
    for secret in (DSN, "sup3rs3cr3t", "db.internal.example"):
        assert secret not in body, f"{secret!r} leaked into the response"
    # And the failure is still reported, rather than swallowed into a success.
    assert response.json()["store"] == "unreachable"


def test_health_answers_when_the_store_is_unreachable():
    """The process is up; ClickHouse is not. Those are different facts."""
    client = ExplodingClient(ConnectionError(f"connection refused to {DSN}"))
    response = build(client).get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["store"] == "unreachable"
    assert "clickhouse_unavailable" in body["detail"]


# -- how routes arrive ------------------------------------------------------


def test_a_router_dropped_into_routes_is_served():
    """Discovery, not an import list: a later task adds a file, not an edit."""
    module_name = "zz_probe_router"
    path = API_PACKAGE / "routes" / f"{module_name}.py"
    path.write_text(
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.get('/probe')\n"
        "def probe():\n"
        "    return {'probe': 'served'}\n"
    )
    importlib.invalidate_caches()
    try:
        response = build(HealthClient()).get("/v1/probe", headers=AUTH)
        assert response.status_code == 200
        assert response.json() == {"probe": "served"}
    finally:
        path.unlink(missing_ok=True)
        sys.modules.pop(f"apex_api.routes.{module_name}", None)
        importlib.invalidate_caches()


# -- who gets in ------------------------------------------------------------


def test_missing_token_is_refused_without_querying():
    client = HealthClient()
    response = TestClient(
        create_app(store=ReadStore(client), settings=SETTINGS)
    ).get("/v1/runs")
    assert response.status_code == 401
    # Refused ahead of routing, so nothing reached the store.
    assert client.calls == []


def test_unknown_token_is_refused():
    response = build(HealthClient()).get(
        "/v1/runs", headers={"Authorization": "Bearer not-the-token"}
    )
    assert response.status_code == 401


def test_configured_token_is_accepted():
    """A good token gets past admission, so routing decides the answer.

    /v1/runs has no handler in this task, so 404 is the proof that the request
    was admitted — an unauthenticated one never gets far enough to 404.
    """
    unauthenticated = build(HealthClient()).get("/v1/runs")
    authenticated = build(HealthClient()).get("/v1/runs", headers=AUTH)
    assert unauthenticated.status_code == 401
    assert authenticated.status_code == 404
    # Same body for a bad token on a real path and on a fake one: no oracle.
    assert unauthenticated.json() == build(HealthClient()).get("/v1/health/nope").json()


def test_startup_refuses_when_no_token_is_configured():
    with pytest.raises(ConfigError) as caught:
        load_settings({})
    assert TOKENS_VAR in str(caught.value)
    # And an app built with no explicit settings inherits that refusal.
    with pytest.raises(ConfigError):
        create_app(settings=load_settings({TOKENS_VAR: "   ,  ,"}))


def test_health_is_reachable_without_a_token():
    assert build(HealthClient()).get("/v1/health").status_code == 200


def test_no_token_literal_in_the_package():
    """No credential may be baked into the source.

    Assignments to credential-ish names are allowed only when the value is an
    environment VARIABLE NAME (all caps), which is what TOKENS_VAR is.
    """
    suspicious = ("token", "secret", "password", "apikey")
    offenders: list[str] = []
    for source in API_PACKAGE.rglob("*.py"):
        tree = ast.parse(source.read_text())
        for node in ast.walk(tree):
            targets = (
                node.targets
                if isinstance(node, ast.Assign)
                else [node.target] if isinstance(node, ast.AnnAssign) else []
            )
            if not isinstance(getattr(node, "value", None), ast.Constant):
                continue
            value = node.value.value
            if not isinstance(value, str):
                continue
            for target in targets:
                name = getattr(target, "id", "")
                if not any(word in name.lower() for word in suspicious):
                    continue
                if value.isupper() or not value:
                    continue  # an env var name, or an empty default
                offenders.append(f"{source.name}: {name} = {value!r}")
    assert offenders == [], f"credential literal in source: {offenders}"
