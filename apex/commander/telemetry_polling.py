"""Polling helpers for Commander telemetry availability."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from apex.commander.telemetry_store import query_envelopes

DEFAULT_POLL_ATTEMPTS = 5
DEFAULT_POLL_INTERVAL_SECONDS = 1.0
MAX_POLL_ATTEMPTS = 60
MAX_POLL_INTERVAL_SECONDS = 60.0
RULE_SET = "apex.commander.telemetry_polling.v1"


def poll_for_telemetry(
    store: Any,
    job_id: str,
    *,
    attempts: int = DEFAULT_POLL_ATTEMPTS,
    interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
    sleeper: Callable[[float], None] | None = None,
) -> dict[str, Any]:
    """Wait until at least one envelope for ``job_id`` is visible in the store."""

    validation = validate_poll_settings(attempts, interval_seconds)
    if validation["status"] != "ok":
        return validation

    validated_attempts = validation["attempts"]
    validated_interval = validation["interval_seconds"]

    sleep = sleeper or time.sleep
    for attempt in range(1, validated_attempts + 1):
        envelopes = query_envelopes(store, job_id)
        if envelopes:
            return {
                "status": "found",
                "rule_set": RULE_SET,
                "job_id": job_id,
                "attempt": attempt,
                "attempts": validated_attempts,
                "interval_seconds": validated_interval,
                "envelope_count": len(envelopes),
            }

        if attempt < validated_attempts and validated_interval > 0:
            sleep(validated_interval)

    return {
        "status": "not_found",
        "rule_set": RULE_SET,
        "job_id": job_id,
        "attempt": validated_attempts,
        "attempts": validated_attempts,
        "interval_seconds": validated_interval,
        "envelope_count": 0,
    }


def validate_poll_settings(attempts: int, interval_seconds: float) -> dict[str, Any]:
    """Validate polling settings without touching the telemetry store."""

    validated_attempts = _validate_attempts(attempts)
    if isinstance(validated_attempts, dict):
        return validated_attempts

    validated_interval = _validate_interval(interval_seconds)
    if isinstance(validated_interval, dict):
        return validated_interval

    return {
        "status": "ok",
        "rule_set": RULE_SET,
        "attempts": validated_attempts,
        "interval_seconds": validated_interval,
    }


def _validate_attempts(value: int) -> int | dict[str, Any]:
    if isinstance(value, bool) or not isinstance(value, int):
        return {
            "status": "invalid_poll_attempts",
            "rule_set": RULE_SET,
            "reason": "attempts must be an integer",
        }
    if value < 1 or value > MAX_POLL_ATTEMPTS:
        return {
            "status": "invalid_poll_attempts",
            "rule_set": RULE_SET,
            "reason": f"attempts must be between 1 and {MAX_POLL_ATTEMPTS}",
        }
    return value


def _validate_interval(value: float) -> float | dict[str, Any]:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return {
            "status": "invalid_poll_interval",
            "rule_set": RULE_SET,
            "reason": "interval_seconds must be a number",
        }

    interval = float(value)
    if interval < 0 or interval > MAX_POLL_INTERVAL_SECONDS:
        return {
            "status": "invalid_poll_interval",
            "rule_set": RULE_SET,
            "reason": f"interval_seconds must be between 0 and {MAX_POLL_INTERVAL_SECONDS}",
        }
    return interval
