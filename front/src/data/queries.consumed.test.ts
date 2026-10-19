import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import * as Q from "./queries";

/**
 * Every statement queries.ts exports is one ClickHouseRepository sends.
 *
 * Text-level, like serve's own tests of this file: the exports are read from
 * the module and the consumers from repository.ts's source, so a statement
 * that is exported, documented and never executed fails here instead of
 * shipping untested — PLAN_MEMORY did exactly that.
 */
const REPOSITORY_TS = fileURLToPath(new URL("./repository.ts", import.meta.url));

describe("queries.ts", () => {
  it("exports nothing repository.ts does not send", () => {
    const repository = readFileSync(REPOSITORY_TS, "utf8");
    const exported = Object.keys(Q).filter((name) => typeof Q[name as keyof typeof Q] === "string");
    expect(exported.length).toBeGreaterThan(0);
    const unconsumed = exported.filter((name) => !new RegExp(`\\bQ\\.${name}\\b`).test(repository));
    expect(unconsumed).toEqual([]);
  });
});
