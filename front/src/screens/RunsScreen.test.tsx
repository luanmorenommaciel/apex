// @vitest-environment jsdom
/**
 * P7.5 — the runs list filters on the SERVER and pages by offset.
 *
 * The screen no longer filters the 50 rows it was handed: it asks the store
 * for the runs matching job_id prefix / plan fingerprint / has findings, and
 * turns pages with offset. These tests drive the mounted screen and read what
 * it asked the repository for.
 */
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as fx from "@/data/fixtures";
import { FixtureRepository, type Repository, type RunListFilters } from "@/data/repository";
import { RUNS_FILTER_DEBOUNCE_MS, RUNS_PAGE_SIZE, RunsScreen } from "./RunsScreen";

const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter> | null = null;
let listRuns: ReturnType<typeof vi.fn<(limit?: number, filters?: RunListFilters) => ReturnType<Repository["listRuns"]>>>;

/** A full page of copies of the recording, so "next" has somewhere to go. */
const page = (n: number) =>
  Array.from({ length: n }, (_, i) => ({ ...fx.runs[i % fx.runs.length], job_id: `job-${i}` }));

const settle = () => act(async () => {
  await new Promise((resolve) => setTimeout(resolve, 0));
});

async function mount() {
  router = createMemoryRouter([{ path: "/runs", element: <RunsScreen /> }], { initialEntries: ["/runs"] });
  await act(async () => {
    root.render(<RouterProvider router={router!} />);
  });
  await settle();
}

function type(label: string, value: string) {
  const input = host.querySelector<HTMLInputElement>(`input[aria-label="${label}"]`)!;
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")!.set!;
  act(() => {
    setter.call(input, value);
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

async function click(text: string) {
  const button = [...host.querySelectorAll("button")].find((b) => b.textContent?.includes(text))!;
  await act(async () => button.click());
  await settle();
}

const button = (text: string) =>
  [...host.querySelectorAll("button")].find((b) => b.textContent?.includes(text))!;

const lastFilters = () => listRuns.mock.calls.at(-1)?.[1];

beforeEach(() => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  host = document.createElement("div");
  document.body.append(host);
  root = createRoot(host);
  const repo = new FixtureRepository();
  listRuns = vi.fn(async () => page(RUNS_PAGE_SIZE));
  current.repo = Object.assign(repo, { listRuns }) as unknown as Repository;
});

afterEach(async () => {
  await act(async () => root.unmount());
  router?.dispose();
  host.remove();
});

describe("RunsScreen (server-side filters, offset paging)", () => {
  it("asks for the first page with no filters", async () => {
    await mount();
    expect(listRuns).toHaveBeenCalledTimes(1);
    expect(listRuns.mock.calls[0][0]).toBe(50);
    expect(lastFilters()).toEqual({
      offset: 0, jobIdPrefix: undefined, planFingerprint: undefined, hasFindings: undefined,
    });
    expect(button("prev").disabled).toBe(true);
    expect(button("next").disabled).toBe(false);
  });

  it("sends the job_id prefix to the store once typing settles", async () => {
    await mount();
    type("job_id prefix", "app-2026");
    type("job_id prefix", "app-20260803");
    expect(listRuns).toHaveBeenCalledTimes(1); // debounced, not per keystroke
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, RUNS_FILTER_DEBOUNCE_MS + 50));
    });
    await settle();
    expect(listRuns).toHaveBeenCalledTimes(2);
    expect(lastFilters()).toMatchObject({ jobIdPrefix: "app-20260803", offset: 0 });
  });

  it("sends the plan fingerprint to the store", async () => {
    await mount();
    type("plan fingerprint", ` ${fx.PLAN_FINGERPRINT} `);
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, RUNS_FILTER_DEBOUNCE_MS + 50));
    });
    await settle();
    expect(lastFilters()).toMatchObject({ planFingerprint: fx.PLAN_FINGERPRINT });
  });

  it("'findings only' asks the store for has_findings=true; 'all' clears it", async () => {
    await mount();
    await click("findings only");
    expect(lastFilters()).toMatchObject({ hasFindings: true, offset: 0 });
    await click("all");
    expect(lastFilters()?.hasFindings).toBeUndefined();
  });

  it("pages with offset, and a filter change starts again from the first page", async () => {
    await mount();
    await click("next");
    expect(lastFilters()).toMatchObject({ offset: 50 });
    await click("next");
    expect(lastFilters()).toMatchObject({ offset: 100 });
    await click("prev");
    expect(lastFilters()).toMatchObject({ offset: 50 });
    await click("findings only");
    expect(lastFilters()).toMatchObject({ offset: 0, hasFindings: true });
  });

  it("disables next on a short page — it is the last one", async () => {
    listRuns.mockImplementation(async () => page(3));
    await mount();
    expect(button("next").disabled).toBe(true);
    expect(host.textContent).toContain("3 runs");
  });

  it("renders the rows the store returned, without filtering them again", async () => {
    listRuns.mockImplementation(async () => page(2).map((r) => ({ ...r, finding_count: 0 })));
    await mount();
    await click("findings only");
    // The store answered; the screen does not second-guess it by dropping rows.
    expect(host.textContent).toContain("job-0");
    expect(host.textContent).toContain("job-1");
  });
});
