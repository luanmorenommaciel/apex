from __future__ import annotations

import os
from pathlib import Path
import stat
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import editable_pth_preflight as preflight
from scripts.editable_pth_preflight import PthCheck, PthStatus, inspect_editable_pth


LANES = (
    ("engine", "apex-engine"),
    ("serve", "apex-mcp"),
    ("memory", "apex-memory"),
    ("verify", "apex-verify"),
)


def check(site_packages: Path, target: Path, distribution: str, *, hidden: set[Path] | None = None):
    hidden = hidden or set()
    return inspect_editable_pth(
        platform="darwin",
        site_packages=[site_packages],
        distribution=distribution,
        expected_target=target,
        is_hidden=lambda path: path in hidden,
    )


def editable_pth(
    site_packages: Path,
    distribution: str,
    target: Path | str,
    *,
    encoding: str = "utf-8",
) -> Path:
    token = distribution.replace("-", "_")
    path = site_packages / f"_editable_impl_{token}.pth"
    path.write_text(f"{target}\n", encoding=encoding)
    return path


def test_absent_editable_pth_is_distinct(tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()

    assert check(site_packages, tmp_path / "engine" / "src", "apex-engine").status is PthStatus.ABSENT


def test_incorrect_editable_target_is_distinct(tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    editable_pth(site_packages, "apex-engine", tmp_path / "other" / "src")

    assert check(site_packages, tmp_path / "engine" / "src", "apex-engine").status is PthStatus.WRONG_TARGET


def test_hidden_correct_editable_pth_is_distinct(tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    path = editable_pth(site_packages, "apex-engine", target)

    assert check(site_packages, target, "apex-engine", hidden={path}).status is PthStatus.HIDDEN


def test_visible_correct_editable_pth_is_normal(tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    editable_pth(site_packages, "apex-engine", target)

    assert check(site_packages, target, "apex-engine").status is PthStatus.NORMAL


def test_relative_target_is_resolved_from_containing_site_packages(tmp_path):
    site_packages = tmp_path / "venv" / "lib" / "site-packages"
    site_packages.mkdir(parents=True)
    target = tmp_path / "engine" / "src"
    relative_target = os.path.relpath(target, site_packages)
    editable_pth(site_packages, "apex-engine", relative_target)

    assert check(site_packages, target, "apex-engine").status is PthStatus.NORMAL


def test_utf8_bom_is_accepted(tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    editable_pth(site_packages, "apex-engine", target, encoding="utf-8-sig")

    assert check(site_packages, target, "apex-engine").status is PthStatus.NORMAL


@pytest.mark.parametrize("prefix", (" ", "\t"))
def test_leading_whitespace_before_absolute_target_is_wrong_target(tmp_path, prefix):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    editable_pth(site_packages, "apex-engine", f"{prefix}{target}")

    assert check(site_packages, target, "apex-engine").status is PthStatus.WRONG_TARGET


def test_import_tab_line_is_ignored_as_executable_code(monkeypatch, tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    path = editable_pth(site_packages, "apex-engine", "import\tpackage")

    def must_not_parse(_path):
        raise AssertionError("executable .pth line was parsed as a path")

    monkeypatch.setattr(Path, "expanduser", must_not_parse)

    assert preflight._points_to(path, target) is False


def test_read_oserror_is_inspection_error(monkeypatch, tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    editable_pth(site_packages, "apex-engine", target)

    def deny_read(_path, **_kwargs):
        raise OSError("denied /Users/example/private-workspace/editable.pth")

    monkeypatch.setattr(Path, "read_text", deny_read)

    result = check(site_packages, target, "apex-engine")

    assert result.status is PthStatus.INSPECTION_ERROR
    assert result.candidate_count == 1


def test_metadata_oserror_is_inspection_error(monkeypatch, tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    editable_pth(site_packages, "apex-engine", target)

    def deny_metadata(_path):
        raise OSError("denied /Users/example/private-workspace/editable.pth")

    result = inspect_editable_pth(
        platform="darwin",
        site_packages=[site_packages],
        distribution="apex-engine",
        expected_target=target,
        is_hidden=deny_metadata,
    )

    assert result.status is PthStatus.INSPECTION_ERROR
    assert result.candidate_count == 1


@pytest.mark.skipif(
    sys.platform != "darwin" or not hasattr(os, "chflags") or not getattr(stat, "UF_HIDDEN", 0),
    reason="requires macOS UF_HIDDEN support",
)
def test_real_uf_hidden_inspection_is_read_only(tmp_path):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    path = editable_pth(site_packages, "apex-engine", target)
    os.chflags(path, path.stat().st_flags | stat.UF_HIDDEN)
    before = path.stat()
    before_contents = path.read_bytes()

    result = inspect_editable_pth(
        platform="darwin",
        site_packages=[site_packages],
        distribution="apex-engine",
        expected_target=target,
    )

    after = path.stat()
    assert result.status is PthStatus.HIDDEN
    assert after.st_flags == before.st_flags
    assert after.st_mode == before.st_mode
    assert path.read_bytes() == before_contents


@pytest.mark.parametrize(("lane", "distribution"), LANES)
def test_each_lane_uses_its_distribution_and_src_target(tmp_path, lane, distribution):
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    target = ROOT / lane / "src"
    editable_pth(site_packages, distribution, target)

    assert preflight.LANE_DISTRIBUTIONS[lane] == distribution
    assert check(site_packages, target, distribution).status is PthStatus.NORMAL


def test_non_macos_is_no_op_before_touching_filesystem():
    def must_not_run(_path):
        raise AssertionError("hidden metadata was inspected outside macOS")

    result = inspect_editable_pth(
        platform="linux",
        site_packages=[Path("/path/that/does/not/exist")],
        distribution="apex-engine",
        expected_target=Path("/also/not/inspected"),
        is_hidden=must_not_run,
    )

    assert result.status is PthStatus.NOT_APPLICABLE
    assert result.candidate_count == 0


@pytest.mark.parametrize(("lane", "distribution"), LANES)
def test_cli_selects_each_lane_distribution_and_src_target(monkeypatch, capsys, lane, distribution):
    observed = {}

    monkeypatch.setattr(preflight.site, "getsitepackages", lambda: ["/Users/example/site-packages"])

    def inspect(**kwargs):
        observed.update(kwargs)
        return PthCheck(PthStatus.NORMAL)

    monkeypatch.setattr(preflight, "inspect_editable_pth", inspect)

    assert preflight.main(["--lane", lane]) == 0
    assert observed["distribution"] == distribution
    assert observed["expected_target"] == ROOT / lane / "src"
    assert "status=normal" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("status", "expected_exit"),
    (
        (PthStatus.NORMAL, 0),
        (PthStatus.NOT_APPLICABLE, 0),
        (PthStatus.ABSENT, 1),
        (PthStatus.WRONG_TARGET, 1),
        (PthStatus.HIDDEN, 1),
        (PthStatus.INSPECTION_ERROR, 1),
    ),
)
def test_cli_exit_codes_and_output_are_sanitized(monkeypatch, capsys, status, expected_exit):
    personal_site_packages = Path("/Users/example/private-workspace/site-packages")

    monkeypatch.setattr(preflight.site, "getsitepackages", lambda: [str(personal_site_packages)])
    monkeypatch.setattr(
        preflight,
        "inspect_editable_pth",
        lambda **_kwargs: PthCheck(status=status, candidate_count=1),
    )

    assert preflight.main(["--lane", "engine"]) == expected_exit
    output = capsys.readouterr().out

    assert f"status={status.value}" in output
    assert str(personal_site_packages) not in output
    assert "/Users/example" not in output
    assert str(ROOT) not in output


@pytest.mark.parametrize(
    "status",
    (PthStatus.ABSENT, PthStatus.WRONG_TARGET, PthStatus.HIDDEN, PthStatus.INSPECTION_ERROR),
)
def test_cli_adversarial_output_does_not_expose_pth_target(monkeypatch, capsys, status):
    personal_target = "/Users/example/private-workspace/engine/src"

    monkeypatch.setattr(
        preflight,
        "inspect_editable_pth",
        lambda **_kwargs: PthCheck(status=status, candidate_count=1),
    )

    assert preflight.main(["--lane", "engine"]) == 1
    output = capsys.readouterr().out

    assert personal_target not in output
    assert "/Users/example" not in output


def test_cli_inspection_error_has_no_path_stderr_or_traceback(monkeypatch, capsys, tmp_path):
    site_packages = tmp_path / "personal-site-packages"
    site_packages.mkdir()
    target = tmp_path / "engine" / "src"
    editable_pth(site_packages, "apex-engine", target)
    personal_path = "/Users/example/private-workspace/editable.pth"

    def deny_read(_path, **_kwargs):
        raise OSError(f"cannot read {personal_path}")

    monkeypatch.setattr(Path, "read_text", deny_read)
    monkeypatch.setattr(preflight.site, "getsitepackages", lambda: [str(site_packages)])
    monkeypatch.setattr(preflight.sys, "platform", "darwin")

    assert preflight.main(["--lane", "engine"]) == 1
    captured = capsys.readouterr()

    assert "status=inspection_error" in captured.out
    assert str(site_packages) not in captured.out
    assert personal_path not in captured.out
    assert "/Users/example" not in captured.out
    assert str(ROOT) not in captured.out
    assert captured.err == ""
    assert "Traceback" not in captured.out


@pytest.mark.parametrize(
    ("expected_status", "pth_target"),
    (
        (PthStatus.ABSENT, None),
        (PthStatus.WRONG_TARGET, Path("/Users/example/private-workspace/engine/src")),
    ),
)
def test_cli_real_adversarial_inputs_are_sanitized(monkeypatch, capsys, tmp_path, expected_status, pth_target):
    site_packages = tmp_path / "personal-site-packages"
    site_packages.mkdir()
    if pth_target is not None:
        editable_pth(site_packages, "apex-engine", pth_target)

    monkeypatch.setattr(preflight.site, "getsitepackages", lambda: [str(site_packages)])
    monkeypatch.setattr(preflight.sys, "platform", "darwin")

    assert preflight.main(["--lane", "engine"]) == 1
    output = capsys.readouterr().out

    assert f"status={expected_status.value}" in output
    assert str(site_packages) not in output
    assert "/Users/example" not in output
