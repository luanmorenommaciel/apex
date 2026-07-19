"""Run an IDE-like MCP stdio smoke against the Apex Commander CLI.

The harness launches ``python -m apex.commander.mcp_stdio_cli`` as an external
process, speaks line-delimited JSON-RPC over stdin/stdout, and writes an
auditable JSONL transcript under ``evidence/``.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.clickstack_mvp import append_envelope


JOB_ID = "job-42"
RECOMMENDATION_ID = "job-42:shuffle_skew_candidate:stage-2:0"
ORIGINAL_SOURCE = "df.join(dim, 'id').count()\n"
REPLACEMENT_SOURCE = (
    "# REVIEW: validate skew before this join\n"
    "df.join(dim, 'id').count()\n"
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the Apex Commander MCP stdio CLI like an IDE MCP client."
    )
    parser.add_argument(
        "--work-dir",
        default="evidence/generated/mcp-ide-subprocess-smoke",
        help="Directory for temporary smoke inputs.",
    )
    parser.add_argument(
        "--evidence",
        default="evidence/g6-mcp-ide-subprocess-smoke.jsonl",
        help="JSONL transcript written by this smoke.",
    )
    args = parser.parse_args(argv)

    work_dir = Path(args.work_dir)
    evidence_path = Path(args.evidence)
    paths = prepare_smoke_inputs(work_dir)

    client = McpStdioClient(
        [
            sys.executable,
            "-m",
            "apex.commander.mcp_stdio_cli",
            "--store",
            str(paths["store"]),
            "--finding-store",
            str(paths["finding_store"]),
            "--apply-root",
            str(work_dir),
        ]
    )

    transcript = []
    try:
        transcript.append(
            event(
                "harness_start",
                command=client.command,
                work_dir=str(work_dir),
                evidence=str(evidence_path),
            )
        )
        initialize = client.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "apex-ide-subprocess-smoke",
                    "version": "0.1.0",
                },
            },
        )
        transcript.append(event("initialize", response=initialize))

        client.notify("notifications/initialized")
        transcript.append(event("initialized_notification"))

        tools = client.request("tools/list")
        tool_names = [tool["name"] for tool in tools["result"]["tools"]]
        transcript.append(event("tools_list", tool_names=tool_names, response=tools))
        require("apply_fix" in tool_names, "apply_fix_not_listed")
        require("crew_judge_diagnose" in tool_names, "crew_judge_diagnose_not_listed")

        recommendation = client.tool_call(
            "recommend_fix",
            {"job_id": JOB_ID},
        )
        transcript.append(event("recommend_fix", payload=recommendation))
        require(recommendation["status"] == "found", "recommendation_not_found")

        judge = client.tool_call(
            "crew_judge_diagnose",
            {"job_id": JOB_ID, "provider": "deterministic"},
        )
        transcript.append(event("crew_judge_diagnose", payload=judge))
        require(judge["status"] == "judged", "judge_not_judged")
        require(judge["provider_used"] == "deterministic", "judge_provider_mismatch")
        require(judge["read_only"] is True, "judge_not_read_only")
        require(judge["mutation_allowed"] is False, "judge_allows_mutation")
        require(
            judge["contract_validation"]["accepted"] is True,
            "judge_contract_invalid",
        )

        preview = client.tool_call(
            "preview_recommendation",
            {
                "job_id": JOB_ID,
                "recommendation_id": RECOMMENDATION_ID,
                "path": str(paths["source"]),
                "replacement": REPLACEMENT_SOURCE,
            },
        )
        transcript.append(event("preview_recommendation", payload=preview))
        require(preview["status"] == "preview_ready", "preview_not_ready")

        apply_result = client.tool_call(
            "apply_fix",
            {
                "job_id": JOB_ID,
                "recommendation_id": RECOMMENDATION_ID,
                "path": str(paths["source"]),
                "replacement": REPLACEMENT_SOURCE,
                "approval_token": preview["approval"]["token"],
            },
        )
        transcript.append(event("apply_fix", payload=apply_result))
        require(apply_result["status"] == "applied", "apply_not_applied")
        require(
            apply_result["verification"]["status"] == "verified",
            "apply_not_verified",
        )

        final_source = paths["source"].read_text(encoding="utf-8")
        transcript.append(
            event(
                "final_source",
                path=str(paths["source"]),
                content=final_source,
                matched_expected=final_source == REPLACEMENT_SOURCE,
            )
        )
        require(final_source == REPLACEMENT_SOURCE, "source_mismatch")

        transcript.append(event("harness_result", status="passed"))
    finally:
        client.close()

    write_transcript(evidence_path, transcript)
    print(f"status=passed evidence={evidence_path}")


def prepare_smoke_inputs(work_dir):
    work_dir.mkdir(parents=True, exist_ok=True)
    source = work_dir / "job.py"
    source.write_text(ORIGINAL_SOURCE, encoding="utf-8")

    store = work_dir / "store.ndjson"
    store.write_text("", encoding="utf-8")
    append_envelope(store, telemetry_envelope())

    finding_store = work_dir / "findings.ndjson"
    finding_store.write_text(json.dumps(persisted_skew_record()) + "\n", encoding="utf-8")

    return {"source": source, "store": store, "finding_store": finding_store}


def persisted_skew_record():
    return {
        "finding": {
            "job_id": JOB_ID,
            "kind": "shuffle_skew_candidate",
            "severity": "warning",
            "confidence": "medium",
            "evidence": {
                "app_id": "app-mcp-stdio",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
            },
        },
        "validation": {"status": "valid", "accepted": True},
    }


def telemetry_envelope():
    return {
        "schema_version": "apex.commander.telemetry.v1",
        "job_id": JOB_ID,
        "app_id": "app-mcp-stdio",
        "event_counts": {"SparkListenerTaskEnd": 4},
        "stages": [
            {
                "stage_id": 2,
                "task_count": 8,
                "records": [165297, 5596, 5600, 5700],
                "total_records": 182193,
                "max_records": 165297,
                "median_cold_records": 5596,
                "ratio": 29.5,
                "evidence_status": "valid",
                "quality_issues": [],
                "disk_bytes_spilled": 0,
                "memory_bytes_spilled": 0,
                "jvm_gc_time_ms": 0,
                "executor_run_time_ms": 10000,
                "failure_reasons": [],
            }
        ],
        "skew_candidates": [
            {
                "kind": "shuffle_skew_candidate",
                "stage_id": 2,
                "ratio": 29.5,
                "hot_records": 165297,
                "median_cold_records": 5596,
                "task_count": 8,
            }
        ],
    }


class McpStdioClient:
    def __init__(self, command):
        self.command = list(command)
        self.next_id = 1
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def request(self, method, params=None):
        request_id = self.next_id
        self.next_id += 1
        message = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self._write(message)
        line = self.process.stdout.readline()
        require(line, f"missing_response:{method}")
        response = json.loads(line)
        require(response.get("id") == request_id, f"response_id_mismatch:{method}")
        require("error" not in response, f"jsonrpc_error:{method}:{response.get('error')}")
        return response

    def notify(self, method, params=None):
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        self._write(message)

    def tool_call(self, name, arguments):
        response = self.request(
            "tools/call",
            {"name": name, "arguments": arguments},
        )
        text = response["result"]["content"][0]["text"]
        return json.loads(text)

    def close(self):
        if self.process.stdin:
            self.process.stdin.close()
        exit_code = self.process.wait(timeout=10)
        stderr = self.process.stderr.read() if self.process.stderr else ""
        require(exit_code == 0, f"mcp_process_exit:{exit_code}:{stderr}")

    def _write(self, message):
        require(self.process.stdin is not None, "stdin_not_available")
        self.process.stdin.write(json.dumps(message, sort_keys=True) + "\n")
        self.process.stdin.flush()


def event(name, **payload):
    record = {"event": name}
    record.update(payload)
    return record


def write_transcript(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


if __name__ == "__main__":
    main()
