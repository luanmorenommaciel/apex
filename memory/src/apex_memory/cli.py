"""`apex-memory` CLI — index the store, or recall against it.

    apex-memory index [--job JOB_ID ...]
    apex-memory recall --job JOB_ID
    apex-memory recall --fingerprint FP
    apex-memory recall --plan-file path/to/plan.txt

Output is JSON on stdout so it composes; logs go to stderr.
"""

from __future__ import annotations

import argparse
import json
import sys

from .clickhouse import MemoryStore
from .config import DEFAULT_TOP_K, MIN_SIMILARITY
from .indexer import reindex
from .recall import recall


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="apex-memory")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="build plan_memory + run_outcomes")
    p_index.add_argument("--job", action="append", dest="jobs", default=None)

    p_recall = sub.add_parser("recall", help="recall history for a plan shape")
    src = p_recall.add_mutually_exclusive_group(required=True)
    src.add_argument("--job")
    src.add_argument("--fingerprint")
    src.add_argument("--plan-file")
    p_recall.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    p_recall.add_argument("--min-similarity", type=float, default=MIN_SIMILARITY)

    args = parser.parse_args(argv)
    store = MemoryStore()

    if args.command == "index":
        print(str(reindex(store, args.jobs)), file=sys.stderr)
        return 0

    plan_json = None
    if args.plan_file:
        with open(args.plan_file, encoding="utf-8") as handle:
            plan_json = handle.read()

    result = recall(
        store,
        job_id=args.job,
        plan_fingerprint=args.fingerprint,
        plan_json=plan_json,
        top_k=args.top_k,
        min_similarity=args.min_similarity,
    )
    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
