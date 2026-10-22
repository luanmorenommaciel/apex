import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { compareCodePoints, overlayEntries, parseProposal } from "./rules";

/**
 * SRP-22 / P7.10 — the console and the MCP read the SAME overlay out of the
 * same stored text. contract/fixtures/proposal_parity.json is shared with
 * serve/tests/test_proposal_parity.py, which drives the MCP door's real parser
 * (VerificationView / read_overlay) over the same cases.
 */
interface ParityCase {
  name: string;
  input: string;
  expected: { kind: "overlay" | "empty-overlay" | "none"; entries: [string, string][] };
}

const fixture = JSON.parse(
  readFileSync(new URL("../../../contract/fixtures/proposal_parity.json", import.meta.url), "utf8"),
) as { cases: ParityCase[] };

function consoleReading(text: string): ParityCase["expected"] {
  const p = parseProposal(text);
  if (p.kind === "overlay") return { kind: "overlay", entries: overlayEntries(p.config) };
  if (p.kind === "empty-overlay") return { kind: "empty-overlay", entries: [] };
  // invalid-json / invalid-overlay / unknown (and diff, which no case is):
  // no usable overlay.
  return { kind: "none", entries: [] };
}

describe("proposal parity fixture (shared with the MCP door)", () => {
  it("covers every rule and every outcome", () => {
    expect(fixture.cases.length).toBeGreaterThan(50);
    const kinds = new Set(fixture.cases.map((c) => c.expected.kind));
    expect([...kinds].sort()).toEqual(["empty-overlay", "none", "overlay"]);
  });

  it.each(fixture.cases.map((c) => [c.name, c] as const))("%s", (_name, c) => {
    expect(consoleReading(c.input)).toEqual(c.expected);
  });

  it("reads an overlay nested ~1500 deep as unusable, without throwing", () => {
    const nested = `{"spark.a":${"[".repeat(1500)}${"]".repeat(1500)}}`;
    expect(consoleReading(nested)).toEqual({ kind: "none", entries: [] });
  });
});

describe("overlayEntries / compareCodePoints", () => {
  it("does not put integer-like keys first the way Object.entries does", () => {
    const config = parseProposal('{"spark.a":"x","10":"a","9":"b"}');
    expect(config.kind).toBe("overlay");
    if (config.kind !== "overlay") return;
    expect(Object.keys(config.config)).toEqual(["9", "10", "spark.a"]); // the trap
    expect(overlayEntries(config.config).map(([k]) => k)).toEqual(["10", "9", "spark.a"]);
  });

  it("orders astral after high-BMP keys (code point, not UTF-16 unit)", () => {
    expect(["\u{1F600}", "￿"].sort()).toEqual(["\u{1F600}", "￿"]); // the trap
    expect(["\u{1F600}", "￿"].sort(compareCodePoints)).toEqual(["￿", "\u{1F600}"]);
    expect(compareCodePoints("a", "ab")).toBeLessThan(0);
    expect(compareCodePoints("ab", "a")).toBeGreaterThan(0);
    expect(compareCodePoints("ab", "ab")).toBe(0);
  });

  it("an empty object is empty-overlay, never an overlay with zero keys", () => {
    expect(parseProposal("{}")).toEqual({ kind: "empty-overlay" });
    expect(parseProposal("  { }﻿")).toEqual({ kind: "empty-overlay" });
  });
});
