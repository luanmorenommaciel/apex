// @vitest-environment jsdom
/**
 * P7.5 — the run list through the browser's ClickHouse door and the recording.
 *
 * The HTTP door's URL is covered in httpRepository.test.ts; serve's
 * test_run_list_alignment.py proves RUN_LIST is serve's RUN_LIST_SQL.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { execFileSync } from "node:child_process";

vi.mock("./runtimeConfig", () => ({
  runtimeConfig: {
    database: "apex", user: "apex_ro", password: "", dataSource: "clickhouse",
    apiUrl: "", apiToken: "",
  },
}));

import * as fx from "./fixtures";
import { RUN_LIST } from "./queries";
import { ClickHouseRepository, FixtureRepository, RUN_LIST_DEFAULTS } from "./repository";

type Sent = { url: URL; body: string };
const sent: Sent[] = [];

beforeEach(() => {
  sent.length = 0;
  vi.stubGlobal("fetch", (url: string, init?: RequestInit) => {
    sent.push({ url: new URL(url), body: String(init?.body ?? "") });
    return Promise.resolve({
      ok: true, status: 200,
      json: async () => ({ meta: [], data: [] }),
      text: async () => "",
    } as unknown as Response);
  });
});

const params = (s: Sent) =>
  Object.fromEntries([...s.url.searchParams].filter(([k]) => k.startsWith("param_")));

/**
 * Execute the actual sent shape predicate in stdlib SQLite, without a service.
 * Only parameter syntax, FINAL and FixedString padding need dialect adapters;
 * SQL boolean/subquery evaluation is SQLite's. Hex fixtures are ASCII so byte
 * and character lengths agree. This is not a live ClickHouse parser check.
 */
function offlineShapeRows(statement: Sent): { rows: string[]; unguarded: string[] } {
  return JSON.parse(execFileSync("python3", ["-c", `
import json, re, sqlite3, sys
request = json.load(sys.stdin)
match = re.search(r" AND \\(\\{plan_fingerprint:String\\} = ''.*?\\)\\)\\)", request["sql"], re.S)
assert match, "actual sent SQL must contain the shape predicate"
predicate = match[0].replace("{plan_fingerprint:String}", ":fingerprint").replace(" AS o FINAL", " AS o")
with sqlite3.connect(":memory:") as db:
    db.create_function("toFixedString", 2, lambda value, size: value.encode().ljust(size, b"\\0"))
    db.execute("CREATE TABLE candidates (job_id TEXT)")
    db.execute("CREATE TABLE run_outcomes (job_id TEXT, plan_fingerprint BLOB)")
    db.execute("INSERT INTO candidates VALUES ('matching-prefix')")
    db.execute("INSERT INTO run_outcomes VALUES (?, ?)", ("matching-prefix", b"c" * 64))
    def evaluate(clause):
        return [r[0] for r in db.execute("SELECT job_id FROM candidates WHERE 1" + clause,
                                       {"fingerprint": request["fingerprint"]})]
    print(json.dumps({"rows": evaluate(predicate),
                      "unguarded": evaluate(predicate.replace("length(:fingerprint) <= 64 AND ", ""))}))
`], {
    encoding: "utf8",
    input: JSON.stringify({ sql: statement.body, fingerprint: params(statement).param_plan_fingerprint }),
  }));
}

describe("ClickHouseRepository.listRuns", () => {
  it("binds every placeholder RUN_LIST names, at the shared defaults", async () => {
    await new ClickHouseRepository().listRuns(50);
    expect(sent[0].body).toBe(RUN_LIST);
    expect(params(sent[0])).toEqual({
      param_limit: "50",
      param_since_hours: "168",
      param_offset: "0",
      param_app_name: "",
      param_job_id_prefix: "",
      param_plan_fingerprint: "",
      param_has_findings: "-1",
    });
    for (const name of RUN_LIST.match(/\{(\w+):/g) ?? []) {
      expect(params(sent[0])).toHaveProperty(`param_${name.slice(1, -1)}`);
    }
  });

  it("binds a hostile filter as a parameter; the statement does not change", async () => {
    const hostile = "' OR 1=1 --";
    await new ClickHouseRepository().listRuns(10, {
      jobIdPrefix: hostile, planFingerprint: hostile, appName: hostile,
      hasFindings: false, offset: 30, sinceHours: 2,
    });
    expect(sent[0].body).toBe(RUN_LIST);
    expect(sent[0].body).not.toContain(hostile);
    expect(params(sent[0])).toMatchObject({
      param_job_id_prefix: hostile, param_plan_fingerprint: hostile, param_app_name: hostile,
      param_has_findings: "0", param_offset: "30", param_since_hours: "2", param_limit: "10",
    });
  });

  it.each([
    { fingerprint: "", expected: ["matching-prefix"] },
    { fingerprint: "c".repeat(64), expected: ["matching-prefix"] },
    { fingerprint: "d".repeat(64), expected: [] },
    { fingerprint: "c".repeat(63), expected: [] },
    { fingerprint: "c".repeat(64) + "d", expected: [] },
    { fingerprint: "c".repeat(64) + "d".repeat(64), expected: [] },
  ])("executes the sent SQL shape predicate for $fingerprint", async ({ fingerprint, expected }) => {
    await new ClickHouseRepository().listRuns(50, { planFingerprint: fingerprint });
    expect(sent).toHaveLength(1);
    expect(sent[0].body).toBe(RUN_LIST);
    expect(params(sent[0]).param_plan_fingerprint).toBe(fingerprint);
    const actual = offlineShapeRows(sent[0]);
    expect(actual.rows).toEqual(expected);
    if (fingerprint.length > 64) {
      // Negative control: the same valid prefix matches under the old predicate.
      expect(actual.unguarded).toEqual(["matching-prefix"]);
    }
  });
});

describe("RUN_LIST", () => {
  it("windows on ts in the membership and orders with a job_id tie-break", () => {
    expect(RUN_LIST).toContain("w.ts >= now() - toIntervalHour({since_hours:UInt32})");
    expect(RUN_LIST).toContain("ORDER BY b.started_at DESC, b.job_id ASC LIMIT {limit:UInt32} OFFSET {offset:UInt32}");
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
