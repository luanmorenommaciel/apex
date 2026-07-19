"""Generate the static Apex product-readiness report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.product_report import write_product_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="docs/presentations/apex-product-readiness-2026-07-19.html",
    )
    parser.add_argument(
        "--summary",
        default="evidence/apex-product-readiness-2026-07-19-summary.json",
    )
    args = parser.parse_args()

    snapshot = write_product_report(args.root, args.output)
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"product_report={args.output}")
    print(f"summary={args.summary}")
    print(f"status={snapshot['status']}")
    print(f"score={snapshot['score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
