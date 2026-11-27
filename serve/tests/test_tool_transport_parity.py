"""The eight tools answer the same way over MCP and over HTTP.

test_api_diagnostics.py pins the route table and the fidelity of the default
analyze_run call. This file covers every tool, with POPULATED data, with
nothing to read, and with the store down, calling the MCP server directly and
the /v1 route with the equivalent parameters, over the same fake store. No
field is normalized: repeated calls on both transports showed none that varies
between calls, so any difference is a transport difference.

Equality alone could be met by both transports returning the same absence or
the same error, so the populated vector also asserts that each payload is not
an absence, and differs from that tool's payload over an empty store.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from clickhouse_connect.driver.exceptions import OperationalError
from fastapi.testclient import TestClient
from mcp.server.fastmcp.exceptions import ToolError

from apex_api.app import create_app
from apex_mcp.ch import MEMORY_TABLES, ReadStore
from apex_mcp.server import create_server
from tests.conftest import FakeClient, FakeResult, reads
from tests.test_api_diagnostics import AUTH, DSN, SETTINGS, fake_client
from tests.test_ch import _outcome_row, _plan_row
from tests.test_verify_fix import _row as verification_row

NEAR_FINGERPRINT = "2" * 64


class _NoVerificationTable(FakeClient):
    """An older deployment: fix_verifications and the memory tables are absent.

    The conftest double answers every system.columns probe with columns, so
    fix_verifications would otherwise "exist" and be served stage rows."""

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        if "system.columns" in query and (parameters or {}).get("table") == "fix_verifications":
            self.calls.append((query, parameters or {}))
            return FakeResult([])
        return super().query(query, parameters)


class _Populated(FakeClient):
    """Every additive table present and populated: a verification for the run,
    cross-run memory with a similar plan and prior runs, and a recent-runs row."""

    def query(self, query: str, parameters: dict | None = None) -> FakeResult:
        parameters = parameters or {}
        if "system.tables" in query:
            self.calls.append((query, parameters))
            return FakeResult([{"name": name} for name in MEMORY_TABLES])
        if "system.columns" in query and parameters.get("table") == "fix_verifications":
            self.calls.append((query, parameters))
            return FakeResult([{"name": "verification_id"}])
        if reads(query, "fix_verifications"):
            self.calls.append((query, parameters))
            return FakeResult([verification_row(job_id=parameters.get("job_id", "j"))])
        if reads(query, "plan_memory"):
            self.calls.append((query, parameters))
            return FakeResult([_plan_row(NEAR_FINGERPRINT, 0.93)])
        if reads(query, "run_outcomes"):
            self.calls.append((query, parameters))
            return FakeResult([
                _outcome_row("prior-1", 90_000, "2026-09-20 10:00:00"),
                _outcome_row("prior-2", 120_000, "2026-09-21 10:00:00"),
            ])
        if "since" in parameters:  # RUNS_SQL, the only read bounded by `since`
            self.calls.append((query, parameters))
            return FakeResult([{
                "job_id": "j", "app_id": "app-j", "app_name": "nightly_etl",
                "first_ts": "2026-09-27 10:00:00", "last_ts": "2026-09-27 10:05:00",
                "stage_count": 1, "spill_disk_bytes": 0, "worst_p99_ms": 460,
            }])
        return super().query(query, parameters)


class _Unreachable:
    def query(self, query: str, parameters: dict | None = None):
        raise OperationalError(f"could not connect to {DSN}")


def _populated() -> _Populated:
    base = fake_client()
    return _Populated(stages=base.stages, findings=base.findings, transitions=base.transitions, search=base.search)


def _vectors(job: str) -> dict[str, tuple[dict[str, Any], str, str]]:
    """tool -> (MCP arguments, HTTP method, HTTP path) for the same request."""
    return {
        # detail=full, not the default summary test_api_diagnostics already pins.
        "analyze_run": ({"job_id": job, "detail": "full"}, "GET", f"/v1/runs/{job}/diagnosis?detail=full"),
        "explain_stage": ({"job_id": job, "stage_id": 4}, "GET", f"/v1/runs/{job}/stages/4/diagnosis"),
        "compare_runs": (
            {"current_job_id": job, "baseline_job_id": "base", "noise_floor_pct": None},
            "GET", f"/v1/runs/{job}/comparison?baseline_job_id=base",
        ),
        "recall_similar_runs": ({"job_id": job, "top_k": 5, "noise_floor_pct": None}, "GET", f"/v1/runs/{job}/recall"),
        "verify_fix": ({"job_id": job, "finding_id": None}, "GET", f"/v1/runs/{job}/verification"),
        "suggest_fix": (
            {"job_id": job, "finding_id": None, "min_confidence": 0.75},
            "POST", f"/v1/runs/{job}/fix-suggestion",
        ),
        "list_runs": ({"limit": 20, "since_hours": 168, "app_name": ""}, "GET", "/v1/diagnostics/runs"),
        "search_kb": ({"query": "skew", "top_k": 5}, "GET", "/v1/diagnostics/search?q=skew"),
    }


TOOLS = sorted(_vectors("j"))


def _over_mcp(client: Any, tool: str, arguments: dict[str, Any]) -> Any:
    result = asyncio.run(create_server(ReadStore(client)).call_tool(tool, arguments))
    return result[1] if isinstance(result, tuple) else result


def _over_http(client: Any, method: str, path: str):
    app = create_app(store=ReadStore(client), settings=SETTINGS)
    return TestClient(app).request(method, path, headers=AUTH)


# What each tool says when the run has no rows. Pinned so "equal on both
# transports" cannot be satisfied by both inventing the same success.
ABSENT_STATUS = {
    "analyze_run": "not_found",
    "explain_stage": "not_found",
    "compare_runs": "not_comparable",
    "recall_similar_runs": "memory_unavailable",
    "verify_fix": "not_assessed",
}


def _is_absence(tool: str, payload: dict[str, Any]) -> bool:
    if tool in ABSENT_STATUS:
        return payload.get("status") == ABSENT_STATUS[tool]
    if tool == "list_runs":
        return payload.get("runs") == []
    if tool == "search_kb":
        return payload.get("hits") == []
    return False


def test_the_vectors_cover_every_tool():
    names = {tool.name for tool in asyncio.run(create_server(ReadStore(fake_client())).list_tools())}
    assert set(TOOLS) == names


@pytest.mark.parametrize("tool", TOOLS)
def test_a_tool_returns_the_same_populated_payload_over_both_transports(tool):
    """B-1 — the route is a transport, not a second analysis, and the payload
    compared is a real answer, not an absence both sides happen to share."""
    arguments, method, path = _vectors("j")[tool]

    direct = _over_mcp(_populated(), tool, arguments)
    response = _over_http(_populated(), method, path)

    assert response.status_code == 200
    assert response.json() == direct
    assert not _is_absence(tool, direct), f"{tool} answered with an absence over populated data"


def test_the_populated_fixture_reaches_the_additive_reads():
    """B-1 — 'with data' means the verification and memory rows are served,
    not the table-absent path an older deployment takes."""
    verdict = _over_mcp(_populated(), "verify_fix", {"job_id": "j", "finding_id": None})
    assert verdict["status"] != "not_assessed"
    assert verdict["verifications"], "verify_fix returned no verification over a populated table"

    recall = _over_mcp(_populated(), "recall_similar_runs", {"job_id": "j", "top_k": 5, "noise_floor_pct": None})
    assert recall["status"] != "memory_unavailable"
    assert recall["similar_plans"] and recall["prior_runs"]

    runs = _over_mcp(_populated(), "list_runs", {"limit": 20, "since_hours": 168, "app_name": ""})
    assert [run["job_id"] for run in runs["runs"]] == ["j"]


@pytest.mark.parametrize("tool", TOOLS)
def test_absence_reads_the_same_and_is_not_a_success_over_both_transports(tool):
    """B-3 — nothing to read is reported as absence, identically."""
    arguments, method, path = _vectors("missing")[tool]

    direct = _over_mcp(_NoVerificationTable(), tool, arguments)
    response = _over_http(_NoVerificationTable(), method, path)

    assert response.status_code == 200
    assert response.json() == direct
    if tool == "suggest_fix":
        assert direct["applied"] is False
    else:
        assert _is_absence(tool, direct)


@pytest.mark.parametrize("tool", TOOLS)
def test_populated_and_absent_payloads_differ_for_every_tool(tool):
    """B-4 — parity is not satisfied by two identical absences: the same tool
    must answer differently over populated data and over an empty store."""
    arguments, _, _ = _vectors("j")[tool]
    absent_arguments, _, _ = _vectors("missing")[tool]

    assert _over_mcp(_populated(), tool, arguments) != _over_mcp(_NoVerificationTable(), tool, absent_arguments)


@pytest.mark.parametrize("tool", TOOLS)
def test_an_unreachable_store_fails_the_same_way_over_both_transports(tool):
    """B-2 — an outage is an error on both sides, verify_fix included, with the
    same sanitized code, and the connection string reaches neither."""
    arguments, method, path = _vectors("j")[tool]

    with pytest.raises(ToolError) as caught:
        _over_mcp(_Unreachable(), tool, arguments)
    response = _over_http(_Unreachable(), method, path)

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail.startswith("clickhouse_unavailable")
    assert detail in str(caught.value)
    for secret in (DSN, "sup3rs3cr3t", "db.internal.example"):
        assert secret not in response.text
        assert secret not in str(caught.value)
