"""The escalation gate (T10) and the AQE ground-truth watcher (bonus)."""

from apex_engine import Confidence, Finding, FindingType, PlanTransition, Severity, StageAggregate
from apex_engine.context import JobContext
from apex_engine.gate import partition, should_escalate
from apex_engine.jobconf import operator_width
from apex_engine.watchers import aqe, run_all_offline
from apex_engine.watchers.base import JOB_LEVEL_STAGE_ID


def finding(confidence_score: float, severity: Severity, **overrides) -> Finding:
    payload = {
        "job_id": "job-1", "stage_id": 4, "type": FindingType.SKEW_ON_JOIN,
        "severity": severity, "evidence": "e", "impact": "i", "fix": "f",
        "confidence_score": confidence_score, "detected_by": "skew_watcher",
    }
    payload.update(overrides)
    return Finding(**payload)


def transition(transition_type: str, confidence: str = "HIGH", **overrides) -> PlanTransition:
    payload = {"job_id": "job-1", "execution_id": 10, "update_seq": 0,
               "transition_type": transition_type, "detail": f"{transition_type} x2",
               "confidence": confidence}
    payload.update(overrides)
    return PlanTransition.model_validate(payload)


# --- T10: the gate is BOTH conditions -------------------------------------

def test_confident_and_severe_does_not_escalate():
    assert should_escalate(finding(0.9, Severity.CRITICAL)) is False


def test_unconfident_and_severe_escalates():
    assert should_escalate(finding(0.4, Severity.CRITICAL)) is True


def test_unconfident_but_not_severe_does_not_escalate():
    assert should_escalate(finding(0.4, Severity.WARNING)) is False
    assert should_escalate(finding(0.4, Severity.INFO)) is False


def test_blocker_is_above_the_severity_threshold():
    assert should_escalate(finding(0.4, Severity.BLOCKER)) is True


def test_threshold_is_strict_less_than():
    assert should_escalate(finding(0.6, Severity.CRITICAL)) is False
    assert should_escalate(finding(0.599, Severity.CRITICAL)) is True


def test_partition_splits_direct_from_escalated():
    direct, escalated = partition([
        finding(0.9, Severity.CRITICAL),
        finding(0.4, Severity.CRITICAL),
        finding(0.4, Severity.WARNING),
    ])
    assert len(direct) == 2 and len(escalated) == 1
    assert escalated[0].confidence_score == 0.4


def test_a_clean_job_escalates_nothing():
    assert partition([]) == ([], [])


# --- AQE ground truth ------------------------------------------------------

def test_skew_split_is_a_ground_truth_skew_finding():
    findings = aqe.evaluate_job("job-1", "app-1", [transition("skew_split")])
    assert len(findings) == 1
    assert findings[0].type is FindingType.SKEW_ON_JOIN
    assert findings[0].confidence is Confidence.HIGH
    assert findings[0].details["ground_truth"] is True
    assert findings[0].stage_id == JOB_LEVEL_STAGE_ID


def test_coalesce_is_reported_as_partition_sizing_not_as_skew():
    """The real P0 job only coalesces. Calling that skew would be a lie."""
    findings = aqe.evaluate_job("job-1", "app-1", [transition("coalesce")])
    assert len(findings) == 1
    assert findings[0].type is FindingType.AQE_REPLAN
    assert "shuffle partition count" in findings[0].evidence


def test_best_effort_transitions_are_not_treated_as_ground_truth():
    assert aqe.evaluate_job("job-1", "app-1", [transition("skew_split", confidence="BEST_EFFORT")]) == []


def test_no_transitions_means_no_aqe_findings():
    assert aqe.evaluate_job("job-1", "app-1", []) == []


def test_aqe_ground_truth_upgrades_an_ambiguous_heuristic_to_free():
    """The DataFlint-beating move: an ambiguous ratio would cost an LLM call, but
    if AQE split a skewed partition in the same job the heuristic is confirmed
    at $0."""
    heuristic = finding(0.55, Severity.WARNING)
    assert should_escalate(heuristic) is False  # warning, so not yet gate-eligible

    severe_but_unsure = finding(0.55, Severity.CRITICAL)
    assert should_escalate(severe_but_unsure) is True

    upgraded = aqe.corroborate_skew([severe_but_unsure], [transition("skew_split")])
    assert should_escalate(upgraded[0]) is False  # now free
    assert upgraded[0].details["aqe_corroborated"] is True
    assert "corroborated by an AQE skew_split" in upgraded[0].evidence


def test_ground_truth_cannot_launder_a_missing_cluster_width_into_high():
    """A skew_split proves the skew EXISTS. What it costs is CONTRACT.md rule 1,
    which needs `slots` — so a finding carrying no width evidence is corroborated
    only to MEDIUM, and keeps its severity."""
    no_width = finding(0.55, Severity.WARNING)
    upgraded = aqe.corroborate_skew([no_width], [transition("skew_split")])
    assert upgraded[0].confidence is Confidence.MEDIUM
    assert upgraded[0].severity is Severity.WARNING

    with_width = finding(0.55, Severity.WARNING).model_copy(
        update={"details": {"slots_source": "job_conf", "slots": 8}}
    )
    promoted = aqe.corroborate_skew([with_width], [transition("skew_split")])
    assert promoted[0].confidence is Confidence.HIGH
    assert promoted[0].severity is Severity.CRITICAL


def test_coalesce_alone_does_not_upgrade_a_skew_heuristic():
    candidate = finding(0.55, Severity.CRITICAL)
    unchanged = aqe.corroborate_skew([candidate], [transition("coalesce")])
    assert unchanged[0].confidence_score == 0.55
    assert should_escalate(unchanged[0]) is True


def test_end_to_end_offline_run_merges_both_tiers():
    """The heuristic tier needs volume, a Join node and a width before it makes a
    claim at all; given those, both tiers report and both are HIGH."""
    aggregates = [StageAggregate(
        job_id="job-1", app_id="app-1", stage_id=4, task_count=50,
        task_duration_p50_ms=21, task_duration_p99_ms=454,
        shuffle_read_bytes=112_930_867,
        plan_json="'Join Inner, (none#2L = cast(none#0 as bigint))",
    )]
    ctx = JobContext(width=operator_width(8))
    findings = run_all_offline(aggregates, [transition("skew_split")], ctx)
    types = [f.type for f in findings]
    assert types.count(FindingType.SKEW_ON_JOIN) == 2  # heuristic + ground truth
    assert all(f.confidence is Confidence.HIGH for f in findings)
