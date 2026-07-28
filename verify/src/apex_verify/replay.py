"""Stage 2 — REPLAY. Two-arm measurement on the synthetic bench.

A prediction is an extrapolation; a replay is a measurement. This module turns
two sets of timed runs — a BASELINE arm (the observed configuration) and a
TREATMENT arm (the proposed configuration) — into a `Measurement` that a
consumer can safely quote. Three contract rules are enforced here, in code,
not prose:

  RULE 1 (tail-bound). The replay only means anything on a bench where a skew
  fix CAN matter. The shipping bench is dev's calibrated `skew_join`: n=100
  tasks on 8 slots, p99/p50 = 17.7–20.6 against a closed-form threshold of
  (100−1)/(8−1) = 14.14 — tail-bound on every calibrated run, with AQE's
  `skew_split` firing 3/3. (2 slots is provably never tail-bound; 4 fails;
  6 passes at ~1.1× margin; 8 is the shipping default.)

  RULE 2 (noise floor). The floor is MEASURED from the baseline arm's own
  samples, at the level and scale being compared — never inherited. The same
  system produced 5.8% (job level, tiny scale), 9.2% (job level, calibrated
  scale) and 37.7% (shape level, 8 tasks, byte-identical work): a number
  carried across levels is wrong by up to 6.5×. With fewer than
  `MIN_REPS_FOR_FLOOR` baseline samples the floor is UNMEASURED and no delta
  may be quoted at all.

  RULE 3 (attributability). A delta is creditable only if the comparison
  contains ≥ 2 distinct configurations. The two-arm design guarantees this in
  normal use — but when the fix is already on, both arms canonicalise to the
  SAME conf, and the honest report is "unattributable", never "0%
  improvement". (Real case that motivated the rule: an 18.65% spread on
  byte-identical work that cleared a 5.8% floor with nothing to credit it to.)

  RULE 4 (mechanism vs runtime). The two are SEPARATE verdicts, emitted as a
  pair. `mechanism_confirmed` needs ground truth that the fix acted (an AQE
  transition and/or a tail-ratio collapse beyond its own measured floor) — it
  does NOT require clearing the runtime floor. `runtime_certified` requires
  |delta| ≥ measured CV (SE-of-median was rejected: reps on a shared host are
  not independent). When the mechanism fires but magnitude stays inside the
  floor the verdict is `mechanism_confirmed + runtime_unresolved` — the bench
  certifies mechanism today and defers magnitude. Corollary: the control fix
  must be one whose class the model covers — the first control (full AQE)
  coalesced 100→17 partitions, so W was NOT conserved; it tested a
  repartitioning the makespan bound explicitly refuses to model. The
  re-specified control holds partition count constant (coalesce OFF), leaving
  a pure tail redistribution.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Mapping

from .guardrails import normalize_conf_value, runtime_cv_pct
from .models import (
    Confidence,
    ConfigKnowledge,
    FindingRef,
    Measurement,
    Prediction,
    SafetyReport,
    StageObservation,
    Verdict,
    VerifyMethod,
)
from .predict import tail_bound_ratio_threshold

# A CV needs a spread to be a measurement. Two samples give a number that
# looks like a floor and isn't; three is the convention the calibration harness
# and every measured floor in the contract used.
MIN_REPS_FOR_FLOOR = 3

# A measured result (including "no measurable change") starts here and earns
# up to +0.40 from shape fidelity. 0.90 ceiling: bench evidence is strong but
# it is not production evidence, so a replay never reaches the 0.95 a
# deduction from the run's own conf (the no-op gate) can claim.
_MEASURED_BASE_SCORE = 0.50
_MEASURED_FIDELITY_SPAN = 0.40

# Below this fidelity the bench is not the finding's shape in any meaningful
# sense and the verdict text must say so — a replay of the wrong shape is not
# evidence (fix_verifications.shape_fidelity column comment).
FIDELITY_CAVEAT_BELOW = 0.8


def config_identity(conf: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    """A hashable identity for a configuration, for the attributability count.

    Values are canonicalised first (`16m` == `16777216`, `TRUE` == `true`) so
    two spellings of one setting count as ONE configuration. An inflated
    distinct-count directly unlocks delta claims that should stay suppressed —
    the exact failure contract rule 3 exists to prevent.
    """
    return tuple(sorted((k, normalize_conf_value(v)) for k, v in conf.items()))


@dataclass
class Arm:
    """One side of the comparison: a configuration and its timed samples.

    `samples_ms` must be measured at the level the comparison quotes (job
    runtime for a job-level delta, stage duration for a stage-level one) —
    mixing levels is how a 5.8% floor gets applied to a 37.7% comparison.
    """

    name: str
    config: Mapping[str, str]
    samples_ms: list[float] = field(default_factory=list)

    @property
    def reps(self) -> int:
        return len(self.samples_ms)

    @property
    def median_ms(self) -> float:
        return statistics.median(self.samples_ms) if self.samples_ms else 0.0


@dataclass
class MechanismEvidence:
    """Ground truth that the fix ACTED, independent of what it did to runtime.

    Two independent sources, either sufficient:
      * `transition_fired` — the AQE plan transition (`skew_split`) reached
        apex.plan_transitions. Ground truth by contract: Spark's own decision.
      * tail ratios — p99/p50 per rep per arm. A working skew fix collapses
        the ratio far beyond its own measured run-to-run floor.
    """

    transition_fired: bool | None = None    # None = no transition data available
    transition_detail: str = ""
    baseline_ratios: list[float] = field(default_factory=list)
    treatment_ratios: list[float] = field(default_factory=list)


def evaluate_mechanism(evidence: MechanismEvidence | None) -> tuple[bool | None, str]:
    """(confirmed, detail). None = no mechanism data was collected.

    The ratio test obeys the same discipline as the runtime test: the floor is
    the CV of the BASELINE arm's ratios, measured at this level, and the
    collapse must clear it. A mechanism claim below its own floor is the same
    category of fabrication rule 2 exists to block.
    """
    if evidence is None:
        return None, "no mechanism evidence collected"

    parts: list[str] = []
    confirmed: bool | None = None

    if evidence.transition_fired is not None:
        if evidence.transition_fired:
            confirmed = True
            parts.append(
                "the AQE skew_split transition fired — Spark's own re-plan is "
                "ground truth that the mechanism acted"
                + (f" ({evidence.transition_detail})" if evidence.transition_detail else "")
            )
        else:
            confirmed = False
            parts.append("the AQE skew_split transition did NOT fire")

    base_r = [r for r in evidence.baseline_ratios if r > 0]
    treat_r = [r for r in evidence.treatment_ratios if r > 0]
    if base_r and treat_r:
        base_med = statistics.median(base_r)
        treat_med = statistics.median(treat_r)
        delta_pct = 100.0 * (treat_med - base_med) / base_med
        floor = runtime_cv_pct(base_r) if len(base_r) >= MIN_REPS_FOR_FLOOR else None
        ratio_txt = f"tail ratio p99/p50 {base_med:.1f}x -> {treat_med:.1f}x ({delta_pct:+.1f}%)"
        if floor is None:
            parts.append(f"{ratio_txt}; ratio floor unmeasured (< {MIN_REPS_FOR_FLOOR} baseline reps)")
        else:
            collapse = abs(delta_pct) >= floor and delta_pct < 0
            parts.append(f"{ratio_txt} against a measured ±{floor:.1f}% ratio floor")
            if collapse:
                confirmed = True
                parts.append("the tail collapsed well beyond its own run-to-run floor")
            elif confirmed is not False:
                confirmed = False
                parts.append("the tail did not move beyond run-to-run variance")

    if confirmed is None:
        return None, "; ".join(parts) if parts else "no mechanism evidence collected"
    if not confirmed:
        return False, "Mechanism NOT confirmed: " + "; ".join(parts) + "."
    return True, "Mechanism confirmed: " + "; ".join(parts) + "."


def analyse_replay(
    *,
    bench: str,
    baseline: Arm,
    treatment: Arm,
    shape_fidelity: float,
    level: str = "job",
    mechanism: MechanismEvidence | None = None,
) -> Measurement:
    """Reduce two arms to a Measurement with all three contract rules applied.

    The delta is signed, negative = treatment faster, computed on medians.
    `significant` is False — and `resolved_delta_pct` therefore None — when ANY
    of the three rules fails: unattributable arms, unmeasured floor, or a delta
    inside the measured floor. There is no path to a quotable number that
    skips one.
    """
    reps = min(baseline.reps, treatment.reps)
    base_med, treat_med = baseline.median_ms, treatment.median_ms
    delta_pct = 100.0 * (treat_med - base_med) / base_med if base_med > 0 else 0.0

    # ── rule 3: attributability ─────────────────────────────────────────────
    distinct = len({config_identity(baseline.config), config_identity(treatment.config)})
    attributable = distinct >= 2
    if attributable:
        attribution_detail = (
            f"{distinct} distinct configurations in the comparison "
            f"({baseline.name} vs {treatment.name}) — a delta is creditable to the change"
        )
    else:
        attribution_detail = (
            f"both arms canonicalise to the SAME configuration ({distinct} distinct < 2): "
            "the proposed fix is already active in the baseline, or the overlay is empty. "
            "Any observed spread is run-to-run variance with nothing to credit it to — "
            "report 'unattributable', never a percent improvement"
        )

    # ── rule 2: the floor is measured HERE, at this level, or not at all ────
    floor = runtime_cv_pct(baseline.samples_ms) if baseline.reps >= MIN_REPS_FOR_FLOOR else None
    floor_measured = floor is not None

    # ── rule 4: mechanism is judged on its own evidence, not on runtime ─────
    mechanism_confirmed, mechanism_detail = evaluate_mechanism(mechanism)

    return Measurement(
        delta_pct=delta_pct,
        baseline_ms=base_med,
        treatment_ms=treat_med,
        noise_floor_pct=floor if floor_measured else 0.0,
        floor_measured=floor_measured,
        reps=reps,
        bench=bench,
        shape_fidelity=shape_fidelity,
        attributable=attributable,
        attribution_detail=attribution_detail,
        mechanism_confirmed=mechanism_confirmed,
        mechanism_detail=mechanism_detail,
        baseline_samples_ms=list(baseline.samples_ms),
        treatment_samples_ms=list(treatment.samples_ms),
    )


@dataclass(frozen=True)
class BenchShape:
    """The shape a bench actually produces — what fidelity is scored against."""

    name: str
    task_count: int
    p99_p50: float
    bytes_per_task: float
    slots: int


def _ratio_score(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        return 1.0 if a == b else 0.0
    return min(a, b) / max(a, b)


def _bytes_score(a: float, b: float) -> float:
    """Byte magnitudes differ by orders, so score on a log scale: identical
    magnitude = 1.0, three orders of magnitude apart = 0.0."""
    if a <= 0 or b <= 0:
        return 1.0 if a == b else 0.0
    return max(0.0, 1.0 - abs(math.log10(a / b)) / 3.0)


def shape_fidelity(
    observed: StageObservation,
    bench: BenchShape,
    observed_slots: int | None,
) -> float:
    """0–1: how well the bench reproduces the OBSERVED shape.

    Geometric mean of three component ratios — task count, p99/p50, and
    bytes/task (log-scaled) — with a hard cap of 0.5 when the two shapes are
    in different makespan REGIMES: replaying a work-bound finding on a
    tail-bound bench (or vice versa) is different physics, and a high fidelity
    there would be a lie with good decimals. The regime test is skipped (not
    failed) when the observed run's slot count is unknown.
    """
    components = (
        _ratio_score(observed.task_count, bench.task_count),
        _ratio_score(observed.skew_ratio, bench.p99_p50),
        _bytes_score(observed.bytes_per_task, bench.bytes_per_task),
    )
    fidelity = components[0] * components[1] * components[2]
    fidelity = fidelity ** (1.0 / 3.0)

    obs_thr = tail_bound_ratio_threshold(observed.task_count, observed_slots) if observed_slots else None
    bench_thr = tail_bound_ratio_threshold(bench.task_count, bench.slots)
    if obs_thr is not None and bench_thr is not None:
        obs_tail_bound = observed.skew_ratio > obs_thr
        bench_tail_bound = bench.p99_p50 > bench_thr
        if obs_tail_bound != bench_tail_bound:
            fidelity = min(fidelity, 0.5)
    return fidelity


@dataclass(frozen=True)
class PositiveControlResult:
    """Did the harness resolve a fix that is KNOWN to matter on this bench?"""

    passed: bool
    detail: str


def evaluate_positive_control(measurement: Measurement) -> PositiveControlResult:
    """The non-negotiable control, under contract rule 4.

    The control fix is AQE's skew split with coalesce OFF on dev's calibrated
    skew_join bench — a PURE tail redistribution at constant partition count,
    the fix class the makespan model actually covers. (The first control ran
    full AQE, which coalesced 100→17 partitions: W was not conserved, so it
    tested a repartitioning the bound refuses to model. That mis-specification
    — not scale alone — is rule 4's corollary.)

    PASS requires the harness to CONFIRM THE MECHANISM of a fix known to act
    on this exact shape, with attributable arms and a measured floor. The
    runtime outcome is then reported, not gated on:
      * significant runtime delta -> runtime_certified: the bench can certify
        magnitude at this scale.
      * inside the floor -> runtime_unresolved: the bench certifies mechanism
        and defers magnitude. If even a W-conserving control cannot clear the
        floor, that is the honest limit of laptop scale (rule 4).
    If the mechanism itself cannot be confirmed, the bench proves nothing at
    any level and every verdict it emits is unproven.
    """
    if not measurement.attributable:
        return PositiveControlResult(
            passed=False,
            detail=(
                "POSITIVE CONTROL FAILED — the control arms are not attributable "
                f"({measurement.attribution_detail}). The harness compared a "
                "configuration with itself; fix the control setup before trusting "
                "any verdict from this bench."
            ),
        )
    if not measurement.floor_measured:
        return PositiveControlResult(
            passed=False,
            detail=(
                f"POSITIVE CONTROL FAILED — only {measurement.reps} reps per arm "
                f"(< {MIN_REPS_FOR_FLOOR}); the noise floor is unmeasured, so no "
                "delta — including the control's — may be quoted."
            ),
        )
    if measurement.mechanism_confirmed is not True:
        return PositiveControlResult(
            passed=False,
            detail=(
                f"POSITIVE CONTROL FAILED on {measurement.bench} — the mechanism of a "
                "fix known to act on this exact shape could not be confirmed "
                f"({measurement.mechanism_detail or 'no mechanism evidence'}). A bench "
                "that cannot certify even the mechanism certifies nothing; no "
                "verdict from this harness is proven."
            ),
        )
    if measurement.significant and measurement.delta_pct < 0:
        return PositiveControlResult(
            passed=True,
            detail=(
                f"positive control PASSED on {measurement.bench}: mechanism_confirmed "
                f"+ runtime_certified — {measurement.delta_pct:+.1f}% against a measured "
                f"±{measurement.noise_floor_pct:.1f}% floor ({measurement.reps} reps/arm). "
                "The harness can certify BOTH the mechanism and the magnitude of a "
                "real fix at this scale."
            ),
        )
    return PositiveControlResult(
        passed=True,
        detail=(
            f"positive control PASSED on {measurement.bench}: mechanism_confirmed + "
            f"runtime_unresolved — the fix observably acted ({measurement.mechanism_detail}) "
            f"but its {measurement.delta_pct:+.1f}% runtime effect is inside the measured "
            f"±{measurement.noise_floor_pct:.1f}% floor. The bench certifies mechanism and "
            "defers magnitude; if even this W-conserving control cannot clear the "
            "floor, laptop scale cannot certify small runtime effects (contract "
            "rule 4) — that is a limit to report, not to tune away."
        ),
    )


def score_measurement(measurement: Measurement) -> float:
    """Confidence 0–1 in a replayed result, whatever direction it points.

    "No measurable change" at high fidelity is as valuable as a win, so the
    score does not depend on `significant` — it depends on whether the
    measurement is legally quotable at all (attributable, floor measured) and
    on how faithfully the bench reproduced the finding's shape.
    """
    if not measurement.attributable:
        return 0.35  # LOW — a comparison of a config with itself proves nothing
    if not measurement.floor_measured:
        return 0.45  # LOW — timed runs without a floor are anecdotes
    return _MEASURED_BASE_SCORE + _MEASURED_FIDELITY_SPAN * measurement.shape_fidelity


def verdict_from_replay(
    finding: FindingRef,
    proposed_config: Mapping[str, str],
    prediction: Prediction,
    measurement: Measurement,
    safety: SafetyReport,
    config_knowledge: ConfigKnowledge = ConfigKnowledge.UNKNOWN,
) -> Verdict:
    """Assemble the Verdict for a completed two-arm replay."""
    m = measurement
    if not m.attributable:
        evidence = m.attribution_detail
    elif not m.floor_measured:
        evidence = (
            f"Replayed {m.reps} rep(s)/arm on {m.bench} — too few to measure the "
            "noise floor at this level and scale (contract rule 2), so the "
            f"observed {m.delta_pct:+.1f}% may not be quoted."
        )
    elif m.significant:
        evidence = (
            f"Replayed on {m.bench} ({m.reps} reps/arm, fidelity {m.shape_fidelity:.2f}): "
            f"baseline median {m.baseline_ms:,.0f}ms, treatment median {m.treatment_ms:,.0f}ms "
            f"= {m.delta_pct:+.1f}%, outside the measured ±{m.noise_floor_pct:.1f}% floor. "
            f"{m.attribution_detail}."
        )
    else:
        evidence = (
            f"Replayed on {m.bench} ({m.reps} reps/arm, fidelity {m.shape_fidelity:.2f}): "
            f"the observed {m.delta_pct:+.1f}% is inside the measured ±{m.noise_floor_pct:.1f}% "
            "noise floor of the baseline arm — the runtime magnitude is UNRESOLVED, "
            "which is not evidence of zero. The floor was measured at the compared "
            "level and scale, not inherited (contract rule 2)."
        )
        if m.mechanism_confirmed:
            evidence = (
                f"{m.mechanism_detail} The fix observably acted; what cannot be "
                f"certified is its size. " + evidence
            )

    caveats = [
        f"Noise floor measured from the baseline arm's own {m.reps} samples at the "
        f"compared level (contract rule 2); it is not transferable to another level or scale.",
    ]
    if m.shape_fidelity < FIDELITY_CAVEAT_BELOW:
        caveats.append(
            f"Shape fidelity is {m.shape_fidelity:.2f} — the bench only partially "
            "reproduces the observed shape (task count / skew ratio / bytes per task / "
            "makespan regime); treat the measured delta as directional, not exact."
        )
    if prediction.caveats:
        caveats.append(prediction.caveats)

    score = score_measurement(m)
    return Verdict(
        finding_id=finding.finding_id,
        job_id=finding.job_id,
        app_id=finding.app_id,
        proposed_config=dict(proposed_config),
        method=VerifyMethod.REPLAYED,
        predictor=prediction.predictor,
        predicted_delta_pct=prediction.delta_pct,
        predicted_low_pct=prediction.low_pct,
        predicted_high_pct=prediction.high_pct,
        measurement=m,
        safety=safety,
        config_knowledge=config_knowledge,
        confidence=Confidence.from_score(score),
        confidence_score=score,
        evidence=evidence,
        caveats=" ".join(caveats),
        guardrails=list(prediction.guardrails),
    )
