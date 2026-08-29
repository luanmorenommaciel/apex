"""Extract terminal task reasons from a Spark 4 event-log Zstandard object."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import zstandard


def task_reason_kind(reason: Any) -> str:
    if isinstance(reason, dict):
        return str(reason.get("Reason") or reason.get("Class Name") or "unknown")
    if isinstance(reason, str):
        return reason
    return "unknown"


def summarize_event_log(path: Path) -> dict[str, Any]:
    reasons: Counter[str] = Counter()
    speculative_task_ends = 0
    task_ends = 0

    with path.open("rb") as source:
        with zstandard.ZstdDecompressor().stream_reader(source) as reader:
            payload = reader.read().decode("utf-8")
    for line in payload.splitlines():
        event = json.loads(line)
        if event.get("Event") != "SparkListenerTaskEnd":
            continue
        task_ends += 1
        task_info = event.get("Task Info") or {}
        if task_info.get("Speculative") is True:
            speculative_task_ends += 1
        reasons[task_reason_kind(event.get("Task End Reason"))] += 1

    return {
        "event_log": path.name,
        "task_end_count": task_ends,
        "speculative_task_end_count": speculative_task_ends,
        "task_end_reasons": dict(sorted(reasons.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-log", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize_event_log(args.event_log), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
