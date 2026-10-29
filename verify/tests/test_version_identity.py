"""The package declares one version, and every place that reports it agrees.

`pyproject.toml` is the source of truth. `apex_verify.__version__` and the
default `Verdict.verify_version` (persisted as provenance) must match it.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import apex_verify
from apex_verify.models import Verdict

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _pyproject_version() -> str:
    with PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def test_module_version_matches_pyproject():
    assert apex_verify.__version__ == _pyproject_version()


def test_verdict_default_verify_version_matches_pyproject():
    assert Verdict.model_fields["verify_version"].default == _pyproject_version()
