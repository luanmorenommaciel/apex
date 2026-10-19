from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
SCRIPT = DEV / "scripts" / "ensure_env.py"
SPEC = importlib.util.spec_from_file_location("ensure_env", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

BASELINE = """# header comment
SPARK_IMAGE=apache/spark:4.0.1
SPARK_VERSION=4.0.1

# cluster
SPARK_WORKER_CORES=8
APEX_IMAGE=apex-spark:local
"""

OVERLAY = """# Additive cell. Do not replace dev/.env.
SPARK_IMAGE=apache/spark:4.1.2
SPARK_VERSION=4.1.2
APEX_IMAGE=apex-spark:4.1.2-local
MINIO_API_PORT=19100
"""


def _assignments(text: str) -> dict[str, str]:
    pairs = [MODULE.parse_assignment(line) for line in text.splitlines()]
    found = [pair for pair in pairs if pair is not None]
    keys = [key for key, _ in found]
    assert len(keys) == len(set(keys)), f"duplicate keys in output: {keys}"
    return dict(found)


def test_overlay_keys_replace_baseline_values_in_place() -> None:
    merged = MODULE.merge_env(BASELINE, OVERLAY)
    values = _assignments(merged)
    assert values["SPARK_IMAGE"] == "apache/spark:4.1.2"
    assert values["SPARK_VERSION"] == "4.1.2"
    assert values["APEX_IMAGE"] == "apex-spark:4.1.2-local"
    assert values["SPARK_WORKER_CORES"] == "8"
    # Baseline ordering and comments survive.
    lines = merged.splitlines()
    assert lines[0] == "# header comment"
    assert lines.index("SPARK_IMAGE=apache/spark:4.1.2") < lines.index("# cluster")


def test_new_overlay_keys_are_appended_once_under_the_header() -> None:
    merged = MODULE.merge_env(BASELINE, OVERLAY)
    values = _assignments(merged)
    assert values["MINIO_API_PORT"] == "19100"
    lines = merged.splitlines()
    assert lines.count(MODULE.OVERLAY_HEADER) == 1
    assert lines.index(MODULE.OVERLAY_HEADER) < lines.index("MINIO_API_PORT=19100")
    assert merged.count("SPARK_IMAGE=") == 1


def test_no_overlay_returns_baseline_unchanged() -> None:
    assert MODULE.merge_env(BASELINE, None) == BASELINE


def test_duplicate_baseline_keys_collapse_to_the_first_occurrence() -> None:
    baseline = "A=1\nA=2\nB=3\n"
    merged = MODULE.merge_env(baseline, "B=9\n")
    assert _assignments(merged) == {"A": "1", "B": "9"}


def test_existing_destination_is_never_rewritten(tmp_path: Path) -> None:
    example = tmp_path / "example.env"
    overlay = tmp_path / "overlay.env"
    destination = tmp_path / ".env"
    example.write_text(BASELINE, encoding="utf-8")
    overlay.write_text(OVERLAY, encoding="utf-8")
    destination.write_text("KEEP=me\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(example), str(overlay), str(destination)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert destination.read_text(encoding="utf-8") == "KEEP=me\n"


def test_cli_creates_merged_destination(tmp_path: Path) -> None:
    example = tmp_path / "example.env"
    overlay = tmp_path / "overlay.env"
    destination = tmp_path / ".env"
    example.write_text(BASELINE, encoding="utf-8")
    overlay.write_text(OVERLAY, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(example), str(overlay), str(destination)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    values = _assignments(destination.read_text(encoding="utf-8"))
    assert values["SPARK_IMAGE"] == "apache/spark:4.1.2"
    assert values["MINIO_API_PORT"] == "19100"


def test_real_examples_merge_to_one_spark_image_at_4_1_2(tmp_path: Path) -> None:
    merged = MODULE.merge_env(
        (DEV / ".env.example").read_text(encoding="utf-8"),
        (DEV / ".env.spark41.example").read_text(encoding="utf-8"),
    )
    values = _assignments(merged)
    assert values["SPARK_IMAGE"].startswith("apache/spark:4.1.2")
    assert values["APEX_JAR_TARGET"] == "apex_41"
    assert values["SPARK_WORKER_CORES"] == "8"
