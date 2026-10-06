"""The published schema must describe the credential the middleware demands."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apex_api.app import BEARER_SCHEME, create_app
from apex_api.auth import PUBLIC_PATHS
from apex_api.config import Settings
from apex_mcp.ch import ReadStore
from tests.conftest import FakeClient

SETTINGS = Settings(tokens=frozenset({"test-token-6c1f9a"}))


def schema() -> dict:
    return create_app(store=ReadStore(FakeClient()), settings=SETTINGS).openapi()


def test_schema_declares_a_bearer_scheme():
    scheme = schema()["components"]["securitySchemes"][BEARER_SCHEME]
    assert scheme["type"] == "http"
    assert scheme["scheme"] == "bearer"
    # It must not invite anyone to put a database credential here.
    assert "database" in scheme["description"].lower()


def test_every_v1_operation_but_health_requires_it():
    paths = schema()["paths"]
    secured, public = [], []
    for path, operations in paths.items():
        if not path.startswith("/v1"):
            continue
        for method, operation in operations.items():
            (public if path in PUBLIC_PATHS else secured).append(
                (f"{method.upper()} {path}", operation.get("security"))
            )

    assert secured, "no /v1 operations found"
    for label, security in secured:
        assert security == [{BEARER_SCHEME: []}], f"{label} does not document its token"

    assert public, "health should be in the schema"
    for label, security in public:
        # A liveness probe that needs a secret is not a liveness probe, and the
        # schema should not tell an orchestrator otherwise.
        assert not security, f"{label} should not require a token"


def test_docs_are_reachable_without_a_token():
    """A schema is a description; it carries no row from the store."""
    client = TestClient(create_app(store=ReadStore(FakeClient()), settings=SETTINGS))
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 200, path
    # And the gated surface is still gated.
    assert client.get("/v1/runs").status_code == 401
