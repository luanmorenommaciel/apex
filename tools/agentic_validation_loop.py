"""CLI for the deterministic Apex agentic validation loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.agentic_loop import run_agentic_validation_loop


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run Apex local agentic validation loop.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--iterations", type=int, default=1, help="Loop iterations.")
    parser.add_argument(
        "--output",
        default="evidence/agentic-validation-loop-report.json",
        help="JSON report output path.",
    )
    args = parser.parse_args(argv)

    report = run_agentic_validation_loop(args.root, iterations=args.iterations)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in {"pass", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
