"""The verdict tier: the eight MCP tools, over HTTP.

Every handler here dispatches through ``FastMCP.call_tool``. It would be
shorter to call ``diagnose.analyze()`` directly, and it would be wrong: the
tool layer carries annotations, output schemas and docstrings that are part of
the contract a model reads, and two paths into the same analysis is two
answers to the same question.

ROUTE/TOOL PARITY IS A TEST. ``test_the_contracted_tool_surface`` pins the tool
set on the MCP side because "an unnoticed tool on a server a model can call is
a security event". ``TOOL_ROUTES`` below is the same control on this side: the
router is BUILT from it, and a test asserts it matches ``list_tools()``
exactly, so a ninth tool cannot ship without a route and a route cannot exist
without a tool.

On paths: the per-run tools hang off ``/v1/runs/{job_id}``. The two
collection-level tools live under ``/v1/diagnostics/`` instead, because
``list_runs`` returns the MCP ``RunList`` while the resource tier's own
``/v1/runs`` returns the console's rollup rows — different shapes, so they
cannot share a path, and silently shadowing one with the other would depend on
router registration order.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Request
from mcp.server.fastmcp import FastMCP

from apex_mcp.ch import ApexStoreError, ReadStore
from apex_mcp.server import create_server

router = APIRouter(tags=["diagnostics"])

# tool name -> (HTTP method, path). The single source both the router and the
# parity test read. Adding a handler without adding it here, or the reverse,
# fails the test rather than shipping.
TOOL_ROUTES: dict[str, tuple[str, str]] = {
    "analyze_run": ("GET", "/runs/{job_id}/diagnosis"),
    "explain_stage": ("GET", "/runs/{job_id}/stages/{stage_id}/diagnosis"),
    "compare_runs": ("GET", "/runs/{job_id}/comparison"),
    "recall_similar_runs": ("GET", "/runs/{job_id}/recall"),
    "verify_fix": ("GET", "/runs/{job_id}/verification"),
    "suggest_fix": ("POST", "/runs/{job_id}/fix-suggestion"),
    "list_runs": ("GET", "/diagnostics/runs"),
    "search_kb": ("GET", "/diagnostics/search"),
}


def _server(request: Request) -> FastMCP:
    """One FastMCP per app, built on first use.

    Cached on app state rather than rebuilt per request: registering eight
    tools on every call would be pure overhead, and the server holds no
    per-request state — the store it closes over is the app's.
    """
    server = getattr(request.app.state, "mcp_server", None)
    if server is None:
        store: ReadStore = request.app.state.store
        server = create_server(store)
        request.app.state.mcp_server = server
    return server


def _structured(result: Any) -> Any:
    """The structured payload, however call_tool shaped it.

    ``call_tool`` is typed ``Sequence[ContentBlock] | dict``, and with
    ``convert_result=True`` a tool with an output schema comes back as
    ``(content_blocks, structured)``. Reading ``result`` directly would hand
    the client a list of content blocks for one shape and the real payload for
    the other.
    """
    if isinstance(result, tuple):
        return result[1]
    if isinstance(result, dict):
        return result
    raise ApexStoreError(
        "apex_tool_result_unreadable: the tool returned no structured payload."
    )


async def _call(request: Request, tool: str, arguments: dict[str, Any]) -> Any:
    """Dispatch one tool, keeping the store's sanitization intact.

    A tool already wraps its own failures via server._fail, so an
    ApexStoreError arriving here is safe to forward and the app's handler
    turns it into a 502. Anything else is left to the generic handler, which
    deliberately does not echo the exception text.
    """
    try:
        return _structured(await _server(request).call_tool(tool, arguments))
    except ApexStoreError:
        raise
    except Exception as exc:  # noqa: BLE001
        # The SDK wraps a tool's exception; recover the sanitized one when it
        # is in the chain so the client gets the actionable message.
        cause: BaseException | None = exc
        while cause is not None:
            if isinstance(cause, ApexStoreError):
                raise cause from None
            cause = cause.__cause__ or cause.__context__
        raise


@router.get(TOOL_ROUTES["analyze_run"][1])
async def analyze_run(
    request: Request,
    job_id: str,
    detail: Literal["summary", "stages", "full"] = "summary",
) -> Any:
    """Diagnose one run. `detail` widens the payload, never the verdict."""
    return await _call(request, "analyze_run", {"job_id": job_id, "detail": detail})


@router.get(TOOL_ROUTES["explain_stage"][1])
async def explain_stage(request: Request, job_id: str, stage_id: int) -> Any:
    """One stage of one run. `coverage` still describes the RUN."""
    return await _call(
        request, "explain_stage", {"job_id": job_id, "stage_id": stage_id}
    )


@router.get(TOOL_ROUTES["compare_runs"][1])
async def compare_runs(
    request: Request,
    job_id: str,
    baseline_job_id: str = "",
    noise_floor_pct: float | None = None,
) -> Any:
    """Compare against a baseline; omit it and Apex picks the same plan shape."""
    return await _call(
        request,
        "compare_runs",
        {
            "current_job_id": job_id,
            "baseline_job_id": baseline_job_id,
            "noise_floor_pct": noise_floor_pct,
        },
    )


@router.get(TOOL_ROUTES["recall_similar_runs"][1])
async def recall_similar_runs(
    request: Request,
    job_id: str,
    top_k: int = 5,
    noise_floor_pct: float | None = None,
) -> Any:
    """Prior runs of this run's plan shape, as measurements."""
    return await _call(
        request,
        "recall_similar_runs",
        {"job_id": job_id, "top_k": top_k, "noise_floor_pct": noise_floor_pct},
    )


@router.get(TOOL_ROUTES["verify_fix"][1])
async def verify_fix(
    request: Request, job_id: str, finding_id: str | None = None
) -> Any:
    """What the verify lane concluded. 'not_assessed' is not a clean bill."""
    return await _call(
        request, "verify_fix", {"job_id": job_id, "finding_id": finding_id}
    )


@router.post(TOOL_ROUTES["suggest_fix"][1])
async def suggest_fix(
    request: Request,
    job_id: str,
    finding_id: str | None = None,
    min_confidence: float = 0.75,
) -> Any:
    """Propose a fix. APPLIES NOTHING — no file, no git, no PR.

    POST because this is the tool the MCP layer marks as not read-only, and
    the HTTP surface should not describe it as safer than the tool does.
    """
    return await _call(
        request,
        "suggest_fix",
        {
            "job_id": job_id,
            "finding_id": finding_id,
            "min_confidence": min_confidence,
        },
    )


@router.get(TOOL_ROUTES["list_runs"][1])
async def list_runs(
    request: Request,
    limit: int = 20,
    since_hours: int = 168,
    app_name: str = "",
) -> Any:
    """Recent runs, newest first — where a job_id comes from."""
    return await _call(
        request,
        "list_runs",
        {"limit": limit, "since_hours": since_hours, "app_name": app_name},
    )


@router.get(TOOL_ROUTES["search_kb"][1])
async def search_kb(request: Request, q: str, top_k: int = 5) -> Any:
    """Token search over findings and redacted plan text."""
    return await _call(request, "search_kb", {"query": q, "top_k": top_k})
