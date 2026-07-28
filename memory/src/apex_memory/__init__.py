"""apex-memory — cross-job plan memory for APEX.

Gives Apex an answer to a question no single-run analyser can reach: "I have
seen this plan shape N times before; here is what actually worked."

Public surface:
    encode(plan_text)        -> PlanFeatures      (deterministic, offline)
    recall(...)              -> RecallResult      (read-only, ClickHouse)
"""

from __future__ import annotations

from .config import ENCODER_VERSION, NOISE_FLOOR_PCT
from .encoder import PlanFeatures, cosine_similarity, encode

__all__ = [
    "ENCODER_VERSION",
    "NOISE_FLOOR_PCT",
    "PlanFeatures",
    "cosine_similarity",
    "encode",
]
__version__ = "0.1.0"
