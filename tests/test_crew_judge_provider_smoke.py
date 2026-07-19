import json

from tools.crew_judge_provider_smoke import main


def test_crew_judge_provider_smoke_is_safe_by_default(capsys, monkeypatch):
    monkeypatch.delenv("APEX_CREW_JUDGE_ENABLED", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    main([])

    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "checked"
    assert report["deterministic"]["decision"] == "confirm_finding"
    assert report["noop"]["status"] == "not_configured"
    assert report["crew_ai"] == {
        "status": "skipped",
        "provider": "crew_ai",
        "reason": "external_llm_not_authorized_for_smoke",
        "how_to_run": (
            "Set APEX_CREW_JUDGE_ENABLED=1 and provider credentials, then run "
            "python tools/crew_judge_provider_smoke.py --allow-external-llm"
        ),
    }
