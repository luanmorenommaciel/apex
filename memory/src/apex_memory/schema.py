"""In-memory models for the memory lane, matching the proposed v0.3 DDL.

Field names match `memory/sql/030_plan_memory.sql` and `031_run_outcomes.sql`.
As in the engine lane, the DDL is authoritative if prose and model disagree.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

# The six parameters ZEST tunes (arXiv 2503.03826, Table 1), in the order the
# DDL declares them. Named once here so the extractor, the recommender and the
# ZEST seed loader cannot drift apart.
ZEST_CONFIG_FIELDS: tuple[str, ...] = (
    "conf_shuffle_partitions",
    "conf_executor_instances",
    "conf_executor_cores",
    "conf_executor_memory_mb",
    "conf_driver_cores",
    "conf_driver_memory_mb",
)


class ConfigSource(str, Enum):
    """Where a row's configuration came from.

    UNKNOWN is not a failure state to be tidied away -- it is the honest and
    currently universal answer for Apex-derived rows, because nothing in the
    pipeline emits SparkConf yet (verified: zero `spark.*` keys in
    `spark_events.attributes`). Recall keys its `config_unavailable` reason off
    exactly this value.
    """

    OBSERVED = "observed"
    ZEST_SEED = "zest-seed"
    UNKNOWN = "unknown"


class OutcomeSource(str, Enum):
    APEX = "apex"
    ZEST_SEED = "zest-seed"


class MatchTier(str, Enum):
    """How a historical run was matched to the query plan.

    EXACT is strictly stronger evidence: `plan_fingerprint` equality means the
    literal-normalised logical plans are the same plan. STRUCTURAL means the
    encoder could not tell them apart after redaction, which is a weaker claim
    -- see encoder.py § KNOWN LIMIT.
    """

    EXACT = "exact"
    STRUCTURAL = "structural"


class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RunOutcome(BaseModel):
    """One row of apex.run_outcomes: a plan shape, in a run, and how it went."""

    model_config = ConfigDict(extra="forbid")

    job_id: str
    app_id: str = ""
    app_name: str = ""
    plan_fingerprint: str

    conf_shuffle_partitions: int | None = None
    conf_executor_instances: int | None = None
    conf_executor_cores: int | None = None
    conf_executor_memory_mb: int | None = None
    conf_driver_cores: int | None = None
    conf_driver_memory_mb: int | None = None
    conf_extra: dict[str, str] = Field(default_factory=dict)
    config_source: ConfigSource = ConfigSource.UNKNOWN

    stage_count: int = 0
    task_count: int = 0
    wall_clock_ms: int = 0
    task_time_ms: int = 0
    shuffle_read_bytes: int = 0
    shuffle_write_bytes: int = 0
    spill_disk_bytes: int = 0
    spill_mem_bytes: int = 0
    gc_time_ms: int = 0
    input_bytes: int = 0
    output_bytes: int = 0
    peak_execution_mem_bytes: int = 0
    max_skew_ratio: float = 0.0

    aqe_skew_splits: int = 0
    aqe_coalesces: int = 0
    finding_count: int = 0
    worst_severity: str = ""

    outcome_source: OutcomeSource = OutcomeSource.APEX
    observed_at: datetime
    indexed_at: datetime

    @property
    def observed_conf(self) -> dict[str, str]:
        """The full canonicalised allowlisted SparkConf this run used.

        This -- not the ZEST-six subset -- is what config variation and the
        recommendation are computed over, because in Apex's corpus the ZEST six
        are nearly constant (shuffle.partitions varies; executor.*/driver.* are
        mostly absent) while the AQE knobs are what actually differ between
        runs. Restricting to ZEST's six would report "no configuration
        variation" on a corpus that demonstrably has it.

        An empty dict means no configuration evidence, never "defaults".
        """
        return dict(self.conf_extra)

    @property
    def known_zest_config(self) -> dict[str, int]:
        """The subset of the ZEST six that was actually captured, for parity
        with the paper's parameter set and with any future ZEST-seeded row."""
        return {
            name: value
            for name in ZEST_CONFIG_FIELDS
            if (value := getattr(self, name)) is not None
        }


class SimilarRun(BaseModel):
    """One cited piece of evidence behind a recall result."""

    model_config = ConfigDict(extra="forbid")

    job_id: str
    app_name: str = ""
    plan_fingerprint: str
    tier: MatchTier
    similarity: float
    outcome: RunOutcome

    @property
    def citation(self) -> str:
        """A row a human can go read for themselves."""
        return (
            f"apex.run_outcomes WHERE plan_fingerprint='{self.plan_fingerprint}' "
            f"AND job_id='{self.job_id}'"
        )


class PredictedDelta(BaseModel):
    """A predicted improvement, gated on the measured run-to-run noise floor."""

    model_config = ConfigDict(extra="forbid")

    metric: str = "task_time_ms"
    baseline_value: float
    best_value: float
    delta_pct: float
    meaningful: bool
    noise_floor_pct: float
    reason: str


class ConfigRecommendation(BaseModel):
    """A recommended configuration, or an explicit refusal to invent one."""

    model_config = ConfigDict(extra="forbid")

    available: bool
    # Real `spark.*` keys mapped to canonical values, so the result can be
    # pasted into a spark-submit rather than translated first.
    config: dict[str, str] = Field(default_factory=dict)
    # How many contributing runs actually carried each key. A key supported by
    # one run out of six is a far weaker recommendation than one they all
    # agreed on, and hiding that difference would overstate the whole result.
    key_support: dict[str, int] = Field(default_factory=dict)
    contributor_count: int = 0
    # Keys where the recommendation differs from what the querying run used.
    # More than one entry means history compared BUNDLES, not individual knobs,
    # so the gain cannot be attributed to any single setting -- stated plainly
    # because "switch AQE on for 69%" would be a stronger claim than the
    # evidence supports when partitions and advisory size also changed.
    differs_from_current: dict[str, str] = Field(default_factory=dict)
    derived_from_jobs: list[str] = Field(default_factory=list)
    method: str = ""
    reason: str = ""


class RecallResult(BaseModel):
    """What recall() returns. Read-only; nothing here mutates any table."""

    model_config = ConfigDict(extra="forbid")

    query_plan_fingerprint: str | None = None
    query_job_id: str | None = None
    encoder_version: str

    similar_runs: list[SimilarRun] = Field(default_factory=list)
    best_known_config: ConfigRecommendation
    predicted_delta: PredictedDelta | None = None

    confidence: Confidence
    confidence_score: float
    confidence_reasons: list[str] = Field(default_factory=list)

    n_exact_jobs: int = 0
    n_structural_jobs: int = 0
    n_distinct_fingerprints: int = 0
    n_config_variants: int = 0

    # Mirrors serve/'s convention. `plan_json` and any text echoed out of a
    # finding is written by the OBSERVED SPARK JOB, not by Apex -- an
    # indirect-injection vector. Naming the untrusted fields on every response
    # keeps that visible to whatever consumes this.
    untrusted_fields: list[str] = Field(
        default_factory=lambda: ["similar_runs[].outcome.worst_severity", "sample_plan_json"]
    )
