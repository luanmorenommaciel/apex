"""Preview-only fix support for Commander recommendations."""

from difflib import unified_diff
from hashlib import sha256
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
        "before_sha256": _sha256_text(original),
        "after_sha256": _sha256_text(replacement),
        "diff_sha256": _sha256_text(diff),
    }


def _sha256_text(value):
    return sha256(value.encode("utf-8")).hexdigest()
