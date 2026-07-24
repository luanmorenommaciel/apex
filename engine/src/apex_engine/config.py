"""Engine configuration — every knob is an env var with a local-dev default.

ClickHouse defaults match the values infra publishes in `infra/.env.example`
(host ports per CONTRACT.md § Port Map: HTTP 8123). No secret is invented here;
override anything via the environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Gate thresholds (CONTRACT.md + docs/lanes/ENGINE.md T10).
ESCALATE_BELOW_CONFIDENCE = 0.6

# Confidence bucketing. The `apex.findings.confidence` column is
# Enum8('LOW','MEDIUM','HIGH') while the gate needs a number, so the engine
# carries a float and buckets it on write. The LOW boundary is deliberately the
# gate threshold: `confidence == LOW` <=> the finding is escalation-eligible.
CONFIDENCE_LOW_MAX = ESCALATE_BELOW_CONFIDENCE  # < 0.60 -> LOW
CONFIDENCE_MEDIUM_MAX = 0.85  # < 0.85 -> MEDIUM, else HIGH

# Model tiering (docs/lanes/ENGINE.md). CrewAI requires the provider prefix.
TRIAGE_MODEL = os.getenv("APEX_TRIAGE_MODEL", "anthropic/claude-haiku-4-5")
CORRELATION_MODEL = os.getenv("APEX_CORRELATION_MODEL", "anthropic/claude-sonnet-5")
JUDGE_MODEL = os.getenv("APEX_JUDGE_MODEL", "anthropic/claude-opus-4-8")


@dataclass(frozen=True)
class ClickHouseSettings:
    host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    port: int = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    username: str = os.getenv("CLICKHOUSE_USER", "apex")
    password: str = os.getenv("CLICKHOUSE_PASSWORD", "apex_local_dev")
    database: str = os.getenv("CLICKHOUSE_DATABASE", "apex")

    def connect(self):
        """Open a clickhouse-connect client. Imported lazily so the pure
        deterministic core stays importable without the driver installed."""
        import clickhouse_connect

        return clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )


def anthropic_api_key() -> str | None:
    return os.getenv("ANTHROPIC_API_KEY")
