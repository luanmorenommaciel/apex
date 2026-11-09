// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { RunsScreen } from "./RunsScreen";

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

async function mount(repo: Repository = new FixtureRepository()) {
  current.repo = repo;
  router = createMemoryRouter([{ path: "/runs", element: <RunsScreen /> }], { initialEntries: ["/runs"] });
  await act(async () => { root.render(<RouterProvider router={router!} />); });
  await act(async () => { await new Promise((r) => setTimeout(r, 0)); });
}

async function type(value: string) {
  const input = host.querySelector("input");
  expect(input).not.toBeNull();
  // React listens for the native input event and reads the value React did
  // not set itself, so the prototype setter is used rather than the instance.
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")!.set!;
  await act(async () => {
    setter.call(input, value);
    input!.dispatchEvent(new Event("input", { bubbles: true }));
  });
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

describe("RunsScreen against the recorded run", () => {
  it("lists every recorded run with its app name and status", async () => {
    await mount();
    for (const run of fx.runs) {
      expect(text()).toContain(run.job_id);
      expect(text()).toContain(run.app_name);
    }
    expect(text()).toContain(`${fx.runs.length} most recent applications`);
    expect(text()).not.toContain("querying");
  });

  it("filters the list by what is typed", async () => {
    await mount();
    await type("sessionize");
    expect(text()).toContain("app-20260802194030-0068");
    expect(text()).not.toContain(fx.CURRENT_JOB);
    expect(text()).toContain(`1 of ${fx.runs.length}`);
    await type("");
    expect(text()).toContain(fx.CURRENT_JOB);
  });

  it("reports a rejected listRuns by source, never by message", async () => {
    await mount(failing("listRuns"));
    expect(text()).toContain("apex-api");
    expect(text()).toContain("query failed");
    expect(text()).not.toContain("PRIVATE");
    expect(text()).not.toContain("No rows match this filter");
  });
});
