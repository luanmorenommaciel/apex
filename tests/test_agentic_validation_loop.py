import json

from apex.commander.agentic_loop import (
    PARTIAL,
    check_g6_oracle_drift,
    check_judge_policy_contract,
    check_mcp_project_config,
    run_agentic_validation_loop,
)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_minimal_agentic_fixture(root):
    write(
        root / ".mcp.json",
        json.dumps(
            {
                "mcpServers": {
                    "apex-commander": {
                        "type": "stdio",
                        "command": "python",
                        "args": [
                            "-m",
                            "apex.commander.mcp_stdio_cli",
                            "--store",
                            "store.ndjson",
                            "--apply-root",
                            "workspace",
                        ],
                        "env": {},
                    }
                }
            }
        ),
    )
    write(
        root / "evidence" / "g6-claude-code-project-mcp-smoke.log",
        "Status: Pending approval (run `claude` to approve)",
    )
    write(
        root / "evidence" / "g6-oracle-drift-summary.json",
        json.dumps({"status": "passed"}),
    )
    write(
        root / ".github" / "workflows" / "scenario-gate.yml",
        "on:\n  workflow_dispatch:\n  schedule:\n    - cron: '17 6 * * 1'\njobs:\n  g6-oracle-drift:\n",
    )


def test_agentic_loop_reports_partial_when_mcp_needs_gui_approval(tmp_path):
    write_minimal_agentic_fixture(tmp_path)

    report = run_agentic_validation_loop(tmp_path, iterations=2)

    assert report["status"] == PARTIAL
    assert len(report["iterations"]) == 2
    assert any("approve apex-commander" in item for item in report["next_actions"])
    assert "no_llm_required" in report["guardrails"]


def test_mcp_project_config_missing_fails_with_next_action(tmp_path):
    result = check_mcp_project_config(tmp_path)

    assert result["status"] == "fail"
    assert result["next_action"] == "create .mcp.json for apex-commander"


def test_g6_oracle_drift_passes_when_summary_and_workflow_exist(tmp_path):
    write_minimal_agentic_fixture(tmp_path)

    result = check_g6_oracle_drift(tmp_path)

    assert result["status"] == "pass"
    assert "manual/weekly workflow is defined" in result["details"]


def test_judge_policy_contract_keeps_llm_optional(tmp_path):
    result = check_judge_policy_contract(tmp_path)

    assert result["status"] == "pass"
    assert "low confidence escalates to future Crew/Judge" in result["details"]
