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

import ipaddress
import logging
import math
import re
from typing import Any, TypeVar
from urllib.parse import quote, urlsplit

import httpx
from pydantic import BaseModel, ValidationError

from .ch import ApexStoreError, _require_job_id, require_run_offset
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
    "apex_api_invalid_request: the Apex API rejected the arguments of this "
    "call. See the server's stderr log for details."
)
BAD_RESPONSE = (
    "apex_api_bad_response: the Apex API answered with a payload that is not "
    "the contracted shape. See the server's stderr log for details."
)
FAILED = (
    "apex_api_failed: the Apex API could not complete the request. See the "
    "server's stderr log for details."
)
OUTDATED = (
    "apex_api_outdated: the Apex API predates list_runs filters and paging "
    "and would have ignored them. Upgrade apex-api (deploy it before "
    "apex-mcp), or call list_runs without filters or offset."
)

# The API's 502 handler forwards ``str(ApexStoreError)``. Its TEXT is never
# forwarded: only its leading code is read, and only a code on this allowlist
# maps to a message — one authored HERE. Everything the API can raise on a
# tool path is listed (ch._sanitize, ch's id guards, server._fail,
# diagnostics._structured). The store these describe is the API PROCESS's
# store, so the messages point at its configuration, not this server's.
_API_STORE = "the Apex API process's"
STORE_ERRORS: dict[str, str] = {
    "clickhouse_unavailable": (
        f"clickhouse_unavailable: the Apex API could not reach its ClickHouse "
        f"store. Check the CLICKHOUSE_* environment of {_API_STORE} "
        f"deployment, not of this MCP server."
    ),
    "clickhouse_access_denied": (
        f"clickhouse_access_denied: ClickHouse refused the Apex API's database "
        f"user. Check CLICKHOUSE_USER, CLICKHOUSE_PASSWORD and that user's "
        f"grants in {_API_STORE} deployment, not this MCP server's."
    ),
    "clickhouse_database_missing": (
        f"clickhouse_database_missing: the database the Apex API is configured "
        f"to read does not exist. Check CLICKHOUSE_DATABASE of {_API_STORE} "
        f"deployment."
    ),
    "clickhouse_schema_missing": (
        "clickhouse_schema_missing: the apex schema is not applied on the Apex "
        "API's store. Apply contract/*.ddl.sql via the infra lane."
    ),
    "clickhouse_query_failed": (
        "clickhouse_query_failed: the Apex API's store rejected the query. See "
        "the Apex API's stderr log for details."
    ),
    "memory_unavailable": (
        "memory_unavailable: the cross-run memory tables are not present on the "
        "Apex API's store."
    ),
    "job_id_required": "job_id_required: pass a non-empty job_id.",
    "job_id_too_long": "job_id_too_long: job_id exceeds 512 characters.",
    "finding_id_required": "finding_id_required: pass a non-empty finding_id.",
    "finding_id_too_long": (
        "finding_id_too_long: finding_id exceeds 512 characters."
    ),
    # list_runs' filters (P7.5), refused by the API's ReadStore exactly as by
    # a direct one, so both backends report the same text.
    "app_name_too_long": "app_name_too_long: app_name exceeds 512 characters.",
    "job_id_prefix_too_long": (
        "job_id_prefix_too_long: job_id_prefix exceeds 512 characters."
    ),
    "plan_fingerprint_too_long": (
        "plan_fingerprint_too_long: plan_fingerprint exceeds 64 characters."
    ),
    "offset_out_of_range": "offset_out_of_range: offset must be between 0 and 10000.",
    "apex_tool_failed": (
        "apex_tool_failed: the Apex API could not complete the request. See the "
        "Apex API's stderr log for details."
    ),
    "apex_tool_result_unreadable": (
        "apex_tool_result_unreadable: the Apex API's tool returned no "
        "structured payload."
    ),
}
_CODE_RE = re.compile(r"^([a-z][a-z0-9_]{1,63}):")

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
    """http(s), a host, a usable port if one is given, and NO userinfo.

    Userinfo is refused rather than ignored: httpx turns ``user:pw@`` into
    Basic auth, which REPLACES the bearer header — the token would silently
    not be sent, and the password would be.
    """
    try:
        parts = urlsplit(url)
        port = parts.port  # raises ValueError when malformed or out of range
    except ValueError:
        return False
    if port is not None and not 0 < port <= 65535:
        return False
    if "@" in parts.netloc or parts.username is not None:
        return False
    return parts.scheme in ("http", "https") and bool(parts.hostname)


def sends_token_in_clear(url: str) -> bool:
    """Plain http to a host that is not loopback: the token crosses a network."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme != "http":
        return False
    host = parts.hostname or ""
    if host == "localhost" or host.endswith(".localhost"):
        return False
    try:
        return not ipaddress.ip_address(host).is_loopback
    except ValueError:
        return True


def _floor(value: float | None) -> float | None:
    """A noise floor the API will accept, or None.

    Direct mode treats a negative or non-finite floor as no floor at all
    (diagnose._valid_noise_floor). The API instead rejects it with 422, which
    would turn the same call into an error. Sending None keeps the verdict
    identical. diagnose's note then says "no floor was supplied", so
    ApiTools swaps in direct mode's "an invalid floor was supplied" sentence
    (see COMPARE_INVALID_FLOOR_NOTE / RECALL_INVALID_FLOOR_NOTE).
    """
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _segment(value: str) -> str:
    """One path segment, percent-encoded so it can never become two.

    ``safe=""`` encodes "/" and "?". Dots are encoded too: a job_id of ".."
    left literal would be resolved as a dot-segment and address a DIFFERENT
    route. The API decodes the segment back to the same value.
    """
    return quote(value, safe="").replace(".", "%2E")


class _Bearer(httpx.Auth):
    """The token as an httpx auth flow, not a hand-set header.

    An explicit ``auth=`` outranks the auth httpx would otherwise derive from
    the request: URL userinfo becomes Basic auth, which REPLACES a hand-set
    Authorization header and sends no bearer token at all. valid_base_url
    already refuses userinfo; this keeps a directly constructed client safe
    too. (httpx 0.28 applies no implicit .netrc auth.)
    """

    def __init__(self, token: str) -> None:
        self._token = token

    def auth_flow(self, request: httpx.Request):  # noqa: ANN201
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


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
                headers={"Accept": "application/json"},
                auth=_Bearer(self._token),
                # Per request, so an injected client that follows by default
                # cannot carry the token to wherever a redirect points.
                follow_redirects=False,
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
            raise ApexStoreError(self._store_error(response))
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

    @staticmethod
    def _store_error(response: httpx.Response) -> str:
        """A locally-authored message for the API's 502, never its text.

        Only the API's own ``store_error`` body is read, and from it only the
        leading code, looked up in STORE_ERRORS. A known code gets its fixed
        message; an unknown one is ``apex_api_failed`` (the API answered, so
        it is not "unavailable"). A 502 that is not the API's shape came from
        something in between — a proxy whose upstream is down — and is
        ``apex_api_unavailable``.
        """
        try:
            body = response.json()
        except ValueError:
            return UNAVAILABLE
        if not isinstance(body, dict) or body.get("error") != "store_error":
            return UNAVAILABLE
        detail = body.get("detail")
        match = _CODE_RE.match(detail) if isinstance(detail, str) else None
        code = match.group(1) if match else ""
        return STORE_ERRORS.get(code, FAILED)


# diagnose.py builds these inline, so they are copied VERBATIM rather than
# imported; a test asserts each equals what diagnose produces. They let API
# mode report an invalid floor exactly as direct mode does: the API refuses
# the value (422) before diagnose can see it, so the client sends no floor and
# swaps diagnose's "none supplied" sentence for its "invalid" one.
COMPARE_NO_FLOOR_NOTE = (
    "No noise floor was supplied, so metric deltas above are "
    "measurements, not regressions (CONTRACT.md rule 2: the floor is "
    "MEASURED per shape and scale — 32-59% at 8 tasks and 32.9% at "
    "100 tasks on this system — and two runs cannot measure their "
    "own). Pass noise_floor_pct to adjudicate them; an unresolvable "
    "delta is not proof of zero change."
)
COMPARE_INVALID_FLOOR_NOTE = (
    "An invalid noise floor was supplied, so metric deltas above remain "
    "measurements, not adjudicated regressions."
)
RECALL_NO_FLOOR_NOTE = (
    "No noise floor was supplied (CONTRACT.md rule 2: the floor is "
    "MEASURED per shape and scale, and these runs cannot measure "
    "their own). Pass noise_floor_pct to adjudicate the spread."
)
RECALL_INVALID_FLOOR_NOTE = (
    "An invalid noise floor was supplied; no faster or slower "
    "claim can be adjudicated from it."
)


def _swap(notes: list[str], old: str, new: str) -> list[str]:
    """Exact-match replacement only: any other note passes through untouched."""
    return [new if note == old else note for note in notes]


# Fields added to a model AFTER its first release. An older API omits them,
# and that is not a malformed answer: they take their model defaults. A caller
# whose meaning depends on one must check model_fields_set itself, as
# ApiTools.list_runs does — a missing echo there means the filters were
# ignored, and that is refused rather than returned as a filtered page.
RUN_LIST_ECHO_FIELDS = frozenset(
    {"offset", "job_id_prefix_filter", "plan_fingerprint_filter", "has_findings_filter"}
)
_ADDITIVE_FIELDS: dict[type[BaseModel], frozenset[str]] = {RunList: RUN_LIST_ECHO_FIELDS}


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
        set(model.model_fields) - set(payload) - _ADDITIVE_FIELDS.get(model, set())
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
        sent = _floor(noise_floor_pct)
        comparison = self._call(
            "compare_runs",
            RunComparison,
            {"baseline_job_id": baseline_job_id, "noise_floor_pct": sent},
            job_id=_require_job_id(current_job_id),
        )
        if noise_floor_pct is not None and sent is None:
            comparison = comparison.model_copy(update={"notes": _swap(
                comparison.notes, COMPARE_NO_FLOOR_NOTE, COMPARE_INVALID_FLOOR_NOTE)})
        return comparison

    def list_runs(
        self, limit: int, since_hours: int, app_name: str,
        offset: int = 0, job_id_prefix: str = "", plan_fingerprint: str = "",
        has_findings: bool | None = None,
    ) -> RunList:
        # Refused HERE, with the direct backend's own error: the route answers
        # an out-of-range offset with a 422, which would read as
        # apex_api_invalid_request and make the two backends disagree.
        offset = require_run_offset(offset)
        # has_findings None is dropped by get_json, which is the route's own
        # "no filter" default; the strings travel as query parameters and are
        # bound again by the API's ReadStore.
        listed = self._call(
            "list_runs",
            RunList,
            {
                "limit": limit, "since_hours": since_hours, "app_name": app_name,
                "offset": offset, "job_id_prefix": job_id_prefix,
                "plan_fingerprint": plan_fingerprint, "has_findings": has_findings,
            },
        )
        narrowed = bool(offset or job_id_prefix or plan_fingerprint) or has_findings is not None
        if narrowed and not RUN_LIST_ECHO_FIELDS <= listed.model_fields_set:
            # A pre-P7.5 API ignores offset and the new filters and answers
            # with an unfiltered first page. Returned as-is, that page would
            # read as the filtered answer.
            log.error("apex api predates list_runs filters; refusing its page")
            raise ApexStoreError(OUTDATED)
        return listed

    def search_kb(self, query: str, top_k: int) -> KbHits:
        return self._call("search_kb", KbHits, {"q": query, "top_k": top_k})

    def recall_similar_runs(self, job_id: str, top_k: int,
                            noise_floor_pct: float | None) -> RecallResult:
        sent = _floor(noise_floor_pct)
        recall = self._call(
            "recall_similar_runs",
            RecallResult,
            {"top_k": top_k, "noise_floor_pct": sent},
            job_id=_require_job_id(job_id),
        )
        if noise_floor_pct is not None and sent is None and recall.summary:
            summary = recall.summary.model_copy(update={"notes": _swap(
                recall.summary.notes, RECALL_NO_FLOOR_NOTE, RECALL_INVALID_FLOOR_NOTE)})
            recall = recall.model_copy(update={"summary": summary})
        return recall

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
