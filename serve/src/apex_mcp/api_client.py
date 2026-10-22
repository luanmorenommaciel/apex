"""The MCP tools, read through the Apex API instead of ClickHouse.

Decision of 2026-09-15: FastAPI sits between ClickHouse and every consumer,
and apex-mcp is one of those consumers. In API mode each MCP tool forwards to
the diagnostic route that serves the same tool (``apex_api.routes.diagnostics.
TOOL_ROUTES``) and validates the JSON it gets back into the tool's own pydantic
return model. The verdict is computed ONCE, by diagnose.py inside the API
process; this module transports it and checks its shape, nothing more.

Why validate rather than pass the JSON through: the return model is the
contract the model reads. ``FixSuggestion.applied`` is ``Literal[False]``, so a
payload claiming otherwise fails validation here instead of reaching a model —
a suggestion that says it was applied cannot be constructed on this side
either.

ERRORS FOLLOW ch._sanitize. A transport exception's text names the URL, the
host and the port; a response body is whatever the far side chose to say. None
of it reaches the model. The real failure goes to STDERR, and the model gets a
short opaque code naming the environment variable to check. The token is never
logged and never echoed.

STDOUT IS THE JSON-RPC CHANNEL. Nothing here may print().
"""

from __future__ import annotations

import logging
import re
from typing import Any, TypeVar
from urllib.parse import quote, urlsplit

import httpx
from pydantic import BaseModel, ValidationError

from .ch import ApexStoreError, _require_job_id
from .models import (
    Diagnosis,
    FixSuggestion,
    FixVerdict,
    KbHits,
    RecallResult,
    RunComparison,
    RunList,
)

log = logging.getLogger("apex_mcp.api")

API_URL_VAR = "APEX_API_URL"
API_TOKEN_VAR = "APEX_API_TOKEN"
API_TIMEOUT_VAR = "APEX_API_TIMEOUT_S"
DEFAULT_TIMEOUT_S = 30.0

# The prefix the API mounts every route under (apex_api.app.API_PREFIX). Not
# imported from apex_api: this package must not depend on the API package,
# which imports THIS one.
API_PREFIX = "/v1"

# Mirrors apex_api.routes.diagnostics.TOOL_ROUTES. A test asserts the two are
# identical, so the client cannot drift from the server's routes silently.
TOOL_PATHS: dict[str, tuple[str, str]] = {
    "analyze_run": ("GET", "/runs/{job_id}/diagnosis"),
    "explain_stage": ("GET", "/runs/{job_id}/stages/{stage_id}/diagnosis"),
    "compare_runs": ("GET", "/runs/{job_id}/comparison"),
    "recall_similar_runs": ("GET", "/runs/{job_id}/recall"),
    "verify_fix": ("GET", "/runs/{job_id}/verification"),
    "suggest_fix": ("POST", "/runs/{job_id}/fix-suggestion"),
    "list_runs": ("GET", "/diagnostics/runs"),
    "search_kb": ("GET", "/diagnostics/search"),
}

# -- model-facing failures ---------------------------------------------------
# Each names the failure class and the variable to check. None carries any part
# of the URL or the token — they are fixed strings for exactly that reason.
UNAVAILABLE = (
    "apex_api_unavailable: the Apex API did not answer. Check APEX_API_URL of "
    "the MCP server and that the API is running."
)
TIMEOUT = (
    "apex_api_timeout: the Apex API did not answer in time. Check that the API "
    "is healthy, or raise APEX_API_TIMEOUT_S of the MCP server."
)
UNAUTHORIZED = (
    "apex_api_unauthorized: the Apex API refused the configured token. Check "
    "APEX_API_TOKEN of the MCP server against the API's APEX_API_TOKENS."
)
NOT_FOUND = (
    "apex_api_not_found: the Apex API has no route for this request. Check that "
    "APEX_API_URL is the API root and that the API version matches this "
    "server. A job_id containing '/' cannot be addressed over HTTP."
)
INVALID_REQUEST = (
    "apex_api_invalid_request: the Apex API rejected the arguments. "
    "noise_floor_pct, when given, must be a finite non-negative fraction."
)
BAD_RESPONSE = (
    "apex_api_bad_response: the Apex API answered with a payload that is not "
    "the contracted shape. See the server's stderr log for details."
)
FAILED = (
    "apex_api_failed: the Apex API could not complete the request. See the "
    "server's stderr log for details."
)

# What an ApexStoreError looks like: a lowercase code, a colon, a sentence.
# The API forwards these from its 502 handler after ch._sanitize produced them.
_STORE_DETAIL_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}: [^\r\n]{1,480}$")

M = TypeVar("M", bound=BaseModel)


def normalize_base_url(url: str) -> str:
    """The API ROOT, without a trailing slash or a trailing ``/v1``.

    Accepting ``.../v1`` as well is a convenience: it is the URL an operator
    copies out of the API's own docs, and doubling the prefix would 404 every
    call with nothing to explain why.
    """
    url = url.strip().rstrip("/")
    if url.endswith(API_PREFIX):
        url = url[: -len(API_PREFIX)]
    return url


def valid_base_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and bool(parts.hostname)


def _segment(value: str) -> str:
    """One path segment, percent-encoded so it can never become two.

    ``safe=""`` encodes "/" and "?". Dots are encoded too: a job_id of ".."
    left literal would be resolved as a dot-segment and address a DIFFERENT
    route. The API decodes the segment back to the same value.
    """
    return quote(value, safe="").replace(".", "%2E")


class ApiClient:
    """A bearer-authenticated HTTP client for the Apex API ``/v1`` surface.

    ``http`` is injectable so a test can drive the real FastAPI app in-process
    (Starlette's TestClient IS an ``httpx.Client``). Without it the client is
    built on first use, so a server with a down API still starts and lists its
    tools — the same reason LazyClient defers ClickHouse.

    Redirects are NOT followed: following one would send the bearer token to
    wherever the redirect points.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = DEFAULT_TIMEOUT_S,
        http: httpx.Client | None = None,
    ) -> None:
        self._base_url = normalize_base_url(base_url)
        self._token = token
        self._timeout = timeout
        self._http = http
        parts = urlsplit(self._base_url)
        # Everything that could identify the endpoint. A forwarded detail that
        # contains any of these is dropped, not trimmed.
        self._secrets = tuple(
            s
            for s in (
                token,
                self._base_url,
                parts.netloc,
                parts.hostname or "",
                str(parts.port) if parts.port else "",
            )
            if s
        )

    def _client(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(
                base_url=self._base_url,
                timeout=self._timeout,
                follow_redirects=False,
            )
        return self._http

    def get_json(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        """One call, returning parsed JSON or raising a model-safe ApexStoreError."""
        query = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            response = self._client().request(
                method,
                f"{API_PREFIX}{path}",
                params=query,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept": "application/json",
                },
            )
        except httpx.TimeoutException as exc:
            self._log_failure("timed out", exc)
            raise ApexStoreError(TIMEOUT) from None
        except httpx.TransportError as exc:
            self._log_failure("unreachable", exc)
            raise ApexStoreError(UNAVAILABLE) from None
        except Exception as exc:  # noqa: BLE001 — sanitize everything
            self._log_failure("request failed", exc)
            raise ApexStoreError(FAILED) from None

        status = response.status_code
        if status == 200:
            try:
                return response.json()
            except ValueError as exc:
                log.error("apex api returned non-JSON for %s %s", method, path,
                          exc_info=exc)
                raise ApexStoreError(BAD_RESPONSE) from None

        log.error("apex api answered HTTP %s for %s %s", status, method, path)
        if status in (401, 403):
            raise ApexStoreError(UNAUTHORIZED)
        if status == 404:
            raise ApexStoreError(NOT_FOUND)
        if status == 422:
            raise ApexStoreError(INVALID_REQUEST)
        if status == 502:
            raise ApexStoreError(self._store_detail(response) or UNAVAILABLE)
        if status in (503, 504):
            raise ApexStoreError(UNAVAILABLE)
        raise ApexStoreError(FAILED)

    def _log_failure(self, what: str, exc: Exception) -> None:
        """The detail an operator needs, on STDERR, with the token scrubbed.

        The URL stays — stderr is the operator's channel and the URL is what
        they need to fix. The token does not: no httpx exception carries the
        Authorization header today, but a log line is copied into tickets and
        chat, so the scrub does not rely on that. No traceback either, for the
        same reason: its last line is ``str(exc)`` unscrubbed.
        """
        text = str(exc)
        if self._token:
            text = text.replace(self._token, "[redacted]")
        log.error("apex api %s: %s: %s", what, type(exc).__name__, text)

    def _store_detail(self, response: httpx.Response) -> str | None:
        """The API's sanitized store error, when it is provably that.

        The API's 502 handler forwards ``str(ApexStoreError)``, which
        ch._sanitize (or a fixed string in ch/server) produced and which
        carries no connection detail by construction. Forwarding it keeps the
        actionable code (``clickhouse_unavailable``, ``job_id_required``...)
        identical to what direct mode reports.

        It is still checked, because a 502 can come from a proxy in between
        and not from the API: the body must be the API's ``store_error``
        shape, the detail must look like a code-prefixed sentence, carry no
        URL, and contain none of this client's token, URL, host or port.
        Anything else is replaced by the generic code.
        """
        try:
            body = response.json()
        except ValueError:
            return None
        if not isinstance(body, dict) or body.get("error") != "store_error":
            return None
        detail = body.get("detail")
        if not isinstance(detail, str) or not _STORE_DETAIL_RE.match(detail):
            return None
        if "://" in detail or any(secret in detail for secret in self._secrets):
            return None
        return f"{detail} (reported by the Apex API)"


def _validated(model: type[M], payload: Any) -> M:
    """The payload as the tool's own model, or a sanitized failure.

    Every field must be PRESENT, not merely valid. The API serializes the
    tool's result with a full ``model_dump`` (FastMCP's structured output), so
    a genuine answer always carries every field; several models default every
    field (RunList does), and without this an arbitrary JSON object — a
    proxy's error page, a different service — would validate as an empty,
    successful answer. Extra keys are tolerated, so a newer API that adds a
    field does not break an older MCP server.
    """
    missing = (
        set(model.model_fields) - set(payload)
        if isinstance(payload, dict)
        else {"<not an object>"}
    )
    if missing:
        log.error("apex api payload is not a %s; missing %s",
                  model.__name__, sorted(missing))
        raise ApexStoreError(BAD_RESPONSE)
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        log.error("apex api payload failed %s validation", model.__name__,
                  exc_info=exc)
        raise ApexStoreError(BAD_RESPONSE) from None


class ApiTools:
    """The tool backend for API mode: one HTTP call per tool.

    Method signatures match server._StoreTools, so server._build_server
    registers the identical tool surface over either backend.
    """

    def __init__(self, client: ApiClient) -> None:
        if not isinstance(client, ApiClient):
            raise TypeError("ApiTools needs an ApiClient")
        self._client = client

    def _call(self, tool: str, model: type[M], params: dict[str, Any],
              **path_args: str) -> M:
        method, template = TOOL_PATHS[tool]
        path = template.format(**{k: _segment(v) for k, v in path_args.items()})
        return _validated(model, self._client.get_json(method, path, params))

    def analyze_run(self, job_id: str, detail: str) -> Diagnosis:
        return self._call("analyze_run", Diagnosis, {"detail": detail},
                          job_id=_require_job_id(job_id))

    def explain_stage(self, job_id: str, stage_id: int) -> Diagnosis:
        return self._call("explain_stage", Diagnosis, {},
                          job_id=_require_job_id(job_id), stage_id=str(int(stage_id)))

    def compare_runs(self, current_job_id: str, baseline_job_id: str,
                     noise_floor_pct: float | None) -> RunComparison:
        return self._call(
            "compare_runs",
            RunComparison,
            {"baseline_job_id": baseline_job_id, "noise_floor_pct": noise_floor_pct},
            job_id=_require_job_id(current_job_id),
        )

    def list_runs(self, limit: int, since_hours: int, app_name: str) -> RunList:
        return self._call(
            "list_runs",
            RunList,
            {"limit": limit, "since_hours": since_hours, "app_name": app_name},
        )

    def search_kb(self, query: str, top_k: int) -> KbHits:
        return self._call("search_kb", KbHits, {"q": query, "top_k": top_k})

    def recall_similar_runs(self, job_id: str, top_k: int,
                            noise_floor_pct: float | None) -> RecallResult:
        return self._call(
            "recall_similar_runs",
            RecallResult,
            {"top_k": top_k, "noise_floor_pct": noise_floor_pct},
            job_id=_require_job_id(job_id),
        )

    def verify_fix(self, job_id: str, finding_id: str | None) -> FixVerdict:
        return self._call("verify_fix", FixVerdict, {"finding_id": finding_id},
                          job_id=_require_job_id(job_id))

    def suggest_fix(self, job_id: str, finding_id: str | None,
                    min_confidence: float) -> FixSuggestion:
        suggestion = self._call(
            "suggest_fix",
            FixSuggestion,
            {"finding_id": finding_id, "min_confidence": min_confidence},
            job_id=_require_job_id(job_id),
        )
        # Already enforced by the Literal types during validation; restated so
        # the invariant does not rest on one mechanism.
        if suggestion.applied is not False or suggestion.requires_human_approval is not True:
            raise ApexStoreError(BAD_RESPONSE)
        return suggestion

    def runs_resource(self) -> RunList:
        """apex://runs: list_runs at the route's defaults, reshaped.

        The direct resource returns ``RunList(runs, returned)`` with every
        other field at its model default, so the same is built here from the
        route's payload — the resource reads byte-identically over either
        backend, and no resource-only API route is needed.
        """
        listed = self._call("list_runs", RunList, {})
        return RunList(runs=listed.runs, returned=len(listed.runs))
