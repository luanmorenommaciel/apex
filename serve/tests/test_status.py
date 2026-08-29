"""The apex_status payload: constructible degraded, schema-renderable, credential-free.

ServerStatus is the one model that must be constructible when nothing works —
a status tool that needs a healthy store to answer only answers when you do
not need it. These tests pin that, and pin the absence of any field that could
carry a credential to the model.
"""

from __future__ import annotations

from apex_mcp.models import ServerStatus

CREDENTIAL_NAMES = {"password", "dsn", "secret", "user", "username", "url"}


def test_degraded_status_constructs_with_only_connected():
    """B-1 — connected is the only required field; everything else defaults."""
    status = ServerStatus(connected=False)

    assert status.connected is False
    assert status.run_count == 0
    assert status.job_count == 0
    assert status.latest_ingest_ts is None
    assert status.latest_ingest_age_seconds is None
    assert status.contract_tables == {}
    assert status.using_defaults == []
    assert status.tools == []
    assert status.degraded_reason is None
    assert status.remediation is None


def test_contracted_field_set_is_present():
    """B-1 — the fields apex_status promises are all on the model."""
    keys = set(ServerStatus(connected=False).model_dump())

    expected = {
        "connected",
        "database",
        "run_count",
        "latest_ingest_age_seconds",
        "contract_tables",
        "using_defaults",
        "degraded_reason",
        "remediation",
        "tools",
    }
    assert expected <= keys, expected - keys


def test_schema_renders_with_connected_required_and_boolean():
    """B-2 — FastMCP derives the output schema from this; it must render."""
    schema = ServerStatus.model_json_schema()

    assert "connected" in schema["required"]
    assert schema["properties"]["connected"]["type"] == "boolean"


def test_no_field_can_carry_a_credential():
    """B-3 — the model has no slot a password could ever land in."""
    fields = set(ServerStatus.model_fields)

    assert not (fields & CREDENTIAL_NAMES), fields & CREDENTIAL_NAMES


def test_using_defaults_carries_names_not_values():
    """B-3 — naming CLICKHOUSE_PASSWORD is safe; carrying its value is not."""
    status = ServerStatus(
        connected=True,
        using_defaults=["CLICKHOUSE_HOST", "CLICKHOUSE_PASSWORD"],
    )

    dumped = status.model_dump()
    assert dumped["using_defaults"] == ["CLICKHOUSE_HOST", "CLICKHOUSE_PASSWORD"]
    # A value would show up as anything that is not one of the known names.
    assert all(name.startswith("CLICKHOUSE_") for name in dumped["using_defaults"])
