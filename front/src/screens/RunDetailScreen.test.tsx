// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { RunDetailScreen } from "./RunDetailScreen";

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

async function mount(jobId: string, repo: Repository = new FixtureRepository()) {
  current.repo = repo;
  router = createMemoryRouter(
    [{ path: "/runs/:jobId", element: <RunDetailScreen /> }],
    { initialEntries: [`/runs/${jobId}`] },
  );
  await act(async () => { root.render(<RouterProvider router={router!} />); });
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

describe("RunDetailScreen against the recorded run", () => {
  it("renders the run, its stages and its findings", async () => {
    await mount(fx.CURRENT_JOB);
    const run = fx.runs.find((r) => r.job_id === fx.CURRENT_JOB)!;
    expect(text()).toContain(run.app_name);
    // The detail panel shows the finding of the SELECTED stage - the first
    // stage carrying one - and the header counts them all.
    const findings = fx.findingsByJob[fx.CURRENT_JOB];
    const onStage = findings.find((f) => f.stage_id >= 0)!;
    expect(text()).toContain(onStage.type);
    expect(text()).toContain(onStage.finding_id);
    expect(text()).toContain(`${findings.length} findings`);
    expect(text()).not.toContain("Loading run");
    expect(text()).not.toContain("No stage rows");
  });

  it("says when a job has no stage rows instead of inventing one", async () => {
    await mount("app-unknown");
    expect(text()).toContain("No stage rows");
    expect(text()).toContain("app-unknown");
  });

  it("reports a rejected stages read by source, never by message", async () => {
    await mount(fx.CURRENT_JOB, failing("stages"));
    expect(text()).toContain("ClickHouse");
    expect(text()).not.toContain("PRIVATE");
    expect(text()).not.toContain("No stage rows");
  });
});
