"""T-20261103-infra-skew-closed-form — sql/050 judges skew by CONTRACT.md rule 1.

Offline: no HAVING compares a ratio against the literals 5 or 4 in 005, verify.sh,
run.sh or the dashboard; verify.sh and run.sh substitute APEX_CLUSTER_SLOTS into the
marker line. Live (APEX_INFRA_LIVE=1): the successful-task population is preferred,
the closed form flags the skewed stage and clears the balanced one at a job_conf
width, an unknown width abstains, and verify.sh's own query builder flags seed-shaped
skew at 8 slots.
"""
from __future__ import annotations

import json
import re
import subprocess
import time

from _live import REPO, SQL_DIR, DisposableClickHouse, live_only, sql_files

SKEW_SQL = SQL_DIR / "050_skew.sql"
VERIFY = REPO / "infra" / "scripts" / "verify.sh"
RUN = REPO / "tests" / "e2e" / "run.sh"
DASHBOARD = REPO / "infra" / "dashboards" / "skew_dashboard.json"
MARKER = "WITH NULL AS operator_slots"
FIXED = re.compile(r"HAVING\s+\w+\s*>\s*[45]\b")


# -- offline ---------------------------------------------------------------------


def test_skew_sql_has_no_fixed_threshold():
    for path in (SKEW_SQL, VERIFY, RUN):
        live = "\n".join(l for l in path.read_text().splitlines() if not l.lstrip().startswith("#"))
        assert not FIXED.search(live), path.name
    board = DASHBOARD.read_text()
    assert not FIXED.search(board)
    assert "> 5" not in json.loads(board)["tiles"][0]["title"]
    assert "(n_tasks - 1) / (slots - 1)" in SKEW_SQL.read_text()


def test_skew_override_wired():
    sql = "\n".join(re.sub(r"--.*$", "", l) for l in SKEW_SQL.read_text().splitlines())
    assert sql.count(MARKER) == 1, "exactly one marker line"
    for path in (VERIFY, RUN):
        text = path.read_text()
        assert "APEX_CLUSTER_SLOTS" in text, path.name
        assert "AS operator_slots" in text, path.name
        assert "skew_query_a" in text, path.name
    assert "tail_bound = 1" in RUN.read_text()


def test_dashboard_tiles_mirror_005():
    sql = SKEW_SQL.read_text()
    def flat(block):
        block = "\n".join(re.sub(r"--.*$", "", l) for l in block.splitlines())
        return re.sub(r"\s+", " ", block).strip().rstrip(";")
    tiles = json.loads(DASHBOARD.read_text())["tiles"]
    assert tiles[0]["sql"] == flat(sql.split("-- (A)")[1].split("-- (B)")[0])
    assert tiles[4]["sql"] == flat(sql.split("-- (B)")[1])


# -- live ------------------------------------------------------------------------


def query_a(slots: str) -> str:
    """The exact text verify.sh sends: its own skew_query_a, sourced."""
    return subprocess.run(
        ["bash", "-c", f"source ./verify.sh; skew_query_a {slots}"],
        cwd=VERIFY.parent, capture_output=True, text=True, check=True,
    ).stdout


def stage(job, now_ms, stage_id, n, p50, p99, successful=True, legacy=(10, 500)):
    attrs = {"job_id": job, "app_id": "app-1", "app_name": "skew", "stage_id": str(stage_id), "stage_attempt": "0",
             "ts": str(now_ms), "task_count": str(n), "task_duration_p50_ms": str(legacy[0]),
             "task_duration_p99_ms": str(legacy[1]), "plan_fingerprint": "c" * 64, "plan_json": "{}"}
    if successful:
        attrs.update({"successful_task_sample_count": str(n), "successful_task_duration_p50_ms": str(p50),
                      "successful_task_duration_p99_ms": str(p99)})
    else:
        attrs.update({"task_duration_p50_ms": str(p50), "task_duration_p99_ms": str(p99)})
    m = ",".join(f"'{k}':'{v}'" for k, v in attrs.items())
    return ("INSERT INTO apex.otel_traces (Timestamp, TraceId, SpanId, SpanName, ServiceName, SpanAttributes) "
            f"VALUES (fromUnixTimestamp64Milli({now_ms}), 'trace-{job}', 'span-{stage_id}', 'apex.stage', 'apex-jar', {{{m}}})")


def job_conf(job, now_ms, instances, cores):
    attrs = {"job_id": job, "app_id": "app-1", "app_name": "skew", "ts": str(now_ms),
             "spark.executor.instances": str(instances), "spark.executor.cores": str(cores)}
    m = ",".join(f"'{k}':'{v}'" for k, v in attrs.items())
    return ("INSERT INTO apex.otel_traces (Timestamp, TraceId, SpanId, SpanName, ServiceName, SpanAttributes) "
            f"VALUES (fromUnixTimestamp64Milli({now_ms}), 'trace-{job}', 'span-conf', 'apex.job_conf', 'apex-jar', {{{m}}})")


COLS = "job_id, stage_id, population, n_tasks, p50_ms, p99_ms, skew_ratio, slots, tail_bound_threshold, tail_bound, min_slots_for_tail_bound"


def rows(ch, slots="NULL", job=None):
    where = f" WHERE job_id = '{job}'" if job else ""
    out = ch.query(f"SELECT {COLS} FROM ({query_a(slots)}){where} ORDER BY stage_id").strip()
    return [dict(zip(COLS.split(", "), line.split("\t"))) for line in out.splitlines()]


@live_only
def test_skew_prefers_successful():
    now_ms = int(time.time() * 1000)
    job = f"skew-pop-{now_ms}"
    with DisposableClickHouse(sql_files()) as ch:
        ch.query(stage(job, now_ms, 1, n=50, p50=100, p99=200, successful=True, legacy=(10, 500)), fmt=None)
        ch.query(stage(job, now_ms, 2, n=50, p50=10, p99=500, successful=False), fmt=None)
        r = rows(ch, job=job)
        assert (r[0]["population"], r[0]["p50_ms"], r[0]["p99_ms"], r[0]["skew_ratio"]) == ("successful", "100", "200", "2")
        assert (r[1]["population"], r[1]["skew_ratio"]) == ("all_attempts", "50")


@live_only
def test_skew_closed_form_verdicts():
    now_ms = int(time.time() * 1000)
    job = f"skew-verdict-{now_ms}"
    with DisposableClickHouse(sql_files()) as ch:
        ch.query(job_conf(job, now_ms, instances=2, cores=4), fmt=None)       # 8 slots
        ch.query(stage(job, now_ms, 1, n=100, p50=100, p99=2000), fmt=None)   # ratio 20 > 14.14
        ch.query(stage(job, now_ms, 2, n=100, p50=100, p99=900), fmt=None)    # ratio 9  < 14.14
        ch.query(stage(job, now_ms, 3, n=8, p50=100, p99=900), fmt=None)      # single wave: n <= slots
        r = rows(ch, job=job)
        assert (r[0]["slots"], r[0]["tail_bound_threshold"], r[0]["tail_bound"]) == ("8", "14.14", "1"), r[0]
        assert (r[1]["slots"], r[1]["tail_bound_threshold"], r[1]["tail_bound"]) == ("8", "14.14", "0"), r[1]
        assert (r[2]["tail_bound_threshold"], r[2]["tail_bound"]) == ("\\N", "\\N"), r[2]


@live_only
def test_skew_unknown_width_abstains():
    now_ms = int(time.time() * 1000)
    job = f"skew-unknown-{now_ms}"
    with DisposableClickHouse(sql_files()) as ch:
        ch.query(stage(job, now_ms, 1, n=100, p50=100, p99=2000), fmt=None)
        r = rows(ch, job=job)[0]
        assert (r["slots"], r["tail_bound"], r["min_slots_for_tail_bound"]) == ("\\N", "\\N", "5.95"), r
        r = rows(ch, slots="8", job=job)[0]   # the operator width fills the gap
        assert (r["slots"], r["tail_bound"]) == ("8", "1"), r


@live_only
def test_verify_step4_flags_seeded_skew():
    """seed.sh shapes: p99 = p50 x 30..60 on the skewed stage, task_count in {8, 50, 200}."""
    now_ms = int(time.time() * 1000)
    job = f"seedlike-{now_ms}"
    with DisposableClickHouse(sql_files()) as ch:
        for sid, n, mult in ((7, 200, 40), (8, 50, 30), (9, 8, 60), (1, 200, 1), (2, 50, 1)):
            p50 = 1000
            ch.query(stage(job, now_ms, sid, n=n, p50=p50, p99=int(p50 * (mult if mult > 1 else 1.5)), successful=False), fmt=None)
        flagged = ch.query(f"SELECT count() FROM ({query_a('8')}) WHERE job_id = '{job}' AND tail_bound = 1").strip()
        assert flagged == "2", rows(ch, slots="8", job=job)   # stages 7 and 8; stage 9 is a single wave
        assert ch.query(f"SELECT count() FROM ({query_a('')}) WHERE job_id = '{job}' AND tail_bound = 1").strip() == "0"
