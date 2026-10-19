// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { FindingScreen } from "./FindingScreen";

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

const finding = fx.findingsByJob[fx.CURRENT_JOB][0];
let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter> | null = null;
const text = () => host.textContent ?? "";

async function mount(findingId: string, repo: Repository = new FixtureRepository()) {
  current.repo = repo;
  router = createMemoryRouter(
    [{ path: "/runs/:jobId/findings/:findingId", element: <FindingScreen /> }],
    { initialEntries: [`/runs/${fx.CURRENT_JOB}/findings/${findingId}`] },
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

describe("FindingScreen against the recorded run", () => {
  it("renders the finding's type, id, detector and the stored proposal", async () => {
    await mount(finding.finding_id);
    expect(text()).toContain(finding.type);
    expect(text()).toContain(finding.finding_id);
    expect(text()).toContain(finding.detected_by);
    expect(text()).toContain(finding.severity);
    expect(text()).not.toContain("Loading finding");
    expect(text()).not.toContain("No finding");
  });

  it("names an unknown finding id rather than showing another finding", async () => {
    await mount("f-missing");
    expect(text()).toContain("No finding");
    expect(text()).toContain("f-missing");
    expect(text()).not.toContain(finding.detected_by);
  });

  it("keeps the finding on screen when a decoration read fails, and names the source", async () => {
    await mount(finding.finding_id, failing("fixVerification"));
    expect(text()).toContain(finding.finding_id);
    expect(text()).toContain("ClickHouse");
    expect(text()).toContain("verification");
    expect(text()).not.toContain("PRIVATE");
  });
});
