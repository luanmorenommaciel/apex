"""analyze() end to end with a mocked crew: does the gate actually hold?

The claim under test is the economic one — 95%+ of findings emit from Tier 1 at
$0, and an LLM is touched only for a candidate that is BOTH unsure AND severe.
These tests count crew invocations to prove it.

The escalating case here is the ONE Tier-1 path that can produce that
combination: a GC ratio high enough to be critical, measured against a PROXY
denominator (`task_count x p50`) because `executor_run_time_ms` is absent from
the contract. Severe symptom, weak evidence — exactly what a judge is for.
Every other rule is either confident when severe, or not severe when unsure.
"""

from __future__ import annotations

import pytest

from apex_engine import Confidence, FindingType, Severity, analyze
from apex_engine.clickhouse import _signature
from apex_engine.context import ShapeSample
from apex_engine.gate import should_escalate
from apex_engine.jobconf import JobConf
from apex_engine.schema import Finding, PlanTransition, StageAggregate

# A skew claim now needs VOLUME and a Join node before its ratio is a statistic
# at all (CONTRACT.md rule 1 + dev's volume finding), so the skew fixtures carry
# both. Without them these stages are correctly invisible to the watcher.
JOINED = {
    "shuffle_read_bytes": 112_930_867,
    "plan_json": "'Join Inner, (none#2L = cast(none#0 as bigint))",
}
CLEAN = {**JOINED, "task_duration_p50_ms": 100, "task_duration_p99_ms": 110, "task_count": 50}
SEVERE_SKEW = {**JOINED, "task_duration_p50_ms": 21, "task_duration_p99_ms": 454, "task_count": 50}
AMBIGUOUS_SKEW = {**JOINED, "task_duration_p50_ms": 100, "task_duration_p99_ms": 710, "task_count": 50}
# critical GC ratio on an estimated denominator -> severity critical, confidence 0.45
ESCALATING = {"gc_time_ms": 3_000, "task_count": 10, "task_duration_p50_ms": 100}

# 4 x 2 = 8 slots, the width this lab actually runs. Contract v0.4 carries these
# keys only when they are explicitly set, which is why the width being ABSENT is
# a first-class fixture below rather than an edge case.
CLUSTER_CONF = {"spark.executor.instances": "4", "spark.executor.cores": "2"}


class FakeStore:
    """Serves aggregates/transitions/conf and records what would be written."""

    def __init__(self, stages: list[dict], transitions=None, conf=CLUSTER_CONF):
        self.aggregates = [
            StageAggregate(job_id="job-1", app_id="app-1", stage_id=i, **s)
            for i, s in enumerate(stages)
        ]
        self.transitions = transitions or []
        self.conf = conf
        self.persisted: list[Finding] = []

    def stage_aggregates(self, job_id):
        return self.aggregates

    def plan_transitions(self, job_id):
        return self.transitions

    def job_conf(self, job_id):
        if self.conf is None:
            return JobConf.missing(job_id)
        return JobConf(job_id=job_id, app_id="app-1", conf=dict(self.conf), present=True)

    def persist_new_findings(self, job_id, findings):
        findings = list(findings)
        self.persisted.extend(findings)
        return {"mode": "inserted" if findings else "no_findings",
                "written_rows": len(findings), "skipped_existing": 0}


class SpyCrew:
    """Counts kickoffs and returns a scripted verdict."""

    invocations = 0

    def __init__(self, verdict: Finding | None):
        self.verdict = verdict

    def kickoff(self, inputs=None):
        type(self).invocations += 1
        return type("Out", (), {"pydantic": self.verdict})()


def spy_factory(verdict_builder):
    SpyCrew.invocations = 0

    def factory(candidate, store=None):
        return SpyCrew(verdict_builder(candidate))

    return factory


def confident_verdict(candidate: Finding) -> Finding:
    return candidate.model_copy(update={"confidence_score": 0.85, "confidence": Confidence.HIGH})


def rejecting_verdict(candidate: Finding) -> Finding:
    return candidate.model_copy(update={"confidence_score": 0.05, "confidence": Confidence.LOW})


# --- the exit criterion ----------------------------------------------------

def test_clean_job_writes_nothing_and_never_touches_an_llm():
    store = FakeStore([CLEAN, CLEAN, CLEAN])
    result = analyze("job-1", store, crew_factory=spy_factory(confident_verdict))

    assert result["findings"] == []
    assert result["written_rows"] == 0
    assert result["llm_calls"] == 0
    assert SpyCrew.invocations == 0
    assert result["crew"] == "not_needed"


def test_a_confident_severe_finding_emits_free():
    """21.62x is unambiguous — paying a model to confirm it would be waste."""
    store = FakeStore([SEVERE_SKEW])
    result = analyze("job-1", store, crew_factory=spy_factory(confident_verdict))

    assert len(result["findings"]) == 1
    assert result["findings"][0].confidence is Confidence.HIGH
    assert result["llm_calls"] == 0
    assert SpyCrew.invocations == 0
    assert result["escalated"] == []


def test_an_unsure_but_non_severe_finding_also_emits_free():
    """The gate needs BOTH conditions, and an unknown cluster width is exactly
    the unsure-but-not-severe case: rule 1 caps confidence, and no model can
    supply the missing width, so escalating would buy nothing."""
    store = FakeStore([AMBIGUOUS_SKEW], conf=None)   # no job_conf row -> width unknown
    result = analyze("job-1", store, crew_factory=spy_factory(confident_verdict))

    finding = result["findings"][0]
    assert finding.confidence_score < 0.6          # unsure
    assert finding.severity is Severity.WARNING    # but not severe
    assert finding.details["slots"] is None
    assert SpyCrew.invocations == 0
    assert result["llm_calls"] == 0
    assert "unknown" in result["cluster_width"]


def test_only_the_unsure_and_severe_candidate_reaches_the_crew():
    store = FakeStore([SEVERE_SKEW, ESCALATING, CLEAN, AMBIGUOUS_SKEW])
    result = analyze("job-1", store, crew_factory=spy_factory(confident_verdict))

    escalated = result["escalated"]
    assert len(escalated) == 1, "exactly one candidate satisfies both conditions"
    assert escalated[0].type is FindingType.MEMORY
    assert all(f.confidence_score < 0.6 for f in escalated)
    assert all(f.severity.at_least(Severity.CRITICAL) for f in escalated)

    assert SpyCrew.invocations == 1
    assert result["llm_calls"] == 2                # correlate + judge, once
    # ...while the other findings in the same job cost nothing
    assert len(result["findings"]) > 1


def test_a_judged_finding_is_persisted_with_the_recalibrated_confidence():
    store = FakeStore([ESCALATING])
    result = analyze("job-1", store, crew_factory=spy_factory(confident_verdict))

    judged = [f for f in result["findings"] if "judger" in f.detected_by]
    assert len(judged) == 1
    assert judged[0].confidence_score == pytest.approx(0.85)
    assert judged[0].confidence is Confidence.HIGH
    assert judged[0].details["tier1_confidence_score"] == pytest.approx(0.45)
    assert judged[0] in store.persisted


def test_a_rejected_finding_is_never_persisted():
    store = FakeStore([ESCALATING])
    result = analyze("job-1", store, crew_factory=spy_factory(rejecting_verdict))

    assert SpyCrew.invocations == 1   # it cost a crew run to find out
    assert store.persisted == []      # but nothing reached the user
    assert result["written_rows"] == 0
    assert result["judge_rejected"] == 1


def test_use_crew_false_never_calls_out_even_when_the_gate_would():
    store = FakeStore([ESCALATING])
    result = analyze("job-1", store, use_crew=False, crew_factory=spy_factory(confident_verdict))

    assert result["escalated"], "this fixture must produce an escalation candidate"
    assert SpyCrew.invocations == 0
    assert result["llm_calls"] == 0
    assert result["crew"] == "disabled"
    # kept at the Tier-1 confidence rather than dropped
    assert any(f.confidence_score == pytest.approx(0.45) for f in result["findings"])


def test_a_severe_finding_the_judge_cannot_reach_is_still_reported(monkeypatch):
    """The judge being unreachable must never lose a measured finding.

    INJECT the unavailability; do not try to manufacture it from the environment.
    Deleting ANTHROPIC_API_KEY and hoping was wrong in three different ways, one
    per environment this suite runs in:

      * CI — crewai is not installed, so the reason is `crewai_not_installed`,
        not `no_anthropic_api_key`. Six consecutive CI runs failed on the string
        mismatch while the suite passed locally, which is how it went unnoticed.
      * this laptop — crewai IS installed and credentials resolve from outside
        the deleted variable, so the crew actually RAN and issued a live network
        call to the Anthropic API from a unit test. It then failed on an
        unrelated deprecated `temperature` parameter.
      * a laptop with crewai installed and no credentials anywhere — the only
        environment where the original assertion held.

    A unit test must not depend on which machine runs it, and must never make a
    network call. Patching `is_available` makes the unavailable branch the thing
    under test in every environment, and the assertion checks the CLASS rather
    than a reason string that is a property of the environment, not of this
    behaviour.
    """
    import apex_engine.crew as crew_mod

    monkeypatch.setattr(crew_mod, "is_available", lambda: (False, "crewai_not_installed"))
    store = FakeStore([ESCALATING])
    result = analyze("job-1", store, use_crew=True, crew_factory=None)

    assert result["crew"].startswith("unavailable:")
    assert result["crew"] != "unavailable:"          # a reason must still be given
    assert result["llm_calls"] == 0
    assert len(result["findings"]) == 1
    assert result["findings"][0].confidence_score == pytest.approx(0.45)


# --- AQE ground truth changes the economics --------------------------------

def test_aqe_ground_truth_makes_an_ambiguous_skew_free():
    """Spark's own skew_split replaces what would otherwise need a model."""
    skew_split = PlanTransition(job_id="job-1", execution_id=10, transition_type="skew_split",
                                detail="split x3", confidence="HIGH")
    store = FakeStore([AMBIGUOUS_SKEW], transitions=[skew_split])
    result = analyze("job-1", store, crew_factory=spy_factory(confident_verdict))

    heuristic = [f for f in result["findings"] if f.detected_by.startswith("skew_watcher")]
    assert heuristic[0].confidence is Confidence.HIGH        # upgraded from LOW
    assert heuristic[0].details["aqe_corroborated"] is True
    assert should_escalate(heuristic[0]) is False
    assert result["llm_calls"] == 0
    assert SpyCrew.invocations == 0


def test_engine_runs_the_full_deterministic_tier_without_crewai_installed(monkeypatch):
    """Tier 1 must not depend on Tier 2 being present at all."""
    import builtins

    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "crewai" or name.startswith("crewai."):
            raise ImportError("No module named 'crewai'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)

    from apex_engine.crew import is_available

    assert is_available() == (False, "crewai_not_installed")

    store = FakeStore([SEVERE_SKEW, ESCALATING])
    result = analyze("job-1", store, use_crew=True, crew_factory=None)

    assert result["llm_calls"] == 0
    assert result["crew"] == "unavailable:crewai_not_installed"
    assert len(result["findings"]) == 2  # nothing lost


# --- re-analysis converges, even as shape history grows --------------------

class HistoryStore(FakeStore):
    """A store whose shape history can GROW between analyze() calls, and which
    dedups by the real persisted signature — the two properties the
    identity-drift regression needs."""

    def __init__(self, stages: list[dict], conf=CLUSTER_CONF):
        super().__init__(stages, conf=conf)
        self.samples: list[ShapeSample] = []
        self.signatures: set = set()

    def shape_history(self, fingerprints):
        return [s for s in self.samples if s.plan_fingerprint in fingerprints]

    def job_confs(self, job_ids):
        return {j: JobConf(job_id=j, app_id="app-1", conf=dict(self.conf), present=True)
                for j in job_ids}

    def persist_new_findings(self, job_id, findings):
        findings = list(findings)
        fresh = [f for f in findings if _signature(f) not in self.signatures]
        self.signatures.update(_signature(f) for f in fresh)
        self.persisted.extend(fresh)
        return {"mode": "inserted" if fresh else ("already_present" if findings else "no_findings"),
                "written_rows": len(fresh), "skipped_existing": len(findings) - len(fresh)}


def _sibling(run: str, p99: float) -> ShapeSample:
    """One more run of the SEVERE_SKEW shape at the same config and scale."""
    return ShapeSample(job_id=run, stage_id=0, plan_fingerprint="fp",
                       task_count=50, task_duration_p50_ms=21,
                       task_duration_p99_ms=p99, bytes_touched=112_930_867)


def test_a_new_sibling_run_between_analyses_does_not_duplicate_a_finding():
    """Identity must not be derived from something that quietly moves.

    The dedup signature includes `evidence`, which used to quote the measured
    floor (pct + sample count) and the ratio spread — all functions of OTHER
    runs. Seeding one sibling between two analyses moved those numbers, moved
    the signature, and a second row landed for the same finding. The volatile
    context now lives in `details` (never persisted), and re-analysis converges.
    """
    store = HistoryStore([{**SEVERE_SKEW, "plan_fingerprint": "fp"}])
    # the smallest history a floor can be measured over (MIN_SAMPLES_FOR_FLOOR)
    store.samples = [_sibling("run-1", 448), _sibling("run-2", 460), _sibling("run-3", 451)]

    first = analyze("job-1", store, use_crew=False)
    assert first["written_rows"] == 1
    assert first["findings"][0].details["noise_floor_samples"] == 3

    store.samples.append(_sibling("run-4", 475))  # a new run of the same shape lands

    second = analyze("job-1", store, use_crew=False)
    # the volatile context DID move — without that, this test proves nothing
    assert second["findings"][0].details["noise_floor_samples"] == 4
    assert (second["findings"][0].details["ratio_spread"]
            != first["findings"][0].details["ratio_spread"])
    # ...and the finding's identity did NOT: one row, not two
    assert second["written_rows"] == 0
    assert second["persistence"]["skipped_existing"] == 1
    assert len(store.persisted) == 1


def test_retry_pressure_reanalysis_is_idempotent():
    """The new finding uses the existing stable persisted signature."""
    store = HistoryStore([{
        "task_attempt_count": 62,
        "task_failed_attempt_count": 5,
        "task_counted_failure_attempt_count": 3,
    }])

    first = analyze("job-1", store, use_crew=False)
    second = analyze("job-1", store, use_crew=False)

    assert [f.type for f in first["findings"]] == [FindingType.RETRY_PRESSURE]
    assert first["written_rows"] == 1
    assert second["written_rows"] == 0
    assert second["persistence"]["skipped_existing"] == 1
    assert len(store.persisted) == 1
