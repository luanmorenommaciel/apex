"""Canonical DEV -> JAR -> COLLECT -> INFRA -> ENGINE -> SERVE E2E gate.

The runner validates one already-submitted Spark job. It never manages Docker,
deletes telemetry, invokes an LLM, or prints connection credentials.
"""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from collections.abc import Awaitable, Callable
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for source_dir in (ROOT / "engine" / "src", ROOT / "serve" / "src"):
    source = str(source_dir)
    if source not in sys.path:
        sys.path.insert(0, source)

from apex_engine import analyze, analyze_events  # noqa: E402
from apex_engine.clickhouse import EngineStore  # noqa: E402


FINDING_SIGNATURES_SQL = """
SELECT job_id, stage_id, type, severity, detected_by
FROM apex.findings
WHERE job_id = {job_id:String}
ORDER BY stage_id, type, severity, detected_by
"""

FindingSignature = tuple[str, int, str, str, str]
McpProbe = Callable[[str], Awaitable[dict[str, Any]]]


class GateFailure(RuntimeError):
    """A canonical E2E invariant was not satisfied."""


def _finding_signature(finding: Any) -> FindingSignature:
    read = lambda name: getattr(finding, name, None) if not isinstance(finding, dict) else finding.get(name)
    finding_type = read("type")
    severity = read("severity")
    return (
        str(read("job_id")),
        int(read("stage_id")),
        str(getattr(finding_type, "value", finding_type)),
        str(getattr(severity, "value", severity)),
        str(read("detected_by")),
    )


def _persisted_signatures(client: Any, job_id: str) -> list[FindingSignature]:
    result = client.query(FINDING_SIGNATURES_SQL, parameters={"job_id": job_id})
    return [_finding_signature(dict(row)) for row in result.named_results()]


def _counter_diff(expected: list[FindingSignature], actual: list[FindingSignature]) -> str:
    missing = list((Counter(expected) - Counter(actual)).elements())
    unexpected = list((Counter(actual) - Counter(expected)).elements())
    return f"missing={missing!r};unexpected={unexpected!r}"


def ensure_idempotent_findings(*, client: Any, store: EngineStore, job_id: str, findings: list[Any]) -> dict[str, Any]:
    """Persist once, then prove repeated runs observe the same findings."""
    expected = [_finding_signature(finding) for finding in findings]
    before = _persisted_signatures(client, job_id)
    if before:
        if Counter(before) != Counter(expected):
            raise GateFailure(f"persisted_finding_mismatch:{_counter_diff(expected, before)}")
        return {"mode": "already_present", "written_rows": 0, "persisted_count": len(before)}

    written = store.persist_findings(findings)
    after = _persisted_signatures(client, job_id)
    if Counter(after) != Counter(expected):
        raise GateFailure(f"finding_persistence_mismatch:{_counter_diff(expected, after)}")
    return {"mode": "inserted" if findings else "empty", "written_rows": written, "persisted_count": len(after)}


def _validate_mcp(payload: dict[str, Any], *, job_id: str, stage_count: int, findings: list[Any]) -> dict[str, Any]:
    tools = payload.get("tools", [])
    analyze_tool = next((tool for tool in tools if tool.get("name") == "analyze_run"), None)
    if not analyze_tool or analyze_tool.get("read_only") is not True:
        raise GateFailure("mcp_analyze_run_not_read_only")

    diagnosis = payload.get("diagnosis", {})
    if diagnosis.get("job_id") != job_id:
        raise GateFailure("mcp_job_id_mismatch")
    stages = diagnosis.get("stages", [])
    if len(stages) != stage_count:
        raise GateFailure(f"mcp_stage_count_mismatch:{len(stages)}!={stage_count}")
    actual = [_finding_signature(finding) for finding in diagnosis.get("findings", [])]
    expected = [_finding_signature(finding) for finding in findings]
    if Counter(actual) != Counter(expected):
        raise GateFailure(f"mcp_finding_mismatch:{_counter_diff(expected, actual)}")
    return {
        "tool": "analyze_run",
        "read_only": True,
        "status": diagnosis.get("status"),
        "stage_count": len(stages),
        "finding_count": len(actual),
    }


async def run_gate(*, job_id: str, client: Any, mcp_probe: McpProbe, analyzer: Callable[[list[Any]], dict[str, Any]] = analyze_events) -> dict[str, Any]:
    if not job_id:
        raise GateFailure("job_id_required")

    store = EngineStore(client)
    events = store.stage_events(job_id)
    if not events:
        raise GateFailure("canonical_telemetry_not_found")
    app_ids = sorted({event.app_id for event in events})
    if len(app_ids) != 1:
        raise GateFailure(f"app_id_cardinality_invalid:{app_ids!r}")

    # Determinism check runs on the stage-events path (analyzer).
    engine_result = analyzer(events)
    if engine_result.get("mode") != "deterministic" or engine_result.get("llm_calls") != 0:
        raise GateFailure("engine_path_is_not_deterministic")
    rejected = list(engine_result.get("rejected", []))
    if rejected:
        raise GateFailure(f"evidence_validator_rejected:{len(rejected)}")
    # Expected findings must come from the AQE-INCLUSIVE analysis (reads plan_transitions),
    # which is what engine actually persists. analyze_events sees stage rows only and omits
    # the aqe_watcher's AQE_REPLAN finding — using it here caused persisted_finding_mismatch.
    # persist=False + use_crew=False keeps this deterministic and side-effect-free.
    full_result = analyze(job_id, store, persist=False, use_crew=False)
    if full_result.get("llm_calls") != 0:
        raise GateFailure("engine_full_path_is_not_deterministic")
    findings = list(full_result.get("findings", []))
    persistence = ensure_idempotent_findings(client=client, store=store, job_id=job_id, findings=findings)
    mcp_result = _validate_mcp(await mcp_probe(job_id), job_id=job_id, stage_count=len(events), findings=findings)
    fingerprint_count = sum(bool(event.plan_fingerprint) for event in events)
    return {
        "gate": "six-lane-canonical-e2e",
        "job_id": job_id,
        "app_id": app_ids[0],
        "lanes": {
            "dev": {"status": "passed", "submitted_job_observed": True},
            "jar": {"status": "passed", "canonical_stage_events": len(events), "plan_fingerprint_count": fingerprint_count},
            "collect": {"status": "passed", "otlp_stage_rows_observed": len(events)},
            "infra": {"status": "passed", "clickhouse_stage_rows": len(events)},
            "engine": {"status": "passed", "mode": "deterministic", "llm_calls": 0, "accepted_findings": len(findings), "validator_rejections": 0, "persistence": persistence},
            "serve": {"status": "passed", **mcp_result},
        },
        "status": "passed",
    }


async def live_mcp_probe(job_id: str) -> dict[str, Any]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    child_env = dict(os.environ)
    serve_source = str(ROOT / "serve" / "src")
    current_path = child_env.get("PYTHONPATH", "")
    child_env["PYTHONPATH"] = os.pathsep.join(filter(None, (serve_source, current_path)))
    server = StdioServerParameters(command=sys.executable, args=["-c", "from apex_mcp.server import main; main()"], env=child_env)
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            listed = await session.list_tools()
            called = await session.call_tool("analyze_run", {"job_id": job_id})
    diagnosis = json.loads(called.content[0].text)
    return {
        "tools": [{"name": tool.name, "read_only": bool(tool.annotations and tool.annotations.readOnlyHint)} for tool in listed.tools],
        "diagnosis": diagnosis,
    }


def _connect_clickhouse() -> Any:
    import clickhouse_connect

    return clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "apex"),
        password=os.environ["CLICKHOUSE_PASSWORD"],
        database=os.getenv("CLICKHOUSE_DATABASE", "apex"),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-id", required=True, help="Persisted canonical job_id to validate")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        result = asyncio.run(run_gate(job_id=args.job_id, client=_connect_clickhouse(), mcp_probe=live_mcp_probe))
    except Exception as exc:
        result = {"gate": "six-lane-canonical-e2e", "job_id": args.job_id, "status": "failed", "error": f"{type(exc).__name__}:{exc}"}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
