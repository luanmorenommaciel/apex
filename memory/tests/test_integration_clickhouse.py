"""Live ClickHouse integration. Auto-skips when the store is down.

Mirrors engine/'s convention: the deterministic suite must pass with no
infrastructure, and these add coverage when infra/ is up.
"""

from __future__ import annotations

import pytest

from apex_memory.clickhouse import MemoryStore
from apex_memory.config import ENCODER_VERSION
from apex_memory.encoder import VECTOR_DIM
from apex_memory.recall import recall
from apex_memory.schema import Confidence

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def store():
    candidate = MemoryStore()
    try:
        candidate.query("SELECT 1")
    except Exception:  # noqa: BLE001
        pytest.skip("ClickHouse unavailable")
    if not candidate.query("SELECT count() AS n FROM apex.plan_memory FINAL")[0]["n"]:
        pytest.skip("plan_memory empty — run `python -m apex_memory index` first")
    return candidate


def test_every_indexed_embedding_matches_the_current_encoder(store):
    """A stale-dimension row would make cosineDistance error or silently
    mis-rank, so the index must never mix encoder generations."""
    row = store.query(
        "SELECT min(dim) AS lo, max(dim) AS hi, uniqExact(encoder_version) AS versions "
        "FROM apex.plan_memory FINAL"
    )[0]
    assert row["lo"] == row["hi"] == VECTOR_DIM
    assert row["versions"] == 1


def test_no_degenerate_plan_in_the_fuzzy_index(store):
    """Single-node plans all collapse to one point; the live store contains 52
    such fingerprints that would otherwise be perfect-similarity neighbours."""
    assert store.query(
        "SELECT min(node_count) AS n FROM apex.plan_memory FINAL"
    )[0]["n"] >= 2


def test_no_zero_vectors(store):
    assert store.query(
        "SELECT count() AS n FROM apex.plan_memory FINAL WHERE length(embedding) = 0"
    )[0]["n"] == 0


def test_recall_returns_cited_evidence(store):
    row = store.query(
        "SELECT toString(plan_fingerprint) AS fp, any(job_id) AS sample_job, "
        "uniqExact(job_id) AS jobs FROM apex.run_outcomes FINAL "
        "GROUP BY plan_fingerprint ORDER BY jobs DESC LIMIT 1"
    )[0]
    if row["jobs"] < 2:
        pytest.skip("no cross-job history in the store")

    result = recall(store, job_id=row["sample_job"], plan_fingerprint=row["fp"])
    assert result.similar_runs
    assert all(r.job_id != row["sample_job"] for r in result.similar_runs)
    assert all(r.citation for r in result.similar_runs)
    assert result.encoder_version == ENCODER_VERSION


def test_a_meaningful_delta_always_clears_its_own_floor_and_has_two_configs(store):
    """Contract v0.4 rule 3, asserted against whatever is really stored."""
    for row in store.query(
        "SELECT toString(plan_fingerprint) AS fp, any(job_id) AS sample_job "
        "FROM apex.run_outcomes FINAL GROUP BY plan_fingerprint "
        "HAVING uniqExact(job_id) > 1 LIMIT 10"
    ):
        result = recall(store, job_id=row["sample_job"], plan_fingerprint=row["fp"])
        delta = result.predicted_delta
        if delta and delta.meaningful:
            assert delta.delta_pct > delta.noise_floor_pct
            assert result.n_config_variants >= 2
        if delta:
            assert delta.reason


def test_thin_history_reads_low(store):
    thin = store.query(
        "SELECT toString(plan_fingerprint) AS fp FROM apex.run_outcomes FINAL "
        "GROUP BY plan_fingerprint HAVING uniqExact(job_id) <= 2 LIMIT 1"
    )
    if not thin:
        pytest.skip("no thin-history shape in the store")
    assert recall(store, plan_fingerprint=thin[0]["fp"]).confidence is Confidence.LOW


def test_apex_is_not_claimed_to_be_zest_seeded(store):
    assert store.query(
        "SELECT count() AS n FROM apex.run_outcomes FINAL "
        "WHERE outcome_source = 'zest-seed'"
    )[0]["n"] == 0
