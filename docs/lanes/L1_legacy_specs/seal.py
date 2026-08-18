#!/usr/bin/env python3
"""Seal a task-spec to its body so the two cannot drift apart.

    python3 tasks/seal.py sign  tasks/T-*.md    # stamp / restamp
    python3 tasks/seal.py check tasks/*.md      # verify, exit 1 on drift

The digest covers everything from the frontmatter through the last body line,
excluding the signed_off line itself. With APEX_SPEC_KEY set the algorithm is
hmac-sha256; without it, sha256 — and the stamp says which, because an unkeyed
digest proves the body has not changed, not who approved it.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import sys
from pathlib import Path

MARKER = re.compile(r"^signed_off:\s*(\S+)\s*$", re.MULTILINE)


def body_of(text: str) -> str:
    return MARKER.sub("", text).rstrip() + "\n"


def digest(text: str) -> str:
    key = os.getenv("APEX_SPEC_KEY", "")
    payload = body_of(text).encode()
    if key:
        return "hmac-sha256:" + hmac.new(key.encode(), payload, hashlib.sha256).hexdigest()[:32]
    return "sha256:" + hashlib.sha256(payload).hexdigest()[:32]


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in {"sign", "check"}:
        print(__doc__, file=sys.stderr)
        return 2
    mode, paths = sys.argv[1], [Path(p) for p in sys.argv[2:]]
    failures = 0
    for path in paths:
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        want = digest(text)
        found = MARKER.search(text)
        if mode == "sign":
            stamped = MARKER.sub("", text).rstrip() + f"\n\nsigned_off: {want}\n"
            path.write_text(stamped, encoding="utf-8")
            print(f"signed  {path.name}  {want}")
        else:
            if not found:
                print(f"UNSEALED {path.name}")
                failures += 1
            elif found.group(1) != want:
                print(f"DRIFTED  {path.name}\n  spec says {found.group(1)}\n  body is  {want}")
                failures += 1
            else:
                print(f"ok      {path.name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
