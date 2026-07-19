"""Smoke the optional Crew/Judge providers without hidden external LLM calls."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.judge_contract import build_judge_envelope
from apex.commander.judge_providers import (
    CrewAIJudgeProvider,
    DeterministicJudgeProvider,
    NoopJudgeProvider,
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Crew/Judge provider wiring without hidden LLM cost."
    )
    parser.add_argument(
        "--allow-external-llm",
        action="store_true",
        help="Actually attempt Crew.ai execution when env/credentials are configured.",
    )
    args = parser.parse_args(argv)

    envelope = sample_envelope()
    report = {
        "status": "checked",
        "crewai_installed": importlib.util.find_spec("crewai") is not None,
        "environment": {
            "APEX_CREW_JUDGE_ENABLED": os.environ.get("APEX_CREW_JUDGE_ENABLED", ""),
            "OPENAI_API_KEY_set": bool(os.environ.get("OPENAI_API_KEY")),
            "ANTHROPIC_API_KEY_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
        },
        "deterministic": DeterministicJudgeProvider().diagnose(envelope),
        "noop": NoopJudgeProvider("smoke").diagnose(envelope),
        "crew_ai": crew_ai_result(envelope, allow_external_llm=args.allow_external_llm),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


def crew_ai_result(envelope, *, allow_external_llm):
    if not allow_external_llm:
        return {
            "status": "skipped",
            "provider": "crew_ai",
            "reason": "external_llm_not_authorized_for_smoke",
            "how_to_run": (
                "Set APEX_CREW_JUDGE_ENABLED=1 and provider credentials, then run "
                "python tools/crew_judge_provider_smoke.py --allow-external-llm"
            ),
        }
    return CrewAIJudgeProvider(enabled=True).diagnose(envelope)


def sample_envelope():
    finding = {
        "job_id": "job-crew-smoke",
        "kind": "shuffle_skew_candidate",
        "severity": "warning",
        "confidence": "medium",
        "evidence": {
            "app_id": "app-crew-smoke",
            "stage_id": 2,
            "ratio": 29.5,
            "hot_records": 165297,
            "median_cold_records": 5596,
        },
    }
    validation = {"status": "valid", "accepted": True}
    policy = {
        "status": "keep_deterministic",
        "route": "deterministic_t1",
        "should_escalate": False,
        "threshold": 0.6,
        "confidence": "medium",
        "confidence_score": 0.6,
        "reasons": [],
        "finding_kind": "shuffle_skew_candidate",
        "job_id": "job-crew-smoke",
    }
    return build_judge_envelope(
        job_id="job-crew-smoke",
        finding=finding,
        validation=validation,
        policy=policy,
        evidence={"app_id": "app-crew-smoke"},
        candidate_recommendations=[],
    )


if __name__ == "__main__":
    main()
