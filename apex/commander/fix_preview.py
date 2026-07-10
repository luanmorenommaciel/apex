"""Preview-only fix support for Commander recommendations."""

from difflib import unified_diff
from pathlib import Path


def build_fix_preview(path, recommendation, *, replacement):
    """Build a unified diff without modifying the target file."""
    target = Path(path)
    original = target.read_text(encoding="utf-8")
    diff = "".join(
        unified_diff(
            original.splitlines(keepends=True),
            replacement.splitlines(keepends=True),
            fromfile=str(target),
            tofile=f"{target} (apex preview)",
        )
    )
    return {
        "mode": "preview",
        "target": str(target),
        "recommendation": recommendation,
        "diff": diff,
    }
