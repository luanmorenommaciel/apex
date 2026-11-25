import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { CONTRACT_VERSION } from "./types";

/**
 * The badge in the header renders CONTRACT_VERSION. CONTRACT.md is the one
 * place the contract's version is declared, so it is READ here rather than
 * restated: the console said v0.5 for a whole minor version because nothing
 * compared the two.
 */
const CONTRACT_MD = fileURLToPath(new URL("../../../CONTRACT.md", import.meta.url));

describe("CONTRACT_VERSION", () => {
  it("is the version CONTRACT.md declares in its status line", () => {
    const status = readFileSync(CONTRACT_MD, "utf8")
      .split("\n")
      .find((line) => line.startsWith("**Status:** contract **v"));
    expect(status, "CONTRACT.md status line").toBeDefined();
    const declared = /contract \*\*v(\d+\.\d+)\*\*/.exec(status!)?.[1];
    expect(declared).toBe(CONTRACT_VERSION);
  });
});
