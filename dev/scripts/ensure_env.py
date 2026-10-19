"""Create a local .env from one example or a baseline plus an overlay.

The overlay is MERGED, not appended: a key the overlay defines replaces the
baseline value in place (keeping the baseline's comments and ordering), and
only genuinely new keys are appended under the overlay header. The result
holds every key exactly once, so readers that disagree on "first wins" versus
"last wins" (shell `source`, compose --env-file, python parsers) all see the
same value. An existing destination is never rewritten.
"""

from __future__ import annotations

import sys
from pathlib import Path

OVERLAY_HEADER = "# Spark compatibility overlay"


def parse_assignment(line: str) -> tuple[str, str] | None:
    """Return (key, value) for a KEY=value line, else None for comments/blanks."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, _, value = stripped.partition("=")
    key = key.strip()
    if not key or " " in key:
        return None
    return key, value.strip()


def merge_env(baseline: str, overlay: str | None) -> str:
    """Merge overlay assignments into the baseline text (see module docstring)."""
    if overlay is None:
        return baseline

    overrides: dict[str, str] = {}
    order: list[str] = []
    for line in overlay.splitlines():
        parsed = parse_assignment(line)
        if parsed is None:
            continue
        key, value = parsed
        if key not in overrides:
            order.append(key)
        overrides[key] = value

    merged: list[str] = []
    seen: set[str] = set()
    for line in baseline.splitlines():
        parsed = parse_assignment(line)
        if parsed is None:
            merged.append(line)
            continue
        key, _ = parsed
        if key in seen:
            # Duplicate key inside the baseline itself: keep the first occurrence
            # only, so the output never carries a key twice.
            continue
        seen.add(key)
        if key in overrides:
            merged.append(f"{key}={overrides[key]}")
        else:
            merged.append(line)

    new_keys = [key for key in order if key not in seen]
    if new_keys:
        merged.append("")
        merged.append(OVERLAY_HEADER)
        merged.extend(f"{key}={overrides[key]}" for key in new_keys)
    return "\n".join(merged).rstrip("\n") + "\n"


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

    baseline_text = example.read_text(encoding="utf-8")
    overlay_text = overlay.read_text(encoding="utf-8") if overlay else None
    destination.write_text(merge_env(baseline_text, overlay_text), encoding="utf-8")
    if overlay:
        print(f"created {destination} from {example} + {overlay}")
    else:
        print(f"created {destination} from {example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
