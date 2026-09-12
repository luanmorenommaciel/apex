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

  it("presents and copies a valid overlay as its original text without patch advice", async () => {
    const original = '  {\n  "spark.z.setting" : true,\n  "spark.sql.shuffle.partitions" : 2e2\n}  \n';
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
    vi.spyOn(repo, "fixVerification").mockResolvedValue({ ...row, proposed_diff: original });
    await mount();
    expect(text()).toContain("proposed_config · valid JSON overlay");
    const raw = host.querySelector('pre[aria-label="Original proposal"]');
    expect(raw?.textContent).toBe(original);
    expect(raw?.closest('[hidden], [aria-hidden="true"]')).toBeNull();
    expect(raw?.classList.contains("whitespace-pre")).toBe(true);
    expect(text()).toContain("spark.sql.shuffle.partitions");
    expect(text()).toContain("no-op gate · shuffle.partitions");
    expect(text()).toContain("configuration overlay, not a patch");
    expect(text()).not.toContain("git apply");
    await click("copy original proposal");
    expect(writeText).toHaveBeenCalledWith(original);
  });

  it("keeps invalid overlay JSON intact and does not create a per-key gate", async () => {
    const original = '{"spark.keep":"yes","invalid":{"nested":true}}';
    vi.spyOn(repo, "fixVerification").mockResolvedValue({ ...row, proposed_diff: original });
    await mount();
    expect(text()).toContain("proposed_config · invalid overlay");
    expect(text()).toContain(original);
    expect(text()).toContain("proposal is not a valid conf overlay — nothing to gate");
    expect(text()).not.toContain("no-op gate · keep");
  });

  it("keeps a unified diff manual and reserves git apply advice for that format", async () => {
    const diff = [
      "--- a/conf/spark-defaults.conf",
      "+++ b/conf/spark-defaults.conf",
      "@@ -1 +1 @@",
      "- spark.sql.shuffle.partitions 200",
      "+ spark.sql.shuffle.partitions 800",
    ].join("\n");
    vi.spyOn(repo, "fixVerification").mockResolvedValue({ ...row, proposed_diff: diff });
    await mount();
    expect(text()).toContain("proposed_diff · unified diff");
    expect(text()).toContain("review this unified diff, then git apply");
    expect(text()).toContain("proposal is not a valid conf overlay — nothing to gate");
  });

  it.each([
    "@@ -1 +1 @@\n+ spark.sql.shuffle.partitions 800",
    row.proposed_diff,
  ])("shows headerless proposal as unknown without git apply advice: %s", async (original) => {
    vi.spyOn(repo, "fixVerification").mockResolvedValue({ ...row, proposed_diff: original });
    await mount();
    expect(text()).toContain("proposal · unknown format");
    expect(text()).not.toContain("git apply");
    expect(text()).toContain("inspect or copy the original text without executing it");
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

  it("describes safety as a local namespace check without inventing stronger coverage", async () => {
    vi.spyOn(repo, "fixVerification").mockResolvedValue({
      ...row,
      proposed_diff: '{"spark.sql.shuffle.partitions":200}',
    });
    await mount();
    const safety = guard("safety");
    expect(safety).toContain("local namespace check");
    expect(safety).toContain("under spark.*");
    expect(safety).toContain("does not validate values");
    expect(safety).toContain("does not inspect data paths");
    expect(safety).not.toContain("no data path named");
  });

  it.each([
    ["improved", false, true, "The verify lane recorded that the fix did not fire."],
    ["regressed", true, true, "The verify lane recorded that the fix demonstrably fired."],
    ["unresolved", true, false, "The verify lane recorded that the fix demonstrably fired."],
  ] as const)("renders %s runtime direction independently from mechanism and certification", async (
    verdict, mechanismConfirmed, runtimeCertified, mechanismText,
  ) => {
    vi.spyOn(repo, "fixVerification").mockResolvedValue({
      ...row,
      mechanism_confirmed: mechanismConfirmed,
      runtime_certified: runtimeCertified,
      runtime_verdict: verdict,
    });
    await mount();
    expect(text()).toContain(mechanismText);
    expect(text()).toContain(`Direction: ${verdict}`);
    expect(text()).toContain("This query derives the runtime fields from the measured delta and recorded noise floor.");
    expect(text()).toContain("measured magnitude exceeds that floor");
    expect(text()).toContain("does not attribute the observed runtime change to this proposal");
    if (verdict === "regressed") expect(text()).toContain("A certified regression is not a runtime saving.");
  });

  it("separates loading and failure of run context from the available proposal", async () => {
    const request = deferred<Awaited<ReturnType<FixtureRepository["run"]>>>();
    const spy = vi.spyOn(repo, "run").mockReturnValueOnce(request.promise);
    await mount();
    expect(text()).toContain("Proposed fix");
    expect(text()).toContain("Loading the selected run context");
    await act(async () => request.reject(secret()));
    expect(text()).toContain("The selected run context is unavailable");
    expect(text()).not.toContain("PRIVATE");
    await click("Retry run context");
    expect(text()).toContain("Consulted run fingerprint");
    expect(spy).toHaveBeenCalledTimes(2);
  });

  it("separates loading and failure of shape memory from the available proposal", async () => {
    const request = deferred<Awaited<ReturnType<FixtureRepository["shapeRuns"]>>>();
    const spy = vi.spyOn(repo, "shapeRuns").mockReturnValueOnce(request.promise);
    await mount();
    expect(text()).toContain("Proposed fix");
    expect(text()).toContain("Loading plan memory for this fingerprint");
    await act(async () => request.reject(secret()));
    expect(text()).toContain("Plan memory is unavailable for this fingerprint");
    expect(text()).not.toContain("PRIVATE");
    await click("Retry plan memory");
    expect(text()).toContain("Consulted run fingerprint");
    expect(spy).toHaveBeenCalledTimes(2);
  });

  it("treats a memory response containing only the selected run as current context", async () => {
    vi.spyOn(repo, "shapeRuns").mockResolvedValue([{ ...fx.shapeRuns[0], job_id: row.job_id }]);
    await mount();
    expect(text()).toContain("The memory response contains only the selected run");
    expect(text()).toContain("not previous experience");
    expect(text()).not.toContain("Prior outcomes on this consulted shape");
  });

  it("lists only prior shape runs and discloses the consulted run fingerprint", async () => {
    const prior = { ...fx.shapeRuns[0], job_id: "prior-shape-run" };
    vi.spyOn(repo, "shapeRuns").mockResolvedValue([
      { ...fx.shapeRuns[1], job_id: row.job_id }, prior,
    ]);
    await mount();
    expect(text()).toContain("Consulted run fingerprint");
    expect(text()).toContain("does not establish it as the selected finding's shape");
    expect(text()).toContain("Prior outcomes on this consulted shape");
    expect(text()).toContain(prior.job_id.slice(-12));
    expect(text()).not.toContain(row.job_id.slice(-12));
  });

  it("does not call a missing run fingerprint an empty history", async () => {
    const selected = await repo.run(row.job_id);
    const memory = vi.spyOn(repo, "shapeRuns");
    vi.spyOn(repo, "run").mockResolvedValue({ ...selected!, plan_fingerprint: "" });
    await mount();
    expect(text()).toContain("The selected run has no plan fingerprint");
    expect(text()).toContain("did not query plan memory");
    expect(text()).not.toContain("no indexed runs for this fingerprint");
    expect(memory).not.toHaveBeenCalled();
  });

  it("keeps a successful empty run context distinct from a failed one", async () => {
    const memory = vi.spyOn(repo, "shapeRuns");
    vi.spyOn(repo, "run").mockResolvedValue(null);
    await mount();
    expect(text()).toContain("The run query returned no row for this selection");
    expect(text()).toContain("unknown rather than empty");
    expect(text()).not.toContain("run context is unavailable");
    expect(memory).not.toHaveBeenCalled();
  });

  it("keeps a successful empty shape-memory response distinct from a failed one", async () => {
    vi.spyOn(repo, "shapeRuns").mockResolvedValue([]);
    await mount();
    expect(text()).toContain("Plan memory returned no indexed runs for this fingerprint");
    expect(text()).not.toContain("Plan memory is unavailable");
    expect(text()).toContain("Proposed fix");
  });

  it("keeps B's shape context when a late A memory response settles", async () => {
    const fingerprintA = "a".repeat(64);
    const fingerprintB = "b".repeat(64);
    const pendingA = deferred<Awaited<ReturnType<FixtureRepository["shapeRuns"]>>>();
    const pendingB = deferred<Awaited<ReturnType<FixtureRepository["shapeRuns"]>>>();
    const selected = (await repo.run(row.job_id))!;
    const findingA = (await repo.findings(row.job_id)).find((f) => f.finding_id === row.finding_id)!;
    const findingB = { ...findingA, finding_id: "finding-B", job_id: "job-B" };
    vi.spyOn(repo, "run").mockImplementation(async (job) => ({
      ...selected, job_id: job, plan_fingerprint: job === "job-B" ? fingerprintB : fingerprintA,
    }));
    vi.spyOn(repo, "findings").mockImplementation(async (job) => job === "job-B" ? [findingB] : [findingA]);
    vi.spyOn(repo, "fixVerification").mockImplementation(async (finding) => finding === "finding-B"
      ? { ...row, job_id: "job-B", finding_id: "finding-B" }
      : row);
    const shapeSpy = vi.spyOn(repo, "shapeRuns").mockImplementation((fingerprint) =>
      fingerprint === fingerprintB ? pendingB.promise : pendingA.promise,
    );
    await mount();
    expect(shapeSpy).toHaveBeenCalledWith(fingerprintA);
    await act(async () => { await router.navigate("/verify?job=job-B&finding=finding-B"); });
    expect(shapeSpy).toHaveBeenCalledWith(fingerprintB);
    const priorB = { ...fx.shapeRuns[0], job_id: "prior-B-shape" };
    await act(async () => pendingB.resolve([priorB]));
    expect(text()).toContain(fingerprintB);
    expect(text()).toContain(priorB.job_id.slice(-12));
    const priorA = { ...fx.shapeRuns[1], job_id: "prior-A-shape" };
    await act(async () => pendingA.resolve([priorA]));
    expect(text()).toContain(fingerprintB);
    expect(text()).not.toContain(priorA.job_id.slice(-12));
  });
});
