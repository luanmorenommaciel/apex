"""The resource tier: one route per Repository method, and the console's shapes."""

from __future__ import annotations

import pathlib
import re
from typing import Any

from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings
from apex_api.routes.resources import (
    LIMIT_HEADER,
    RESOURCE_ROUTES,
    TRUNCATED_HEADER,
)
from apex_mcp.ch import ReadStore
from tests.conftest import FakeClient, finding_row, stage_row, transition_row
from tests.test_ch import _ConsoleClient

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}

REPOSITORY_TS = (
    pathlib.Path(__file__).resolve().parents[2] / "front" / "src" / "data" / "repository.ts"
)

RUN_ROW = {
    "job_id": "j", "app_name": "nightly-rollup", "stage_count": 34,
    "started_at": "2026-09-20 10:00:00", "finding_count": 3, "has_critical": 1,
    "task_time_ms": 91000, "plan_fingerprint": "a" * 64, "shape_count": 2,
    "shaped_stage_count": 30, "config_source": "observed",
    "conf_executor_instances": 8, "conf_shuffle_partitions": 200,
}


def build(client: Any) -> TestClient:
    return TestClient(create_app(store=ReadStore(client), settings=SETTINGS))


def repository_methods() -> set[str]:
    """The method names declared on the Repository interface itself.

    Read from the TypeScript rather than restated here, so the parity test
    cannot pass because two hand-kept lists agree with each other while both
    disagree with the console. `kind` is a property, not a data method, and
    has nothing to serve.
    """
    source = REPOSITORY_TS.read_text()
    body = source.split("export interface Repository {", 1)[1].split("\n}", 1)[0]
    return set(re.findall(r"^\s*(\w+)\s*\(", body, flags=re.MULTILINE))


# -- parity -----------------------------------------------------------------


def test_every_repository_method_has_a_route():
    declared = repository_methods()
    assert declared, "could not read the Repository interface"
    missing = declared - set(RESOURCE_ROUTES)
    assert missing == set(), f"Repository methods with no route: {sorted(missing)}"
    extra = set(RESOURCE_ROUTES) - declared
    assert extra == set(), f"routes with no Repository method: {sorted(extra)}"

    # And the declared table is what the app serves. Read from the OpenAPI
    # schema: an included router appears in app.routes as an opaque wrapper
    # carrying neither path nor methods, so walking those would see nothing.
    schema = create_app(store=ReadStore(FakeClient()), settings=SETTINGS).openapi()
    served = {
        (method.upper(), path.removeprefix("/v1"))
        for path, operations in schema["paths"].items()
        for method in operations
    }
    for name, (method, path) in RESOURCE_ROUTES.items():
        assert (method, path) in served, f"{name} is declared but not served"


def test_row_shapes_match_the_console_contract():
    """The console renders these rows unchanged, so the columns must be there."""
    client = FakeClient(
        stages={"j": [stage_row(4)]},
        findings={"j": [finding_row(job_id="j")]},
        transitions={"j": [transition_row("skew_split")]},
    )
    app = build(client)

    stages = app.get("/v1/runs/j/stages", headers=AUTH).json()
    assert stages and {"stage_id", "task_count", "plan_fingerprint"} <= set(stages[0])

    got = app.get("/v1/runs/j/findings", headers=AUTH).json()
    assert got and {"finding_id", "severity", "evidence", "fix"} <= set(got[0])

    got = app.get("/v1/runs/j/transitions", headers=AUTH).json()
    assert got and {"transition_type", "detail", "confidence"} <= set(got[0])

    conf = build(_ConsoleClient(conf_rows=[{"job_id": "j", "key": "k", "value": "v", "ts": None}]))
    got = conf.get("/v1/runs/j/conf", headers=AUTH).json()
    assert got and {"job_id", "key", "value"} <= set(got[0])

    runs = build(_ConsoleClient(run_rows=[RUN_ROW]))
    listed = runs.get("/v1/runs", headers=AUTH).json()
    # The console's rollup, not the MCP's RunSummary: task_time_ms and
    # finding_count exist here and do not exist in ReadStore.runs().
    assert listed and {"task_time_ms", "finding_count", "shape_count"} <= set(listed[0])


# -- absence ----------------------------------------------------------------


def test_unknown_job_is_404_not_a_zero_row():
    response = build(_ConsoleClient(run_rows=[])).get("/v1/runs/nope", headers=AUTH)
    assert response.status_code == 404
    # A found run still answers 200 through the same handler.
    assert build(_ConsoleClient(run_rows=[RUN_ROW])).get(
        "/v1/runs/j", headers=AUTH
    ).status_code == 200


def test_absent_memory_tables_are_reported():
    """No table is not an empty history, and the response says which."""
    app = build(_ConsoleClient(tables=()))
    for path in ("/v1/plans", "/v1/plans/" + "a" * 64 + "/runs", "/v1/runs/j/baseline-candidates"):
        response = app.get(path, headers=AUTH)
        assert response.status_code == 502, path
        assert "memory_unavailable" in response.text
        assert response.json() != []
    # The reads that do not need v0.3 still work on the same deployment.
    assert build(_ConsoleClient(tables=(), conf_rows=[])).get(
        "/v1/runs/j/conf", headers=AUTH
    ).json() == []


# -- bounds -----------------------------------------------------------------


def test_unbounded_listing_is_truncated_and_reported():
    rows = [dict(RUN_ROW, job_id=f"j{i}") for i in range(ReadStore.MAX_RUNS)]
    response = build(_ConsoleClient(run_rows=rows)).get(
        "/v1/runs?limit=100000", headers=AUTH
    )
    assert response.status_code == 200
    # The body stays a bare array, because listRuns is typed as one.
    assert isinstance(response.json(), list)
    assert response.headers[TRUNCATED_HEADER] == "true"
    assert response.headers[LIMIT_HEADER] == str(ReadStore.MAX_RUNS)

    # A short page carries no truncation claim.
    short = build(_ConsoleClient(run_rows=[RUN_ROW])).get("/v1/runs", headers=AUTH)
    assert TRUNCATED_HEADER not in short.headers
