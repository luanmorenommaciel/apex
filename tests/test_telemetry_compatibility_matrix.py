"""Structural regression guard for the offline telemetry compatibility matrix."""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/architecture/TELEMETRY-COMPATIBILITY-MATRIX.md"

EXPECTED_EDGES = {
    ("dev", "jar", "primary", "real_jobs"),
    ("jar", "collect", "primary", "OTLP"),
    ("collect", "store", "primary", "INSERT"),
    ("store", "engine", "primary", "telemetry"),
    ("store", "serve", "primary", "telemetry"),
    ("engine", "store", "primary", "findings"),
    ("store", "memory", "cross_cutting", "plan_history"),
    ("memory", "engine", "cross_cutting", "prior_outcomes"),
    ("engine", "verify", "cross_cutting", "proposed_fix"),
    ("verify", "store", "cross_cutting", "verdicts"),
}
V05_MV_EVOLUTION = [
    "infra/sql/034_stage_duration_max_additive.sql",
    "infra/sql/035_successful_task_sample_additive.sql",
    "infra/sql/036_task_termination_additive.sql",
    "infra/sql/037_task_shuffle_volume_additive.sql",
    "infra/sql/038_scheduler_failure_semantics_additive.sql",
    "infra/sql/039_executor_runtime_additive.sql",
]


def _text(relative_path: str) -> str:
    path = ROOT / relative_path
    assert path.is_file(), f"evidence source is missing: {relative_path}"
    return path.read_text(encoding="utf-8")


def _lane_source(lane: str) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / lane / "src").glob("**/*.py"))
    )


def _verify_to_row_ast() -> ast.FunctionDef:
    module = ast.parse(_text("verify/src/apex_verify/models.py"))
    result = next(
        node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "Verdict"
    )
    return next(
        node for node in result.body if isinstance(node, ast.FunctionDef) and node.name == "to_row"
    )


def _manifest() -> dict[str, Any]:
    assert MATRIX.is_file(), "canonical telemetry compatibility matrix is missing"
    match = re.search(
        r"## Manifesto estrutural verificável.*?~~~json\n(.*?)\n~~~",
        MATRIX.read_text(encoding="utf-8").replace(chr(96) * 3, "~~~"),
        re.DOTALL,
    )
    assert match, "matrix must contain one structured JSON manifest"
    return json.loads(match.group(1))


def _edge_set(manifest: dict[str, Any]) -> set[tuple[str, str, str, str]]:
    return {
        (edge["from"], edge["to"], edge["role"], edge["payload"])
        for edge in manifest["edges"]
    }


def _drift(manifest: dict[str, Any], drift_id: str) -> dict[str, Any]:
    return next(drift for drift in manifest["drifts"] if drift["id"] == drift_id)


def _validate(manifest: dict[str, Any]) -> None:
    """Compare structured claims with independent, tracked source evidence."""
    assert manifest["contract_version"] == "v0.5"
    assert "contract **v0.5**" in _text("CONTRACT.md")
    assert manifest["runtime_caveat"] == "offline_unproven"

    assert _edge_set(manifest) == EXPECTED_EDGES
    pipeline = _text("PIPELINE.md")
    for edge in (
        "D -->|real jobs| J -->|OTLP| K -->|INSERT| I",
        "I --> E & S",
        "E -->|findings| I",
        "I -->|plan history| M",
        "M -->|prior outcomes| E",
        "E -->|proposed fix| V",
        "V -->|verdicts| I",
    ):
        assert edge in pipeline

    owners = manifest["owners"]
    assert owners["infra"]["responsibility"] == "apply_all_ddl"
    assert "**owns all DDL application**" in pipeline
    jar_emissions = set(
        re.findall(r'tracer\.spanBuilder\("(apex\.[^"]+)"\)', _text("jar/src/main/scala/apex/ApexOtelSink.scala"))
    )
    assert set(owners["jar"]["emits"]) == jar_emissions
    assert owners["engine"]["writes"] == ["apex.findings"]
    assert owners["memory"]["writes"] == ["apex.plan_memory", "apex.run_outcomes"]
    verify = owners["verify"]
    assert verify == {
        "declared_owner": "verify",
        "declared_output": "apex.fix_verifications",
        "serialization_observed": "Verdict.to_row",
        "persistence_observed": "absent",
    }
    assert "def persist_findings" in _text("engine/src/apex_engine/clickhouse.py")
    assert 'store.insert("apex.plan_memory"' in _text("memory/src/apex_memory/indexer.py")
    assert 'store.insert("apex.run_outcomes"' in _text("memory/src/apex_memory/indexer.py")
    assert "Owns `apex.fix_verifications`" in _text("docs/lanes/VERIFY.md")
    to_row = _verify_to_row_ast()
    assert any(isinstance(node, ast.Return) and isinstance(node.value, ast.Dict) for node in ast.walk(to_row))
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"insert", "execute", "query"}
        for node in ast.walk(to_row)
    )
    verify_source = _lane_source("verify")
    assert not re.search(r"\.insert\s*\(", verify_source)
    assert "INSERT INTO" not in verify_source
    assert not re.search(r"\.(?:insert|execute|query)\s*\([^)]*fix_verifications", verify_source, re.DOTALL)

    mv_chain = manifest["mv_chain"]
    assert mv_chain["initial"] == "infra/sql/020_mv_reshape.sql"
    assert mv_chain["job_conf"] == "infra/sql/021_mv_job_conf.sql"
    assert mv_chain["v05_evolution"] == V05_MV_EVOLUTION
    assert "CREATE MATERIALIZED VIEW IF NOT EXISTS apex.mv_spark_events" in _text(mv_chain["initial"])
    assert "apex.job_conf" in _text(mv_chain["job_conf"])
    for migration in mv_chain["v05_evolution"]:
        assert "ALTER TABLE apex.mv_spark_events MODIFY QUERY" in _text(migration)
    assert "executor_run_time_ms" in _text("infra/sql/039_executor_runtime_additive.sql")

    assert "PROPOSED v0.4" in _text("contract/job_conf.ddl.sql")
    for source in ("memory/sql/030_plan_memory.sql", "memory/sql/031_run_outcomes.sql"):
        assert "PROPOSED, not ratified" in _text(source)

    sample_count_gap = _drift(manifest, "v05_sample_count_consumer_gap")
    assert sample_count_gap["contract"] == "sample_count_zero_is_absent"
    assert sample_count_gap["observed_consumers_without_sample_count"] == ["engine", "memory", "verify"]
    assert sample_count_gap["legacy_p50_p99_consumers"] == ["engine", "memory"]
    assert "sample_count=0" in _text("CONTRACT.md")
    for lane in sample_count_gap["observed_consumers_without_sample_count"]:
        assert "sample_count" not in _lane_source(lane)
    for lane in sample_count_gap["legacy_p50_p99_consumers"]:
        assert "task_duration_p50_ms" in _lane_source(lane)
        assert "task_duration_p99_ms" in _lane_source(lane)

    runtime_drift = _drift(manifest, "verify_executor_runtime_claim_outdated")
    assert runtime_drift["verify_claim"] == "not_a_spark_events_column"
    assert runtime_drift["contradicted_by"] == [
        "infra/sql/039_executor_runtime_additive.sql",
        "engine/src/apex_engine/clickhouse.py",
    ]
    assert "NOT a\n# column in apex.spark_events" in _text("verify/src/apex_verify/models.py")
    for source in runtime_drift["contradicted_by"]:
        assert "executor_run_time_ms" in _text(source)


def _must_fail(mutator: Callable[[dict[str, Any]], None]) -> None:
    broken = deepcopy(_manifest())
    mutator(broken)
    try:
        _validate(broken)
    except (AssertionError, KeyError, StopIteration):
        return
    raise AssertionError("negative mutation unexpectedly preserved matrix validity")


def test_matrix_is_structural_and_derived_from_independent_sources() -> None:
    _validate(_manifest())


def test_negative_mutations_are_discriminating() -> None:
    _must_fail(
        lambda matrix: matrix["edges"].__setitem__(
            1, {"from": "jar", "to": "serve", "role": "primary", "payload": "OTLP"}
        )
    )
    _must_fail(lambda matrix: matrix["owners"]["engine"].__setitem__("writes", ["apex.spark_events"]))
    _must_fail(lambda matrix: matrix["owners"]["verify"].__setitem__("persistence_observed", "present"))
    _must_fail(lambda matrix: matrix.__setitem__("drifts", [matrix["drifts"][1]]))
    _must_fail(lambda matrix: matrix.__setitem__("runtime_caveat", ""))
    _must_fail(
        lambda matrix: matrix.__setitem__(
            "mv_chain",
            {"initial": "infra/sql/020_mv_reshape.sql", "job_conf": None, "v05_evolution": []},
        )
    )
