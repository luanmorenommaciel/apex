"""Config sources: ClickHouse job_conf primary, History Server fallback."""

from __future__ import annotations

import io
import json
from types import SimpleNamespace

import pytest

from apex_verify.config_source import (
    ClickHouseJobConfSource,
    HistoryServerSource,
    resolve_config,
    slots_from_conf,
)
from apex_verify.models import ConfigKnowledge

JOB = "app-20260728120000-0001"

FULL_CONF = {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    "spark.sql.shuffle.partitions": "100",
}


def _ch_client(rows):
    """A fake clickhouse-connect query result carrying `conf` Map rows."""
    def query(sql, parameters=None):
        assert parameters == {"job_id": JOB}      # bound, never interpolated
        return SimpleNamespace(column_names=["conf"], result_rows=rows)
    return SimpleNamespace(query=query)


class _Resp:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


# ── slots: derived from facts or not at all ──────────────────────────────────
def test_slots_from_explicitly_set_executor_keys():
    conf = {**FULL_CONF, "spark.executor.instances": "2", "spark.executor.cores": "4"}
    assert slots_from_conf(conf) == 8


@pytest.mark.parametrize("conf", [
    FULL_CONF,                                                    # keys absent (not explicitly set)
    {**FULL_CONF, "spark.executor.instances": "2"},               # only one key
    {**FULL_CONF, "spark.executor.instances": "2", "spark.executor.cores": "auto"},
    {**FULL_CONF, "spark.executor.instances": "0", "spark.executor.cores": "4"},
    None,
])
def test_slots_is_none_rather_than_a_guess(conf):
    assert slots_from_conf(conf) is None


# ── ClickHouse primary ───────────────────────────────────────────────────────
def test_clickhouse_row_is_known_and_carries_slots_when_set():
    conf = {**FULL_CONF, "spark.executor.instances": "1", "spark.executor.cores": "8"}
    src = ClickHouseJobConfSource(client=_ch_client([(conf,)]))
    r = src.fetch(JOB)
    assert r.knowledge is ConfigKnowledge.KNOWN
    assert r.source == "clickhouse_job_conf"
    assert r.config == conf
    assert r.slots == 8


def test_clickhouse_row_without_resource_keys_is_known_but_slotsless():
    src = ClickHouseJobConfSource(client=_ch_client([(FULL_CONF,)]))
    r = src.fetch(JOB)
    assert r.knowledge is ConfigKnowledge.KNOWN
    assert r.slots is None
    assert "confidence capped" in r.detail


def test_clickhouse_with_no_row_is_unknown_not_unavailable():
    src = ClickHouseJobConfSource(client=_ch_client([]))
    r = src.fetch(JOB)
    assert r.knowledge is ConfigKnowledge.UNKNOWN
    assert r.config is None


def test_clickhouse_driver_failure_is_unavailable():
    def boom(sql, parameters=None):
        raise ConnectionError("refused")
    src = ClickHouseJobConfSource(client=SimpleNamespace(query=boom))
    r = src.fetch(JOB)
    assert r.knowledge is ConfigKnowledge.UNAVAILABLE


# ── History Server fallback ──────────────────────────────────────────────────
def _patch_urlopen(monkeypatch, fn):
    monkeypatch.setattr("apex_verify.config_source.urllib.request.urlopen", fn)


def test_history_server_filters_to_the_allowlist(monkeypatch):
    env = {"sparkProperties": [
        ["spark.sql.adaptive.skewJoin.enabled", "true"],
        ["spark.executor.instances", "2"],
        ["spark.executor.cores", "4"],
        ["spark.hadoop.fs.s3a.secret.key", "AKIA-LEAK-ME-NOT"],   # must be dropped
        ["spark.eventLog.dir", "s3a://logs"],
    ]}
    _patch_urlopen(monkeypatch, lambda url, timeout=None: _Resp(env))
    r = HistoryServerSource("http://hs:18080").fetch(JOB)
    assert r.knowledge is ConfigKnowledge.KNOWN
    assert r.source == "history_server"
    assert "spark.sql.adaptive.skewJoin.enabled" in r.config
    assert not any("secret" in k for k in r.config)               # credentials never carried
    assert "spark.eventLog.dir" not in r.config
    assert r.slots == 8


def test_history_server_unreachable_is_unavailable(monkeypatch):
    def boom(url, timeout=None):
        raise OSError("connection refused")
    _patch_urlopen(monkeypatch, boom)
    r = HistoryServerSource("http://hs:18080").fetch(JOB)
    assert r.knowledge is ConfigKnowledge.UNAVAILABLE


def test_history_server_with_no_allowlisted_keys_is_unknown(monkeypatch):
    _patch_urlopen(monkeypatch, lambda url, timeout=None: _Resp({"sparkProperties": []}))
    r = HistoryServerSource("http://hs:18080").fetch(JOB)
    assert r.knowledge is ConfigKnowledge.UNKNOWN


# ── the chain: ClickHouse first, history as fallback ─────────────────────────
def test_chain_prefers_clickhouse_and_never_consults_the_fallback(monkeypatch):
    called = []

    def spy(url, timeout=None):
        called.append(url)
        return _Resp({"sparkProperties": [["spark.sql.adaptive.enabled", "false"]]})

    _patch_urlopen(monkeypatch, spy)
    ch = ClickHouseJobConfSource(client=_ch_client([(FULL_CONF,)]))
    r = resolve_config(JOB, sources=[ch, HistoryServerSource("http://hs:18080")])
    assert r.knowledge is ConfigKnowledge.KNOWN
    assert r.source == "clickhouse_job_conf"
    assert called == []


def test_chain_falls_back_to_history_when_clickhouse_has_no_row(monkeypatch):
    env = {"sparkProperties": [["spark.sql.adaptive.enabled", "false"]]}
    _patch_urlopen(monkeypatch, lambda url, timeout=None: _Resp(env))
    ch = ClickHouseJobConfSource(client=_ch_client([]))
    r = resolve_config(JOB, sources=[ch, HistoryServerSource("http://hs:18080")])
    assert r.knowledge is ConfigKnowledge.KNOWN
    assert r.source == "history_server"
    assert len(r.attempts) == 2
    assert "unknown" in r.attempts[0]


def test_chain_reports_unknown_with_full_provenance_when_all_sources_fail(monkeypatch):
    def boom(url, timeout=None):
        raise OSError("no history server on this platform")
    _patch_urlopen(monkeypatch, boom)
    ch = ClickHouseJobConfSource(client=_ch_client([]))
    r = resolve_config(JOB, sources=[ch, HistoryServerSource("http://hs:18080")])
    assert r.knowledge is ConfigKnowledge.UNKNOWN
    assert r.source == "none"
    assert r.config is None
    assert len(r.attempts) == 2
    assert "clickhouse_job_conf" in r.attempts[0]
    assert "history_server" in r.attempts[1]
