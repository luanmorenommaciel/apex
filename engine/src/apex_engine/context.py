"""Job-level context: what a stage rule needs that a stage row cannot carry.

A `StageAggregate` is one stage of one run. Three of CONTRACT.md's cross-lane
rules need more than that:

  * rule 1 needs the **cluster width** — an attribute of the run's config, not
    of the stage (`jobconf.JobConf.cluster_width`);
  * rule 2 needs **repeated observations of the same shape** to measure a floor,
    which by definition come from other runs;
  * rule 3 needs the **configurations behind those runs** to decide whether any
    difference between them is creditable to tuning.

`JobContext` bundles exactly that and nothing else. `JobContext.EMPTY` is the
honest zero value — unknown width, no baselines, no history — and it is what the
offline/fixture path gets unless a caller supplies more. Every rule must behave
correctly with EMPTY, degrading to "cannot determine" rather than to a guess.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from .jobconf import JobConf, operator_width
from .noise import Attribution, NoiseFloor, attribution, measure_floor
from .physics import ClusterWidth, TailBound, evaluate_tail_bound
from .schema import StageAggregate


# Two measurements are of the same SCALE when the bytes they move are within this
# factor. Deliberately loose: it separates "the same work again" from "the same
# plan over 10x the data", nothing finer.
SAME_SCALE_FACTOR = 2.0


@dataclass(frozen=True)
class ShapeSample:
    """One run's measurement of one stage shape.

    A shape is `(plan_fingerprint, task_count, stage_id)`. The `stage_id` is in
    the key because a fingerprint is NOT unique within a run — verified on this
    store, where one run has fingerprint `11e45dbd…` on both stage 21 (p99
    1035ms) and stage 22 (p99 51ms) at the same 100 tasks. Pooling those two
    would manufacture a 90% "noise floor" out of two different stages. Stage ids
    are stable across repeated runs of the same DAG (verified: 5 runs, identical
    numbering); when they are not, the baseline simply comes up short and the
    floor reports UNKNOWN, which fails safe.
    """

    job_id: str
    stage_id: int
    plan_fingerprint: str
    task_count: int
    task_duration_p50_ms: float
    task_duration_p99_ms: float
    bytes_touched: int = 0

    @property
    def key(self) -> tuple[str, int, int]:
        return (self.plan_fingerprint, self.task_count, self.stage_id)

    @property
    def ratio(self) -> float:
        return self.task_duration_p99_ms / self.task_duration_p50_ms if self.task_duration_p50_ms else 0.0


@dataclass(frozen=True)
class JobContext:
    """Everything job-scoped a watcher may consult. Frozen and side-effect free."""

    job_conf: JobConf = field(default_factory=JobConf.missing)
    width: ClusterWidth = field(default_factory=ClusterWidth)
    shape_samples: Sequence[ShapeSample] = ()
    run_confs: Mapping[str, JobConf] = field(default_factory=dict)

    # --- rule 1 ------------------------------------------------------------

    def tail_bound(self, stage: StageAggregate) -> TailBound:
        return evaluate_tail_bound(
            n_tasks=stage.task_count,
            p50_ms=stage.task_duration_p50_ms,
            p99_ms=stage.task_duration_p99_ms,
            width=self.width,
        )

    # --- rule 2 ------------------------------------------------------------

    def comparable_runs(self, stage: StageAggregate) -> list[ShapeSample]:
        """One sample per run of this exact shape AT THE SAME CONFIG AND SCALE.

        Three filters, each demanded by a cross-lane rule:

          * same shape — `(plan_fingerprint, task_count, stage_id)`;
          * same CONFIG — rule 3: variation across two different configurations is
            a config effect, not noise. Pooling them inflates the floor and can
            suppress a real finding (measured: 32.9% pooled vs 6.4% same-config on
            stage 21 of the skew bench, which straddles that stage's own 29-40%
            predicted win and made emission flip run to run);
          * same SCALE — rule 2: "measure it at the level AND SCALE you are
            comparing". The same plan over 10x the data is not a repeat of the
            same measurement.

        Deduped by `job_id`: within-run repetition is not run-to-run variance,
        which is the only thing a noise floor may be measured over.
        """
        if not stage.plan_fingerprint:
            return []
        wanted = (stage.plan_fingerprint, stage.task_count, stage.stage_id)
        signature = self.job_conf.signature_map() if self.job_conf.present else None

        by_job: dict[str, ShapeSample] = {}
        for sample in self.shape_samples:
            if sample.key != wanted or not self._same_scale(stage, sample):
                continue
            if signature is not None and not self._same_config(signature, sample.job_id):
                continue
            by_job.setdefault(sample.job_id, sample)
        return [by_job[job_id] for job_id in sorted(by_job)]

    def _same_config(self, signature: Mapping[str, str], job_id: str) -> bool:
        other = self.run_confs.get(job_id)
        # An unknown config cannot be asserted to match. The run being analyzed is
        # always its own comparable, so it is admitted explicitly.
        if other is None or not other.present:
            return job_id == self.job_conf.job_id
        return other.signature_map() == dict(signature)

    @staticmethod
    def _same_scale(stage: StageAggregate, sample: ShapeSample) -> bool:
        """Within a factor of `SAME_SCALE_FACTOR` on bytes moved.

        A comparability window, not a decision threshold: it decides which
        measurements are repeats of each other, never whether a finding fires.
        """
        if not stage.bytes_touched or not sample.bytes_touched:
            return True  # nothing to compare scale on; the shape key still holds
        ratio = stage.bytes_touched / sample.bytes_touched
        return 1 / SAME_SCALE_FACTOR <= ratio <= SAME_SCALE_FACTOR

    def noise_floor(self, stage: StageAggregate) -> NoiseFloor:
        """Measured floor for THIS stage shape at THIS scale, or UNKNOWN.

        Measured over p99 — the quantity a tail claim is about — across repeated
        runs of the same plan at the same task count. The level string carries the
        scale because the floor is meaningless without it (9.2% at job level and
        37.7% at 8-task shape level are both correct on this system).
        """
        samples = self.comparable_runs(stage)
        return measure_floor(
            (s.task_duration_p99_ms for s in samples),
            level=f"stage shape @ {stage.task_count} tasks",
        )

    def ratio_spread(self, stage: StageAggregate) -> list[float]:
        """The p99/p50 ratios this shape produced across runs, for precision."""
        return [s.ratio for s in self.comparable_runs(stage) if s.ratio > 0]

    # --- rule 3 ------------------------------------------------------------

    def attribution(self, stage: StageAggregate) -> Attribution:
        """How many DISTINCT configs are behind the runs of this shape."""
        samples = self.comparable_runs(stage)
        confs = [self.run_confs.get(s.job_id) for s in samples]
        return attribution(c.signature_map() if c else None for c in confs)


EMPTY = JobContext()


def context_for(ctx: JobContext | None) -> JobContext:
    """Every watcher's entry point: a missing context is the EMPTY one."""
    return ctx if ctx is not None else EMPTY


def build_context(
    store,
    job_id: str,
    aggregates: Iterable[StageAggregate],
    *,
    slots: int | None = None,
    slots_source: str = "operator",
) -> JobContext:
    """Assemble the context for one job out of ClickHouse.

    Width precedence: an explicitly supplied `slots` (an operator observation)
    outranks `job_conf`, because the caller has seen the cluster and contract
    v0.4 deliberately does not synthesize the keys that would prove it. If
    neither is available the width stays UNKNOWN — nothing else is consulted,
    and in particular `spark.sql.shuffle.partitions` and `task_count` are never
    read as a width.

    Every read here is best-effort in two directions: v0.4's table may not exist
    yet in a given deployment, and `store` is duck-typed — `analyze()` accepts any
    object with the reads it uses, including stores written before v0.4 existed.
    A store that cannot answer one of these questions costs the run its noise
    floor or its width, never its analysis.
    """
    conf = _ask(store, "job_conf", JobConf.missing(job_id), job_id)
    width = operator_width(slots, slots_source) if slots else conf.cluster_width()

    fingerprints = sorted({s.plan_fingerprint for s in aggregates if s.plan_fingerprint})
    samples = _ask(store, "shape_history", [], fingerprints) if fingerprints else []
    job_ids = sorted({s.job_id for s in samples})
    run_confs = _ask(store, "job_confs", {}, job_ids) if job_ids else {}

    return JobContext(job_conf=conf, width=width, shape_samples=samples, run_confs=run_confs)


def _ask(store, method: str, default, *args):
    """Call an OPTIONAL store read, falling back to an explicit unknown."""
    read = getattr(store, method, None)
    if read is None:
        return default
    try:
        return read(*args)
    except Exception:  # noqa: BLE001 - an enrichment read must never fail analyze()
        return default
