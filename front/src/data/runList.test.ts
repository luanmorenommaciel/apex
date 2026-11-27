/**
 * P7.5 — the run list through the recording.
 *
 * The HTTP door's URL is covered in httpRepository.test.ts. The statement the
 * API runs (window, order, bound filters, the 64-char fingerprint guard) is
 * serve's RUN_LIST_SQL, covered by serve/tests/test_run_list_alignment.py;
 * since #182 the browser holds no SQL of its own.
 */
import { describe, expect, it } from "vitest";
import * as fx from "./fixtures";
import { FixtureRepository, RUN_LIST_DEFAULTS } from "./repository";

describe("RUN_LIST_DEFAULTS", () => {
  it("are serve's DEFAULT_RUNS_LIMIT / DEFAULT_SINCE_HOURS and offset 0", () => {
    expect(RUN_LIST_DEFAULTS).toEqual({ limit: 50, sinceHours: 168, offset: 0 });
  });
});

describe("FixtureRepository.listRuns applies the filters in memory", () => {
  const repo = new FixtureRepository();
  const ids = (rows: { job_id: string }[]) => rows.map((r) => r.job_id);

  it("lists the recording, in recorded order, when unfiltered", async () => {
    expect(ids(await repo.listRuns(50))).toEqual(ids(fx.runs).slice(0, 50));
  });

  it("filters on job_id prefix", async () => {
    const prefix = fx.runs[0].job_id.slice(0, 13);
    const rows = await repo.listRuns(50, { jobIdPrefix: prefix });
    expect(rows.length).toBeGreaterThan(0);
    expect(rows.every((r) => r.job_id.startsWith(prefix))).toBe(true);
    expect(ids(rows)).toEqual(ids(fx.runs.filter((r) => r.job_id.startsWith(prefix))));
  });

  it("filters on plan fingerprint, exactly", async () => {
    const rows = await repo.listRuns(50, { planFingerprint: fx.PLAN_FINGERPRINT });
    expect(rows.length).toBeGreaterThan(0);
    expect(rows.every((r) => r.plan_fingerprint === fx.PLAN_FINGERPRINT)).toBe(true);
    expect(await repo.listRuns(50, { planFingerprint: fx.PLAN_FINGERPRINT.slice(0, 10) })).toEqual([]);
  });

  it("matches a run on ANY shape its stages ran, like run_outcomes on the server", async () => {
    const rows = await repo.listRuns(50, { planFingerprint: fx.PLAN_FINGERPRINT });
    const expected = fx.runs.filter((r) =>
      r.plan_fingerprint === fx.PLAN_FINGERPRINT ||
      (fx.stagesByJob[r.job_id] ?? []).some((st) => st.plan_fingerprint === fx.PLAN_FINGERPRINT));
    expect(ids(rows)).toEqual(ids(expected));
    // The recording's "n/a" means no shape; it is not a fingerprint to match.
    expect(await repo.listRuns(50, { planFingerprint: "n/a" })).toEqual([]);
  });

  it("filters on has_findings, both ways", async () => {
    const withF = await repo.listRuns(50, { hasFindings: true });
    const without = await repo.listRuns(50, { hasFindings: false });
    expect(withF.every((r) => r.finding_count > 0)).toBe(true);
    expect(without.every((r) => r.finding_count === 0)).toBe(true);
    expect(withF.length + without.length).toBe(Math.min(50, fx.runs.length));
  });

  it("pages with offset and limit", async () => {
    const all = ids(await repo.listRuns(50));
    expect(ids(await repo.listRuns(2, { offset: 1 }))).toEqual(all.slice(1, 3));
    expect(await repo.listRuns(2, { offset: 10_000 })).toEqual([]);
  });
});
