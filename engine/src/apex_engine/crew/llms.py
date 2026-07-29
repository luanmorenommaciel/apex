"""Tiered LLMs (T11). Cheap model decides, expensive model judges.

CrewAI requires a PROVIDER PREFIX on the model string — `anthropic/claude-...`,
never the bare id — and the native provider only loads with the
`crewai[anthropic]` extra plus `ANTHROPIC_API_KEY`.

The ladder:
  haiku-4-5   triage      — is this candidate even worth correlating?
  sonnet-5    correlation — reason across signals on one stage
  opus-4-8    judge       — adversarially try to kill the finding

Temperatures fall as authority rises: the judge is deterministic (0.0) because
its verdict decides whether a finding reaches the user.
"""

from __future__ import annotations

from ..config import CORRELATION_MODEL, JUDGE_MODEL, TRIAGE_MODEL


def _llm(model: str, temperature: float):
    from crewai import LLM

    return LLM(model=model, temperature=temperature)


def triage_llm():
    return _llm(TRIAGE_MODEL, 0.0)


def correlation_llm():
    return _llm(CORRELATION_MODEL, 0.1)


def judge_llm():
    return _llm(JUDGE_MODEL, 0.0)
