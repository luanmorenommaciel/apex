import os
from pathlib import Path

import yaml
from pydantic import BaseModel

from apex_diagnostics.models import Severity

DEFAULT_THRESHOLDS_PATH = Path(__file__).resolve().parents[1] / "config" / "diagnostics.yaml"
# Plan-text anti-pattern catalog (Seam 1b) — same config/ dir as the thresholds
# so it ships in the Spark image. detectors/plans.py loads it instead of a
# hardcoded list, so new plan-text patterns are a YAML edit, not a code change.
DEFAULT_ANTI_PATTERNS_PATH = Path(__file__).resolve().parents[1] / "config" / "anti_patterns.yaml"
# Conf recommendation grounding map (Seam 2) — same config/ dir so it ships in
# the image. crew/recommendations.py loads it to ground the Crew's writer agent.
DEFAULT_CONF_RECOMMENDATIONS_PATH = Path(__file__).resolve().parents[1] / "config" / "conf_recommendations.yaml"


class SkewThresholds(BaseModel):
    warning_ratio: float = 3.0
    critical_ratio: float = 6.0
    min_tasks: int = 8
    min_duration_ms: int = 5000


class ShuffleThresholds(BaseModel):
    warning_shuffle_bytes: int = 256 * 1024 * 1024
    critical_shuffle_bytes: int = 1024 * 1024 * 1024
    min_shuffle_bytes: int = 16 * 1024 * 1024


class PlanThresholds(BaseModel):
    info_replan_count: int = 3


class GCThresholds(BaseModel):
    warning_ratio: float = 0.10
    critical_ratio: float = 0.20
    min_stage_duration_ms: int = 5000


class DiagnosticsThresholds(BaseModel):
    skew: SkewThresholds = SkewThresholds()
    shuffle: ShuffleThresholds = ShuffleThresholds()
    plans: PlanThresholds = PlanThresholds()
    gc: GCThresholds = GCThresholds()


class PlanPattern(BaseModel):
    """One plan-text anti-pattern loaded from anti_patterns.yaml.

    `signal` is matched as a substring against a SQL execution's physical plan
    text (initial + AQE-adaptive). Pydantic coerces the YAML `severity` string
    into the Severity enum on load, so an invalid severity fails fast at parse
    time rather than at detection time.
    """

    id: str
    name: str
    signal: str
    severity: Severity
    explanation: str


class ConfRecommendation(BaseModel):
    """One grounding recommendation loaded from conf_recommendations.yaml (Seam 2).

    Keyed by (detector, severity) and, for the plans detector, an optional
    `pattern_match` on the finding's evidence["pattern"]. A null `conf_key`
    means the fix is a code change, not a spark.conf setting — the rationale
    still grounds the writer agent.
    """

    detector: str
    severity: Severity
    pattern_match: str | None = None
    conf_key: str | None = None
    suggested_value: str | None = None
    rationale: str


class ClickHouseSettings(BaseModel):
    host: str = "localhost"
    port: int = 28123
    database: str = "spark_observability"
    user: str = "spv0"
    # No committed secret default: a real password must come from the
    # environment (see load_clickhouse_settings). An empty default keeps the
    # model constructible for tests but never ships a usable credential.
    password: str = ""


def load_thresholds(config_path: str | Path | None = None) -> DiagnosticsThresholds:
    path = Path(config_path) if config_path else DEFAULT_THRESHOLDS_PATH
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return DiagnosticsThresholds.model_validate(raw)


def load_plan_patterns(config_path: str | Path | None = None) -> list[PlanPattern]:
    """Load the plan-text anti-pattern catalog (Seam 1b).

    Returns them in file order so a stable, predictable finding order is
    preserved. An empty or `plan_patterns`-less file yields an empty list,
    which safely disables plan-text scanning without breaking the detector.
    """
    path = Path(config_path) if config_path else DEFAULT_ANTI_PATTERNS_PATH
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return [PlanPattern.model_validate(entry) for entry in raw.get("plan_patterns", [])]


def load_conf_recommendations(config_path: str | Path | None = None) -> list[ConfRecommendation]:
    """Load the conf recommendation grounding map (Seam 2).

    An empty or `recommendations`-less file yields an empty list, which safely
    disables grounding (the writer agent falls back to its own knowledge)
    without breaking the crew pipeline.
    """
    path = Path(config_path) if config_path else DEFAULT_CONF_RECOMMENDATIONS_PATH
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return [ConfRecommendation.model_validate(entry) for entry in raw.get("recommendations", [])]


def load_clickhouse_settings() -> ClickHouseSettings:
    # Fail fast on a missing password instead of falling back to a known,
    # committed credential — mirrors the compose-level `${CLICKHOUSE_PASSWORD:?}`
    # guard so the app never silently connects with a public default secret.
    password = os.environ.get("CLICKHOUSE_PASSWORD")
    if not password:
        raise RuntimeError(
            "CLICKHOUSE_PASSWORD is not set. Export it (e.g. from .env) before "
            "running diagnostics; there is no default credential."
        )
    return ClickHouseSettings(
        host=os.environ.get("CLICKHOUSE_HTTP_HOST", "localhost"),
        port=int(os.environ.get("CLICKHOUSE_HTTP_PORT", "28123")),
        database=os.environ.get("CLICKHOUSE_DB", "spark_observability"),
        user=os.environ.get("CLICKHOUSE_USER", "spv0"),
        password=password,
    )
