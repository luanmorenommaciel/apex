// @vitest-environment jsdom
/**
 * The console against a LIVE Apex API, on a job that really ran.
 *
 * Every other test in this tree stubs a door — fetch, the repository, the
 * store. This one mounts the real App, resolves the real HttpRepository
 * against a running apex-api, and reads what a person would read on each
 * screen for one job_id that went Spark → plugin → OTLP → ClickHouse →
 * engine → memory → API. It is the last link of tests/e2e/console_reflection.sh.
 *
 * It is skipped — reported as skipped, never as passed — unless the three
 * variables below name a running API and a job:
 *
 *   APEX_E2E_API_URL=http://127.0.0.1:8099 APEX_E2E_API_TOKEN=… APEX_E2E_JOB_ID=…
 *
 * What it refuses to find on any screen: a number that is not a number, a
 * field that never arrived, an object rendered as text, the console's own
 * failure notices. What it requires: the counts a screen shows are the counts
 * the API returned for that job.
 */
import { appendFileSync } from "node:fs";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const API_URL = (process.env.APEX_E2E_API_URL ?? "").replace(/\/+$/, "");
const API_TOKEN = process.env.APEX_E2E_API_TOKEN ?? "";
const JOB_ID = process.env.APEX_E2E_JOB_ID ?? "";
const LIVE = Boolean(API_URL && API_TOKEN && JOB_ID);

// The bundle's runtime configuration, pointed at the live API. Absolute, so
// node's fetch reaches it without a proxy; the browser would go same-origin.
vi.mock("@/data/runtimeConfig", () => ({
  runtimeConfig: {
    database: "apex",
    user: "apex_ro",
    password: "",
    dataSource: "http",
    apiUrl: (process.env.APEX_E2E_API_URL ?? "").replace(/\/+$/, ""),
    apiToken: process.env.APEX_E2E_API_TOKEN ?? "",
  },
}));

import App from "@/App";
import { RepositoryProvider } from "@/data/useRepository";

/** Text that must never reach a screen. Each is a defect this suite has met. */
const FORBIDDEN = [
  "NaN",                 // a ratio over a field the API did not send
  "undefined",           // a field the screen reads and the row lacks
  "[object Object]",     // a non-text detail rendered as text
  "Infinity",            // a division by a zero that should have been null
  "APEX_API_TOKEN",      // QueryFailure: the token was rejected
  "query failed",        // QueryFailure: a read was rejected
  "could not be reached",
  "NO RUN ROW",          // RunDetail: the run row is missing while stages exist
];

async function api<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { Authorization: `Bearer ${API_TOKEN}`, Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return (await response.json()) as T;
}

let host: HTMLDivElement;
let root: Root;

/** Mount the real App at `path` and wait until it stops changing. */
async function screen(path: string, settled: (text: string) => boolean = () => true): Promise<string> {
  await act(async () => {
    root.render(
      <RepositoryProvider>
        <MemoryRouter initialEntries={[path]}>
          <App />
        </MemoryRouter>
      </RepositoryProvider>,
    );
  });
  const deadline = Date.now() + 20_000;
  let last = "";
  let quiet = 0;
  while (Date.now() < deadline) {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 150));
    });
    const text = host.textContent ?? "";
    quiet = text === last ? quiet + 1 : 0;
    last = text;
    // Settled: the same text three polls in a row, and the caller's condition.
    if (quiet >= 3 && settled(text)) return dump(path, text);
  }
  return dump(path, last);
}

/** With APEX_E2E_DUMP=<file>, append what each screen shows to that file —
 *  the invariants above catch what must never appear; a person still has to
 *  read what does. A file, not the console: vitest owns stdout. */
function dump(path: string, text: string): string {
  const file = process.env.APEX_E2E_DUMP;
  if (file) {
    appendFileSync(file, `\n──── ${path} ────\n${text.replace(/\s+/g, " ").slice(0, 1600)}\n`);
  }
  return text;
}

function clean(text: string, where: string): void {
  for (const token of FORBIDDEN) {
    expect(text, `${where} shows "${token}"`).not.toContain(token);
  }
}

beforeEach(() => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  host = document.createElement("div");
  document.body.append(host);
  root = createRoot(host);
});
afterEach(async () => {
  await act(async () => root.unmount());
  host.remove();
});

describe.skipIf(!LIVE)("the console reflects a job that really ran", () => {
  const T = 60_000;

  it("the header names the API, not the recording", async () => {
    const text = await screen("/runs");
    expect(text).toContain("apex-api");
    expect(text).not.toContain("fixtures");
  }, T);

  it("/runs lists the job, with the run row the API returned", async () => {
    const run = await api<{ job_id: string; stage_count: number; finding_count: number }>(
      `/v1/runs/${encodeURIComponent(JOB_ID)}`,
    );
    const text = await screen("/runs", (t) => !t.includes("querying"));
    clean(text, "/runs");
    // The list shows the id in some form; the last eight characters survive any shortening.
    expect(text).toContain(JOB_ID.slice(-8));
    expect(text).toContain(`${run.stage_count}`);
  }, T);

  it("/runs/:job shows the API's stage and finding counts, and no missing-field rendering", async () => {
    const [stages, findings, transitions] = await Promise.all([
      api<unknown[]>(`/v1/runs/${encodeURIComponent(JOB_ID)}/stages`),
      api<unknown[]>(`/v1/runs/${encodeURIComponent(JOB_ID)}/findings`),
      api<unknown[]>(`/v1/runs/${encodeURIComponent(JOB_ID)}/transitions`),
    ]);
    expect(stages.length, "the job landed no stages").toBeGreaterThan(0);
    const text = await screen(`/runs/${JOB_ID}`, (t) => !t.includes("Loading run"));
    clean(text, `/runs/${JOB_ID}`);
    expect(text).toContain(`${stages.length} stages`);
    expect(text).toContain(`${findings.length} findings`);
    // The transitions the screen counts are the API's collapsed rows, one per execution.
    if (transitions.length > 0) expect(text).toContain(`${transitions.length}`);
  }, T);

  it("/runs/:job/findings/:finding opens the top finding the API ranks first", async () => {
    const findings = await api<Array<{ finding_id: string; type: string; confidence_score: number }>>(
      `/v1/runs/${encodeURIComponent(JOB_ID)}/findings`,
    );
    if (findings.length === 0) return; // an honest clean run has nothing to open
    const [top, ...rest] = findings;
    // The API's order is the console's contract: highest confidence first.
    for (const f of rest) expect(f.confidence_score).toBeLessThanOrEqual(top.confidence_score);
    const text = await screen(`/runs/${JOB_ID}/findings/${top.finding_id}`, (t) => !t.includes("Loading finding"));
    clean(text, "/runs/:job/findings/:finding");
    expect(text).toContain(top.type);
    expect(text).not.toContain("No finding");
  }, T);

  it("/compare aligns the job against whatever baseline the memory lane knows", async () => {
    const text = await screen(`/compare?current=${encodeURIComponent(JOB_ID)}`);
    clean(text, "/compare");
    expect(text).toContain(JOB_ID.slice(-8));
  }, T);

  it("/memory shows the shape when the memory lane indexed it, and says so when it did not", async () => {
    const shapes = await api<Array<{ plan_fingerprint: string; run_count: number }>>("/v1/plans");
    const text = await screen("/memory", (t) => !t.includes("Loading plan memory"));
    clean(text, "/memory");
    if (shapes.length === 0) {
      expect(text).toContain("nothing indexed yet");
    } else {
      expect(text).toContain(shapes[0].plan_fingerprint.slice(0, 12));
      expect(text).toContain(`${shapes[0].run_count} runs`);
    }
  }, T);

  it("/verify reports the verification row or its honest absence", async () => {
    const text = await screen(`/verify?job=${encodeURIComponent(JOB_ID)}`, (t) => !t.includes("Loading"));
    clean(text, "/verify");
    // One of the two truthful states; never a verdict nobody reached.
    expect(
      text.includes("No verification for this finding") ||
        text.includes("requires human approval") ||
        text.includes("Runtime") ||
        text.includes("no finding"),
    ).toBe(true);
  }, T);

  it("the run row carries the indexed cost, not the sentinel, once memory indexed it", async () => {
    const run = await api<{ task_time_ms: number; config_source: string; shape_count: number }>(
      `/v1/runs/${encodeURIComponent(JOB_ID)}`,
    );
    const shapes = await api<unknown[]>("/v1/plans");
    if (shapes.length === 0) {
      // Not indexed: the sentinel, never a measured zero.
      expect(run.task_time_ms).toBe(-1);
      expect(run.config_source).toBe("unknown");
    } else {
      expect(run.task_time_ms).toBeGreaterThan(0);
      expect(run.shape_count).toBeGreaterThan(0);
    }
  }, T);
});
