"""`python -m apex_engine <job_id>` — run the engine against a real job.

    uv run --extra clickhouse python -m apex_engine app-20260724160310-0000
    uv run --extra clickhouse python -m apex_engine <job_id> --dry-run --no-crew
"""

from __future__ import annotations

import argparse
import sys

from .clickhouse import EngineStore
from .pipeline import analyze


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="apex_engine", description="Analyze one Spark job.")
    parser.add_argument("job_id")
    parser.add_argument("--dry-run", action="store_true", help="analyze but do not insert findings")
    parser.add_argument("--no-crew", action="store_true", help="Tier 1 only; never call an LLM")
    args = parser.parse_args(argv)

    result = analyze(
        args.job_id,
        EngineStore.connect(),
        persist=not args.dry_run,
        use_crew=not args.no_crew,
    )

    print(f"job_id         : {result['job_id']}")
    print(f"stages analyzed: {result['stages_analyzed']}  (plan_transitions: {result['plan_transitions']})")
    print(f"mode           : {result['mode']}   crew: {result['crew']}   llm_calls: {result['llm_calls']}")
    print(f"findings       : {len(result['findings'])}  rejected: {len(result['rejected'])}")
    persistence = result["persistence"]
    print(f"written_rows   : {result['written_rows']}  ({persistence['mode']}, "
          f"skipped_existing={persistence['skipped_existing']})")
    if result["findings"]:
        print("\n-- findings " + "-" * 60)
    for finding in result["findings"]:
        stage = "job-level" if finding.stage_id < 0 else f"stage {finding.stage_id}"
        print(f"[{finding.severity.value:>8}] {finding.type.value:<18} {stage:<10} "
              f"conf={finding.confidence.value}({finding.confidence_score:.2f}) via {finding.detected_by}")
        print(f"           evidence: {finding.evidence}")
        print(f"           fix     : {finding.fix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
