// @vitest-environment jsdom
import { act, type ReactElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { NavBar } from "@/components/molecules/NavBar";
import { CompareScreen } from "./CompareScreen";
import { MemoryScreen } from "./MemoryScreen";
import { RunsScreen } from "./RunsScreen";

/**
 * What jsx-a11y cannot see from the source: that every control on the
 * mounted screens has an accessible name, that a status is readable as text
 * and not only as a colour, and that the navigation is a named landmark.
 */
const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

const SCREENS: Array<[string, string, string, ReactElement]> = [
  ["runs", "/runs", "/runs", <RunsScreen />],
  ["compare", "/compare", `/compare?current=${fx.CURRENT_JOB}&baseline=${fx.BASELINE_JOB}`, <CompareScreen />],
  ["memory", "/memory", "/memory", <MemoryScreen />],
];

let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter> | null = null;

async function mount(path: string, entry: string, element: ReactElement) {
  current.repo = new FixtureRepository();
  router = createMemoryRouter([{ path, element }], { initialEntries: [entry] });
  await act(async () => { root.render(<RouterProvider router={router!} />); });
  await act(async () => { await new Promise((r) => setTimeout(r, 0)); });
  await act(async () => { await new Promise((r) => setTimeout(r, 0)); });
}

/** aria-label, aria-labelledby, or a <label for> pointing at it. */
function accessibleName(control: Element): string | null {
  const own = control.getAttribute("aria-label") ?? control.getAttribute("aria-labelledby");
  if (own) return own;
  const id = control.getAttribute("id");
  const label = id ? host.querySelector(`label[for="${id}"]`) : control.closest("label");
  return label?.textContent?.trim() || null;
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

describe("accessible names and text beside colour", () => {
  it.each(SCREENS)("%s: every input and select has an accessible name", async (_name, path, entry, element) => {
    await mount(path, entry, element);
    const controls = [...host.querySelectorAll("input, select, textarea")];
    for (const control of controls) {
      expect(accessibleName(control), `${control.tagName} without a name`).toBeTruthy();
    }
  });

  it("runs: a run's status reads as a word in its status cell, not only as a colour", async () => {
    await mount("/runs", "/runs", <RunsScreen />);
    const cells = [...host.querySelectorAll('[role="cell"][data-column="status"]')];
    expect(cells).toHaveLength(fx.runs.length);
    for (const cell of cells) {
      expect(cell.textContent ?? "").toMatch(/healthy|warning|degraded|failed/i);
    }
  });

  it("runs: a clickable row is reachable by keyboard", async () => {
    await mount("/runs", "/runs", <RunsScreen />);
    const rows = [...host.querySelectorAll('[role="row"][tabindex="0"]')];
    expect(rows).toHaveLength(fx.runs.length);
  });

  it("nav: the primary navigation is a named landmark", async () => {
    current.repo = { kind: "fixtures" } as unknown as Repository;
    router = createMemoryRouter([{ path: "/runs", element: <NavBar /> }], { initialEntries: ["/runs"] });
    await act(async () => { root.render(<RouterProvider router={router!} />); });
    const nav = host.querySelector("nav");
    expect(nav?.getAttribute("aria-label")).toBeTruthy();
  });
});
