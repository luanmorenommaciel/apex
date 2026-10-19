import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as Q from "./queries";
import { ClickHouseRepository } from "./repository";

/**
 * The browser door against a findings table with and without the v0.2
 * additive confidence_score column. fetch is stubbed the way
 * httpRepository.test.ts stubs it; the SQL each call sends is its body.
 */
const sent: string[] = [];

const columns = (names: string[]) => names.map((name) => ({ name }));
const finding = { finding_id: "f-1", job_id: "j", stage_id: 3, type: "SPILL", severity: "critical",
  confidence: "HIGH", confidence_score: 0, detected_by: "w", evidence: "", impact: "", fix: "",
  hot_key: "", ts: "2026-09-20 10:00:00.000" };

const chJson = (data: unknown[], meta: { name: string; type: string }[] = []) =>
  ({ ok: true, status: 200, json: async () => ({ data, meta, rows: data.length }), text: async () => "" }) as unknown as Response;
const chError = (status: number, text: string) =>
  ({ ok: false, status, json: async () => ({}), text: async () => text }) as unknown as Response;

function stubStore(onProbe: () => Response, onFindings: () => Response) {
  vi.stubGlobal("fetch", (_url: string, init?: RequestInit) => {
    const sql = String(init?.body ?? "");
    sent.push(sql);
    return Promise.resolve(sql.includes("system.columns") ? onProbe() : onFindings());
  });
}

beforeEach(() => {
  sent.length = 0;
  vi.stubGlobal("window", { location: { origin: "http://console.test" } });
});
afterEach(() => vi.unstubAllGlobals());

describe("ClickHouseRepository.findings against an additive column", () => {
  it("sends FINDINGS when confidence_score exists, probing once per instance", async () => {
    stubStore(() => chJson(columns(["finding_id", "confidence_score"])), () => chJson([finding]));
    const repo = new ClickHouseRepository();
    await repo.findings("j");
    await repo.findings("j");
    expect(sent.filter((s) => s.includes("system.columns"))).toHaveLength(1);
    expect(sent.filter((s) => !s.includes("system.columns"))).toEqual([Q.FINDINGS, Q.FINDINGS]);
  });

  it("sends FINDINGS_WITHOUT_SCORE when the column is absent, and rows carry 0", async () => {
    stubStore(
      () => chJson(columns(["finding_id", "job_id"])),
      () => chJson([finding], [{ name: "confidence_score", type: "Float64" }]),
    );
    const rows = await new ClickHouseRepository().findings("j");
    expect(sent.at(-1)).toBe(Q.FINDINGS_WITHOUT_SCORE);
    expect(rows[0].confidence_score).toBe(0);
    expect(rows[0].finding_id).toBe("f-1");
  });

  it("sends FINDINGS when the probe fails, and reports the findings error, not the probe's", async () => {
    stubStore(() => chError(403, "PROBE denied"), () => chError(500, "Unknown identifier confidence_score"));
    await expect(new ClickHouseRepository().findings("j")).rejects.toThrow(/Unknown identifier confidence_score/);
    expect(sent.at(-1)).toBe(Q.FINDINGS);
    await expect(new ClickHouseRepository().findings("j")).rejects.not.toThrow(/PROBE/);
  });

  it("keeps the two statements' output columns identical", () => {
    const names = (sql: string) =>
      /SELECT(.*?)FROM/s.exec(sql)![1].split(",").map((c) => c.trim().split(/\s+AS\s+/).at(-1));
    expect(names(Q.FINDINGS_WITHOUT_SCORE)).toEqual(names(Q.FINDINGS));
  });
});
