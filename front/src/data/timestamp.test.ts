import { describe, expect, it } from "vitest";
import { toWireTimestamp, WIRE_TIMESTAMP, withWireTimestamps } from "./timestamp";

const SAME_INSTANT = "2026-09-20T10:00:00.123";

describe("toWireTimestamp", () => {
  it.each([
    ["ClickHouse's own JSON, the browser's path", "2026-09-20 10:00:00.123"],
    ["isoformat() with microseconds, the API before it was pinned", "2026-09-20T10:00:00.123000"],
    ["a Z suffix", "2026-09-20T10:00:00.123Z"],
    ["a +02:00 offset", "2026-09-20T12:00:00.123+02:00"],
    ["a +0200 offset", "2026-09-20T12:00:00.123+0200"],
    ["a -04:30 offset", "2026-09-20T05:30:00.123-04:30"],
    ["a value already on the wire", SAME_INSTANT],
  ])("reads %s as the same instant", (_what, arrived) => {
    expect(toWireTimestamp(arrived)).toBe(SAME_INSTANT);
    expect(toWireTimestamp(arrived)).toMatch(WIRE_TIMESTAMP);
  });

  it("writes the milliseconds even when they are zero, so the width is fixed", () => {
    expect(toWireTimestamp("2026-09-20 10:00:00")).toBe("2026-09-20T10:00:00.000");
    expect(toWireTimestamp("2026-09-20T10:00:00")).toBe("2026-09-20T10:00:00.000");
  });

  it("truncates below the millisecond, never rounds into the next one", () => {
    expect(toWireTimestamp("2026-09-20 10:00:00.123999")).toBe(SAME_INSTANT);
  });

  it.each(["", "yesterday", "2026-09-20", "10:00:00"])(
    "carries %j verbatim: not a timestamp, so not turned into one",
    (value) => {
      expect(toWireTimestamp(value)).toBe(value);
    },
  );
});

describe("withWireTimestamps", () => {
  it("touches only the fields it is given", () => {
    const row = {
      ts: "2026-09-20 10:00:00.123",
      // Untrusted text written by the observed job. A date inside it is text.
      evidence: "2026-09-20 10:00:00.123",
      stage_id: 4,
    };
    expect(withWireTimestamps(row, ["ts"])).toEqual({
      ts: SAME_INSTANT,
      evidence: "2026-09-20 10:00:00.123",
      stage_id: 4,
    });
    // The row it was given is not the row it returns.
    expect(row.ts).toBe("2026-09-20 10:00:00.123");
  });

  it("leaves a null or absent field as it found it", () => {
    const row = { ts: null as string | null, key: "k" };
    expect(withWireTimestamps(row, ["ts"])).toEqual({ ts: null, key: "k" });
  });
});
