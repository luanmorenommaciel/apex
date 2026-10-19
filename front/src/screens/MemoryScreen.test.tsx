// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { MemoryScreen } from "./MemoryScreen";

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
      if (prop === "kind") return "http";
      if (prop === method) return () => Promise.reject(error);
      return Reflect.get(target, prop, receiver);
    },
  }) as unknown as Repository;
}

let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter> | null = null;
const text = () => host.textContent ?? "";

async function mount(entry = "/memory", repo: Repository = new FixtureRepository()) {
  current.repo = repo;
  router = createMemoryRouter([{ path: "/memory", element: <MemoryScreen /> }], { initialEntries: [entry] });
  await act(async () => { root.render(<RouterProvider router={router!} />); });
  // Two rounds: the shapes resolve first, then the runs keyed on the shape.
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

describe("MemoryScreen against the recorded shape", () => {
  it("defaults to the most-run shape and draws every run on it", async () => {
    await mount();
    expect(text()).toContain(fx.PLAN_FINGERPRINT.slice(0, 12));
    expect(text()).toContain(`${fx.shapeRuns.length} runs`);
    for (const run of fx.shapeRuns) expect(text()).toContain(run.job_id.slice(-4));
    expect(text()).not.toContain("nothing indexed yet");
  });

  it("says nothing is indexed when the store knows no shape", async () => {
    const empty = new Proxy(new FixtureRepository(), {
      get: (t, p, r) => (p === "planShapes" ? () => Promise.resolve([]) : Reflect.get(t, p, r)),
    }) as unknown as Repository;
    await mount("/memory", empty);
    expect(text()).toContain("nothing indexed yet");
    expect(text()).not.toContain(fx.PLAN_FINGERPRINT.slice(0, 12));
  });

  it("reports a rejected shape runs read by source, never by message", async () => {
    await mount("/memory", failing("shapeRuns"));
    expect(text()).toContain("apex-api");
    expect(text()).toContain("shape runs");
    expect(text()).not.toContain("PRIVATE");
  });
});
