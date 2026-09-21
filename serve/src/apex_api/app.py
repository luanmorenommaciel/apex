"""The Apex API application.

One HTTP surface in front of the store, so that the console, the MCP server
and any other consumer read the same contract and none of them needs a
database user.

The boundary rule here is the same one apex_mcp holds at the tool layer: a
driver exception embeds the host, user and password of the connection URL, so
NOTHING raw reaches a response body. ch.ReadStore already sanitizes on the way
out (``_query`` wraps every failure in ApexStoreError); this module's job is
to not undo that, and to give the same treatment to anything the store did not
raise.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apex_mcp import ch
from apex_mcp.ch import ApexStoreError, ReadStore

from .auth import PUBLIC_PATHS, build_middleware
from .config import Settings, load_settings
from .routes import discover_routers

log = logging.getLogger("apex_api")

API_PREFIX = "/v1"

# A store failure is an upstream failure, not a client error: the request was
# well formed and the API is up. 502 says that; 500 would blame this service.
STORE_ERROR_STATUS = 502

# Named once so the scheme in the schema and the requirement on each operation
# cannot drift apart.
BEARER_SCHEME = "apexToken"


def _document_auth(app: FastAPI) -> None:
    """Declare in the schema that /v1 needs a bearer token.

    DECLARED, not enforced. auth.py stays the enforcement point: a
    dependency-based scheme would move admission behind routing, and an
    unauthenticated caller would then learn which routes exist from the
    difference between 401 and 404. This only makes the published schema tell
    the truth about what the middleware already does — otherwise a consumer
    reads the docs, calls a route, gets 401, and has nothing to explain it.
    """
    original = app.openapi

    def openapi() -> dict[str, Any]:
        schema = original()
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            BEARER_SCHEME
        ] = {
            "type": "http",
            "scheme": "bearer",
            "description": (
                "An Apex API token. Configured server-side in APEX_API_TOKENS; "
                "never a database credential."
            ),
        }
        for path, operations in schema.get("paths", {}).items():
            if not path.startswith(API_PREFIX) or path in PUBLIC_PATHS:
                # A liveness probe that needs a secret is not a liveness probe.
                continue
            for operation in operations.values():
                operation["security"] = [{BEARER_SCHEME: []}]
        return schema

    app.openapi = openapi  # type: ignore[method-assign]


class _LazyClient:
    """Defers the ClickHouse connection to the first query.

    Mirrors apex_mcp.server.LazyClient and exists for the same reason: the
    service must bind its port and answer /v1/health even when the store is
    down, otherwise the only diagnostic anyone gets is a container that will
    not start.
    """

    def query(self, query: str, parameters: Any = None):  # noqa: ANN001, ANN201
        return ch.get_client().query(query, parameters=parameters)


def get_store(request: Request) -> ReadStore:
    """The store for this request. Injected at build time; never global."""
    return request.app.state.store


def create_app(
    *, store: ReadStore | None = None, settings: Settings | None = None
) -> FastAPI:
    """Build the application.

    ``store`` and ``settings`` are injectable so a test can build the real app
    against a fake client, exactly as serve/tests/conftest.py already does for
    the MCP server. Neither is read from a module-level global, so two apps
    with different stores can exist in one process.

    With no ``settings``, configuration is read from the environment and a
    missing token set raises ConfigError — the server refuses to start rather
    than serving open.
    """
    resolved_settings = settings if settings is not None else load_settings()
    app = FastAPI(
        title="Apex API",
        version="0.1.0",
        summary="Read-only access to the Apex store, in front of ClickHouse.",
    )
    app.state.store = store if store is not None else ReadStore(_LazyClient())
    app.state.settings = resolved_settings

    app.middleware("http")(build_middleware(resolved_settings))

    @app.exception_handler(ApexStoreError)
    async def _store_error(_: Request, exc: ApexStoreError) -> JSONResponse:
        """ApexStoreError text is already sanitized by ch._sanitize.

        It names the failure class and the environment variable to check, and
        deliberately carries no connection detail, so it is safe to forward.
        """
        return JSONResponse(
            {"error": "store_error", "detail": str(exc)},
            status_code=STORE_ERROR_STATUS,
        )

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
        """Anything the store did not raise gets a fixed body.

        str(exc) is NOT included: an exception from below the store layer has
        not been through _sanitize, and that is exactly where a DSN would be.
        """
        log.error("unhandled api failure: %s", type(exc).__name__, exc_info=exc)
        return JSONResponse(
            {
                "error": "internal_error",
                "detail": (
                    "The request could not be completed. See the server's "
                    "stderr log for details."
                ),
            },
            status_code=500,
        )

    @app.get(f"{API_PREFIX}/health", tags=["meta"])
    async def health(request: Request) -> dict[str, Any]:
        """Liveness plus what the store reports about itself.

        Answers 200 whenever the PROCESS is healthy. A store that cannot be
        reached is reported in the body as unreachable rather than raised,
        because a probe that fails on a downstream outage cannot distinguish
        "this service is broken" from "ClickHouse is down" — and those call for
        different people.
        """
        try:
            return {"status": "ok", "store": "ok", **get_store(request).store_health()}
        except ApexStoreError as exc:
            return {"status": "ok", "store": "unreachable", "detail": str(exc)}

    for router in discover_routers():
        app.include_router(router, prefix=API_PREFIX)

    # After the routers, so every operation they added is in the schema.
    _document_auth(app)

    return app


def _configure_logging() -> None:
    logging.basicConfig(
        stream=sys.stderr,
        level=os.getenv("APEX_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    """Console-script entry point."""
    import uvicorn

    _configure_logging()
    uvicorn.run(
        create_app(),
        host=os.getenv("APEX_API_HOST", "127.0.0.1"),
        port=int(os.getenv("APEX_API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
