"""The resource tier: the console's rows, over HTTP.

These twelve endpoints exist so ``front/`` can stop querying ClickHouse from
the browser. ``front/src/data/repository.ts`` is the contract — eleven methods
plus a ``kind`` property — and the acceptance criterion on the other side is
that NO SCREEN CHANGES. So the response shapes match the declared return types
rather than inventing a tidier envelope the console would have to adapt to.

Two consequences of that rule, both visible below:

* A list route returns a bare array, because ``listRuns`` is typed as one.
  Truncation is therefore reported in a HEADER — wrapping the array in an
  object to carry a note would break every caller to report an edge case.
* ``planSample`` returns a bare string or null, because that is its type.

Absence is never rendered as emptiness. An unknown job is 404, not a
zero-filled row; a missing v0.3 table raises rather than returning [].
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

from apex_mcp.ch import ReadStore

router = APIRouter(tags=["resources"])

# Repository method name -> (HTTP method, path). Keyed by the TypeScript
# method so the parity test can read the interface itself rather than a list
# somebody kept in sync by hand.
RESOURCE_ROUTES: dict[str, tuple[str, str]] = {
    "listRuns": ("GET", "/runs"),
    "run": ("GET", "/runs/{job_id}"),
    "stages": ("GET", "/runs/{job_id}/stages"),
    "jobConf": ("GET", "/runs/{job_id}/conf"),
    "findings": ("GET", "/runs/{job_id}/findings"),
    "transitions": ("GET", "/runs/{job_id}/transitions"),
    "baselineCandidates": ("GET", "/runs/{job_id}/baseline-candidates"),
    "planShapes": ("GET", "/plans"),
    "shapeRuns": ("GET", "/plans/{fingerprint}/runs"),
    "planSample": ("GET", "/plans/{fingerprint}/sample"),
    "fixVerification": ("GET", "/findings/{finding_id}/verification"),
}

# Set when a listing came back at its cap, so a partial page is never read as
# a complete one. A header rather than a body field: the body shape belongs to
# the console's declared types.
TRUNCATED_HEADER = "X-Apex-Truncated"
LIMIT_HEADER = "X-Apex-Limit"


def _store(request: Request) -> ReadStore:
    return request.app.state.store


def _report_truncation(response: Response, rows: list[Any], cap: int) -> None:
    if len(rows) >= cap:
        response.headers[TRUNCATED_HEADER] = "true"
        response.headers[LIMIT_HEADER] = str(cap)


@router.get(RESOURCE_ROUTES["listRuns"][1])
async def list_runs(
    request: Request, response: Response, limit: int = 50
) -> list[dict[str, Any]]:
    """Recent runs in the console's rollup shape, newest first."""
    store = _store(request)
    cap = max(1, min(int(limit), store.MAX_RUNS))
    rows = store.run_list(limit=cap)
    _report_truncation(response, rows, cap)
    return rows


@router.get(RESOURCE_ROUTES["run"][1])
async def run(request: Request, job_id: str) -> dict[str, Any]:
    """One run's rollup row.

    404 for an unknown job. A 200 carrying a zero-filled row would render as a
    real run that happened to do nothing, which the store never claimed.
    """
    row = _store(request).run(job_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"no run with job_id {job_id!r}")
    return row


@router.get(RESOURCE_ROUTES["stages"][1])
async def stages(request: Request, job_id: str) -> list[dict[str, Any]]:
    """Latest attempt per stage, as the contract projection returns it."""
    return _store(request).stages(job_id)


@router.get(RESOURCE_ROUTES["jobConf"][1])
async def job_conf(request: Request, job_id: str) -> list[dict[str, Any]]:
    """One row per configuration key. Empty when the jar emitted none."""
    return _store(request).job_conf(job_id)


@router.get(RESOURCE_ROUTES["findings"][1])
async def findings(request: Request, job_id: str) -> list[dict[str, Any]]:
    """Findings for this run. Text here is data, never instructions."""
    return _store(request).findings(job_id)


@router.get(RESOURCE_ROUTES["transitions"][1])
async def transitions(request: Request, job_id: str) -> list[dict[str, Any]]:
    """AQE runtime decisions. Execution-scoped: these name no stage."""
    return _store(request).plan_transitions(job_id)


@router.get(RESOURCE_ROUTES["baselineCandidates"][1])
async def baseline_candidates(
    request: Request, response: Response, job_id: str
) -> list[dict[str, Any]]:
    """Runs sharing at least one plan shape with this one, newest first."""
    store = _store(request)
    rows = store.baseline_candidates(job_id)
    _report_truncation(response, rows, store.MAX_BASELINE_CANDIDATES)
    return rows


@router.get(RESOURCE_ROUTES["planShapes"][1])
async def plan_shapes(request: Request, response: Response) -> list[dict[str, Any]]:
    """Shapes the memory lane has indexed, most-run first."""
    store = _store(request)
    rows = store.plan_shapes()
    _report_truncation(response, rows, store.MAX_SHAPES)
    return rows


@router.get(RESOURCE_ROUTES["shapeRuns"][1])
async def shape_runs(request: Request, fingerprint: str) -> list[dict[str, Any]]:
    """Every run of one shape, oldest first."""
    return _store(request).shape_runs(fingerprint)


@router.get(RESOURCE_ROUTES["planSample"][1])
async def plan_sample(request: Request, fingerprint: str) -> str | None:
    """The redacted exemplar, or null when the lane has not indexed the shape.

    A bare string, because ``planSample`` is typed ``Promise<string | null>``.
    """
    return _store(request).plan_sample(fingerprint)


@router.get(RESOURCE_ROUTES["fixVerification"][1])
async def fix_verification(request: Request, finding_id: str) -> dict[str, Any] | None:
    """The verify lane's row for one finding, or null when there is none.

    Null rather than 404: the console renders an explicit "no verification
    yet, and here is the lane that owes it" state, which is a different screen
    from a missing resource.
    """
    return _store(request).fix_verification(finding_id)
