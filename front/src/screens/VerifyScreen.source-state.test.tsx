// @vitest-environment jsdom
import { act, Profiler, StrictMode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FixtureRepository, type Repository } from "@/data/repository";
import * as fx from "@/data/fixtures";
import { VerifyScreen } from "./VerifyScreen";

const current = vi.hoisted(() => ({ repo: null as Repository | null }));
vi.mock("@/data/useRepository", async (original) => ({
  ...await original<typeof import("@/data/useRepository")>(),
  useRepository: () => current.repo,
}));

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((ok, fail) => { resolve = ok; reject = fail; });
  return { promise, resolve, reject };
}

const row = fx.fixVerifications[0];
const url = `/verify?job=${row.job_id}&finding=${row.finding_id}`;
let host: HTMLDivElement;
let root: Root;
let router: ReturnType<typeof createMemoryRouter>;
let repo: FixtureRepository;
let frames: string[];
const text = () => host.textContent ?? "";
const secret = () => Object.assign(new Error("PRIVATE response token"), { name: "PRIVATE error name" });

async function mount(path = url, strict = false) {
  router = createMemoryRouter([{ path: "/verify", element: <VerifyScreen /> }], { initialEntries: [path] });
  await act(async () => {
    const screen = <Profiler id="verify" onRender={() => frames.push(text())}><RouterProvider router={router} /></Profiler>;
    root.render(strict ? <StrictMode>{screen}</StrictMode> : screen);
  });
}

async function click(label: string) {
  const button = [...host.querySelectorAll("button")].find((b) => b.textContent === label);
  expect(button, label).toBeDefined();
  await act(async () => button!.click());
}

function guard(name: string) {
  const label = [...host.querySelectorAll("span.text-bright")].find((n) => n.textContent === name);
  expect(label, name).toBeDefined();
  return label!.parentElement!.parentElement!.textContent ?? "";
}

beforeEach(() => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  repo = new FixtureRepository();
  frames = [];
  current.repo = repo;
  host = document.createElement("div");
  document.body.append(host);
  root = createRoot(host);
});
afterEach(async () => {
  await act(async () => root.unmount());
  router?.dispose();
  host.remove();
  vi.restoreAllMocks();
});

describe("Verify source states (mounted, real async hooks)", () => {
  it.each(["loading", "error"])("explicit URL renders proposal while runs is %s", async (state) => {
    const request = deferred<Awaited<ReturnType<FixtureRepository["listRuns"]>>>();
    vi.spyOn(repo, "listRuns").mockReturnValue(request.promise);
    await mount();
    if (state === "error") await act(async () => request.reject(secret()));
    expect(text()).toContain("Proposed fix");
    expect(text()).toContain(row.finding_id);
    expect(text()).not.toContain("PRIVATE");
  });

  it("automatic selection waits for runs, reports source failure and retries", async () => {
    const request = deferred<Awaited<ReturnType<FixtureRepository["listRuns"]>>>();
    const spy = vi.spyOn(repo, "listRuns").mockReturnValueOnce(request.promise);
    await mount("/verify");
    expect(text()).toContain("Loading runs");
    await act(async () => request.reject(secret()));
    expect(text()).toContain("Runs data unavailable");
    expect(text()).not.toContain("No finding");
    expect(text()).not.toContain("PRIVATE");
    await click("Retry runs");
    expect(text()).toContain("Proposed fix");
    expect(spy).toHaveBeenCalledTimes(2);
  });

  it("distinguishes successful empty run selection", async () => {
    vi.spyOn(repo, "listRuns").mockResolvedValue([]);
    await mount("/verify");
    expect(text()).toContain("No run with findings in the last 50");
    expect(text()).not.toContain("unavailable");
  });

  it("distinguishes selected finding not found from an empty job", async () => {
    await mount(`/verify?job=${row.job_id}&finding=missing-id`);
    expect(text()).toContain("Selected finding not found");
    expect(text()).toContain("missing-id");
    expect(text()).not.toContain("no run in the last 50");
    await act(async () => { await router.navigate("/verify?job=unknown-job"); });
    expect(text()).toContain("No findings returned for this job");
  });

  it.each(["findings", "fixVerification"] as const)("%s has loading/error/retry without raw errors", async (source) => {
    const request = deferred<never>();
    const spy = vi.spyOn(repo, source).mockReturnValueOnce(request.promise);
    await mount();
    expect(text()).toContain(source === "findings" ? "Loading findings" : "Loading verification");
    expect(text()).not.toContain("Proposed fix");
    await act(async () => request.reject(secret()));
    expect(text()).toContain(source === "findings" ? "Findings data unavailable" : "Verification data unavailable");
    expect(text()).not.toContain("PRIVATE");
    expect(text()).not.toContain("No verification for this finding");
    await click(source === "findings" ? "Retry findings" : "Retry verification");
    expect(text()).toContain("Proposed fix");
    expect(spy).toHaveBeenCalledTimes(2);
  });

  it("zero verification rows makes no pipeline diagnosis", async () => {
    vi.spyOn(repo, "fixVerification").mockResolvedValue(null);
    await mount();
    expect(text()).toContain("No verification for this finding");
    expect(text()).toContain("query returned no row");
    expect(text()).not.toContain("gap in the pipeline");
    expect(text()).not.toContain("until it runs");
  });

  it.each([
    ["jobConf", "configuration", ["cluster width", "reshape check", "bound analysis"]],
    ["stages", "stages", ["bound analysis", "reshape check"]],
    ["transitions", "transitions", ["skew absence"]],
  ] as const)("%s failure/loading affects only dependent checks", async (method, source, checks) => {
    const request = deferred<never>();
    vi.spyOn(repo, method).mockReturnValueOnce(request.promise);
    await mount();
    expect(text()).toContain("Proposed fix");
    for (const check of checks) {
      expect(guard(check)).toContain(`${source} loading`);
      expect(guard(check)).not.toContain("✓");
    }
    if (method === "jobConf") {
      const noOp = [...host.querySelectorAll("span.text-bright")].find((n) => n.textContent?.startsWith("no-op gate"));
      expect(noOp?.parentElement?.textContent).toContain("configuration loading");
    }
    await act(async () => request.reject(secret()));
    expect(text()).toContain("Proposed fix");
    for (const check of checks) expect(guard(check)).toContain(`${source} query failed`);
    expect(text()).not.toContain("PRIVATE");
    await click(`Retry ${source}`);
    expect(text()).not.toContain(`${source} query failed`);
    expect(guard("mechanism")).toContain("plan_json");
  });

  it("a successful missing stage is not mislabeled job-level", async () => {
    vi.spyOn(repo, "stages").mockResolvedValue([]);
    await mount();
    expect(guard("bound analysis")).toContain("no stage row returned");
    expect(guard("bound analysis")).not.toContain("it is job-level");
  });

  it("successful zeros are evaluated, not treated as query failure", async () => {
    const stages = await repo.stages(row.job_id);
    vi.spyOn(repo, "stages").mockResolvedValue(stages.map((s) => ({ ...s, task_count: 0 })));
    vi.spyOn(repo, "jobConf").mockResolvedValue([
      { job_id: row.job_id, key: "spark.sql.shuffle.partitions", value: "0", ts: "2026-09-11T00:00:00.000Z" },
    ]);
    vi.spyOn(repo, "transitions").mockResolvedValue([]);
    await mount();
    expect(guard("reshape check")).toContain("0 tasks = configured 0");
    expect(guard("skew absence")).not.toContain("query failed");
    expect(text()).toContain("Proposed fix");
  });

  it("A→B suppresses late A proposal and never commits A as B", async () => {
    const pendingA = deferred<typeof row | null>();
    const pendingB = deferred<typeof row | null>();
    const findingA = (await repo.findings(row.job_id)).find((f) => f.finding_id === row.finding_id)!;
    const findingB = { ...findingA, finding_id: "finding-B", job_id: "job-B" };
    const baseFindings = repo.findings.bind(repo);
    vi.spyOn(repo, "findings").mockImplementation((job) => job === "job-B" ? Promise.resolve([findingB]) : baseFindings(job));
    vi.spyOn(repo, "fixVerification").mockImplementation((id) => id === "finding-B" ? pendingB.promise : pendingA.promise);
    await mount();
    await act(async () => { await router.navigate("/verify?job=job-B&finding=finding-B"); });
    await act(async () => pendingB.resolve({ ...row, job_id: "job-B", finding_id: "finding-B", proposed_diff: '{"spark.marker":"B-marker"}' }));
    expect(text()).toContain("B-marker");
    await act(async () => pendingA.resolve({ ...row, proposed_diff: '{"spark.marker":"A-marker"}' }));
    expect(text()).toContain("B-marker");
    expect(text()).not.toContain("A-marker");
  });

  it("clears settled old data immediately on job change, including same finding ID", async () => {
    const findingA = (await repo.findings(row.job_id)).find((f) => f.finding_id === row.finding_id)!;
    vi.spyOn(repo, "findings").mockImplementation(async (job) => [{ ...findingA, job_id: job }]);
    const pendingB = deferred<typeof row | null>();
    vi.spyOn(repo, "fixVerification")
      .mockResolvedValueOnce({ ...row, proposed_diff: '{"spark.marker":"A-marker"}' })
      .mockReturnValueOnce(pendingB.promise);
    await mount();
    expect(text()).toContain("A-marker");
    // Capture every DOM commit, not only the final state after effects flush.
    frames = [];
    await act(async () => { await router.navigate(`/verify?job=job-B&finding=${row.finding_id}`); });
    expect(text()).not.toContain("A-marker");
    expect(frames.every((frame) => !frame.includes("A-marker"))).toBe(true);
    await act(async () => pendingB.reject(secret()));
    expect(text()).toContain("Verification data unavailable");
    expect(text()).not.toContain("A-marker");
    await click("Retry verification");
    // Default repository resolves the row for A; its identity must not be accepted as B.
    expect(text()).not.toContain("Proposed fix");
  });

  it("switching finding within the same job clears the prior proposal", async () => {
    const findings = await repo.findings(row.job_id);
    const second = { ...findings[0], finding_id: "second-finding" };
    vi.spyOn(repo, "findings").mockResolvedValue([...findings, second]);
    const pending = deferred<typeof row | null>();
    vi.spyOn(repo, "fixVerification").mockResolvedValueOnce(row).mockReturnValueOnce(pending.promise);
    await mount();
    expect(text()).toContain("Proposed fix");
    await act(async () => { await router.navigate(`/verify?job=${row.job_id}&finding=second-finding`); });
    expect(text()).not.toContain("Proposed fix");
    await act(async () => pending.resolve(null));
    expect(text()).toContain("No verification for this finding");
  });

  it("StrictMode cleanup ignores the abandoned attempt", async () => {
    const abandoned = deferred<typeof row | null>();
    vi.spyOn(repo, "fixVerification").mockReturnValueOnce(abandoned.promise).mockResolvedValue(row);
    await mount(url, true);
    expect(text()).toContain("Proposed fix");
    await act(async () => abandoned.reject(secret()));
    expect(text()).toContain("Proposed fix");
    expect(text()).not.toContain("unavailable");
  });

  it("missing explicit selection stays identifiable even if its verification request fails", async () => {
    vi.spyOn(repo, "fixVerification").mockRejectedValue(secret());
    await mount(`/verify?job=${row.job_id}&finding=missing-id`);
    expect(text()).toContain("Selected finding not found");
    expect(text()).toContain("missing-id");
    expect(text()).not.toContain("PRIVATE");
  });

  it("successful empty configuration means missing keys, not a transport failure", async () => {
    vi.spyOn(repo, "jobConf").mockResolvedValue([]);
    await mount();
    expect(text()).toContain("Proposed fix");
    expect(guard("cluster width")).toContain("absent from job_conf");
    expect(text()).not.toContain("configuration query failed");
  });

  it("run context and memory failures do not block an available proposal (I2 wording deferred)", async () => {
    vi.spyOn(repo, "run").mockRejectedValue(secret());
    vi.spyOn(repo, "shapeRuns").mockRejectedValue(secret());
    await mount();
    expect(text()).toContain("Proposed fix");
    expect(text()).not.toContain("PRIVATE");
  });
});
