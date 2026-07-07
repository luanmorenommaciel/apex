import os
from pathlib import Path

import yaml
from pydantic import BaseModel

DEFAULT_THRESHOLDS_PATH = Path(__file__).resolve().parents[1] / "config" / "diagnostics.yaml"


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
