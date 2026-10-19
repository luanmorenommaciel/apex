/**
 * The boot probe (P-boot-probe, 2026-10-19): http asks /v1/health once; no
 * HTTP answer at all is a named failure, never the recording; a 401 or any
 * JSON answer mounts the app. fixtures is served only by name.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const config = vi.hoisted(() => ({ dataSource: "http" as string, apiUrl: "", apiToken: "" }));
vi.mock("./runtimeConfig", () => ({ runtimeConfig: config }));

import { FixtureRepository, HttpRepository, resolveRepository, StoreUnreachableError } from "./repository";

const calls: string[] = [];
const answer = (status: number, body: unknown = {}) =>
  ({ ok: status < 400, status, json: async () => body }) as unknown as Response;

beforeEach(() => {
  config.dataSource = "http";
  config.apiUrl = "";
  calls.length = 0;
  vi.unstubAllGlobals();
});

describe("resolveRepository", () => {
  it("throws StoreUnreachableError naming /v1/health when the API gives no answer", async () => {
    vi.stubGlobal("fetch", (url: string) => { calls.push(url); return Promise.reject(new TypeError("refused")); });
    const error = await resolveRepository().then(() => { throw new Error("resolved"); }, (e: unknown) => e);
    expect(error).toBeInstanceOf(StoreUnreachableError);
    expect((error as StoreUnreachableError).probed.map((p) => p.path)).toEqual(["/v1/health"]);
    expect(calls).toEqual(["/v1/health"]);
  });

  it("treats a proxy with no upstream (502) as no API", async () => {
    vi.stubGlobal("fetch", () => Promise.resolve(answer(502)));
    await expect(resolveRepository()).rejects.toBeInstanceOf(StoreUnreachableError);
  });

  it("names the absolute API base when one is configured", async () => {
    config.apiUrl = "http://api.test/";
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("refused")));
    const error = await resolveRepository().catch((e: unknown) => e);
    expect((error as StoreUnreachableError).probed[0].path).toBe("http://api.test/v1/health");
  });

  it("mounts on the liveness body and on a 401", async () => {
    vi.stubGlobal("fetch", () => Promise.resolve(answer(200, { status: "ok" })));
    expect(await resolveRepository()).toBeInstanceOf(HttpRepository);
    vi.stubGlobal("fetch", () => Promise.resolve(answer(401)));
    expect(await resolveRepository()).toBeInstanceOf(HttpRepository);
  });

  it("does not mistake an SPA fallback page for the API", async () => {
    vi.stubGlobal("fetch", () => Promise.resolve(answer(200, null)));
    await expect(resolveRepository()).rejects.toBeInstanceOf(StoreUnreachableError);
  });

  it("serves the recording only when DATA_SOURCE says fixtures, and probes nothing", async () => {
    config.dataSource = "fixtures";
    vi.stubGlobal("fetch", (url: string) => { calls.push(url); return Promise.reject(new TypeError("refused")); });
    expect(await resolveRepository()).toBeInstanceOf(FixtureRepository);
    expect(calls).toEqual([]);
  });
});
