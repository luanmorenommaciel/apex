"""The safety gate. Every test here is a thing that must NEVER reach an executor.

The Long.MaxValue cases are the ones worth reading: they are the difference
between a gate that works and a gate that looks like it works.
"""

from __future__ import annotations

import pytest

from apex_verify.safety import (
    DEFAULT_SIZE_BUDGET_BYTES,
    LONG_MAX_VALUE,
    check_size,
    gate,
    validate_read_only,
)
from apex_verify.models import SafetyVerdict

SAFE_REPLAY_CODE = """
fact = spark.read.format("delta").load("s3a://warehouse/fact")
dim = spark.read.format("delta").load("s3a://warehouse/dim")
joined = fact.join(dim, "join_key").groupBy("attr").count()
n = joined.count()
"""


def test_the_actual_replay_code_passes():
    r = validate_read_only(SAFE_REPLAY_CODE)
    assert r.safe and r.verdict is SafetyVerdict.ALLOW


@pytest.mark.parametrize(
    "snippet,needle",
    [
        ('df.write.format("delta").save("s3a://warehouse/fact")', "write path opened"),
        ('df.write.saveAsTable("prod.customers")', "saveAsTable"),
        ('df.write.insertInto("prod.events")', "insertInto"),
        ('spark.sql("DROP TABLE prod.customers")', "DROP"),
        ('spark.sql("delete from prod.orders where 1=1")', "DELETE"),
        ('spark.sql("INSERT INTO prod.t SELECT * FROM s")', "INSERT"),
        ('spark.sql("MERGE INTO prod.t USING s ON s.id = t.id")', "MERGE"),
        ("import os", "forbidden import os"),
        ("import subprocess", "forbidden import subprocess"),
        ("from pathlib import Path", "forbidden import from pathlib"),
        ('exec("print(1)")', "forbidden builtin exec"),
        ('eval("1+1")', "forbidden builtin eval"),
        ("df._jdf.queryExecution()", "escape hatch ._jdf"),
        ("sc = spark._jvm.System", "escape hatch ._jvm"),
        ("df.vacuum()", "destructive call .vacuum()"),
    ],
)
def test_destructive_code_is_blocked(snippet, needle):
    r = validate_read_only(snippet)
    assert not r.safe
    assert r.verdict is SafetyVerdict.BLOCK_AST
    assert needle in r.detail


def test_reading_a_customer_path_is_blocked_even_though_reading_is_read_only():
    # The rule is not "no writes" — it is "never touch customer data at all".
    r = validate_read_only('df = spark.read.parquet("s3a://acme-prod/events/2026/07/")')
    assert not r.safe
    assert "outside the synthetic bench" in r.detail


@pytest.mark.parametrize(
    "path",
    [
        "s3://customer-bucket/tbl", "gs://cust/tbl", "abfss://c@a.dfs.core.windows.net/t",
        "hdfs://nn/user/prod/t", "/dbfs/mnt/prod/t", "/mnt/prod/t",
    ],
)
def test_every_storage_scheme_is_covered_by_the_path_allowlist(path):
    r = validate_read_only(f'spark.read.load("{path}")')
    assert not r.safe and "outside the synthetic bench" in r.detail


def test_all_violations_are_reported_not_just_the_first():
    r = validate_read_only('import os\ndf.write.save("s3a://prod/x")\n')
    assert r.detail.count("line ") >= 2


def test_unparseable_code_is_blocked_not_executed():
    r = validate_read_only("def broken(:\n")
    assert not r.safe and r.verdict is SafetyVerdict.BLOCK_AST
    assert "does not parse" in r.detail


# ── the Long.MaxValue trap ─────────────────────────────────────────────────
def test_long_max_value_is_unknown_not_eight_exabytes():
    r = check_size(LONG_MAX_VALUE)
    assert not r.safe
    assert r.verdict is SafetyVerdict.BLOCK_SIZE_UNKNOWN
    assert "no statistics available" in r.detail
    # It must NOT be reported as a size overrun — that misdiagnoses the cause.
    assert r.verdict is not SafetyVerdict.BLOCK_SIZE


def test_missing_stats_fails_closed():
    r = check_size(None)
    assert not r.safe and r.verdict is SafetyVerdict.BLOCK_SIZE_UNKNOWN


def test_a_real_oversized_plan_is_blocked_as_a_size_overrun():
    r = check_size(DEFAULT_SIZE_BUDGET_BYTES + 1)
    assert not r.safe and r.verdict is SafetyVerdict.BLOCK_SIZE
    assert "OOM risk" in r.detail


def test_a_real_small_plan_is_allowed():
    r = check_size(10 << 20)
    assert r.safe and r.verdict is SafetyVerdict.ALLOW


# ── the composed gate ──────────────────────────────────────────────────────
def test_gate_runs_ast_before_size_so_the_verdict_names_the_real_problem():
    r = gate(code='import os\ndf.count()', size_in_bytes=LONG_MAX_VALUE)
    assert r.verdict is SafetyVerdict.BLOCK_AST


def test_gate_passes_the_real_replay():
    r = gate(code=SAFE_REPLAY_CODE, size_in_bytes=10 << 20)
    assert r.safe and r.verdict is SafetyVerdict.ALLOW


def test_prediction_only_does_not_pretend_to_gate_anything():
    r = gate(will_execute=False)
    assert r.safe and r.verdict is SafetyVerdict.NOT_APPLICABLE
    assert "no code and no query were executed" in r.detail
