"""The resource tier: one route per Repository method, and the console's shapes."""

from __future__ import annotations

import pathlib
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings
from apex_api.wire import TIMESTAMP_FIELDS
from apex_api.routes.resources import (
    LIMIT_HEADER,
    RESOURCE_ROUTES,
    TRUNCATED_HEADER,
)
from apex_mcp import ch
from apex_mcp.ch import ReadStore
from tests.conftest import FakeClient, finding_row, reads, stage_row, transition_row
from tests.test_ch import _ConsoleClient

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}

FRONT_SRC = pathlib.Path(__file__).resolve().parents[2] / "front" / "src"
REPOSITORY_TS = FRONT_SRC / "data" / "repository.ts"
CONTRACT_TS = FRONT_SRC / "contract" / "types.ts"
TIMESTAMP_TS = FRONT_SRC / "data" / "timestamp.ts"

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


def test_stages_route_returns_the_console_projection():
    """Three screens call ratioOf on these timings; the MCP's names give NaN."""
    row = {
        "job_id": "j", "app_name": "nightly", "stage_id": 4, "stage_name": None,
        "stage_attempt": 0, "task_count": 50, "shuffle_read_bytes": 0,
        "shuffle_write_bytes": 0, "input_bytes": 0, "spill_mem_bytes": 0,
        "spill_disk_bytes": 0, "peak_execution_mem_bytes": 0, "gc_time_ms": 0,
        "task_duration_p50_ms": 20, "task_duration_p99_ms": 460,
        "plan_fingerprint": "a" * 64, "ts": "2026-09-20 10:00:00",
    }
    got = build(_ConsoleClient(run_rows=[row])).get("/v1/runs/j/stages", headers=AUTH).json()
    assert got, "the stages route returned nothing"
    for field in ("task_duration_p50_ms", "task_duration_p99_ms", "job_id", "stage_name", "ts"):
        assert field in got[0], f"the console reads {field} and the route omits it"
    # And the MCP's aliases must not leak through in their place.
    assert "p50_ms" not in got[0] and "p99_ms" not in got[0]


def test_findings_route_returns_the_console_projection():
    """VerifyScreen takes the first row as the highest-confidence finding."""
    rows = [
        {"finding_id": "f-hi", "confidence_score": 0.9, "ts": "2026-09-20 10:05:00"},
        {"finding_id": "f-lo", "confidence_score": 0.2, "ts": "2026-09-20 10:00:00"},
    ]
    client = _ConsoleClient(finding_rows=rows)
    got = build(client).get("/v1/runs/j/findings", headers=AUTH).json()
    assert [r["finding_id"] for r in got] == ["f-hi", "f-lo"]
    assert "ts" in got[0], "the console's FindingRow declares ts"
    sql = next(q for q, _ in client.calls if reads(q, "findings") and "shaped_stage_count" not in q)
    assert "ORDER BY confidence_score DESC" in sql and "ORDER BY ts" not in sql


def test_transitions_route_returns_the_console_projection():
    """One row per execution, at max(update_seq), with the run's fingerprint and ts."""
    # ts is a datetime, because that is what the driver hands back; it leaves
    # in the wire format like every other timestamp.
    rows = [{
        "job_id": "j", "execution_id": 1, "update_seq": 2, "transition_type": "skew_split",
        "detail": "AQEShuffleRead skewed x4", "before": "1 skewed", "after": "4 skewed",
        "confidence": "HIGH", "plan_fingerprint": "a" * 64,
        "ts": datetime(2026, 9, 20, 10, 0, 0, 123000),
    }]
    client = _ConsoleClient(transition_rows=rows)
    got = build(client).get("/v1/runs/j/transitions", headers=AUTH).json()
    assert got == [dict(rows[0], ts="2026-09-20T10:00:00.123")]
    sql = next(q for q, _ in client.calls if reads(q, "plan_transitions"))
    assert "GROUP BY t.job_id, t.execution_id" in sql
    for field in ("job_id", "plan_fingerprint", "ts"):
        assert f"AS {field}" in sql, f"the console reads {field} and the route omits it"


# -- projection parity -----------------------------------------------------
#
# Five times a console method was mapped onto a ReadStore method by name and
# served a projection the console does not read: runs, verifications, stages,
# findings, transitions. Each was fixed where it was found. This is the control
# for the CLASS: the field lists are read from the TypeScript, not restated
# here, and every one must be emitted by the final SELECT of the statement that
# serves it.

# Fields the console's own mapper supplies rather than the SQL, with the reason.
MAPPER_SUPPLIED = {
    # toFixVerification in repository.ts: no column stores the individual replay
    # durations, and the two literals are the console's own guarantee.
    "FixVerificationRow": {"replay_durations_ms", "requires_human_approval", "applied"},
}

CONSOLE_PROJECTIONS: dict[tuple[pathlib.Path, str], str] = {
    (CONTRACT_TS, "FindingRow"): ch._console_findings_sql(set(ch._FINDINGS_ADDITIVE)),
    (CONTRACT_TS, "PlanTransitionRow"): ch.CONSOLE_PLAN_TRANSITIONS_SQL,
    (CONTRACT_TS, "JobConfRow"): ch.JOB_CONF_SQL,
    (CONTRACT_TS, "FixVerificationRow"): ch.FIX_VERIFICATION_SQL,
    (REPOSITORY_TS, "RunRollupRow"): ch.RUN_ONE_SQL,
    (REPOSITORY_TS, "PlanShape"): ch.PLAN_SHAPES_SQL,
    (REPOSITORY_TS, "ShapeRun"): ch.SHAPE_RUNS_SQL,
    (REPOSITORY_TS, "BaselineCandidate"): ch.BASELINE_CANDIDATES_SQL,
}


def interface_fields(source_path: pathlib.Path, name: str) -> set[str]:
    """Field names of one `interface NAME { ... }`, comments stripped first."""
    source = source_path.read_text()
    body = source.split(f"interface {name} {{", 1)[1].split("\n}", 1)[0]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    return set(re.findall(r"\b(\w+)\??\s*:", body))


def projected_columns(sql: str) -> set[str]:
    """Column names the statement's FINAL SELECT emits.

    `expr AS name` aliases, plus bare (optionally qualified) columns. CTE
    SELECTs are indented in every statement here, so the last column-0 SELECT
    is the projection the client sees.
    """
    head = sql.rindex("\nSELECT")
    projection = sql[head + len("\nSELECT"): sql.index("\nFROM", head)]
    projection = re.sub(r"--[^\n]*", "", projection)
    names = set(re.findall(r"\bAS\s+(\w+)", projection))
    for piece in re.split(r"[,\n]", projection):
        bare = re.fullmatch(r"\s*(?:\w+\.)?(\w+)\s*", piece)
        if bare:
            names.add(bare.group(1))
    return names


def test_every_console_field_is_projected():
    for (source, name), sql in CONSOLE_PROJECTIONS.items():
        declared = interface_fields(source, name) - MAPPER_SUPPLIED.get(name, set())
        assert declared, f"could not read {name} from {source.name}"
        missing = declared - projected_columns(sql)
        assert missing == set(), f"{name}: the console reads {sorted(missing)} and the SQL does not project them"

    # The check discriminates: drop one column and it must notice.
    findings_sql = ch._console_findings_sql(set(ch._FINDINGS_ADDITIVE))
    assert "hot_key, ts\n" in findings_sql
    assert "ts" not in projected_columns(findings_sql.replace("hot_key, ts\n", "hot_key\n"))
    without_alias = ch.CONSOLE_PLAN_TRANSITIONS_SQL.replace("AS plan_fingerprint", "AS fp_out")
    assert "plan_fingerprint" not in projected_columns(without_alias)
    # And it is the MCP's own projection that fails it — the defect it is for.
    mcp_findings = projected_columns(ch._findings_sql(set(ch._FINDINGS_ADDITIVE)))
    assert "ts" in interface_fields(CONTRACT_TS, "FindingRow") - mcp_findings


# -- the wire format -------------------------------------------------------


def wire_pattern() -> re.Pattern[str]:
    """WIRE_TIMESTAMP, read from the console's own source.

    Not restated here: a pattern kept on both sides by hand is two patterns.
    """
    source = TIMESTAMP_TS.read_text()
    literal = re.search(r"export const WIRE_TIMESTAMP = /(.+)/;", source)
    assert literal, "could not read WIRE_TIMESTAMP from timestamp.ts"
    return re.compile(literal.group(1))


def declared_timestamps(source_path: pathlib.Path, name: str) -> set[str]:
    """The fields one interface declares as WireTimestamp."""
    source = source_path.read_text()
    body = source.split(f"interface {name} {{", 1)[1].split("\n}", 1)[0]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    return set(re.findall(r"\b(\w+)\??\s*:\s*WireTimestamp\b", body))


def test_every_timestamp_leaves_in_the_wire_format():
    pattern = wire_pattern()

    # The allow-list covers every field the console declares as a timestamp.
    declared: set[str] = set()
    for source, name in [*CONSOLE_PROJECTIONS, (CONTRACT_TS, "RunSummary")]:
        declared |= declared_timestamps(source, name)
    assert {"ts", "started_at", "observed_at", "first_run", "last_run"} <= declared, (
        f"the console's interfaces no longer declare their timestamps: {sorted(declared)}"
    )
    assert declared <= TIMESTAMP_FIELDS, (
        f"declared by the console, unknown to the API: {sorted(declared - TIMESTAMP_FIELDS)}"
    )

    paths = (
        "/v1/runs", "/v1/runs/j", "/v1/runs/j/stages", "/v1/runs/j/conf",
        "/v1/runs/j/findings", "/v1/runs/j/transitions",
        "/v1/runs/j/baseline-candidates", "/v1/plans", "/v1/plans/" + "a" * 64 + "/runs",
    )
    moment = datetime(2026, 9, 20, 10, 0, 0, 123000)
    arrivals = (
        moment,                                   # what the driver hands back
        moment.replace(microsecond=0),            # isoformat() wrote NO fraction here
        datetime(2026, 9, 20, 12, 0, 0, 123000, tzinfo=timezone(timedelta(hours=2))),
        "2026-09-20 10:00:00.123",                # text, the way ClickHouse's JSON writes it
    )
    for value in arrivals:
        row = {
            "job_id": "j", "started_at": value, "ts": value, "observed_at": value,
            "first_run": value, "last_run": value,
        }
        app = build(_ConsoleClient(
            run_rows=[row], conf_rows=[row], shape_rows=[row], candidate_rows=[row],
            finding_rows=[row], transition_rows=[row],
        ))
        for path in paths:
            body = app.get(path, headers=AUTH).json()
            seen = 0
            for got in body if isinstance(body, list) else [body]:
                for field in TIMESTAMP_FIELDS & set(got):
                    assert pattern.fullmatch(got[field]), f"{path} {field}={got[field]!r} from {value!r}"
                    seen += 1
            assert seen, f"{path} returned no timestamp to check"
