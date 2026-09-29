/**
 * The one timestamp format a Repository returns — the Apex API's.
 *
 * ISO 8601 with a `T`, UTC, millisecond precision, no offset:
 * `2026-09-20T10:00:00.123`. Millisecond because every time column in the
 * contract is DateTime64(3); fixed width, so it sorts as text.
 *
 * The same row used to carry a different timestamp depending on which door it
 * came through. ClickHouse's own JSON — the browser path — writes
 * `2026-09-20 10:00:00.123`. The API wrote whatever Python's isoformat() made
 * of the driver's value: six fractional digits, or none at all when the
 * milliseconds were zero. Nothing on screen showed it only because one
 * consumer normalised and the other sliced ten characters.
 *
 * The API emits this format deliberately now (serve/src/apex_api/wire.py), and
 * a test on that side reads WIRE_TIMESTAMP from THIS file and holds every
 * route to it. Change the pattern here and that test is what tells you the two
 * hosts no longer agree.
 */
import type { WireTimestamp } from "@/contract/types";

export const WIRE_TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$/;

const PARSEABLE =
  /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:?\d{2})?$/;

/**
 * A timestamp from any source, in the wire format.
 *
 * An offset is CONVERTED to UTC, never dropped: `+02:00` with the offset
 * stripped is a timestamp two hours wrong that still looks valid.
 * Sub-millisecond digits are truncated, not rounded. Anything this does not
 * recognise is returned verbatim — a value that is not a timestamp is not
 * improved by being turned into one.
 */
export function toWireTimestamp(value: string): WireTimestamp {
  const match = PARSEABLE.exec(value.trim());
  if (!match) return value;
  const [, date, time, fraction = "", zone] = match;
  const ms = `${fraction}000`.slice(0, 3);
  if (!zone || zone === "Z") return `${date}T${time}.${ms}`;
  const offset = zone.includes(":") ? zone : `${zone.slice(0, 3)}:${zone.slice(3)}`;
  const instant = new Date(`${date}T${time}.${ms}${offset}`);
  if (!Number.isFinite(instant.getTime())) return value;
  return instant.toISOString().slice(0, 23);
}

/**
 * One row, with the named fields in the wire format.
 *
 * Only the fields NAMED are touched. evidence, detail and fix are untrusted
 * text written by the observed job, and a date inside one of them is part of
 * that text. A field that is null or absent stays that way.
 */
export function withWireTimestamps<T extends object>(row: T, fields: readonly (keyof T)[]): T {
  const out = { ...row };
  for (const field of fields) {
    const value = out[field];
    if (typeof value === "string") out[field] = toWireTimestamp(value) as T[keyof T];
  }
  return out;
}
