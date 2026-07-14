"""Seam 2: conf-recommendation grounding for the Crew writer agent.

These exercise the pure helpers (no crewai), so grounding is verified without a
running Crew — the same detection/LLM boundary that keeps the pipeline testable.
"""

from apex_diagnostics.config import load_conf_recommendations
from apex_diagnostics.crew.recommendations import (
    build_recommendation_grounding,
    select_conf_recommendation,
)
from apex_diagnostics.models import Finding, Severity

APP = "app-20260707-0007"
RECS = load_conf_recommendations()


def finding(detector, severity, *, stage_id=None, execution_id=None, pattern=None):
    evidence = {"pattern": pattern} if pattern else {}
    return Finding(
        detector=detector,
        severity=severity,
        app_id=APP,
        stage_id=stage_id,
        execution_id=execution_id,
        title=f"{detector}/{severity.value}",
        evidence=evidence,
    )


def test_catalog_loads_from_config_yaml():
    detectors = {rec.detector for rec in RECS}
    assert {"skew", "shuffle", "gc", "oom", "plans"} <= detectors
    # severity is coerced to the enum on load.
    assert all(isinstance(rec.severity, Severity) for rec in RECS)


def test_select_matches_by_detector_and_severity():
    rec = select_conf_recommendation(finding("skew", Severity.WARNING, stage_id=4), RECS)
    assert rec is not None
    assert rec.conf_key == "spark.sql.adaptive.skewJoin.enabled"
    assert rec.suggested_value == "true"


def test_select_prefers_pattern_specific_over_generic():
    cartesian = select_conf_recommendation(
        finding("plans", Severity.CRITICAL, execution_id=0, pattern="CartesianProduct"), RECS
    )
    assert cartesian is not None
    assert cartesian.pattern_match == "CartesianProduct"
    assert cartesian.conf_key is None  # code-review fix, not a conf key

    nested = select_conf_recommendation(
        finding("plans", Severity.WARNING, execution_id=1, pattern="BroadcastNestedLoopJoin"), RECS
    )
    assert nested is not None
    assert nested.conf_key == "spark.sql.autoBroadcastJoinThreshold"


def test_select_returns_none_when_no_match():
    # gc has no warning+pattern entry mismatch; use a detector/severity with no rec.
    assert select_conf_recommendation(finding("plans", Severity.INFO, execution_id=2), RECS) is None


def test_grounding_skips_info_and_formats_conf_fix():
    findings = [
        finding("plans", Severity.INFO, execution_id=0),  # skipped (not actionable)
        finding("skew", Severity.WARNING, stage_id=4),
        finding("oom", Severity.CRITICAL, stage_id=9),
    ]
    grounding = build_recommendation_grounding(findings, RECS)
    lines = grounding.splitlines()
    assert len(lines) == 2  # info skipped
    assert "stage 4" in grounding and "spark.sql.adaptive.skewJoin.enabled" in grounding
    assert "stage 9" in grounding and "spark.executor.memoryOverhead" in grounding
    assert "plans/info" not in grounding


def test_grounding_renders_code_review_note_for_null_conf_key():
    findings = [finding("plans", Severity.CRITICAL, execution_id=3, pattern="CartesianProduct")]
    grounding = build_recommendation_grounding(findings, RECS)
    assert "execution 3" in grounding
    assert "no spark.conf fix — code review" in grounding


def test_grounding_empty_when_no_actionable_findings():
    assert build_recommendation_grounding([finding("plans", Severity.INFO, execution_id=0)], RECS) == ""
    assert build_recommendation_grounding([], RECS) == ""
