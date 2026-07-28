"""Measured noise floor + attributability. CONTRACT.md cross-lane rules 2 and 3.

**Rule 2 — the floor is MEASURED, never hardcoded.** On this one system the
floor is 5.8% (job level, tiny scale), 9.2% (job level, calibrated scale) and
37.7% (shape level, 8 tasks, byte-identical work). A single constant cannot be
right at three scales at once, so there is no constant in this module: a floor
is only ever the coefficient of variation of repeated observations *at the level
and scale being compared*. When no repetition exists, the floor is `None` —
UNKNOWN, which is a different statement from "zero" and is reported as such.

Noise proves a delta is *unresolvable*, never that it is *zero*. So this module
answers "may this number be rendered?" and never "is this number 0?".

**Rule 3 — a delta is creditable to tuning only if it is ATTRIBUTABLE.** Fewer
than 2 distinct configurations in history means every observed difference is
run-to-run variance by construction, whatever the noise floor says. Clearing the
floor is necessary, not sufficient. (The case that forced the rule: byte-identical
shuffle/spill across 4 runs still spanned 18.65% in task time.)

Pure; no I/O, no thresholds, no defaults.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

# The smallest sample that has a spread at all. Two points give a CV, but a CV
# from two points is a range, not a dispersion — three is the smallest honest
# floor and is what verify/ uses for the same measurement.
MIN_SAMPLES_FOR_FLOOR = 3


@dataclass(frozen=True)
class NoiseFloor:
    """A floor that was measured, or an explicit admission that none was.

    `pct is None` means UNKNOWN. Callers must branch on that rather than
    defaulting to 0 — a zero floor silently asserts that every delta is real.
    """

    pct: float | None = None
    samples: int = 0
    level: str = "unmeasured"
    detail: str = "no repeated observations at this level, so no floor is known"

    @property
    def known(self) -> bool:
        return self.pct is not None

    def resolves(self, delta_pct: float | None) -> bool | None:
        """Can a delta of this size be told apart from noise? None = unknown."""
        if delta_pct is None or self.pct is None:
            return None
        return abs(delta_pct) > self.pct

    def __str__(self) -> str:
        if not self.known:
            return f"unknown ({self.detail})"
        return f"{self.pct:.1f}% measured over {self.samples} runs at {self.level} level"


UNKNOWN_FLOOR = NoiseFloor()


def cv_pct(values: Iterable[float]) -> float | None:
    """Coefficient of variation in percent. None below 2 samples.

    Same computation verify/ uses (`runtime_cv_pct`), so a floor quoted by one
    lane means the same thing in the other.
    """
    vals = [float(v) for v in values if v is not None and float(v) > 0]
    if len(vals) < 2:
        return None
    mean = statistics.mean(vals)
    if mean <= 0:
        return None
    return 100.0 * statistics.stdev(vals) / mean


def measure_floor(
    values: Iterable[float],
    *,
    level: str,
    min_samples: int = MIN_SAMPLES_FOR_FLOOR,
) -> NoiseFloor:
    """Measure the floor at one level, or return UNKNOWN with the reason.

    `level` names what was compared ("stage shape @ 100 tasks", "job runtime").
    It is carried into evidence because a floor is only meaningful with it:
    9.2% at job level and 37.7% at shape level are both correct.
    """
    vals = [float(v) for v in values if v is not None and float(v) > 0]
    if len(vals) < min_samples:
        return NoiseFloor(
            pct=None,
            samples=len(vals),
            level=level,
            detail=(
                f"{len(vals)} comparable run(s) at {level} level, "
                f"below the {min_samples} needed to measure a floor"
            ),
        )
    pct = cv_pct(vals)
    if pct is None:
        return NoiseFloor(pct=None, samples=len(vals), level=level,
                          detail=f"{len(vals)} runs at {level} level carry no usable spread")
    return NoiseFloor(
        pct=pct,
        samples=len(vals),
        level=level,
        detail=f"CV of {len(vals)} repeated runs at {level} level",
    )


def config_signature(conf: Mapping[str, str] | None) -> str:
    """A stable identity for one configuration, for counting DISTINCT configs.

    Values are compared as the strings Spark reported. Two runs that differ only
    in how a value was spelled (`5` vs `5.0`) would count as distinct here, which
    biases rule 3 toward *more* configs and therefore toward crediting a delta —
    so callers pass values already normalized by `jobconf.normalize_value`.
    """
    if not conf:
        return ""
    return "|".join(f"{k}={conf[k]}" for k in sorted(conf))


@dataclass(frozen=True)
class Attribution:
    """Rule 3: is a difference between runs creditable to a config change?"""

    runs: int = 0
    distinct_configs: int = 0

    @property
    def creditable(self) -> bool:
        return self.distinct_configs >= 2

    def explain(self) -> str:
        if self.runs == 0:
            return "no run history for this shape, so no delta is attributable to tuning"
        if self.creditable:
            return (
                f"history holds {self.distinct_configs} distinct configs over {self.runs} runs, "
                f"so a difference between them can be credited to a config change"
            )
        return (
            f"history holds {self.distinct_configs} distinct config over {self.runs} runs — "
            f"under the 2 required, so any difference between these runs is run-to-run "
            f"variance, not the effect of tuning"
        )


def attribution(confs: Iterable[Mapping[str, str] | None]) -> Attribution:
    """Count runs and DISTINCT configurations behind them (rule 3)."""
    signatures = [config_signature(c) for c in confs]
    return Attribution(
        runs=len(signatures),
        distinct_configs=len({s for s in signatures if s}),
    )
