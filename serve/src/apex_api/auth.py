"""Bearer-token admission, applied before routing.

This is MIDDLEWARE rather than a route dependency on purpose. A dependency
runs after Starlette has resolved the path, so an unauthenticated request to a
path that does not exist answers 404 while the same request to a real path
answers 401 — which tells an anonymous caller exactly which routes exist.
Admission ahead of routing gives one answer to both.
"""

from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import Settings

# A liveness check that needs a secret is not a liveness check — an orchestrator
# probes this before it has any reason to hold a token.
PUBLIC_PATHS = frozenset({"/v1/health"})

API_PREFIX = "/v1"

# One body for every refusal. Saying "unknown token" on a real path and "not
# found" on a fake one is the route oracle this middleware exists to close.
_REFUSAL = {
    "error": "unauthorized",
    "detail": (
        "A valid bearer token is required. Send Authorization: Bearer <token>."
    ),
}


def _presented_token(request: Request) -> str:
    """The token from an Authorization header, or "" when there is none.

    The scheme match is case-insensitive because RFC 7235 says it is; the
    token itself is compared exactly.
    """
    header = request.headers.get("authorization", "")
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer":
        return ""
    return value.strip()


def is_authorized(presented: str, settings: Settings) -> bool:
    """Constant-time membership test.

    ``compare_digest`` against every configured token rather than a set lookup:
    a hash-table hit short-circuits on the first differing byte and leaks the
    shared prefix through timing. The token count is small and fixed at
    startup, so the full scan costs nothing that matters.
    """
    if not presented:
        return False
    allowed = False
    for token in settings.tokens:
        if secrets.compare_digest(presented, token):
            allowed = True
    return allowed


def build_middleware(
    settings: Settings,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    """The admission callable, closed over the token set."""

    async def enforce_token(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        # Only the API surface is gated. Anything outside it (docs, openapi)
        # is served or 404'd by the app as usual.
        if not path.startswith(API_PREFIX) or path in PUBLIC_PATHS:
            return await call_next(request)
        if is_authorized(_presented_token(request), settings):
            return await call_next(request)
        # Returned BEFORE call_next, so no handler runs and the store is never
        # queried on an unauthenticated request.
        return JSONResponse(
            _REFUSAL,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return enforce_token
