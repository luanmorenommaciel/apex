"""Generate the local, read-only Apex Commander UI MVP."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apex.commander.commander_ui import write_commander_ui


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="docs/presentations/apex-commander-ui-mvp.html",
    )
    args = parser.parse_args()
    snapshot = write_commander_ui(args.root, args.output)
    print(f"commander_ui={args.output}")
    print(f"status={snapshot['overview']['status']}")
    print(f"findings={len(snapshot['findings'])}")
    print("mode=read_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
