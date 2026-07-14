"""CLI entrypoint for the Commander MCP stdio server."""

import argparse
import json
from pathlib import Path

from apex.commander.mcp_stdio_server import serve_stdio
from apex.commander.tool_contract import CommanderToolContract


class JsonFindingStore:
    """Tiny NDJSON finding store used by local MCP/IDE smoke tests."""

    def __init__(self, path):
        self.path = Path(path)

    def query_by_job_id(self, job_id):
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            finding = record.get("finding", {})
            if finding.get("job_id") == job_id:
                records.append(record)
        return records


def build_contract(args):
    finding_store = JsonFindingStore(args.finding_store) if args.finding_store else None
    return CommanderToolContract(
        args.store,
        finding_store=finding_store,
        apply_root=args.apply_root,
        rerun_root=args.rerun_root,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Apex Commander MCP over stdio.")
    parser.add_argument("--store", required=True, help="Telemetry store path.")
    parser.add_argument("--finding-store", help="NDJSON finding store path.")
    parser.add_argument("--apply-root", help="Allowed root for guarded apply_fix.")
    parser.add_argument("--rerun-root", help="Allowed root for guarded rerun tools.")
    args = parser.parse_args(argv)
    serve_stdio(build_contract(args))


if __name__ == "__main__":
    main()
