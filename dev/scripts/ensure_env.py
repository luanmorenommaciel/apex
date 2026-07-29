"""Create a local .env from one example or a baseline plus an overlay."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print(
            "usage: ensure_env.py <example> [overlay] <destination>",
            file=sys.stderr,
        )
        return 2

    paths = [Path(value) for value in sys.argv[1:]]
    example = paths[0]
    overlay = paths[1] if len(paths) == 3 else None
    destination = paths[-1]
    if destination.exists():
        return 0

    shutil.copyfile(example, destination)
    if overlay:
        with destination.open("a", encoding="utf-8") as target, overlay.open(
            encoding="utf-8"
        ) as source:
            target.write("\n# Spark compatibility overlay\n")
            shutil.copyfileobj(source, target)
        print(f"created {destination} from {example} + {overlay}")
    else:
        print(f"created {destination} from {example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
