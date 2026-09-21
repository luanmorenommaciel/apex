/**
 * The http data source.
 *
 * The claim under test is that implementing Repository is the WHOLE change —
 * so these tests exercise the interface, not the screens, and a sibling eval
 * asserts `src/screens` has no diff at all.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const config = vi.hoisted(() => ({
  database: "apex",
  user: "apex_ro",
  password: "",
  dataSource: "http" as string,
  apiUrl: "http://api.test",
  apiToken: "tok-123",
}));

vi.mock("./runtimeConfig", () => ({ runtimeConfig: config }));

import { ApiAuthError } from "./http";
import {
  ClickHouseRepository,
  FixtureRepository,
  HttpRepository,
  resolveRepository,
} from "./repository";

type Call = { url: string; init?: RequestInit };

const calls: Call[] = [];

const respond = (body: unknown, init: { status?: number; headers?: Record<string, string> } = {}) =>
  ({
    ok: (init.status ?? 200) < 400,
    status: init.status ?? 200,
    statusText: "",
    headers: new Headers(init.headers ?? {}),
    json: async () => body,
  }) as unknown as Response;

function stubFetch(handler: (url: string) => Response) {
  vi.stubGlobal("fetch", (url: string, init?: RequestInit) => {
    calls.push({ url, init });
    return Promise.resolve(handler(url));
  });
}

beforeEach(() => {
  calls.length = 0;
  config.dataSource = "http";
  config.apiUrl = "http://api.test";
  config.apiToken = "tok-123";
  vi.unstubAllGlobals();
});

describe("selection", () => {
  it("returns an HttpRepository when the data source is http", async () => {
    const repo = await resolveRepository();
    expect(repo).toBeInstanceOf(HttpRepository);
    expect(repo.kind).toBe("http");
  });

  it("leaves clickhouse and fixtures untouched", async () => {
    config.dataSource = "fixtures";
    expect(await resolveRepository()).toBeInstanceOf(FixtureRepository);
    config.dataSource = "clickhouse";
    expect(await resolveRepository()).toBeInstanceOf(ClickHouseRepository);
  });

  it("does not probe when pinned to http", async () => {
    stubFetch(() => respond([]));
    await resolveRepository();
    // Pinned means pinned: no /v1/health ping, no ClickHouse ping.
    expect(calls).toHaveLength(0);
  });
});

describe("the interface", () => {
  const ROUTES: Array<[string, (r: HttpRepository) => Promise<unknown>, string]> = [
    ["listRuns", (r) => r.listRuns(10), "http://api.test/v1/runs?limit=10"],
    ["run", (r) => r.run("j"), "http://api.test/v1/runs/j"],
    ["stages", (r) => r.stages("j"), "http://api.test/v1/runs/j/stages"],
    ["jobConf", (r) => r.jobConf("j"), "http://api.test/v1/runs/j/conf"],
    ["findings", (r) => r.findings("j"), "http://api.test/v1/runs/j/findings"],
    ["transitions", (r) => r.transitions("j"), "http://api.test/v1/runs/j/transitions"],
    [
      "baselineCandidates",
      (r) => r.baselineCandidates("j"),
      "http://api.test/v1/runs/j/baseline-candidates",
    ],
    ["planShapes", (r) => r.planShapes(), "http://api.test/v1/plans"],
    ["shapeRuns", (r) => r.shapeRuns("abc"), "http://api.test/v1/plans/abc/runs"],
    ["planSample", (r) => r.planSample("abc"), "http://api.test/v1/plans/abc/sample"],
    [
      "fixVerification",
      (r) => r.fixVerification("f1"),
      "http://api.test/v1/findings/f1/verification",
    ],
  ];

  it.each(ROUTES)("%s issues one request to its route", async (_name, call, expected) => {
    // null suits every route here: list methods coalesce it to [], and the
    // ones returning a single value are typed to report absence as null. The
    // shapes themselves are pinned by the mapping tests below.
    stubFetch(() => respond(null));
    await call(new HttpRepository());
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toBe(expected);
    // The token travels as a bearer credential, never as a query parameter.
    const headers = calls[0].init?.headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer tok-123");
    expect(calls[0].url).not.toContain("tok-123");
  });

  it("maps a run row to the console's RunSummary", async () => {
    stubFetch(() =>
      respond({
        job_id: "j", app_name: "nightly", stage_count: 34,
        started_at: "2026-09-20 10:00:00", finding_count: 3, has_critical: 1,
        task_time_ms: 91000, plan_fingerprint: "a".repeat(64), shape_count: 2,
        shaped_stage_count: 30, config_source: "observed",
        conf_executor_instances: 8, conf_shuffle_partitions: 200,
      }),
    );
    const run = await new HttpRepository().run("j");
    expect(run?.job_id).toBe("j");
    expect(run?.task_time_ms).toBe(91000);
    // age is derived here, as it is for the ClickHouse path.
    expect(run?.age).toBeTruthy();
  });

  it("reports an unknown run as null rather than an error", async () => {
    stubFetch(() => respond({ detail: "no run" }, { status: 404 }));
    expect(await new HttpRepository().run("nope")).toBeNull();
  });

  it("treats an empty plan exemplar as no exemplar", async () => {
    stubFetch(() => respond(""));
    expect(await new HttpRepository().planSample("abc")).toBeNull();
  });
});

describe("same-origin", () => {
  it("calls /v1 relative when no apiUrl is configured", async () => {
    // The ClickHouse path solved this years ago: proxy in dev and in nginx, so
    // the browser stays on one origin and the upstream needs no CORS header.
    // An absolute URL here would fail preflight in a real browser — which the
    // stubbed fetch in every other test cannot show.
    config.apiUrl = "";
    stubFetch(() => respond(null));
    await new HttpRepository().listRuns(5);
    expect(calls[0].url).toBe("/v1/runs?limit=5");
    expect(calls[0].url.startsWith("http")).toBe(false);
  });

  it("uses the absolute base when an apiUrl is configured, same-origin or not", async () => {
    config.apiUrl = "http://api.test/";
    stubFetch(() => respond(null));
    await new HttpRepository().planShapes();
    // The trailing slash is stripped rather than doubled into //v1.
    expect(calls[0].url).toBe("http://api.test/v1/plans");
  });
});

describe("failure", () => {
  it("surfaces a 401 instead of falling back to ClickHouse", async () => {
    stubFetch(() => respond({ detail: "unauthorized" }, { status: 401 }));
    const repo = new HttpRepository();
    await expect(repo.listRuns()).rejects.toBeInstanceOf(ApiAuthError);
    // Every call went to the API. A fallback would have queried the database
    // with the browser credential this data source exists to remove.
    expect(calls.every((c) => c.url.startsWith("http://api.test"))).toBe(true);
  });

  it("keeps a 401 distinguishable from the API being down", async () => {
    stubFetch(() => respond({ detail: "unauthorized" }, { status: 401 }));
    await expect(new HttpRepository().planShapes()).rejects.toMatchObject({
      name: "ApiAuthError",
      status: 401,
    });
  });

  it("reports a store error without inventing an empty result", async () => {
    stubFetch(() => respond({ detail: "memory_unavailable: ..." }, { status: 502 }));
    await expect(new HttpRepository().planShapes()).rejects.toThrow("memory_unavailable");
  });
});
