"""recall() — the read-only API engine/ and serve/ consume.

    recall(store, job_id=...)           # what do I know about this run?
    recall(store, plan_fingerprint=...) # ...about this exact plan?
    recall(store, plan_json=...)        # ...about a plan I have not run yet?

The third form is the ZEST case: a plan that has never executed still has a
logical plan, so it can be matched against history and configured before its
first run. Nothing in this module writes.

Retrieval is two-tiered, strongest evidence first:
  1. EXACT      -- `plan_fingerprint` equality. Same literal-normalised logical
                   plan, so the historical run did the same work.
  2. STRUCTURAL -- cosine over the encoder's vector. Weaker: it means the plans
                   are indistinguishable after redaction, not that they are the
                   same query (encoder.py § KNOWN LIMIT).
"""

from __future__ import annotations

from .clickhouse import (
    JOB_CONF_SQL,
    NEIGHBOURS_SQL,
    OUTCOMES_FOR_FINGERPRINTS_SQL,
    SHAPE_OUTCOMES_SQL,
    MemoryStore,
    normalise_fingerprint,
)
import statistics

from .conf import canonicalise, config_identity, pool_configs
from .config import (
    DEFAULT_TOP_K,
    ENCODER_VERSION,
    MIN_RUNS_PER_CONFIG_GROUP,
    MIN_SIMILARITY,
)
from .confidence import estimate_noise_floor, predict_delta, score_confidence
from .encoder import VECTOR_DIM, encode
from .schema import (
    ConfigRecommendation,
    Confidence,
    MatchTier,
    RecallResult,
    RunOutcome,
    SimilarRun,
)

EMBEDDING_SQL = """
SELECT embedding, sample_plan_json
FROM apex.plan_memory FINAL
WHERE plan_fingerprint = toFixedString({fp:String}, 64)
  AND encoder_version = {encoder_version:String}
LIMIT 1
"""


def _row_to_outcome(row: dict) -> RunOutcome:
    row = dict(row)
    row["plan_fingerprint"] = normalise_fingerprint(row["plan_fingerprint"])
    return RunOutcome.model_validate(row)


def _baseline_shape(
    store: MemoryStore, job_id: str, plan_fingerprint: str | None = None
) -> tuple[str | None, dict | None]:
    """The querying job's own row for the shape being recalled.

    With no fingerprint supplied, the dominant shape is chosen:
    SHAPE_OUTCOMES_SQL orders by task_time_ms DESC, so the first row is the
    shape the job actually spent its time in. Ranking by stage count instead
    would favour a shape appearing in many trivial stages over the one that
    costs real money.

    When a fingerprint IS supplied alongside a job_id, the baseline must still
    be resolved -- for that specific shape. Skipping it there would silently
    drop predicted_delta from every `recall(job_id=..., plan_fingerprint=...)`
    call, which is the natural way engine/ will ask about a non-dominant stage.
    """
    shapes = store.query(SHAPE_OUTCOMES_SQL, {"job_id": job_id})
    if not shapes:
        return plan_fingerprint, None
    if plan_fingerprint:
        for shape in shapes:
            if normalise_fingerprint(shape["plan_fingerprint"]) == plan_fingerprint:
                return plan_fingerprint, shape
        return plan_fingerprint, None
    top = shapes[0]
    return normalise_fingerprint(top["plan_fingerprint"]), top


def _config_groups(pool: list[SimilarRun]) -> dict[tuple, list[SimilarRun]]:
    """Group matched runs by canonical configuration identity."""
    groups: dict[tuple, list[SimilarRun]] = {}
    for m in pool:
        if m.outcome.observed_conf:
            groups.setdefault(config_identity(m.outcome.observed_conf), []).append(m)
    return groups


def _median_task_time(runs: list[SimilarRun]) -> float:
    return statistics.median([r.outcome.task_time_ms for r in runs])


def _recommend_config(
    matches: list[SimilarRun],
    current_conf: dict[str, str] | None = None,
) -> tuple[ConfigRecommendation, int]:
    """Recommend a configuration from history.

    TWO REGIMES, because the right method depends on what the evidence supports.

    * A/B regime -- the matched runs include two or more distinct configurations
      with enough support to compare. Then history contains a direct experiment,
      and the answer is the configuration that actually won: a config someone
      really ran and measured, reported verbatim. Averaging here would be
      strictly worse, producing a blend that was never executed and may sit
      between two good settings at a bad one.

    * ZEST regime -- only one configuration per shape, so there is no experiment
      to read, only neighbours. This is the situation ZEST Algorithm 1 addresses,
      and it is applied as written: parameter-wise mean over neighbours (with
      majority vote for booleans, which the paper does not cover since it tunes
      only numeric parameters).

    Exact matches are never diluted with structural ones. If any exact match
    exists the pool is exact-only -- averaging a same-plan observation together
    with a merely-similar-looking one throws away what the fingerprint bought.
    """
    exact = [m for m in matches if m.tier is MatchTier.EXACT]
    pool = exact or matches

    groups = _config_groups(pool)
    n_variants = len(groups)

    supported = {k: v for k, v in groups.items() if len(v) >= MIN_RUNS_PER_CONFIG_GROUP}
    if n_variants >= 2 and len(supported) >= 2:
        winner_id, winner_runs = min(supported.items(), key=lambda kv: _median_task_time(kv[1]))
        runner_median = sorted(_median_task_time(v) for v in supported.values())[1]
        winner_conf = dict(winner_id)
        differs = {
            k: v for k, v in winner_conf.items() if (current_conf or {}).get(k) != v
        } if current_conf else {}
        bundle_note = (
            f" NOTE: this differs from the current run in {len(differs)} keys "
            f"({', '.join(sorted(differs))}), so the gain is attributable to the "
            f"bundle as a whole and NOT to any single setting -- history never "
            f"varied them independently."
            if len(differs) > 1
            else ""
        )
        return (
            ConfigRecommendation(
                available=True,
                config=winner_conf,
                key_support={k: len(winner_runs) for k in winner_conf},
                contributor_count=len(winner_runs),
                differs_from_current=differs,
                derived_from_jobs=sorted({r.job_id for r in winner_runs}),
                method=(
                    f"A/B over history: {len(supported)} configurations with "
                    f"{MIN_RUNS_PER_CONFIG_GROUP}+ runs each were compared by "
                    f"median task_time_ms; this one won "
                    f"({_median_task_time(winner_runs):.0f} ms vs "
                    f"{runner_median:.0f} ms next best) over "
                    f"{len(winner_runs)} run(s). Reported as actually run, not "
                    f"averaged.{bundle_note}"
                ),
            ),
            n_variants,
        )

    # Best observed run per distinct plan shape, so a shape that happens to have
    # run 40 times cannot outvote one that ran twice.
    best_per_shape: dict[str, SimilarRun] = {}
    for m in pool:
        cur = best_per_shape.get(m.plan_fingerprint)
        if cur is None or m.outcome.task_time_ms < cur.outcome.task_time_ms:
            best_per_shape[m.plan_fingerprint] = m

    contributors = [m for m in best_per_shape.values() if m.outcome.observed_conf]

    if not contributors:
        return (
            ConfigRecommendation(
                available=False,
                reason=(
                    "config_unavailable: none of the matched historical runs has "
                    "a row in apex.job_conf, so there is no configuration to "
                    "recommend. No default is substituted -- a guessed config "
                    "presented as evidence would be worse than no answer."
                ),
            ),
            0,
        )

    pooled, support = pool_configs([m.outcome.observed_conf for m in contributors])

    return (
        ConfigRecommendation(
            available=True,
            config=pooled,
            key_support=support,
            contributor_count=len(contributors),
            derived_from_jobs=sorted(m.job_id for m in contributors),
            method=(
                f"ZEST Algorithm 1: parameter-wise mean (numeric) / majority "
                f"vote (boolean) over the best-observed config of each of "
                f"{len(contributors)} matched plan shape(s), "
                f"{'exact' if exact else 'structural'} tier. No configuration "
                f"A/B exists in this history, so neighbours are pooled rather "
                f"than compared."
            ),
        ),
        n_variants,
    )


def recall(
    store: MemoryStore,
    *,
    job_id: str | None = None,
    plan_fingerprint: str | None = None,
    plan_json: str | None = None,
    top_k: int = DEFAULT_TOP_K,
    min_similarity: float = MIN_SIMILARITY,
) -> RecallResult:
    """Recall what history knows about a plan shape. Read-only."""
    if not any((job_id, plan_fingerprint, plan_json)):
        raise ValueError("recall() needs one of job_id, plan_fingerprint or plan_json")

    baseline: dict | None = None
    vector: list[float] | None = None

    if job_id:
        plan_fingerprint, baseline = _baseline_shape(store, job_id, plan_fingerprint)

    if plan_json is not None:
        feats = encode(plan_json)
        vector = feats.vector if feats.encodable else None
    elif plan_fingerprint:
        rows = store.query(
            EMBEDDING_SQL,
            {"fp": plan_fingerprint, "encoder_version": ENCODER_VERSION},
        )
        if rows and rows[0]["embedding"]:
            vector = list(rows[0]["embedding"])

    # ── Tier 1: exact fingerprint matches ────────────────────────────────────
    matches: list[SimilarRun] = []
    seen: set[tuple[str, str]] = set()

    if plan_fingerprint:
        for row in store.query(
            OUTCOMES_FOR_FINGERPRINTS_SQL, {"fps": [plan_fingerprint]}
        ):
            outcome = _row_to_outcome(row)
            if outcome.job_id == job_id:
                continue  # a run is not evidence about itself
            seen.add((outcome.job_id, outcome.plan_fingerprint))
            matches.append(
                SimilarRun(
                    job_id=outcome.job_id,
                    app_name=outcome.app_name,
                    plan_fingerprint=outcome.plan_fingerprint,
                    tier=MatchTier.EXACT,
                    similarity=1.0,
                    outcome=outcome,
                )
            )

    # ── Tier 2: structural neighbours ────────────────────────────────────────
    if vector:
        neighbours = store.query(
            NEIGHBOURS_SQL,
            {
                "vec": vector,
                "encoder_version": ENCODER_VERSION,
                "dim": VECTOR_DIM,
                "self_fp": plan_fingerprint or "0" * 64,
                "top_k": top_k,
            },
        )
        sims = {
            normalise_fingerprint(n["plan_fingerprint"]): float(n["similarity"])
            for n in neighbours
            if float(n["similarity"]) >= min_similarity
        }
        if sims:
            for row in store.query(
                OUTCOMES_FOR_FINGERPRINTS_SQL, {"fps": sorted(sims)}
            ):
                outcome = _row_to_outcome(row)
                key = (outcome.job_id, outcome.plan_fingerprint)
                if outcome.job_id == job_id or key in seen:
                    continue
                seen.add(key)
                matches.append(
                    SimilarRun(
                        job_id=outcome.job_id,
                        app_name=outcome.app_name,
                        plan_fingerprint=outcome.plan_fingerprint,
                        tier=MatchTier.STRUCTURAL,
                        similarity=sims[outcome.plan_fingerprint],
                        outcome=outcome,
                    )
                )

    matches.sort(key=lambda m: (m.tier is not MatchTier.EXACT, -m.similarity,
                                m.outcome.task_time_ms))

    # ── Aggregate the evidence ───────────────────────────────────────────────
    exact_jobs = {m.job_id for m in matches if m.tier is MatchTier.EXACT}
    structural_jobs = {m.job_id for m in matches if m.tier is MatchTier.STRUCTURAL}

    current_conf: dict[str, str] = {}
    if job_id:
        conf_rows = store.query(JOB_CONF_SQL, {"job_id": job_id})
        if conf_rows:
            current_conf = canonicalise(dict(conf_rows[0]["conf"]))

    recommendation, n_config_variants = _recommend_config(matches, current_conf)

    mean_similarity = (
        sum(m.similarity for m in matches) / len(matches) if matches else 0.0
    )
    confidence, score, reasons = score_confidence(
        n_exact_jobs=len(exact_jobs),
        n_structural_jobs=len(structural_jobs),
        n_config_variants=n_config_variants,
        mean_similarity=mean_similarity,
    )

    # ── Predicted delta ──────────────────────────────────────────────────────
    delta = None
    if matches and baseline is not None:
        exact_pool = [m for m in matches if m.tier is MatchTier.EXACT] or matches
        groups = _config_groups(exact_pool)

        # The floor is measured from spread WITHIN each configuration, which is
        # by construction not caused by configuration.
        floor, basis = estimate_noise_floor(
            [[r.outcome.task_time_ms for r in runs] for runs in groups.values()]
        )

        if groups:
            best_runs = min(groups.values(), key=_median_task_time)
            best_value = _median_task_time(best_runs)
            best_input = statistics.median([r.outcome.input_bytes for r in best_runs])
            best_n = len(best_runs)
        else:
            # No configuration captured anywhere in the pool. Gate 1 will
            # suppress this regardless; the single fastest run is used only so
            # the reported numbers are not fabricated.
            fastest = min(matches, key=lambda m: m.outcome.task_time_ms)
            best_value = float(fastest.outcome.task_time_ms)
            best_input = fastest.outcome.input_bytes
            best_n = 1

        delta = predict_delta(
            baseline_task_time_ms=float(baseline["task_time_ms"]),
            best_task_time_ms=float(best_value),
            baseline_input_bytes=int(baseline["input_bytes"]),
            best_input_bytes=int(best_input),
            n_config_variants=n_config_variants,
            best_group_n=best_n,
            noise_floor_pct=floor,
            noise_floor_basis=basis,
        )

    if confidence is Confidence.LOW and matches:
        reasons.append(
            "treat this as a lead to verify, not a recommendation to apply"
        )

    return RecallResult(
        query_plan_fingerprint=plan_fingerprint,
        query_job_id=job_id,
        encoder_version=ENCODER_VERSION,
        similar_runs=matches,
        best_known_config=recommendation,
        predicted_delta=delta,
        confidence=confidence,
        confidence_score=score,
        confidence_reasons=reasons,
        n_exact_jobs=len(exact_jobs),
        n_structural_jobs=len(structural_jobs),
        n_distinct_fingerprints=len({m.plan_fingerprint for m in matches}),
        n_config_variants=n_config_variants,
    )
