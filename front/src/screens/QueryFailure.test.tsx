// @vitest-environment jsdom
import { act, type ReactElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiAuthError, ApiError } from "@/data/http";
import type { Repository } from "@/data/repository";
import { CompareScreen } from "./CompareScreen";
import { FindingScreen } from "./FindingScreen";
import { MemoryScreen } from "./MemoryScreen";
import { RunDetailScreen } from "./RunDetailScreen";
import { RunsScreen } from "./RunsScreen";

const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

/** A repository whose every query rejects with `error`. */
function rejecting(error: Error, kind: Repository["kind"] = "http"): Repository {
  const fail = () => Promise.reject(error);
  return {
    kind, listRuns: fail, run: fail, baselineCandidates: fail, planShapes: fail,
    shapeRuns: fail, planSample: fail, stages: fail, jobConf: fail, findings: fail,
    transitions: fail, fixVerification: fail,
  };
}

// name · route · entry url · element · the empty-state copy that must NOT
// render in the failure's place
const SCREENS: Array<[string, string, string, ReactElement, string]> = [
  ["runs", "/runs", "/runs", <RunsScreen />, "No rows match this filter"],
  ["run detail", "/runs/:jobId", "/runs/j1", <RunDetailScreen />, "No stage rows"],
  ["finding", "/runs/:jobId/findings/:findingId", "/runs/j1/findings/f1", <FindingScreen />, "No finding"],
  ["compare", "/compare", "/compare", <CompareScreen />, "no comparable run"],
  ["memory", "/memory", "/memory", <MemoryScreen />, "nothing indexed yet"],
];

let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter> | null = null;

async function mount(path: string, entry: string, element: ReactElement): Promise<string> {
  router = createMemoryRouter([{ path, element }], { initialEntries: [entry] });
  await act(async () => {
    root.render(<RouterProvider router={router!} />);
  });
  // Let the rejections settle and the state updates flush.
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0));
  });
  return host.textContent ?? "";
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

describe("a rejected query on every screen", () => {
  it.each(SCREENS)("%s names a rejected token and renders no empty state in its place", async (_name, path, entry, element, emptyCopy) => {
    current.repo = rejecting(new ApiAuthError("token rejected", "/v1/x"));
    const text = await mount(path, entry, element);
    expect(text).toContain("APEX_API_TOKEN");
    expect(text).not.toContain(emptyCopy);
  });

  it("shows the API's detail on memory: no TABLE is not no HISTORY", async () => {
    current.repo = rejecting(new ApiError(502, "memory_unavailable: the contract v0.3 tables are not present", "/v1/plans"));
    const text = await mount("/memory", "/memory", <MemoryScreen />);
    expect(text).toContain("memory_unavailable");
    expect(text).toContain("502");
    expect(text).not.toContain("nothing indexed yet");
  });

  it("survives an API detail that is not text, as FastAPI's 422 sends", async () => {
    // http.ts types `detail` as a string; a 422 body carries a list of
    // validation errors there. Rendered as a React child it would throw.
    const notText = [{ loc: ["query", "limit"], msg: "value is not a valid integer" }];
    current.repo = rejecting(new ApiError(422, notText as unknown as string, "/v1/runs"));
    const text = await mount("/runs", "/runs", <RunsScreen />);
    expect(text).toContain("422");
    expect(text).toContain("no readable detail");
    expect(text).not.toContain("[object Object]");
  });

  it("never renders a non-API error's message, which can carry a response body", async () => {
    current.repo = rejecting(Object.assign(new Error("PRIVATE response body"), { name: "PRIVATE name" }));
    const text = await mount("/runs", "/runs", <RunsScreen />);
    expect(text).toContain("query against apex-api failed");
    expect(text).not.toContain("PRIVATE");
  });

  it("names the source that was resolved, never ClickHouse for the http kind", async () => {
    current.repo = rejecting(new ApiAuthError("token rejected", "/v1/runs"), "http");
    expect(await mount("/runs", "/runs", <RunsScreen />)).not.toContain("ClickHouse");
    await act(async () => root.unmount());
    root = createRoot(host);
    current.repo = rejecting(new Error("boom"), "clickhouse");
    expect(await mount("/runs", "/runs", <RunsScreen />)).toContain("ClickHouse");
  });
});
