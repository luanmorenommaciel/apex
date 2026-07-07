import os
from typing import Any

from spark_platform.utils.logger import logger

ENV_MODEL_KEY = "CREW_LLM_MODEL"


def build_llm() -> Any | None:
    """Build the CrewAI LLM from CREW_LLM_MODEL (e.g. anthropic/claude-sonnet-4-5).

    Returns None when unconfigured so callers degrade to a detectors-only
    report instead of failing (design D-004 / acceptance test AT-005).
    """
    model = os.environ.get(ENV_MODEL_KEY, "").strip()
    if not model:
        logger.warning(f"{ENV_MODEL_KEY} is not set; Crew A analysis will be skipped")
        return None
    try:
        from crewai import LLM

        # Determinism + cost/latency caps: a diagnostic report should be
        # reproducible (temperature=0), and the completion is bounded so a large
        # physical plan or many findings cannot balloon tokens or hang the run.
        return LLM(
            model=model,
            temperature=0,
            max_tokens=int(os.environ.get("CREW_LLM_MAX_TOKENS", "2000")),
            timeout=int(os.environ.get("CREW_LLM_TIMEOUT_SECONDS", "120")),
        )
    except Exception as exc:
        logger.warning(f"Could not build LLM for model '{model}': {exc}")
        return None
