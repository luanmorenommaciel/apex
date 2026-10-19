/**
 * DATA_SOURCE=auto with no store answering: a named failure, never the
 * recording. The recording is served only when asked for by name.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const config = vi.hoisted(() => ({
  database: "apex", user: "apex_ro", password: "", dataSource: "auto" as string,
  apiUrl: "", apiToken: "",
}));
vi.mock("./runtimeConfig", () => ({ runtimeConfig: config }));

const chPing = vi.hoisted(() => vi.fn<() => Promise<boolean>>());
vi.mock("./clickhouse", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./clickhouse")>()),
  ping: chPing,
}));

import {
  ClickHouseRepository, FixtureRepository, HttpRepository, resolveRepository, StoreUnreachableError,
} from "./repository";

const fixtureConstructions = vi.fn();

beforeEach(() => {
  config.dataSource = "auto";
  config.apiUrl = "";
  vi.unstubAllGlobals();
  chPing.mockReset();
  chPing.mockResolvedValue(false);
  fixtureConstructions.mockReset();
});

describe("resolveRepository in auto", () => {
  it("throws StoreUnreachableError naming both probes when nothing answers", async () => {
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("refused")));
    const error = await resolveRepository().then(
      () => { throw new Error("resolved"); },
      (e: unknown) => e,
    );
    expect(error).toBeInstanceOf(StoreUnreachableError);
    const probed = (error as StoreUnreachableError).probed.map((p) => p.path);
    expect(probed).toEqual(["/v1/health", "/clickhouse/ping"]);
    expect(chPing).toHaveBeenCalledTimes(1);
  });

  it("names the absolute API base when one is configured", async () => {
    config.apiUrl = "http://api.test/";
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("refused")));
    const error = await resolveRepository().catch((e: unknown) => e);
    expect((error as StoreUnreachableError).probed[0].path).toBe("http://api.test/v1/health");
  });

  it("still prefers the API, then ClickHouse", async () => {
    vi.stubGlobal("fetch", () => Promise.resolve({ ok: true, status: 200, json: async () => ({ status: "ok" }) }));
    expect(await resolveRepository()).toBeInstanceOf(HttpRepository);
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("refused")));
    chPing.mockResolvedValue(true);
    expect(await resolveRepository()).toBeInstanceOf(ClickHouseRepository);
  });

  it("serves the recording only when DATA_SOURCE says fixtures", async () => {
    config.dataSource = "fixtures";
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("refused")));
    expect(await resolveRepository()).toBeInstanceOf(FixtureRepository);
  });
});
