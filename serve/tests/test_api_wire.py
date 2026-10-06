"""The wire format: one timestamp shape, whatever the driver hands over."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from apex_api.app import create_app
from apex_api.config import Settings
from apex_api.wire import wire, wire_timestamp, wire_timestamp_text
from apex_mcp.ch import ReadStore
from tests.test_ch import _ConsoleClient

TOKEN = "test-token-6c1f9a"
SETTINGS = Settings(tokens=frozenset({TOKEN}))
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def test_a_datetime_leaves_in_one_shape_whatever_its_precision():
    """isoformat() gave six digits, or none at all when the milliseconds were zero."""
    assert wire_timestamp(datetime(2026, 9, 20, 10, 0, 0, 123000)) == "2026-09-20T10:00:00.123"
    assert wire_timestamp(datetime(2026, 9, 20, 10, 0, 0)) == "2026-09-20T10:00:00.000"
    # Truncated, never rounded: a value does not move into the next millisecond.
    assert wire_timestamp(datetime(2026, 9, 20, 10, 0, 0, 123999)) == "2026-09-20T10:00:00.123"


def test_an_aware_datetime_is_converted_not_stripped():
    """+02:00 with the offset dropped is two hours wrong and still looks valid."""
    plus_two = timezone(timedelta(hours=2))
    assert wire_timestamp(datetime(2026, 9, 20, 12, 0, 0, tzinfo=plus_two)) == "2026-09-20T10:00:00.000"
    assert wire_timestamp(datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)) == "2026-09-20T10:00:00.000"


def test_text_timestamps_reach_the_same_instant():
    same = "2026-09-20T10:00:00.123"
    for arrived in (
        "2026-09-20 10:00:00.123",        # ClickHouse's own JSON, the browser's path
        "2026-09-20T10:00:00.123000",     # isoformat() with microseconds
        "2026-09-20T10:00:00.123Z",
        "2026-09-20T12:00:00.123+02:00",
        "2026-09-20T12:00:00.123+0200",
        "2026-09-20T05:30:00.123-04:30",
        same,                             # already on the wire: unchanged
    ):
        assert wire_timestamp_text(arrived) == same, arrived
    assert wire_timestamp_text("2026-09-20 10:00:00") == "2026-09-20T10:00:00.000"


def test_what_is_not_a_timestamp_is_carried_verbatim():
    for value in ("", "yesterday", "2026-09-20", "2026-13-45 99:99:99", "10:00:00"):
        assert wire_timestamp_text(value) == value, value


def test_only_timestamp_fields_are_read_as_timestamps():
    """evidence, detail and fix are untrusted text; a date inside one is text."""
    row = {
        "ts": "2026-09-20 10:00:00.123",
        "evidence": "2026-09-20 10:00:00.123",
        "detail": "seen at 2026-09-20 10:00:00",
        "stage_id": 4,
        "value": None,
        "nested": [{"observed_at": datetime(2026, 9, 20, 10, 0, 0, 5000)}],
    }
    assert wire(row) == {
        "ts": "2026-09-20T10:00:00.123",
        "evidence": "2026-09-20 10:00:00.123",
        "detail": "seen at 2026-09-20 10:00:00",
        "stage_id": 4,
        "value": None,
        "nested": [{"observed_at": "2026-09-20T10:00:00.005"}],
    }
    # A datetime VALUE is converted under any key: nothing else leaves as one.
    assert wire({"anything": datetime(2026, 9, 20, 10, 0, 0)}) == {"anything": "2026-09-20T10:00:00.000"}
    assert wire(None) is None


def test_a_route_emits_the_wire_format_from_a_driver_datetime():
    rows = [{"job_id": "j", "stage_id": 1, "ts": datetime(2026, 9, 20, 10, 0, 0, 123000)}]
    app = TestClient(create_app(store=ReadStore(_ConsoleClient(run_rows=rows)), settings=SETTINGS))
    got = app.get("/v1/runs/j/stages", headers=AUTH).json()
    assert got[0]["ts"] == "2026-09-20T10:00:00.123"


def test_health_reports_its_timestamp_in_the_wire_format():
    class _Health(_ConsoleClient):
        def query(self, query: str, parameters: dict | None = None):
            self.calls.append((query, parameters or {}))
            rows = [{"row_count": 3, "job_count": 1, "latest_ts": datetime(2026, 9, 20, 10, 0, 0)}]
            return type("R", (), {"named_results": lambda _s: list(rows)})()

    app = TestClient(create_app(store=ReadStore(_Health()), settings=SETTINGS))
    assert app.get("/v1/health").json()["latest_ts"] == "2026-09-20T10:00:00.000"
