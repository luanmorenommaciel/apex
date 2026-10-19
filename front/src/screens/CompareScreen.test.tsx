// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { CompareScreen } from "./CompareScreen";

const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

/** FixtureRepository with ONE read rejecting on a message that must never render. */
function failing(method: keyof Repository): Repository {
  const error = Object.assign(new Error("PRIVATE response body"), { name: "PRIVATE name" });
  return new Proxy(new FixtureRepository(), {
    get(target, prop, receiver) {
      if (prop === "kind") return "clickhouse";
      if (prop === method) return () => Promise.reject(error);
      return Reflect.get(target, prop, receiver);
    },
  }) as unknown as Repository;
}

let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter> | null = null;
const text = () => host.textContent ?? "";

async function mount(entry: string, repo: Repository = new FixtureRepository()) {
  current.repo = repo;
  router = createMemoryRouter([{ path: "/compare", element: <CompareScreen /> }], { initialEntries: [entry] });
  await act(async () => { root.render(<RouterProvider router={router!} />); });
  // Two rounds: the run list resolves first, then the reads keyed on it.
  await act(async () => { await new Promise((r) => setTimeout(r, 0)); });
  await act(async () => { await new Promise((r) => setTimeout(r, 0)); });
}

beforeEach(() => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  host = document.createElement("div");
  document.body.append(host);
  root = createRoot(host);
});
afterEach(async () => {
  await act(async () => root.unmount());
  router?.dispose();
  host.remove();
});

describe("CompareScreen against the recorded pair", () => {
  it("compares the two runs named in the URL and counts their shared shape", async () => {
    await mount(`/compare?current=${fx.CURRENT_JOB}&baseline=${fx.BASELINE_JOB}`);
    expect(text()).toContain(fx.CURRENT_JOB);
    expect(text()).toContain(fx.BASELINE_JOB);
    expect(text()).toContain("1 shared plan shape");
    expect(text()).not.toContain("no comparable run");
    expect(text()).not.toContain("no baseline");
  });

  it("picks the newest run and its recorded baseline when the URL names none", async () => {
    await mount("/compare");
    expect(text()).toContain(fx.CURRENT_JOB);
    expect(text()).toContain(fx.BASELINE_JOB);
  });

  it("reports a rejected run list by source, never by message", async () => {
    await mount("/compare", failing("listRuns"));
    expect(text()).toContain("ClickHouse");
    expect(text()).toContain("query failed");
    expect(text()).not.toContain("PRIVATE");
  });
});
