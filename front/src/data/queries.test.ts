import { describe, expect, it } from "vitest";
import { PLAN_TRANSITIONS, RUN_LIST, RUN_ONE } from "./queries";

describe("PLAN_TRANSITIONS", () => {
  it("does not shadow the source fingerprint inside the ClickHouse CTE", () => {
    expect(PLAN_TRANSITIONS).toContain(
      "any(toString(plan_fingerprint)) AS fingerprint",
    );
    expect(PLAN_TRANSITIONS).toContain(
      "ifNull(any(fp.fingerprint), '')      AS plan_fingerprint",
    );
    expect(PLAN_TRANSITIONS).not.toMatch(
      /any\(toString\(plan_fingerprint\)\)\s+AS plan_fingerprint/,
    );
  });
});

describe("run rollup on an unindexed run", () => {
  // A missed LEFT JOIN is filled with each column's DEFAULT, never NULL, so
  // ifNull(s.task_time_ms, -1) never fired and an unindexed run rendered a
  // measured zero. The shapes CTE now emits a sentinel the miss cannot.
  it.each([
    ["RUN_ONE", RUN_ONE],
    ["RUN_LIST", RUN_LIST],
  ])("%s reads the join sentinel, not the defaulted value", (_name, sql) => {
    expect(sql).toMatch(/\b1\s+AS indexed\b/);
    expect(sql).toContain("if(s.indexed = 1, toInt64(s.task_time_ms), -1)");
    expect(sql).toContain("if(s.indexed = 1, toInt64(s.shaped_stage_count), -1)");
    expect(sql).toContain("if(s.indexed = 1, toString(s.config_source), 'unknown')");
    expect(sql).toContain("if(s.indexed = 1, s.plan_fingerprint, '')");
    expect(sql).not.toMatch(/ifNull\(s\./);
  });

  it("carries no SETTINGS clause, because apex_ro is readonly = 1", () => {
    for (const sql of [RUN_ONE, RUN_LIST]) {
      expect(sql.replace(/--[^\n]*/g, "").toUpperCase()).not.toContain("SETTINGS");
    }
  });
});
