"""The wire format: what a timestamp looks like when it leaves the API.

ONE format, fixed width: ISO 8601 with a ``T``, UTC, millisecond precision and
no offset — ``2026-09-20T10:00:00.123``. Millisecond because every time column
in the contract is ``DateTime64(3)``.

It used to be whatever FastAPI's encoder made of the driver's value, which is
``datetime.isoformat()``: six fractional digits when there were milliseconds,
NONE when there were not, and a ``+00:00`` suffix if the driver ever returned
an aware value — three shapes for one column. The console's browser path
meanwhile read ClickHouse's own JSON, ``2026-09-20 10:00:00.123``. The same
row carried a different timestamp depending on which door it came through.

The console normalises to this same format on its side
(``front/src/data/timestamp.ts``), and a test reads the pattern from that file
and holds every resource route to it.

Converted HERE, at the HTTP boundary, and not in ``ReadStore``: the MCP tools
read those rows as datetimes and do arithmetic on them.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

# The console's names for a point in time, across every row it reads, plus the
# one health reports. A datetime VALUE is converted wherever it appears. A
# STRING is normalised only under one of these keys: evidence, detail and fix
# are untrusted text written by the observed job, and a date inside one of
# them is part of that text, not a timestamp to reformat.
TIMESTAMP_FIELDS = frozenset(
    {"ts", "started_at", "observed_at", "first_run", "last_run", "latest_ts"}
)

_PARSEABLE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:?\d{2})?$"
)


def wire_timestamp(value: datetime) -> str:
    """One datetime, in the wire format.

    An aware value is CONVERTED to UTC, never stripped: ``+02:00`` with the
    offset dropped is a timestamp two hours wrong that still looks valid. A
    naive value is UTC already — that is what the driver hands back.
    Sub-millisecond digits are truncated, not rounded, so a value never moves
    into the next millisecond on its way out.
    """
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(sep="T", timespec="milliseconds")


def wire_timestamp_text(value: str) -> str:
    """A timestamp that arrived as text, in the wire format.

    Anything this does not recognise is returned VERBATIM. A value that is not
    a timestamp is not improved by being turned into one.
    """
    match = _PARSEABLE.match(value.strip())
    if match is None:
        return value
    date, time, fraction, zone = match.groups()
    try:
        moment = datetime.fromisoformat(f"{date}T{time}")
    except ValueError:
        return value
    moment = moment.replace(microsecond=int(((fraction or "") + "000000")[:6]))
    if zone and zone != "Z":
        digits = zone[1:].replace(":", "")
        offset = timedelta(hours=int(digits[:2]), minutes=int(digits[2:]))
        moment = moment - offset if zone[0] == "+" else moment + offset
    return wire_timestamp(moment)


def wire(payload: Any, key: str | None = None) -> Any:
    """A response payload with every timestamp in the wire format.

    Walks rows and lists; leaves every other value exactly as it was.
    """
    if isinstance(payload, datetime):
        return wire_timestamp(payload)
    if isinstance(payload, dict):
        return {name: wire(value, name) for name, value in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [wire(value, key) for value in payload]
    if isinstance(payload, str) and key in TIMESTAMP_FIELDS:
        return wire_timestamp_text(payload)
    return payload
