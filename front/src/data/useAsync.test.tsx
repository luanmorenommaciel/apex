// @vitest-environment jsdom
import { act, StrictMode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as fx from "./fixtures";
import {
  ClickHouseRepository, FixtureRepository, HttpRepository, type Repository,
} from "./repository";
import { READ_TTL_MS, useRead } from "./useRepository";
import { RunDetailScreen } from "@/screens/RunDetailScreen";

/**
 * The reads behind every screen: one request per key however many hooks
 * ask, a short cache across screens, a StrictMode mount that issues each
 * read once, and a request nobody waits for aborted at the fetch.
 */
const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

/** FixtureRepository that counts every method call. One instance, one cache. */
function counting(): { repo: Repository; calls: Record<string, number> } {
  const calls: Record<string, number> = {};
  const target = new FixtureRepository();
  const repo = new Proxy(target, {
    get(t, prop, receiver) {
      const value = Reflect.get(t, prop, receiver);
      if (typeof value !== "function" || typeof prop !== "string") return value;
      return (...args: unknown[]) => {
        calls[prop] = (calls[prop] ?? 0) + 1;
        return (value as (...a: unknown[]) => unknown).apply(t, args);
      };
    },
  }) as unknown as Repository;
  return { repo, calls };
}

function Stages({ repo, jobId }: { repo: Repository; jobId: string }) {
  const q = useRead(repo, ["stages", jobId]);
  return <span>{q.loading ? "loading" : q.error ? "error" : `${q.data?.length ?? 0} stages`}</span>;
}

let host: HTMLDivElement;
let root: Root;
const text = () => host.textContent ?? "";
const tick = () => act(async () => { await new Promise((r) => setTimeout(r, 0)); });

beforeEach(() => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  host = document.createElement("div");
  document.body.append(host);
  root = createRoot(host);
});
afterEach(async () => {
  await act(async () => root.unmount());
  host.remove();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("useRead", () => {
  it("shares one request between two hooks on the same key", async () => {
    const { repo, calls } = counting();
    await act(async () => {
      root.render(<><Stages repo={repo} jobId={fx.CURRENT_JOB} /><Stages repo={repo} jobId={fx.CURRENT_JOB} /></>);
    });
    await tick();
    expect(text()).toBe("34 stages34 stages");
    expect(calls.stages).toBe(1);
  });

  it("answers from the cache within the TTL and asks again after it", async () => {
    const { repo, calls } = counting();
    const t0 = Date.now();
    const now = vi.spyOn(Date, "now").mockReturnValue(t0);
    await act(async () => { root.render(<Stages repo={repo} jobId={fx.CURRENT_JOB} />); });
    await tick();
    await act(async () => root.unmount());
    root = createRoot(host);
    await act(async () => { root.render(<Stages repo={repo} jobId={fx.CURRENT_JOB} />); });
    await tick();
    expect(text()).toBe("34 stages");
    expect(calls.stages).toBe(1);

    now.mockReturnValue(t0 + READ_TTL_MS + 1);
    await act(async () => root.unmount());
    root = createRoot(host);
    await act(async () => { root.render(<Stages repo={repo} jobId={fx.CURRENT_JOB} />); });
    await tick();
    expect(calls.stages).toBe(2);
  });

  it("does not cache a failure", async () => {
    const { repo, calls } = counting();
    let fail = true;
    const failing = new Proxy(repo, {
      get: (t, p, r) => (p === "stages" && fail ? () => Promise.reject(new Error("down")) : Reflect.get(t, p, r)),
    }) as unknown as Repository;
    await act(async () => { root.render(<Stages repo={failing} jobId={fx.CURRENT_JOB} />); });
    await tick();
    expect(text()).toBe("error");
    fail = false;
    await act(async () => root.unmount());
    root = createRoot(host);
    await act(async () => { root.render(<Stages repo={failing} jobId={fx.CURRENT_JOB} />); });
    await tick();
    expect(text()).toBe("34 stages");
    expect(calls.stages).toBe(1);
  });

  it("mounts RunDetail under StrictMode with each read issued once", async () => {
    const { repo, calls } = counting();
    current.repo = repo;
    const router = createMemoryRouter(
      [{ path: "/runs/:jobId", element: <RunDetailScreen /> }],
      { initialEntries: [`/runs/${fx.CURRENT_JOB}`] },
    );
    await act(async () => { root.render(<StrictMode><RouterProvider router={router} /></StrictMode>); });
    await tick();
    await tick();
    expect(text()).toContain("daily_revenue_rollup");
    for (const method of ["run", "stages", "jobConf", "findings", "transitions"]) {
      expect(calls[method], method).toBe(1);
    }
    router.dispose();
  });

  it.each([
    ["clickhouse", () => new ClickHouseRepository()],
    ["http", () => new HttpRepository()],
  ])("%s: aborts at the fetch when the only reader unmounts", async (_kind, make) => {
    // jsdom supplies window.location.origin; stubbing window here would take
    // react-dom's own globals with it.
    const signals: AbortSignal[] = [];
    vi.stubGlobal("fetch", (_url: string, init?: RequestInit) => {
      if (init?.signal) signals.push(init.signal);
      // Never settles: the only way out is the abort.
      return new Promise<Response>(() => {});
    });
    const repo = make();
    await act(async () => { root.render(<Stages repo={repo} jobId="j" />); });
    expect(text()).toBe("loading");
    // The browser door probes system.columns before its first findings read,
    // not before stages; either way every fetch here carries a signal.
    expect(signals.length).toBeGreaterThan(0);
    await act(async () => root.unmount());
    root = createRoot(host);
    await tick();
    expect(signals.every((s) => s.aborted)).toBe(true);
  });
});
