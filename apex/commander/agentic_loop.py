"""Deterministic local agentic loop for Apex validation gaps.

The loop is intentionally not an LLM agent. It models the agentic workflow as
small local roles: collect evidence, judge status, and recommend the next safe
action. Mutations remain outside this module.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from apex.commander.judge_policy import evaluate_judge_policy


PASS = "pass"
PARTIAL = "partial"
FAIL = "fail"


def check_mcp_project_config(root: Path) -> dict[str, Any]:
    config_path = root / ".mcp.json"
    evidence_path = root / "evidence" / "g6-claude-code-project-mcp-smoke.log"
    result = {
        "id": "mcp_project_config",
        "title": "Claude Code project MCP config",
        "status": FAIL,
        "evidence": [str(config_path), str(evidence_path)],
        "details": [],
        "next_action": "create .mcp.json for apex-commander",
    }

    if not config_path.exists():
        result["details"].append(".mcp.json not found")
        return result

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result["details"].append(f".mcp.json invalid: {exc}")
        return result

    server = (config.get("mcpServers") or {}).get("apex-commander")
    if not server:
        result["details"].append("apex-commander server not configured")
        return result

    args = server.get("args") or []
    command_ok = server.get("command") == "python"
    module_ok = "-m" in args and "apex.commander.mcp_stdio_cli" in args
    apply_root_ok = "--apply-root" in args

    if not (command_ok and module_ok and apply_root_ok):
        result["details"].append("apex-commander command is incomplete")
        return result

    result["status"] = PARTIAL
    result["details"].append("project-scoped MCP server configured")
    result["next_action"] = "approve apex-commander in Claude Code/Cursor/VS Code GUI"

    if evidence_path.exists():
        evidence = evidence_path.read_text(encoding="utf-8", errors="replace")
        if "Pending approval" in evidence:
            result["details"].append("Claude Code CLI recognized server but pending approval")
        elif "Status:" in evidence:
            result["status"] = PASS
            result["details"].append("Claude Code CLI status evidence present")

    return result


def check_g6_oracle_drift(root: Path) -> dict[str, Any]:
    summary_path = root / "evidence" / "g6-oracle-drift-summary.json"
    remote_summary_path = root / "evidence" / "g6-remote-workflow-run-29378169451-summary.json"
    workflow_path = root / ".github" / "workflows" / "scenario-gate.yml"
    result = {
        "id": "g6_oracle_drift",
        "title": "G6 oracle drift smoke and schedule",
        "status": FAIL,
        "evidence": [str(summary_path), str(workflow_path), str(remote_summary_path)],
        "details": [],
        "next_action": "run tools/g6_oracle_drift_smoke.py and create CI workflow",
    }

    if not summary_path.exists():
        result["details"].append("G6 summary JSON not found")
        return result

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result["details"].append(f"G6 summary invalid: {exc}")
        return result

    if summary.get("status") != "passed":
        result["details"].append(f"G6 summary status is {summary.get('status')!r}")
        return result

    result["status"] = PARTIAL
    result["details"].append("local G6 smoke passed")
    result["next_action"] = "observe one remote GitHub Actions run"

    if workflow_path.exists():
        workflow = workflow_path.read_text(encoding="utf-8", errors="replace")
        has_dispatch = "workflow_dispatch" in workflow
        has_schedule = "schedule:" in workflow and "cron:" in workflow
        has_job = "g6-oracle-drift" in workflow
        if has_dispatch and has_schedule and has_job:
            result["status"] = PASS
            result["details"].append("manual/weekly workflow is defined")
            result["next_action"] = "trigger or observe remote workflow execution"
        else:
            result["details"].append("workflow exists but lacks dispatch/schedule/job")

    if remote_summary_path.exists():
        try:
            remote_summary = json.loads(remote_summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result["status"] = PARTIAL
            result["details"].append(f"remote workflow summary invalid: {exc}")
            return result

        jobs = remote_summary.get("jobs") or []
        g6_jobs = [job for job in jobs if job.get("name") == "g6-oracle-drift"]
        gate_jobs = [job for job in jobs if job.get("name") == "gate"]
        if g6_jobs and g6_jobs[0].get("conclusion") == "success":
            result["status"] = PASS
            result["details"].append(
                f"remote G6 workflow job passed: {g6_jobs[0].get('url')}"
            )
            if gate_jobs and gate_jobs[0].get("conclusion") != "success":
                result["details"].append(
                    "overall workflow failed because legacy gate job failed separately"
                )
            result["next_action"] = "monitor scheduled G6 runs"
        else:
            result["status"] = PARTIAL
            result["details"].append("remote workflow observed, but G6 job did not pass")

    return result


def check_judge_policy_contract(root: Path) -> dict[str, Any]:
    result = {
        "id": "judge_policy_contract",
        "title": "Future Crew/Judge escalation policy",
        "status": FAIL,
        "evidence": [
            str(root / "apex" / "commander" / "judge_policy.py"),
            str(root / "tests" / "test_commander_judge_policy.py"),
        ],
        "details": [],
        "next_action": "implement deterministic judge policy contract",
    }

    low = evaluate_judge_policy(
        {"job_id": "agentic-loop-low", "kind": "shuffle_skew_candidate", "confidence": "low"}
    )
    high = evaluate_judge_policy(
        {"job_id": "agentic-loop-high", "kind": "shuffle_skew_candidate", "confidence": "high"},
        validation={"accepted": True},
    )

    if low["route"] == "crew_judge" and high["route"] == "deterministic_t1":
        result["status"] = PASS
        result["details"].append("low confidence escalates to future Crew/Judge")
        result["details"].append("high confidence with accepted evidence stays deterministic")
        result["next_action"] = "keep Crew/Judge external until IDE and CI evidence are complete"
    else:
        result["details"].append("judge policy routing did not match expected contract")

    return result


CHECKS = [check_mcp_project_config, check_g6_oracle_drift, check_judge_policy_contract]


def _overall_status(checks: list[dict[str, Any]]) -> str:
    statuses = {check["status"] for check in checks}
    if FAIL in statuses:
        return FAIL
    if PARTIAL in statuses:
        return PARTIAL
    return PASS


def _next_actions(checks: list[dict[str, Any]]) -> list[str]:
    return [
        f"{check['id']}: {check['next_action']}"
        for check in checks
        if check["status"] != PASS
    ]


def run_agentic_validation_loop(root: str | Path = ".", iterations: int = 1) -> dict[str, Any]:
    """Run deterministic validation loop iterations and return a report."""
    root_path = Path(root).resolve()
    iterations = max(1, int(iterations))
    records = []

    for iteration in range(1, iterations + 1):
        checks = [check(root_path) for check in CHECKS]
        records.append(
            {
                "iteration": iteration,
                "agents": [
                    "EvidenceCollector",
                    "DeterministicJudge",
                    "NextActionPlanner",
                ],
                "checks": checks,
                "status": _overall_status(checks),
                "next_actions": _next_actions(checks),
            }
        )

    final = records[-1]
    return {
        "name": "apex_agentic_validation_loop",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "iterations": records,
        "status": final["status"],
        "next_actions": final["next_actions"],
        "guardrails": [
            "no_llm_required",
            "no_file_mutation",
            "evidence_first",
            "human_approval_required_for_apply",
        ],
    }
