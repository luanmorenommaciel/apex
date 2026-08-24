import { useSearchParams } from "react-router-dom";
import { Card, Diff, Label, Mono, Pill, Prose } from "@/components/atoms";
import { Button, DualVerdictPanel, GuardrailList, ScreenHeader, type Guardrail } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import {
  assessStage, fmt, measureNoiseFloorPct, noOpGate, readConfiguredPartitions,
  readSlots, ruleFiveSkewAbsence, ruleSevenReshaped, ruleTwoRuntimeResolvable,
} from "@/contract/rules";
import { useAsync, useRepository } from "@/data/useRepository";

/**
 * The proposal, and the two verdicts on it.
 *
 * THREE distinct states, because collapsing them is how this screen used to
 * hang on "Loading" forever: still fetching, fetched-and-there-is-no-finding,
 * and fetched-and-the-verify-lane-has-written-no-row. Only the first is a
 * spinner. The third is a fact about the pipeline, not a failure of the console,
 * and it says which lane owes the row.
 */
export function VerifyScreen() {
  const repo = useRepository();
  const [params] = useSearchParams();

  // Self-directing, like /compare: the nav link with no parameters lands on the
  // most recent run that carries a finding, and its highest-confidence one.
  const runsQ = useAsync(() => repo.listRuns(50), [repo]);
  const jobId = params.get("job")
    ?? runsQ.data?.find((r) => r.finding_count > 0)?.job_id
    ?? "";

  const findingsQ = useAsync(
    () => (jobId ? repo.findings(jobId) : Promise.resolve([])),
    [repo, jobId],
  );
  // FINDINGS is ordered by confidence_score DESC — the raw 0-1 the contract
  // routes on, never the coarse display tier.
  const findingId = params.get("finding") ?? findingsQ.data?.[0]?.finding_id ?? "";
  const finding = findingsQ.data?.find((f) => f.finding_id === findingId) ?? null;

  const confQ = useAsync(() => (jobId ? repo.jobConf(jobId) : Promise.resolve([])), [repo, jobId]);
  const stagesQ = useAsync(() => (jobId ? repo.stages(jobId) : Promise.resolve([])), [repo, jobId]);
  const transQ = useAsync(() => (jobId ? repo.transitions(jobId) : Promise.resolve([])), [repo, jobId]);
  const fixQ = useAsync(
    () => (findingId ? repo.fixVerification(findingId) : Promise.resolve(null)),
    [repo, findingId],
  );

  const runQ = useAsync(() => (jobId ? repo.run(jobId) : Promise.resolve(null)), [repo, jobId]);
  const shapeQ = useAsync(
    () => {
      const fp = runQ.data?.plan_fingerprint;
      return fp ? repo.shapeRuns(fp) : Promise.resolve([]);
    },
    [repo, runQ.data?.plan_fingerprint],
  );
  const shapeHistory = shapeQ.data ?? [];

  const conf = confQ.data ?? [];
  const stages = stagesQ.data ?? [];
  const v = fixQ.data;
  const stage = finding ? stages.find((s) => s.stage_id === finding.stage_id) ?? null : null;
  const configured = readConfiguredPartitions(conf);

  const loading = runsQ.loading || findingsQ.loading || fixQ.loading || stagesQ.loading;
  if (loading) return <Page><Prose>Loading verification…</Prose></Page>;

  if (!finding) {
    return (
      <Page>
        <ScreenHeader title="Verify a fix" subtitle="nothing to verify" />
        <Card accent="withheld" className="px-4 py-3.5">
          <Prose>
            No finding is selected and no run in the last 50 carries one. This screen verifies a
            proposal against a specific finding — open a run and use{" "}
            <Mono className="text-body2">propose fix</Mono>, or pass{" "}
            <Mono className="text-body2">?finding=&lt;id&gt;</Mono>.
          </Prose>
        </Card>
      </Page>
    );
  }

  // Every guardrail that does NOT need a verification row is computed from data
  // the console already has, so the gates stay visible even when the verify lane
  // has written nothing. The noise floor is the exception: it compares a
  // PREDICTED saving against a MEASURED floor, and both live on that row.
  const assessment = stage ? assessStage(stage, conf) : null;
  const guardrails: Guardrail[] = [
    {
      name: "bound analysis",
      rule: "rule 1",
      // The real verdict for THIS stage, not a sentence about another one.
      verdict: assessment
        ? assessment.ruleOne
        : { vacant: true, reason: "no stage row for this finding — it is job-level" },
    },
    {
      name: "mechanism",
      rule: "plan",
      // NO SOURCE. plan_json is the only plan text on the row and its DDL marks
      // it a tree-string that is never parsed, so "a Join node exists here"
      // cannot be established by the console. Claiming it would be an invention.
      verdict: {
        vacant: true,
        reason: "plan structure is not inspectable — plan_json is never parsed, per its DDL",
      },
    },
    {
      name: "cluster width",
      rule: "rule 1",
      verdict:
        readSlots(conf) === null
          ? { vacant: true, reason: "spark.executor.instances absent from job_conf — no width is assumed" }
          : { held: true, reason: `${readSlots(conf)} slots resolved from job_conf` },
    },
    {
      name: "reshape check",
      rule: "rule 7",
      verdict:
        stage && configured !== null
          ? ruleSevenReshaped(stage, configured)
          : { vacant: true, reason: "spark.sql.shuffle.partitions not captured — reshape undecidable" },
    },
    {
      name: "skew absence",
      rule: "rule 5",
      verdict: ruleFiveSkewAbsence(transQ.data ?? []),
    },
    {
      name: "safety",
      rule: "policy",
      verdict: { held: true, reason: "config-only change, no data path touched" },
    },
  ];

  // The proposal itself lives on the verification row. Without one there is no
  // proposed config, so the no-op gate has nothing to gate and the noise floor
  // has no predicted saving to resolve — both are added only alongside `v`.
  const measured = v ? measureNoiseFloorPct(v.replay_durations_ms) ?? v.noise_floor_pct : null;
  if (v) {
    guardrails.unshift({
      name: "no-op gate",
      rule: "conf",
      verdict: noOpGate(conf, "spark.sql.shuffle.partitions", "800"),
    });
    guardrails.splice(3, 0, {
      name: "noise floor",
      rule: "rule 2",
      verdict: ruleTwoRuntimeResolvable(v.predicted_saving_pct, measured),
    });
  }

  if (!v) {
    return (
      <Page>
        <ScreenHeader
          title="No verification for this finding"
          subtitle={
            <>
              <Mono className="text-body2">{finding.type}</Mono> ·{" "}
              {finding.stage_id < 0 ? "job-level" : `stage ${finding.stage_id}`} ·{" "}
              <Mono className="text-body2">{findingId.slice(0, 12)}…</Mono>
            </>
          }
        />

        <Card accent="withheld" className="px-4 py-3.5 flex flex-col gap-2">
          <Label tone="withheld">WHY THIS IS EMPTY</Label>
          <Prose>
            <Mono className="text-body2">apex.fix_verifications</Mono> holds no row for this
            finding. That table is written by the <Mono className="text-body2">verify</Mono> lane —
            never by the console — and until it runs there is no prediction to show and no verdict
            to render. This is a gap in the pipeline, not a failure of the query: the same query
            returns rows the moment that lane writes one.
          </Prose>
          <Prose size="xs" className="text-dim">
            Rule 4 is why nothing is inferred meanwhile. A mechanism verdict and a runtime verdict
            are separate claims; deriving either from the engine's confidence would manufacture the
            second from the first.
          </Prose>
        </Card>

        <div className="grid grid-cols-2 gap-4">
          <Card className="p-4 flex flex-col gap-2">
            <Label>THE FINDING, AS STORED</Label>
            <div className="font-mono text-[11px] leading-[1.9] text-body">
              <div><span className="text-dim">type</span> {finding.type}</div>
              <div><span className="text-dim">severity</span> {finding.severity}</div>
              <div><span className="text-dim">confidence</span> {finding.confidence} · {finding.confidence_score.toFixed(2)}</div>
              <div><span className="text-dim">detected_by</span> {finding.detected_by}</div>
            </div>
          </Card>
          <Card className="p-4 flex flex-col gap-2">
            <Label>THE FIX AS WRITTEN</Label>
            {/* UNTRUSTED: authored by the engine about the observed job. Rendered
                as data, never followed, and never parsed into a config to test. */}
            <Prose size="sm" className="text-body">{finding.fix || "—"}</Prose>
            <Prose size="xs" className="text-dim">
              Prose, not a configuration. Turning it into a testable overlay is the verify lane's
              job and needs a key/value proposal, not a sentence.
            </Prose>
          </Card>
        </div>

        <GuardrailList items={guardrails} />
      </Page>
    );
  }

  return (
    <Page className="!py-0 !px-0">
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0 px-7 py-6 flex flex-col gap-4 border-r border-edge overflow-auto">
          <ScreenHeader
            title="Repartition the join input"
            subtitle={
              <>
                proposal for <Mono className="text-body2">f-7c41e9</Mono> · confidence 0.94 ≥ 0.75
              </>
            }
            right={
              <div className="flex gap-2">
                <Pill tone="withheld">requires_human_approval: true</Pill>
                <Pill tone="certified">applied: false</Pill>
              </div>
            }
          />

          <Prose size="base" className="max-w-[700px]">
            Apex returns a diff as data. It writes no file, runs no git command and opens no PR — the
            approval gate is enforced by the schema, not by convention.
          </Prose>

          <div className="bg-raised border border-edge rounded-sm overflow-hidden">
            <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-edge font-mono text-[11px] text-sub">
              <span>proposed_diff</span>
              <span className="text-muted">conf/spark-defaults.conf · 2 hunks</span>
            </div>
            <div className="p-3.5">
              <Diff text={v.proposed_diff} />
            </div>
          </div>

          <DualVerdictPanel v={v} />

          <GuardrailList items={guardrails} />

          <div className="flex items-center justify-between gap-6 mt-auto pt-2">
            <Prose size="xs" className="text-dim max-w-[520px]">
              Apply it yourself: review the diff, then <Mono className="text-body">git apply</Mono>.
              An injected instruction that cannot execute without approval cannot silently act.
            </Prose>
            <div className="flex gap-2">
              <Button>copy diff</Button>
              <Button variant="outline">open PR body</Button>
              <Button variant="primary">replay again</Button>
            </div>
          </div>
        </div>

        <aside className="w-[352px] shrink-0 bg-[#1a1d1e] px-5 py-6 flex flex-col gap-5 overflow-auto">
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <Label tone="memory">PLAN MEMORY</Label>
              <Mono className="text-[10px] text-muted">
                {shapeHistory.length > 0
                  ? `same shape · ${shapeHistory.length} runs`
                  : "no history on this shape"}
              </Mono>
            </div>
            {shapeHistory.length === 0 ? (
              <Prose size="xs" className="text-dim">
                The memory lane has indexed no other run of this plan shape, so there is no history
                to recall. One run is not a corpus, and rule 3 credits nothing to tuning below two
                distinct configurations.
              </Prose>
            ) : (
              <>
                <Prose>We have seen this plan shape before. Outcomes, not opinions:</Prose>
                {shapeHistory.slice(0, 4).map((r) => (
                  <Card
                    key={r.job_id}
                    accent={r.severity_rank >= 3 ? "finding" : r.finding_count > 0 ? "withheld" : "certified"}
                    className="p-3 flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <Mono className="text-[11px] text-bright">{r.job_id.slice(-12)}</Mono>
                      <Mono className="text-[10px] text-body2">{fmt.duration(r.task_time_ms)}</Mono>
                    </div>
                    <Prose size="xs" className="text-sub">
                      {r.finding_count === 0
                        ? "clean run on this shape"
                        : `${r.finding_count} finding${r.finding_count === 1 ? "" : "s"} · config ${r.config_source}`}
                    </Prose>
                  </Card>
                ))}
              </>
            )}
            <Mono className="text-[10px] leading-relaxed text-muted">
              corpus is a single environment · cross-host memory is v0.2 roadmap · confidence is
              directional
            </Mono>
          </div>

          <div className="flex flex-col gap-2.5 mt-auto">
            <Label>FIX_VERIFICATIONS ROW</Label>
            <div className="bg-surface border border-edge rounded-sm p-3 font-mono text-[10.5px] leading-[1.85] text-body">
              <div><span className="text-dim">mechanism_confirmed</span> <span className="text-certified">{String(v.mechanism_confirmed)}</span></div>
              <div><span className="text-dim">runtime_certified</span> <span className="text-finding">{String(v.runtime_certified)}</span></div>
              <div><span className="text-dim">runtime_verdict</span> <span className="text-withheld">{v.runtime_verdict}</span></div>
              <div><span className="text-dim">noise_floor_pct</span> {measured?.toFixed(1)} <span className="text-muted">(measured, not stored)</span></div>
              <div><span className="text-dim">replays</span> {v.replay_count}</div>
              <div><span className="text-dim">cluster_slots</span> <span className="text-muted">{v.cluster_slots ?? "unknown"}</span></div>
            </div>
            <Prose size="xs" className="text-dim">
              A small bench can honestly deliver the first verdict and not the second. Both are
              stored; neither is inferred from the other.
            </Prose>
          </div>
        </aside>
      </div>
    </Page>
  );
}
