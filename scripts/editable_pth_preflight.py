"""Read-only diagnosis for macOS editable-install ``.pth`` metadata.

Run this with the target lane's active Python interpreter.  The command never
repairs or otherwise changes the environment it inspects.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import site
import stat
import sys
from typing import Callable, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
LANE_DISTRIBUTIONS = {
    "engine": "apex-engine",
    "serve": "apex-mcp",
    "memory": "apex-memory",
    "verify": "apex-verify",
}


class PthStatus(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    ABSENT = "pth_absent"
    WRONG_TARGET = "target_incorrect"
    HIDDEN = "pth_hidden"
    INSPECTION_ERROR = "inspection_error"
    NORMAL = "normal"


@dataclass(frozen=True)
class PthCheck:
    status: PthStatus
    candidate_count: int = 0


def _distribution_token(distribution: str) -> str:
    return distribution.lower().replace("-", "_").replace(".", "_")


def _candidate_pth_files(site_packages: Iterable[Path], distribution: str) -> list[Path]:
    token = _distribution_token(distribution)
    candidates: list[Path] = []
    for directory in site_packages:
        if not directory.is_dir():
            continue
        candidates.extend(
            path
            for path in directory.glob("*.pth")
            if "editable" in path.name.lower() and token in path.name.lower()
        )
    return sorted(candidates)


def _points_to(path: Path, expected_target: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeError:
        return False

    expected = expected_target.resolve(strict=False)
    for line in lines:
        if not line.strip() or line.startswith("#") or line.startswith(("import ", "import\t")):
            continue
        candidate = Path(line.rstrip()).expanduser()
        if not candidate.is_absolute():
            candidate = path.parent / candidate
        if candidate.resolve(strict=False) == expected:
            return True
    return False


def _has_macos_hidden_flag(path: Path) -> bool:
    hidden_flag = getattr(stat, "UF_HIDDEN", 0)
    flags = getattr(path.lstat(), "st_flags", 0)
    return bool(hidden_flag and flags & hidden_flag)


def inspect_editable_pth(
    *,
    platform: str,
    site_packages: Iterable[Path],
    distribution: str,
    expected_target: Path,
    is_hidden: Callable[[Path], bool] = _has_macos_hidden_flag,
) -> PthCheck:
    """Classify one lane's editable ``.pth`` without mutating the filesystem."""
    if platform != "darwin":
        return PthCheck(PthStatus.NOT_APPLICABLE)

    candidates: list[Path] = []
    try:
        candidates = _candidate_pth_files(site_packages, distribution)
        if not candidates:
            return PthCheck(PthStatus.ABSENT)

        correct = [path for path in candidates if _points_to(path, expected_target)]
        if not correct:
            return PthCheck(PthStatus.WRONG_TARGET, len(candidates))
        if any(not is_hidden(path) for path in correct):
            return PthCheck(PthStatus.NORMAL, len(candidates))
        return PthCheck(PthStatus.HIDDEN, len(candidates))
    except OSError:
        return PthCheck(PthStatus.INSPECTION_ERROR, len(candidates))


def _message(check: PthCheck, *, lane: str, distribution: str, version: str) -> str:
    header = (
        f"editable_pth_preflight status={check.status.value} "
        f"lane={lane} python={version} candidates={check.candidate_count}"
    )
    details = {
        PthStatus.NOT_APPLICABLE: "macOS hidden-file flags do not apply; no inspection performed.",
        PthStatus.ABSENT: f"No editable .pth for {distribution} was found in the active interpreter.",
        PthStatus.WRONG_TARGET: (
            f"The editable .pth for {distribution} does not point to {lane}/src; "
            "activate or rebuild the intended lane environment."
        ),
        PthStatus.HIDDEN: (
            f"The editable .pth points to {lane}/src but macOS marks it hidden; "
            "CPython may skip it. Rebuild the environment or inspect its flags manually."
        ),
        PthStatus.INSPECTION_ERROR: (
            "The editable .pth could not be inspected safely; "
            "check the active environment without changing its files or metadata."
        ),
        PthStatus.NORMAL: f"The editable .pth points to {lane}/src and is not hidden.",
    }
    return f"{header}\n{details[check.status]}"


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", required=True, choices=sorted(LANE_DISTRIBUTIONS))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    distribution = LANE_DISTRIBUTIONS[args.lane]
    version = ".".join(str(part) for part in sys.version_info[:3])
    site_packages = [Path(path) for path in site.getsitepackages()]
    check = inspect_editable_pth(
        platform=sys.platform,
        site_packages=site_packages,
        distribution=distribution,
        expected_target=ROOT / args.lane / "src",
    )
    print(_message(check, lane=args.lane, distribution=distribution, version=version))
    return 0 if check.status in {PthStatus.NORMAL, PthStatus.NOT_APPLICABLE} else 1


if __name__ == "__main__":
    raise SystemExit(main())
