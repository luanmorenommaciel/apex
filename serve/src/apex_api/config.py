"""Server configuration for the Apex API.

Nothing here carries a default credential. The API exists so that a consumer
holds an API token and never a database user; an API that serves openly when
no token is configured would move that problem rather than solve it, so the
absence of tokens is a startup failure and not a permissive default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

# Comma-separated. Whitespace around an entry is stripped; empty entries are
# dropped, so a trailing comma is not a nameless token.
TOKENS_VAR = "APEX_API_TOKENS"


class ConfigError(RuntimeError):
    """The server cannot be configured safely. Raised at startup, never per request."""


@dataclass(frozen=True)
class Settings:
    """Everything the app needs that is not the store.

    ``tokens`` is a frozenset so a caller cannot mutate the accepted set after
    the app is built.
    """

    tokens: frozenset[str]


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Read settings from the environment.

    Raises ConfigError when no token is configured. That is deliberate: the
    failure is loud, at startup, in the operator's terminal — the one place it
    can still be fixed before anyone is served.
    """
    source = os.environ if env is None else env
    raw = source.get(TOKENS_VAR, "")
    tokens = frozenset(token.strip() for token in raw.split(",") if token.strip())
    if not tokens:
        raise ConfigError(
            f"apex_api_unconfigured: no API token in {TOKENS_VAR}. Set it to a "
            f"comma-separated list of tokens. The server does not serve "
            f"without one."
        )
    return Settings(tokens=tokens)
