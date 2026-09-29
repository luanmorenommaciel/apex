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

// Both stores' probes, so `auto` can be exercised without a network. The real
// ClickHouse ping is replaced; the API probe (apiPing) is NOT — it is the unit
// under test and runs against the stubbed fetch.
const chPing = vi.hoisted(() => vi.fn<() => Promise<boolean>>());
vi.mock("./clickhouse", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./clickhouse")>()),
  ping: chPing,
}));

import { ApiAuthError } from "./http";
import * as fx from "./fixtures";
import { WIRE_TIMESTAMP } from "./timestamp";
import type { Repository } from "./repository";
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
  chPing.mockReset();
  chPing.mockResolvedValue(false);
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

describe("auto", () => {
  beforeEach(() => {
    config.dataSource = "auto";
  });

  const health = (body: unknown = { status: "ok", store: "ok" }) =>
    respond(body);

  it("probes the same-origin /v1/health when apiUrl is empty and selects the API", async () => {
    // The supported same-origin deployment: VITE_APEX_API_PROXY_TARGET reaches
    // the dev server and APEX_API_UPSTREAM reaches nginx, never the bundle, so
    // apiUrl is deliberately empty. Skipping the probe there made `auto` fall
    // back to ClickHouse in the one setup this data source was built for.
    config.apiUrl = "";
    stubFetch(() => health());
    const repo = await resolveRepository();
    expect(repo).toBeInstanceOf(HttpRepository);
    expect(calls.map((c) => c.url)).toEqual(["/v1/health"]);
    expect(chPing).not.toHaveBeenCalled();
  });

  it("probes an absolute apiUrl when one is configured", async () => {
    stubFetch(() => health());
    expect(await resolveRepository()).toBeInstanceOf(HttpRepository);
    expect(calls.map((c) => c.url)).toEqual(["http://api.test/v1/health"]);
  });

  it("falls back to ClickHouse when no API answers", async () => {
    config.apiUrl = "";
    // A proxy whose upstream is absent answers 502.
    stubFetch(() => respond({}, { status: 502 }));
    chPing.mockResolvedValue(true);
    expect(await resolveRepository()).toBeInstanceOf(ClickHouseRepository);
  });

  it("falls back to fixtures when neither store answers", async () => {
    config.apiUrl = "";
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("refused")));
    expect(await resolveRepository()).toBeInstanceOf(FixtureRepository);
  });

  it("does not mistake an SPA fallback page for the API", async () => {
    // A static host answers /v1/health with index.html and a 200. The probe
    // must see that the body is not the API's liveness document.
    config.apiUrl = "";
    vi.stubGlobal("fetch", () =>
      Promise.resolve({
        ok: true,
        status: 200,
        statusText: "",
        headers: new Headers(),
        json: async () => {
          throw new SyntaxError("Unexpected token '<'");
        },
      } as unknown as Response),
    );
    chPing.mockResolvedValue(true);
    expect(await resolveRepository()).toBeInstanceOf(ClickHouseRepository);
  });

  it("never falls back on a 401: a gated API is still the API", async () => {
    config.apiUrl = "";
    stubFetch(() => respond({ detail: "unauthorized" }, { status: 401 }));
    // ClickHouse is reachable, and must still not be chosen: that would quietly
    // restore the browser-side database credential the API exists to remove.
    chPing.mockResolvedValue(true);
    const repo = await resolveRepository();
    expect(repo).toBeInstanceOf(HttpRepository);
    expect(chPing).not.toHaveBeenCalled();
    // And the refusal then surfaces from the API's own calls.
    await expect(repo.listRuns()).rejects.toBeInstanceOf(ApiAuthError);
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

describe("proxy target", () => {
  it("leaves apiUrl empty under the documented dev setup, so requests stay same-origin", async () => {
    // VITE_APEX_API_PROXY_TARGET configures the dev server, not the bundle.
    // When the two shared one variable, the documented command made the
    // browser call an absolute url and bypass the proxy — and the API sends
    // no CORS header, so a real browser blocked every request.
    config.apiUrl = "";
    stubFetch(() => respond(null));
    await new HttpRepository().stages("j");
    expect(calls[0].url).toBe("/v1/runs/j/stages");
    expect(calls[0].url.startsWith("http")).toBe(false);
  });

  it("still honours an explicit absolute apiUrl for a deliberate cross-origin call", async () => {
    config.apiUrl = "http://api.test";
    stubFetch(() => respond(null));
    await new HttpRepository().stages("j");
    expect(calls[0].url).toBe("http://api.test/v1/runs/j/stages");
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

describe("wire timestamp", () => {
  // One row carrying every timestamp field the console reads, in a form that is
  // NOT the wire format. Each repository is handed it through its own door.
  const row = (raw: string) => ({
    job_id: "j", app_name: "nightly", stage_count: 1, finding_count: 0, has_critical: 0,
    task_time_ms: 1, plan_fingerprint: "a".repeat(64), shape_count: 1, shaped_stage_count: 1,
    config_source: "observed", conf_executor_instances: null, conf_shuffle_partitions: null,
    started_at: raw, ts: raw, observed_at: raw, first_run: raw, last_run: raw,
  });
  /**
   * Every timestamp a repository returns, read from the fields each METHOD
   * owns — a stage row's `ts`, a shape's `first_run` and `last_run`. The test
   * row above carries all five on every row only so one fixture serves every
   * route; a field a method does not declare is not that method's to convert.
   */
  async function everyTimestamp(repo: Repository, job: string, fingerprint: string): Promise<string[]> {
    const owned: Array<[unknown[], readonly string[]]> = [
      [await repo.listRuns(5), ["started_at"]],
      [[await repo.run(job)], ["started_at"]],
      [await repo.stages(job), ["ts"]],
      [await repo.jobConf(job), ["ts"]],
      [await repo.findings(job), ["ts"]],
      [await repo.transitions(job), ["ts"]],
      [await repo.baselineCandidates(job), ["observed_at"]],
      [await repo.planShapes(), ["first_run", "last_run"]],
      [await repo.shapeRuns(fingerprint), ["observed_at"]],
    ];
    return owned.flatMap(([rows, fields]) =>
      rows.flatMap((r) =>
        fields.flatMap((field) => {
          const value = (r as Record<string, unknown> | null)?.[field];
          return typeof value === "string" ? [value] : [];
        }),
      ),
    );
  }

  it.each([
    ["the API before it was pinned", "2026-09-20T10:00:00.123000"],
    ["an API that dropped a zero fraction", "2026-09-20T10:00:00"],
    ["an aware value", "2026-09-20T12:00:00.123+02:00"],
  ])("HttpRepository returns the wire format from %s", async (_what, raw) => {
    stubFetch((url) => respond(/\/v1\/runs\/j$/.test(url) ? row(raw) : [row(raw)]));
    const times = await everyTimestamp(new HttpRepository(), "j", "a".repeat(64));
    // Ten: one per method, and a shape has two.
    expect(times).toHaveLength(10);
    for (const value of times) expect(value).toMatch(WIRE_TIMESTAMP);
  });

  it("ClickHouseRepository returns the wire format from ClickHouse's own JSON", async () => {
    // The browser path builds its url from window.location, which node has not.
    vi.stubGlobal("window", { location: { origin: "http://console.test" } });
    stubFetch(() => respond({ data: [row("2026-09-20 10:00:00.123")], meta: [], rows: 1 }));
    const times = await everyTimestamp(new ClickHouseRepository(), "j", "a".repeat(64));
    expect(times).toHaveLength(10);
    for (const value of times) expect(value).toBe("2026-09-20T10:00:00.123");
    expect(calls.every((c) => c.url.startsWith("http://console.test/clickhouse/"))).toBe(true);
  });

  it("FixtureRepository returns the wire format from the recording", async () => {
    const times = await everyTimestamp(new FixtureRepository(), fx.CURRENT_JOB, fx.PLAN_FINGERPRINT);
    expect(times.length).toBeGreaterThan(9);
    for (const value of times) expect(value).toMatch(WIRE_TIMESTAMP);
    // The recording itself is untouched: it becomes a row in the repository.
    expect(fx.runs[0].started_at).not.toMatch(WIRE_TIMESTAMP);
  });

  it("derives the same age whichever form the timestamp arrived in", async () => {
    const ages: Array<string | undefined> = [];
    for (const raw of ["2026-09-20 10:00:00.123", "2026-09-20T10:00:00.123"]) {
      stubFetch(() => respond(row(raw)));
      ages.push((await new HttpRepository().run("j"))?.age);
    }
    expect(ages[0]).toBeTruthy();
    expect(ages[0]).toBe(ages[1]);
  });
});
