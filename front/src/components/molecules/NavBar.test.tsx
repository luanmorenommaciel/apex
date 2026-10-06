// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Repository } from "@/data/repository";
import { NavBar } from "./NavBar";

const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

let host: HTMLDivElement;
let root: Root;

async function mount(kind: Repository["kind"]): Promise<string> {
  // The badge reads nothing but `kind`; a real repository would drag a data
  // source into a test about a label.
  current.repo = { kind } as unknown as Repository;
  await act(async () => {
    root.render(<MemoryRouter><NavBar /></MemoryRouter>);
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
  host.remove();
});

describe("NavBar source badge", () => {
  it("names apex-api for the http kind, and not the recorded run", async () => {
    const text = await mount("http");
    expect(text).toContain("apex-api");
    expect(text).toContain("http");
    expect(text).not.toContain("fixtures");
  });

  it("keeps the clickhouse label", async () => {
    expect(await mount("clickhouse")).toContain("clickhouse ● apex");
  });

  it("keeps the fixtures label", async () => {
    expect(await mount("fixtures")).toContain("source ◐ fixtures");
  });
});
