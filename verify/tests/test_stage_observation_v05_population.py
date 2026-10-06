"""Verify stage-duration population selection for the v0.5 contract.

Scope = apply the rule CONTRACT.md:28 (v0.5) already fixes for `verify (read)`,
mirroring engine's StageAggregate: successful_* when successful_task_sample_count
> 0, legacy fields otherwise. No coverage threshold, no new absence semantics.

Groups:
  NEW    — fail on 055db99, must pass after the leaf (discriminating);
  LEGACY — pass on 055db99 and must keep passing (historical rows unchanged);
  HOLD   — pin only the population choice for cases whose VALUE semantics
           (p50 == 0, absent duration) are a pending decision. They must not be
           read as "absent sample == measured zero". They fail on 055db99 only
           because the population attributes do not exist there.
All values are synthetic (NA-09 shapes, inlined — no file dependency).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apex_verify.models import StageObservation
from apex_verify.predict import bound_analysis
from apex_verify.guardrails import noise_floor

SLOTS, JOB_RUNTIME_MS = 20, 20_000.0

V05_ZERO = {
    "task_duration_max_ms": 0, "task_duration_sample_count": 0,
    "successful_task_duration_p50_ms": 0, "successful_task_duration_p99_ms": 0,
    "successful_task_duration_max_ms": 0, "successful_task_sample_count": 0,
}
BASE = {"stage_id": 0, "task_count": 100, "shuffle_read_bytes": 209_715_200}


def obs(**kw) -> StageObservation:
    return StageObservation.model_validate({**BASE, **V05_ZERO, **kw})


# NA-09 "speculation": killed originals put 9000 ms into the legacy p99 only.
SPEC = dict(task_duration_p50_ms=1005, task_duration_p99_ms=9000,
            successful_task_duration_p50_ms=999, successful_task_duration_p99_ms=1098,
            successful_task_sample_count=100)
# NA-09 "executor loss": failed attempts move legacy p50 AND p99.
LOSS = dict(task_duration_p50_ms=1298, task_duration_p99_ms=4000,
            successful_task_duration_p50_ms=995, successful_task_duration_p99_ms=1490,
            successful_task_sample_count=100)
CLEAN = dict(task_duration_p50_ms=999, task_duration_p99_ms=1098,
             successful_task_duration_p50_ms=999, successful_task_duration_p99_ms=1098,
             successful_task_sample_count=100)


# ── NEW ─────────────────────────────────────────────────────────────────────
def test_new_successful_fields_survive_validation():
    dumped = obs(**SPEC).model_dump()
    assert dumped["successful_task_sample_count"] == 100
    assert dumped["successful_task_duration_p99_ms"] == 1098


def test_new_skew_ratio_uses_successful_population_when_sampled():
    s = obs(**SPEC)
    assert s.duration_sample_source == "successful_tasks"
    assert s.skew_ratio == pytest.approx(1098 / 999)
    assert s.legacy_skew_ratio == pytest.approx(9000 / 1005)


def test_new_skew_ratio_discriminates_even_when_verdict_does_not_move():
    # Both populations are work-bound at 20 slots; only the ratio tells them apart.
    assert obs(**LOSS).skew_ratio == pytest.approx(1490 / 995)


def test_new_bound_analysis_uses_successful_population():
    g, _, low, high = bound_analysis(obs(**SPEC), SLOTS, JOB_RUNTIME_MS)
    assert g.verdict == "work_bound_saves_nothing"
    assert (low, high) == (0.0, 0.0)
    assert "p99=1098ms" in g.detail


def test_new_partial_successful_sample_follows_the_literal_contract():
    # CONTRACT.md:28 conditions on > 0 only. A coverage threshold would be a NEW
    # policy; if owners adopt one, this test changes by that decision.
    s = obs(task_duration_p50_ms=999, task_duration_p99_ms=9000,
            successful_task_duration_p50_ms=990, successful_task_duration_p99_ms=1098,
            successful_task_sample_count=60)
    assert s.duration_sample_source == "successful_tasks"
    assert bound_analysis(s, SLOTS, JOB_RUNTIME_MS)[0].verdict == "work_bound_saves_nothing"


def test_new_pre_v05_row_reports_legacy_population():
    s = obs(task_duration_p50_ms=999, task_duration_p99_ms=9000)
    assert s.duration_sample_source == "legacy_all_attempts"
    assert s.legacy_skew_ratio == s.skew_ratio


def test_new_negative_control_successful_values_are_not_discarded():
    same_legacy = dict(task_duration_p50_ms=999, task_duration_p99_ms=9000, successful_task_sample_count=100)
    a = obs(**same_legacy, successful_task_duration_p50_ms=999, successful_task_duration_p99_ms=1098)
    b = obs(**same_legacy, successful_task_duration_p50_ms=100, successful_task_duration_p99_ms=9000)
    assert a.skew_ratio != b.skew_ratio


def test_new_noise_floor_quotes_the_population_it_compares():
    sib = [obs(**SPEC), obs(**CLEAN), obs(**CLEAN)]
    g = noise_floor(sib[0], sib, ())
    assert "8.96x" not in g.detail and "1.10x" in g.detail


# ── LEGACY ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("keys_present", [True, False])
def test_legacy_pre_v05_row_keeps_legacy_values(keys_present):
    row = {**BASE, "task_duration_p50_ms": 999, "task_duration_p99_ms": 9000}
    if keys_present:
        row.update(V05_ZERO)
    s = StageObservation.model_validate(row)
    assert s.skew_ratio == pytest.approx(9000 / 999)
    g, _, low, high = bound_analysis(s, SLOTS, JOB_RUNTIME_MS)
    assert g.verdict == "tail_bound"
    assert round(low, 3) == -18.025 and round(high, 3) == -0.022


def test_legacy_no_divergence_control_is_unchanged():
    s = obs(**CLEAN)
    assert s.skew_ratio == pytest.approx(1098 / 999)
    assert bound_analysis(s, SLOTS, JOB_RUNTIME_MS)[0].verdict == "work_bound_saves_nothing"


def test_legacy_duration_fields_remain_required():
    # Representation is out of scope for the leaf (see NEXT-ACTIONS decisions).
    with pytest.raises(ValidationError):
        StageObservation.model_validate({**BASE, **V05_ZERO})


# ── HOLD (population only; value semantics pending decision) ────────────────
def test_hold_absent_duration_selects_legacy_population_only():
    s = obs(task_duration_p50_ms=0, task_duration_p99_ms=0)
    assert s.duration_sample_source == "legacy_all_attempts"
    assert s.skew_ratio == s.legacy_skew_ratio   # value NOT asserted: absent is not measured zero


def test_hold_successful_p50_zero_selects_successful_population_only():
    s = obs(task_duration_p50_ms=5, task_duration_p99_ms=9000,
            successful_task_duration_p50_ms=0, successful_task_duration_p99_ms=40,
            successful_task_sample_count=100)
    assert s.duration_sample_source == "successful_tasks"
    assert s.effective_task_duration_p99_ms == 40   # ratio value at p50 == 0 is a pending decision


def test_new_noise_floor_excludes_sibling_without_effective_p50():
    measured = [obs(**CLEAN), obs(**CLEAN)]
    absent_successful_p50 = obs(
        task_duration_p50_ms=5, task_duration_p99_ms=9000,
        successful_task_duration_p50_ms=0, successful_task_duration_p99_ms=40,
        successful_task_sample_count=100,
    )
    g = noise_floor(measured[0], [*measured, absent_successful_p50], ())
    assert g.verdict == "no_baseline"
    assert not g.fired
