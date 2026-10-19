from __future__ import annotations

import sys
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEV))

from common.drain import DEFAULT_DRAIN_SECONDS, drain_seconds, plugin_attached  # noqa: E402


def test_no_plugin_means_no_drain() -> None:
    assert drain_seconds(None, {}) == 0.0
    assert drain_seconds("", {}) == 0.0
    assert drain_seconds("com.example.OtherPlugin", {}) == 0.0


def test_plugin_attached_uses_the_default_of_five_seconds() -> None:
    assert drain_seconds("apex.ApexPlugin", {}) == DEFAULT_DRAIN_SECONDS == 5.0


def test_plugin_attached_honours_the_env_override() -> None:
    assert drain_seconds("apex.ApexPlugin", {"APEX_OTLP_DRAIN_SECONDS": "2.5"}) == 2.5
    assert drain_seconds("apex.ApexPlugin", {"APEX_OTLP_DRAIN_SECONDS": "0"}) == 0.0


def test_env_override_is_ignored_without_the_plugin() -> None:
    assert drain_seconds("", {"APEX_OTLP_DRAIN_SECONDS": "30"}) == 0.0


def test_invalid_or_negative_override_falls_back_safely() -> None:
    assert drain_seconds("apex.ApexPlugin", {"APEX_OTLP_DRAIN_SECONDS": "abc"}) == 5.0
    assert drain_seconds("apex.ApexPlugin", {"APEX_OTLP_DRAIN_SECONDS": "-3"}) == 0.0
    assert drain_seconds("apex.ApexPlugin", {"APEX_OTLP_DRAIN_SECONDS": "  "}) == 5.0


def test_plugin_detection_handles_comma_separated_lists() -> None:
    assert plugin_attached("com.example.A, apex.ApexPlugin ,com.example.B")
    assert not plugin_attached("apex.ApexPluginX")


def test_common_drain_has_no_pyspark_import() -> None:
    source = (DEV / "common" / "drain.py").read_text(encoding="utf-8")
    assert "import pyspark" not in source and "from pyspark" not in source
