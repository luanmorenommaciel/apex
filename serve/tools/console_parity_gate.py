"""Live gate: the console's rows, the same through both doors.

Every statement the console issues is run TWICE against a real ClickHouse — as
the browser does, over the HTTP interface as the read-only user, and through
the Apex API — and the two must return the same rows. A status code cannot
satisfy this: status codes are what passed while three routes returned the
wrong projection.

It also proves the behaviours only a live store can show, because the fill,
the type check and the ordering are ClickHouse's and no fake has them:

1. an unindexed run reports -1 / -1 / '' / 'unknown', not the defaults a
   missed LEFT JOIN is filled with;
2. every statement executes as a ``readonly = 1`` user — no setting is needed,
   and ``if()`` found a common type for every branch;
3. findings come back ``confidence_score DESC`` when that differs from ts ASC,
   and ``finding_id ASC`` where two of them tie on confidence_score — on EACH
   door, because two doors wrong in the same way still agree with each other;
4. an execution re-planned three times is ONE transition, carrying the last;
5. every timestamp leaves the API in the wire format the console declares.

It seeds its own disposable rows, under job ids carrying a random suffix, and
removes exactly those rows — the same arrangement as ``read_only_gate.py``.
Those writes are the FIXTURE's. Every code path under test, on both doors,
issues SELECTs only.

    uv run python tools/console_parity_gate.py
    uv run python tools/console_parity_gate.py --job-id <id>    # seeds nothing
    uv run python tools/console_parity_gate.py --api-url http://127.0.0.1:8099 \\
        --api-token <token>                                     # a running API

With ``--job-id`` the gate writes nothing and compares the two doors on a run
the store already holds. A behaviour that run's data cannot exercise prints
NOT EXERCISED and does not count as passed.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import pathlib
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

FRONT_DATA = pathlib.Path(__file__).resolve().parents[2] / "front" / "src" / "data"
QUERIES_TS = FRONT_DATA / "queries.ts"
TIMESTAMP_TS = FRONT_DATA / "timestamp.ts"

# clickhouse.ts converts by DECLARED type, because ClickHouse quotes 64-bit
# integers in JSON and apex_ro may not switch that off. Same pattern, so the
# gate sees the rows the console's screens see.
_NUMERIC = re.compile(r"^(Nullable\()?(U?Int(8|16|32|64|128|256)|Float(32|64)|Decimal)")

PASS, FAIL, SKIP = "PASS", "FAIL", "NOT EXERCISED"


# --------------------------------------------------------------------------
# The console's own statements, read from its source
# --------------------------------------------------------------------------
def console_statements(source: str) -> dict[str, str]:
    """Every exported statement in queries.ts, as the browser sends it.

    Read, not restated: a copy kept here would compare the API against the
    gate's idea of the console rather than against the console.
    """

    def unescape(text: str) -> str:
        return text.replace("\\`", "`")

    statements = {
        match.group(1): unescape(match.group(2))
        for match in re.finditer(r"export const (\w+) = `(.*?)`;", source, re.S)
    }
    rollup = re.search(
        r"const runRollup = \(where: string, tail: string\) => `(.*?)\n`;", source, re.S
    )
    if rollup:
        body = unescape(rollup.group(1))
        for match in re.finditer(
            r'export const (\w+) = runRollup\(\s*"([^"]*)",\s*"([^"]*)"\s*\);', source
        ):
            statements[match.group(1)] = body.replace("${where}", match.group(2)).replace(
                "${tail}", match.group(3)
            )
    return statements


def wire_pattern(source: str) -> re.Pattern[str]:
    literal = re.search(r"export const WIRE_TIMESTAMP = /(.+)/;", source)
    if literal is None:
        raise SystemExit("could not read WIRE_TIMESTAMP from front/src/data/timestamp.ts")
    return re.compile(literal.group(1))


def coerce_numerics(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """What clickhouse.ts does to a JSON response before a screen sees it."""
    numeric = [m["name"] for m in payload.get("meta") or [] if _NUMERIC.match(m["type"])]
    rows = []
    for row in payload.get("data") or []:
        out = dict(row)
        for column in numeric:
            value = out.get(column)
            if isinstance(value, str) and value != "":
                out[column] = float(value) if re.search(r"[.eE]|nan|inf", value) else int(value)
        rows.append(out)
    return rows


# --------------------------------------------------------------------------
# Comparing rows
# --------------------------------------------------------------------------
def difference(browser: Any, api: Any, at: str = "") -> str | None:
    """The first place two payloads differ, or None when they are the same.

    Floats are compared within Float32's precision: the browser reads
    ClickHouse's shortest decimal for a Float32 (0.9) and the driver widens the
    same value to a double (0.8999999761581421). That is one number.
    """
    if isinstance(browser, float) or isinstance(api, float):
        both_numbers = all(
            isinstance(v, (int, float)) and not isinstance(v, bool) for v in (browser, api)
        )
        if both_numbers and math.isclose(browser, api, rel_tol=1e-6, abs_tol=1e-9):
            return None
        return f"{at or 'value'}: browser {browser!r} != api {api!r}"
    if isinstance(browser, dict) and isinstance(api, dict):
        if browser.keys() != api.keys():
            only_browser = sorted(browser.keys() - api.keys())
            only_api = sorted(api.keys() - browser.keys())
            return f"{at or 'row'}: columns differ — browser only {only_browser}, api only {only_api}"
        for key in browser:
            found = difference(browser[key], api[key], f"{at}.{key}" if at else key)
            if found:
                return found
        return None
    if isinstance(browser, list) and isinstance(api, list):
        if len(browser) != len(api):
            return f"{at or 'rows'}: browser returned {len(browser)}, api returned {len(api)}"
        for index, (left, right) in enumerate(zip(browser, api)):
            found = difference(left, right, f"{at}[{index}]")
            if found:
                return found
        return None
    if browser != api:
        return f"{at or 'value'}: browser {browser!r} != api {api!r}"
    return None


def keyed(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    """Rows in a stable order, for listings whose ORDER BY can tie."""
    return sorted(rows, key=lambda row: str(row.get(key)))


# --------------------------------------------------------------------------
# The two doors
# --------------------------------------------------------------------------
@dataclass
class Store:
    host: str
    port: int
    database: str
    admin_user: str
    admin_password: str
    console_user: str
    console_password: str
    secure: bool = False

    @property
    def http_url(self) -> str:
        return f"{'https' if self.secure else 'http'}://{self.host}:{self.port}"


class DoorError(RuntimeError):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(f"{status}: {detail}")
        self.status = status
        self.detail = detail


def browser_query(store: Store, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """One statement, sent the way clickhouse.ts sends it."""
    query = {
        "database": store.database,
        "default_format": "JSON",
        "readonly": "1",
        **{f"param_{name}": str(value) for name, value in params.items()},
    }
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "X-ClickHouse-User": store.console_user,
    }
    if store.console_password:
        headers["X-ClickHouse-Key"] = store.console_password
    request = urllib.request.Request(
        f"{store.http_url}/?{urllib.parse.urlencode(query)}",
        data=sql.encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return coerce_numerics(json.load(response))
    except urllib.error.HTTPError as exc:
        raise DoorError(exc.code, exc.read().decode("utf-8", "replace")[:300]) from None


async def _asgi_get(app: Any, path: str, headers: dict[str, str]) -> tuple[int, bytes]:
    """GET against an ASGI app in-process, with nothing but the standard library."""
    raw_path, _, query = path.partition("?")
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": urllib.parse.unquote(raw_path),
        "raw_path": raw_path.encode(),
        "query_string": query.encode(),
        "root_path": "",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "server": ("console-parity-gate", 80),
        "client": ("console-parity-gate", 0),
    }
    delivered = False
    finished = asyncio.Event()

    async def receive() -> dict[str, Any]:
        nonlocal delivered
        if not delivered:
            delivered = True
            return {"type": "http.request", "body": b"", "more_body": False}
        await finished.wait()
        return {"type": "http.disconnect"}

    status = 0
    body = bytearray()

    async def send(message: dict[str, Any]) -> None:
        nonlocal status
        if message["type"] == "http.response.start":
            status = message["status"]
        elif message["type"] == "http.response.body":
            body.extend(message.get("body", b""))
            if not message.get("more_body"):
                finished.set()

    await app(scope, receive, send)
    finished.set()
    return status, bytes(body)


@dataclass
class Api:
    """The API door: in-process by default, or a running service by url."""

    get: Callable[[str], tuple[int, Any]]
    label: str


def in_process_api(store: Store) -> Api:
    import clickhouse_connect

    from apex_api.app import create_app
    from apex_api.config import Settings
    from apex_mcp.ch import ReadStore

    client = clickhouse_connect.get_client(
        host=store.host, port=store.port, username=store.admin_user,
        password=store.admin_password, database=store.database, secure=store.secure,
    )
    token = secrets.token_urlsafe(24)
    app = create_app(store=ReadStore(client, database=store.database), settings=Settings(tokens=frozenset({token})))

    def get(path: str) -> tuple[int, Any]:
        status, body = asyncio.run(_asgi_get(app, path, {"authorization": f"Bearer {token}"}))
        return status, (json.loads(body) if body else None)

    return Api(get=get, label="in-process create_app() over a real ReadStore")


def remote_api(url: str, token: str) -> Api:
    base = url.rstrip("/")

    def get(path: str) -> tuple[int, Any]:
        request = urllib.request.Request(
            f"{base}{path}", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            try:
                return exc.code, json.loads(raw)
            except ValueError:
                return exc.code, raw[:300]

    return Api(get=get, label=f"running service at {base}")


# --------------------------------------------------------------------------
# Disposable fixture rows
# --------------------------------------------------------------------------
@dataclass
class Fixture:
    run: str
    indexed: str
    baseline: str
    unindexed: str
    fingerprint: str
    other_fingerprint: str
    finding_high: str
    finding_low: str
    finding_tie_first: str
    finding_tie_second: str
    job_ids: list[str] = field(default_factory=list)


def new_fixture() -> Fixture:
    run = uuid.uuid4().hex[:8]
    digest = lambda text: hashlib.sha256(text.encode()).hexdigest()  # noqa: E731
    fixture = Fixture(
        run=run,
        indexed=f"parity-gate-indexed-{run}",
        baseline=f"parity-gate-baseline-{run}",
        unindexed=f"parity-gate-unindexed-{run}",
        fingerprint=digest(f"parity-gate-shape-{run}"),
        other_fingerprint=digest(f"parity-gate-other-{run}"),
        finding_high=f"parity-gate-hi-{run}",
        finding_low=f"parity-gate-lo-{run}",
        # Same run suffix, so -a- sorts before -b- whatever the suffix is.
        finding_tie_first=f"parity-gate-tie-a-{run}",
        finding_tie_second=f"parity-gate-tie-b-{run}",
    )
    fixture.job_ids = [fixture.indexed, fixture.baseline, fixture.unindexed]
    return fixture


def seed(client: Any, fx: Fixture) -> None:
    """Rows that exercise all five live-only behaviours. Recent, because the
    contract tables carry a 90-day TTL on ts."""
    # .123 so a millisecond survives both doors; one row at .000 so the fixed
    # width is exercised too — isoformat() wrote no fraction at all for that.
    base = datetime.now(timezone.utc).replace(microsecond=123000) - timedelta(hours=2)
    whole = base.replace(microsecond=0)

    def event(job: str, stage: int, attempt: int, ts: datetime, fingerprint: str, p99: int = 400) -> list[Any]:
        return [
            job, f"app-{job}", "parity-gate", stage, attempt, ts,
            5_000_000_000, 1_000_000, 0, 0, 120, 9_000_000_000, 0, 0, 50,
            100, p99, fingerprint, "SortMergeJoin Inner", {},
        ]

    client.insert(
        "spark_events",
        [
            event(fx.indexed, 1, 0, base, fx.fingerprint),
            event(fx.indexed, 2, 0, base + timedelta(seconds=30), fx.fingerprint, p99=900),
            # A retry of stage 2: the latest attempt is the row a screen must see.
            event(fx.indexed, 2, 1, base + timedelta(seconds=90), fx.fingerprint, p99=450),
            event(fx.baseline, 1, 0, whole - timedelta(hours=1), fx.fingerprint),
            event(fx.unindexed, 1, 0, base + timedelta(minutes=10), fx.other_fingerprint),
        ],
        column_names=[
            "job_id", "app_id", "app_name", "stage_id", "stage_attempt", "ts",
            "shuffle_read_bytes", "shuffle_write_bytes", "spill_disk_bytes",
            "spill_mem_bytes", "gc_time_ms", "input_bytes", "output_bytes",
            "peak_execution_mem_bytes", "task_count", "task_duration_p50_ms",
            "task_duration_p99_ms", "plan_fingerprint", "plan_json", "attributes",
        ],
    )
    # The LOW-confidence finding is the OLDER one, so confidence_score DESC and
    # ts ASC disagree about which comes first.
    #
    # The two TIE findings share confidence_score AND ts AND severity, so
    # neither the score nor the table's ORDER BY (job_id, severity, ts) can
    # order them: only finding_id ASC can. They are inserted in the OPPOSITE
    # order, -b- before -a-, so insertion order is not what puts them right
    # when a statement has lost its tie-break. 0.5 is exact in Float32.
    tied = base + timedelta(minutes=3)
    findings = [
        [fx.finding_low, fx.indexed, f"app-{fx.indexed}", 1, "SPILL", "warning",
         "spill on stage 1", "", "slower", "raise memory", "LOW", 0.2, "memory_watcher", base],
        [fx.finding_high, fx.indexed, f"app-{fx.indexed}", 2, "SKEW_ON_JOIN", "critical",
         "p99/p50 = 9x", "customer_id=7", "slow", "enable AQE skew join", "HIGH", 0.9,
         "skew_watcher", base + timedelta(minutes=5)],
        [fx.finding_tie_second, fx.indexed, f"app-{fx.indexed}", 1, "BAD_SHUFFLE", "warning",
         "tied b", "", "slower", "coalesce partitions", "MEDIUM", 0.5, "correlation", tied],
        [fx.finding_tie_first, fx.indexed, f"app-{fx.indexed}", 1, "BAD_SHUFFLE", "warning",
         "tied a", "", "slower", "coalesce partitions", "MEDIUM", 0.5, "correlation", tied],
    ]
    client.insert(
        "findings",
        findings,
        column_names=[
            "finding_id", "job_id", "app_id", "stage_id", "type", "severity", "evidence",
            "hot_key", "impact", "fix", "confidence", "confidence_score", "detected_by", "ts",
        ],
    )
    # Execution 1 re-planned three times; execution 2 once.
    client.insert(
        "plan_transitions",
        [
            [fx.indexed, 1, 0, "join_switch", "SMJ to BHJ", "SortMergeJoin", "BroadcastHashJoin", "HIGH", base],
            [fx.indexed, 1, 1, "skew_split", "split x2", "1 skewed", "2 skewed", "HIGH", base + timedelta(seconds=5)],
            [fx.indexed, 1, 2, "skew_split", "split x4", "2 skewed", "4 skewed", "BEST_EFFORT", base + timedelta(seconds=9)],
            [fx.indexed, 2, 0, "coalesce", "coalesced", "200 partitions", "40 partitions", "HIGH", base + timedelta(seconds=20)],
        ],
        column_names=[
            "job_id", "execution_id", "update_seq", "transition_type", "detail",
            "before", "after", "confidence", "ts",
        ],
    )
    client.insert(
        "job_conf",
        [[fx.indexed, f"app-{fx.indexed}", "parity-gate",
          {"spark.executor.cores": "4", "spark.executor.instances": "8",
           "spark.sql.shuffle.partitions": "200"}, base]],
        column_names=["job_id", "app_id", "app_name", "conf", "ts"],
    )
    outcome_columns = [
        "job_id", "app_id", "app_name", "plan_fingerprint", "conf_shuffle_partitions",
        "conf_executor_instances", "conf_executor_cores", "conf_executor_memory_mb",
        "config_source", "stage_count", "task_count", "wall_clock_ms", "task_time_ms",
        "finding_count", "worst_severity", "outcome_source", "observed_at", "indexed_at",
    ]
    client.insert(
        "run_outcomes",
        [
            [fx.indexed, f"app-{fx.indexed}", "parity-gate", fx.fingerprint, 200, 8, 4, 8192,
             "observed", 2, 100, 90_000, 91_000,
             sum(1 for row in findings if row[1] == fx.indexed), "critical", "apex",
             base + timedelta(seconds=90), base + timedelta(minutes=20)],
            [fx.baseline, f"app-{fx.baseline}", "parity-gate", fx.fingerprint, 800, 8, 4, 8192,
             "observed", 1, 50, 0, 40_000, 0, "", "apex",
             whole - timedelta(hours=1), base + timedelta(minutes=20)],
        ],
        column_names=outcome_columns,
    )
    client.insert(
        "plan_memory",
        [[fx.fingerprint, "struct-v1", "structural", [1.0, 0.0, 0.0, 0.0], 4, {}, 12, 4, 1, 1,
          2, 2, 0, 34, "== Physical Plan ==\nSortMergeJoin Inner", whole - timedelta(hours=1),
          base + timedelta(seconds=90), base + timedelta(minutes=20)]],
        column_names=[
            "plan_fingerprint", "encoder_version", "embedding_kind", "embedding", "dim",
            "op_counts", "node_count", "max_depth", "join_count", "agg_count",
            "exchange_count", "scan_count", "has_udf", "plan_chars", "sample_plan_json",
            "first_seen", "last_seen", "indexed_at",
        ],
    )
    client.insert(
        "fix_verifications",
        [[f"parity-gate-v-{fx.run}", fx.finding_high, fx.indexed, f"app-{fx.indexed}",
          '{"spark.sql.shuffle.partitions":"800"}', "replayed", "partition_sizing",
          -11.0, -15.0, -7.0, -12.0, 1000.0, 880.0, 5.0, 5, "dev:skew_join", 0.8, 1,
          "allow", "HIGH", 0.9, "replayed 5x per arm", base + timedelta(minutes=30)]],
        column_names=[
            "verification_id", "finding_id", "job_id", "app_id", "proposed_config", "method",
            "predictor", "predicted_delta_pct", "predicted_low_pct", "predicted_high_pct",
            "measured_delta_pct", "baseline_ms", "treatment_ms", "noise_floor_pct",
            "replay_reps", "bench", "shape_fidelity", "safe", "safety_verdict", "confidence",
            "confidence_score", "evidence", "verified_at",
        ],
    )


def remove(client: Any, fx: Fixture) -> None:
    """The gate removes only its own rows — by its own ids, never by a pattern.

    Tables are named unqualified, like every statement in ch.py: the session
    database, opened from CLICKHOUSE_DATABASE, is the only selector.
    """
    jobs = ", ".join(f"'{job}'" for job in fx.job_ids)
    wait = {"mutations_sync": 1}
    tables = ["spark_events", "findings", "plan_transitions", "job_conf",
              "run_outcomes", "fix_verifications"]
    # Deleting the source rows does not retract an incremental MV's target.
    # The rollup is optional on older stores; a query error is not absence.
    if client.query("EXISTS TABLE spark_jobs_1m").result_rows[0][0]:
        tables.append("spark_jobs_1m")
    for table in tables:
        client.command(f"ALTER TABLE {table} DELETE WHERE job_id IN ({jobs})", settings=wait)
    client.command(
        "ALTER TABLE plan_memory DELETE WHERE plan_fingerprint = "
        f"toFixedString('{fx.fingerprint}', 64)",
        settings=wait,
    )


# --------------------------------------------------------------------------
# The checks
# --------------------------------------------------------------------------
@dataclass
class Report:
    lines: list[tuple[str, str, str]] = field(default_factory=list)

    def add(self, verdict: str, name: str, detail: str) -> None:
        self.lines.append((verdict, name, detail))
        print(f"  {verdict:<14} {name:<34} {detail}", flush=True)

    @property
    def failed(self) -> bool:
        return any(verdict == FAIL for verdict, _, _ in self.lines)

    def count(self, verdict: str) -> int:
        return sum(1 for seen, _, _ in self.lines if seen == verdict)


def compare_doors(
    report: Report, store: Store, api: Api, statements: dict[str, str],
    job: str, fingerprint: str, finding: str,
    *, only: set[str] | None = None, suffix: str = "",
    browser_seen: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Each console statement through both doors. Returns the API's payloads.

    ``only`` narrows the run to the named checks; ``suffix`` tells two runs of
    the same check apart in the report. ``browser_seen``, when given, receives
    the browser door's rows in the order that door returned them: parity alone
    cannot see two doors that are wrong the same way.
    """
    from apex_api.wire import wire

    enc = urllib.parse.quote
    plan: list[tuple[str, str, dict[str, Any], str, str | None]] = [
        # name, console statement, its parameters, the API path, tie-break key
        ("runs", "RUN_LIST", {"limit": 50}, "/v1/runs?limit=50", "job_id"),
        ("run", "RUN_ONE", {"job": job}, f"/v1/runs/{enc(job)}", None),
        ("stages", "LATEST_STAGES", {"job": job}, f"/v1/runs/{enc(job)}/stages", None),
        ("conf", "JOB_CONF", {"job": job}, f"/v1/runs/{enc(job)}/conf", None),
        ("findings", "FINDINGS", {"job": job}, f"/v1/runs/{enc(job)}/findings", None),
        ("transitions", "PLAN_TRANSITIONS", {"job": job}, f"/v1/runs/{enc(job)}/transitions", None),
        ("baseline-candidates", "RUNS_SHARING_SHAPE", {"job": job},
         f"/v1/runs/{enc(job)}/baseline-candidates", "job_id"),
        ("plans", "PLAN_SHAPES", {}, "/v1/plans", "plan_fingerprint"),
    ]
    if fingerprint:
        plan += [
            ("shape runs", "SHAPE_RUNS", {"fingerprint": fingerprint},
             f"/v1/plans/{enc(fingerprint)}/runs", None),
            ("plan sample", "PLAN_SAMPLE", {"fingerprint": fingerprint},
             f"/v1/plans/{enc(fingerprint)}/sample", None),
        ]
    if finding:
        plan.append(("verification", "FIX_VERIFICATIONS", {"finding": finding},
                     f"/v1/findings/{enc(finding)}/verification", None))

    seen: dict[str, Any] = {}
    for name, statement, params, path, tie_key in plan:
        if only is not None and name not in only:
            continue
        label = f"{name}{suffix}  [{statement}]"
        sql = statements.get(statement)
        if sql is None:
            report.add(FAIL, label, "the console no longer exports this statement")
            continue
        try:
            browser = browser_query(store, sql, params)
        except DoorError as exc:
            browser_error: DoorError | None = exc
            browser = []
        else:
            browser_error = None
        status, payload = api.get(path)

        if browser_error is not None or status >= 400:
            # Both doors refusing for the same reason is agreement, not a pass.
            absent = browser_error is not None and "UNKNOWN_TABLE" in browser_error.detail
            unavailable = status == 502 and "memory_unavailable" in json.dumps(payload)
            if absent and unavailable:
                report.add(SKIP, label, "the v0.3 memory tables are absent on this store")
            else:
                report.add(FAIL, label, f"browser: {browser_error or 'ok'} · api: {status} {str(payload)[:160]}")
            continue

        # The browser's rows as a screen receives them: numerics coerced by
        # clickhouse.ts, timestamps brought to the wire format by the repository.
        browser = wire(browser)
        if browser_seen is not None:
            browser_seen[name] = browser
        if name == "run":
            expected: Any = browser[0] if browser else None
        elif name == "plan sample":
            expected = (browser[0].get("sample_plan_json") or None) if browser else None
            payload = payload or None
        elif name == "verification":
            expected = browser[0] if browser else None
        else:
            expected = keyed(browser, tie_key) if tie_key else browser
            payload = keyed(payload, tie_key) if tie_key else payload

        found = difference(expected, payload)
        size = f"{len(payload)} rows" if isinstance(payload, list) else ("1 row" if payload else "no row")
        report.add(FAIL if found else PASS, label, found or f"same through both doors · {size}")
        seen[name] = payload
    return seen


TIE_BREAK = "findings tie-break by finding_id"


def _is_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(value)


def tie_break(rows: Any) -> tuple[str, str]:
    """Findings where confidence_score cannot decide: ``finding_id ASC``.

    Separate from the primary order check, which is exercised by scores that
    DIFFER and cannot see a tie. Exercised only when two findings share a
    confidence_score — a score of 0, the column's default, ties like any other
    — and then the whole list must be ``confidence_score DESC, finding_id
    ASC``. A row this cannot read is a FAIL that names it, never an exception
    and never a guess: a missing score is not taken to be 0, and a value of a
    type the console does not declare is not compared. Python orders str by
    code point, which for UTF-8 is ClickHouse's byte order on a String.
    """
    if rows is None:
        rows = []
    if not isinstance(rows, list):
        return FAIL, f"findings came back as {type(rows).__name__}, not a list of rows"
    if len(rows) < 2:
        return SKIP, f"{len(rows)} finding(s); needs two findings tied on confidence_score"
    unreadable = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            unreadable.append(f"[{index}] is {type(row).__name__}, not a row")
            continue
        if "finding_id" not in row:
            unreadable.append(f"[{index}] carries no finding_id")
        elif not isinstance(row["finding_id"], str):
            unreadable.append(f"[{index}].finding_id is {type(row['finding_id']).__name__} "
                              f"{row['finding_id']!r}, not a String")
        if "confidence_score" not in row:
            unreadable.append(f"[{index}] carries no confidence_score")
        elif not _is_score(row["confidence_score"]):
            unreadable.append(f"[{index}].confidence_score is {type(row['confidence_score']).__name__} "
                              f"{row['confidence_score']!r}, not a number this can order")
    if unreadable:
        return FAIL, "no tie-break can be established: " + "; ".join(unreadable[:4])
    scores = [row["confidence_score"] for row in rows]
    tied = sorted({score for score in scores if scores.count(score) > 1}, reverse=True)
    if not tied:
        return SKIP, (f"{len(rows)} findings, no two share a confidence_score; "
                      "needs two findings tied on confidence_score")
    returned = [row["finding_id"] for row in rows]
    canonical = [row["finding_id"] for row in
                 sorted(rows, key=lambda row: (-row["confidence_score"], row["finding_id"]))]
    groups = "; ".join(f"{score}: {[r['finding_id'] for r in rows if r['confidence_score'] == score]}"
                       for score in tied)
    if returned == canonical:
        return PASS, f"tied on confidence_score — {groups} — each tie in finding_id ASC"
    at = next(i for i, (got, want) in enumerate(zip(returned, canonical)) if got != want)
    return FAIL, (f"[{at}] is {returned[at]!r} where confidence_score DESC, finding_id ASC "
                  f"puts {canonical[at]!r}; returned {returned}")


def live_only(
    report: Report, store: Store, api: Api, statements: dict[str, str],
    pattern: re.Pattern[str], seen: dict[str, Any], *, job: str, unindexed_job: str | None,
    browser_seen: dict[str, Any] | None = None, seeded_tie: bool = False,
) -> None:
    """What only a live store can show. Each check says what it proves.

    ``browser_seen`` adds the browser door's rows to the checks that judge an
    order. ``seeded_tie`` says the fixture wrote tied findings, so a tie-break
    check with no tie to see is a missing row, not a run without one.
    """
    from apex_api.wire import TIMESTAMP_FIELDS

    def count(sql: str, **params: Any) -> int:
        rows = browser_query(store, sql, params)
        return int(next(iter(rows[0].values()))) if rows else 0

    # 1 · the sentinel ------------------------------------------------------
    candidate = unindexed_job or job
    outcomes = count("SELECT count() FROM run_outcomes WHERE job_id = {job:String}", job=candidate)
    if outcomes:
        report.add(SKIP, "unindexed run reads as not indexed",
                   f"{candidate} has {outcomes} run_outcomes row(s); needs a run the memory lane has not indexed")
    else:
        want = {"task_time_ms": -1, "shaped_stage_count": -1, "plan_fingerprint": "",
                "config_source": "unknown", "shape_count": 0}
        status, via_api = api.get(f"/v1/runs/{urllib.parse.quote(candidate)}")
        via_browser = browser_query(store, statements["RUN_ONE"], {"job": candidate})
        problems = []
        for door, row in (("api", via_api if status == 200 else None),
                          ("browser", via_browser[0] if via_browser else None)):
            if row is None:
                problems.append(f"{door}: no row for {candidate}")
                continue
            for column, value in want.items():
                if row.get(column) != value:
                    problems.append(f"{door}.{column} = {row.get(column)!r}, not {value!r}")
        report.add(FAIL if problems else PASS, "unindexed run reads as not indexed",
                   "; ".join(problems) or "-1 / -1 / '' / 'unknown' on both doors — a missed join is not a measured zero")

    # 2 · readonly ----------------------------------------------------------
    level = count("SELECT toUInt8(getSetting('readonly'))")
    report.add(PASS if level >= 1 else FAIL, "statements run as a read-only user",
               f"{store.console_user} has readonly = {level}"
               + ("" if level >= 1 else " — every browser-door result above was NOT proven under readonly"))

    # 3 · findings order ----------------------------------------------------
    findings = seen.get("findings") or []
    incomplete = [row.get("finding_id") for row in findings
                  if "ts" not in row or "confidence_score" not in row]
    scores = [row.get("confidence_score") for row in findings]
    unorderable = [f"{row.get('finding_id')}: {type(row['confidence_score']).__name__} "
                   f"{row['confidence_score']!r}" for row in findings
                   if "confidence_score" in row and not _is_score(row["confidence_score"])]
    invalid_times = [f"{row.get('finding_id')}: {type(row['ts']).__name__} {row['ts']!r}"
                     for row in findings if "ts" in row
                     and not (isinstance(row["ts"], str) and pattern.fullmatch(row["ts"]))]
    by_time = [] if incomplete or invalid_times else sorted(findings, key=lambda row: row["ts"])
    if incomplete:
        # Reported, never raised: a route that dropped the column is the very
        # defect this gate exists to name, and a traceback names nothing.
        report.add(FAIL, "findings ordered by confidence_score",
                   f"no order can be established: {incomplete} carry no ts or no confidence_score")
    elif invalid_times:
        # A malformed projection must be named before sorting mixed types;
        # no guessed or converted timestamp can establish the ts order.
        report.add(FAIL, "findings ordered by confidence_score",
                   f"no order can be established: {invalid_times} not in the timestamp wire format")
    elif len(findings) < 2 or by_time == findings:
        report.add(SKIP, "findings ordered by confidence_score",
                   f"{len(findings)} finding(s) whose confidence order equals their ts order; "
                   "needs two findings where the older one is the less confident")
    elif unorderable:
        # Named, never converted: '0.5' beside 0.5 is a projection defect, and
        # sorted() over the two raised before any check could report it.
        report.add(FAIL, "findings ordered by confidence_score",
                   f"no order can be established: {unorderable} not a number this can order")
    else:
        ordered = scores == sorted(scores, reverse=True)
        report.add(PASS if ordered else FAIL, "findings ordered by confidence_score",
                   f"scores {scores} — first is {findings[0].get('finding_id')}, which is not the oldest"
                   if ordered else f"scores {scores} are not descending")

    # 3b · findings tie-break, on each door ---------------------------------
    doors = [("api", seen.get("findings"))]
    if browser_seen is not None:
        doors.append(("browser", browser_seen.get("findings")))
    for door, rows in doors:
        verdict, detail = tie_break(rows)
        if verdict == SKIP and seeded_tie:
            verdict, detail = FAIL, f"the fixture seeded two tied findings; this door returned none — {detail}"
        report.add(verdict, f"{TIE_BREAK} · {door}", detail)

    # 4 · transitions collapse ----------------------------------------------
    raw = count("SELECT count() FROM plan_transitions WHERE job_id = {job:String}", job=job)
    executions = count("SELECT uniqExact(execution_id) FROM plan_transitions WHERE job_id = {job:String}", job=job)
    transitions = seen.get("transitions") or []
    if raw == executions:
        report.add(SKIP, "one transition per execution",
                   f"{raw} transition row(s) over {executions} execution(s): no execution was re-planned twice")
    else:
        latest = {
            row["execution_id"]: row for row in browser_query(
                store,
                "SELECT execution_id, max(update_seq) AS update_seq FROM plan_transitions "
                "WHERE job_id = {job:String} GROUP BY execution_id", {"job": job})
        }
        wrong = [row.get("execution_id") for row in transitions
                 if row.get("update_seq") != latest.get(row.get("execution_id"), {}).get("update_seq")]
        ok = len(transitions) == executions and not wrong
        report.add(PASS if ok else FAIL, "one transition per execution",
                   f"{raw} rows stored, {len(transitions)} returned for {executions} executions, each at its last update_seq"
                   if ok else f"{len(transitions)} returned for {executions} executions; not at last update_seq: {wrong}")

    # 5 · the wire format ---------------------------------------------------
    checked, bad = 0, []
    for name, payload in seen.items():
        for row in payload if isinstance(payload, list) else [payload]:
            if not isinstance(row, dict):
                continue
            for column in TIMESTAMP_FIELDS & row.keys():
                checked += 1
                if not (isinstance(row[column], str) and pattern.fullmatch(row[column])):
                    bad.append(f"{name}.{column} = {row[column]!r}")
    if not checked:
        report.add(SKIP, "timestamps in the wire format", "no route returned a timestamp")
    else:
        report.add(FAIL if bad else PASS, "timestamps in the wire format",
                   "; ".join(bad[:4]) or f"{checked} timestamps match {pattern.pattern}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--job-id", help="compare on a run the store already holds; seeds nothing")
    parser.add_argument("--api-url", help="check a running API instead of an in-process one")
    parser.add_argument("--api-token", default=os.getenv("APEX_API_TOKEN", ""))
    args = parser.parse_args(argv)
    if args.api_url and not args.api_token:
        parser.error("--api-url needs --api-token (or APEX_API_TOKEN)")

    store = Store(
        host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
        admin_user=os.getenv("CLICKHOUSE_USER", "apex"),
        admin_password=os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev"),
        console_user=os.getenv("APEX_CONSOLE_USER", "apex_ro"),
        console_password=os.getenv("APEX_CONSOLE_PASSWORD", ""),
        secure=os.getenv("CLICKHOUSE_SECURE", "").lower() in {"1", "true", "yes"},
    )
    statements = console_statements(QUERIES_TS.read_text())
    pattern = wire_pattern(TIMESTAMP_TS.read_text())
    api = remote_api(args.api_url, args.api_token) if args.api_url else in_process_api(store)
    report = Report()

    print(f"store    {store.http_url}  database {store.database}")
    print(f"browser  ClickHouse HTTP as {store.console_user}, the way front/src/data/clickhouse.ts sends it")
    print(f"api      {api.label}")

    fixture: Fixture | None = None
    admin = None
    try:
        if args.job_id:
            print(f"mode     --job-id {args.job_id} · nothing is written\n")
            job, unindexed = args.job_id, None
            status, run = api.get(f"/v1/runs/{urllib.parse.quote(job)}")
            if status != 200 or not run:
                print(f"  {FAIL:<14} the API has no run {job!r} ({status})")
                return 1
            fingerprint = run.get("plan_fingerprint") or ""
            _, found = api.get(f"/v1/runs/{urllib.parse.quote(job)}/findings")
            finding = found[0]["finding_id"] if isinstance(found, list) and found else ""
        else:
            import clickhouse_connect

            fixture = new_fixture()
            print(f"mode     seeded · run {fixture.run} · its rows are removed afterwards\n")
            admin = clickhouse_connect.get_client(
                host=store.host, port=store.port, username=store.admin_user,
                password=store.admin_password, database=store.database, secure=store.secure,
            )
            seed(admin, fixture)
            job, unindexed = fixture.indexed, fixture.unindexed
            fingerprint, finding = fixture.fingerprint, fixture.finding_high

        browser_seen: dict[str, Any] = {}
        seen = compare_doors(report, store, api, statements, job, fingerprint, finding,
                             browser_seen=browser_seen)
        if unindexed:
            # The unindexed run through both doors too: parity on the miss itself.
            compare_doors(report, store, api, statements, unindexed, "", "",
                          only={"run"}, suffix=" (unindexed)")
        print()
        live_only(report, store, api, statements, pattern, seen, job=job, unindexed_job=unindexed,
                  browser_seen=browser_seen, seeded_tie=fixture is not None)
    finally:
        if fixture is not None and admin is not None:
            remove(admin, fixture)

    verdict = "FAIL" if report.failed else "PASS"
    print(f"\n{report.count(PASS)} passed · {report.count(FAIL)} failed · {report.count(SKIP)} not exercised")
    if report.count(SKIP) and not report.failed:
        print("A check that was not exercised proved nothing. It is not a pass.")
    print(f"CONSOLE_PARITY_GATE={verdict}")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
