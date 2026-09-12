import { useCallback, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Card, ConfidencePill, Diff, Label, Metric, Mono, Pill, Prose, SeverityBadge,
} from "@/components/atoms";
import { Button, DualVerdictPanel, GuardrailList, ScreenHeader, type Guardrail } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import {
  assessStage, fmt, measureNoiseFloorPct, noOpGate, parseProposal,
  readConfiguredPartitions, readSlots, ruleFiveSkewAbsence, ruleSevenReshaped,
  ruleTwoRuntimeResolvable,
} from "@/contract/rules";
import { useRepository, type AsyncState } from "@/data/useRepository";
import { useVerifyQuery } from "./useVerifyQuery";

function sourceGap(source: string, query: AsyncState<unknown>) {
  return query.loading ? { vacant: true as const, reason: `${source} loading — dependent check unavailable` }
    : query.error ? { vacant: true as const, reason: `${source} query failed — dependent check unavailable` }
    : null;
}

function SourceState({ source, query }: {
  source: string; query: AsyncState<unknown> & { retry: () => void };
}) {
  return <Page>
    <ScreenHeader title={query.loading ? `Loading ${source}…` : `${source[0].toUpperCase()}${source.slice(1)} data unavailable`} />
    <Card accent="withheld" className="px-4 py-3.5 flex flex-col gap-2">
      <Prose>{query.loading ? `Waiting for ${source}.` : `The ${source} query failed. No absence conclusion can be drawn.`}</Prose>
      {query.error && <Button onClick={query.retry}>Retry {source}</Button>}
    </Card>
  </Page>;
}

/**
 * The proposal, and the two verdicts on it.
 *
 * Each source has its own loading, failure and successful-empty state.
 * A successful empty result says nothing about why a verification row is absent.
 */
export function VerifyScreen() {
  const repo = useRepository();
  const [params] = useSearchParams();
  const [copied, setCopied] = useState(false);

  // Self-directing, like /compare: the nav link with no parameters lands on the
  // most recent run that carries a finding, and its highest-confidence one.
  const explicitJob = params.get("job") || null;
  const runsQ = useVerifyQuery(repo, "runs", () => repo.listRuns(50));
  const jobId = explicitJob
    ?? runsQ.data?.find((r) => r.finding_count > 0)?.job_id
    ?? "";

  const findingsQ = useVerifyQuery(repo, jobId,
    () => (jobId ? repo.findings(jobId) : Promise.resolve([])),
  );
  // FINDINGS is ordered by confidence_score DESC — the raw 0-1 the contract
  // routes on, never the coarse display tier.
  const explicitFinding = params.get("finding") || null;
  const findingId = explicitFinding ?? findingsQ.data?.[0]?.finding_id ?? "";
  const finding = findingsQ.data?.find((f) => f.finding_id === findingId && f.job_id === jobId) ?? null;

  const confQ = useVerifyQuery(repo, jobId, () => (jobId ? repo.jobConf(jobId) : Promise.resolve([])));
  const stagesQ = useVerifyQuery(repo, jobId, () => (jobId ? repo.stages(jobId) : Promise.resolve([])));
  const transQ = useVerifyQuery(repo, jobId, () => (jobId ? repo.transitions(jobId) : Promise.resolve([])));
  const fixQ = useVerifyQuery(repo, JSON.stringify([jobId, findingId]),
    () => (jobId && findingId ? repo.fixVerification(findingId) : Promise.resolve(null)),
  );

  const runQ = useVerifyQuery(repo, jobId, () => (jobId ? repo.run(jobId) : Promise.resolve(null)));
  const shapeQ = useVerifyQuery(repo, JSON.stringify([jobId, runQ.data?.plan_fingerprint]),
    () => {
      const fp = runQ.data?.plan_fingerprint;
      return fp ? repo.shapeRuns(fp) : Promise.resolve([]);
    },
  );
  const shapeRuns = shapeQ.data ?? [];
  // A shapeRuns response includes the selected run when the memory lane has
  // indexed it. It is context for this screen, not previous experience.
  const otherShapeRuns = shapeRuns.filter((r) => r.job_id !== jobId);

  const conf = confQ.data ?? [];
  const stages = stagesQ.data ?? [];
  const rowMismatch = fixQ.data !== null
    && (fixQ.data.finding_id !== findingId || fixQ.data.job_id !== jobId);
  const v = rowMismatch ? null : fixQ.data;
  // Through a ref: the button is declared in the same render as `v` and the
  // handler must not capture a stale one.
  const proposalRef = useRef<string>("");
  proposalRef.current = v?.proposed_diff ?? "";
  const copyProposal = useCallback(() => {
    const text = proposalRef.current;
    if (!text) return;
    // navigator.clipboard needs a secure context; localhost qualifies, an IP
    // over plain http does not. Failure is reported, never swallowed.
    void navigator.clipboard
      ?.writeText(text)
      .then(() => setCopied(true))
      .catch(() => setCopied(false));
  }, []);
  const stage = finding ? stages.find((s) => s.stage_id === finding.stage_id) ?? null : null;
  const configured = readConfiguredPartitions(conf);

  if (!explicitJob && (runsQ.loading || runsQ.error)) return <SourceState source="runs" query={runsQ} />;
  if (jobId && (findingsQ.loading || findingsQ.error)) return <SourceState source="findings" query={findingsQ} />;
  if (jobId && findingId && fixQ.loading && finding) return <SourceState source="verification" query={fixQ} />;

  if (fixQ.error && finding) {
    return (
      <Page>
        <ScreenHeader
          title="Verification data unavailable"
          subtitle={
            <>
              <Mono className="text-body2">{finding?.type ?? "selected finding"}</Mono> ·{" "}
              <Mono className="text-body2">{findingId}</Mono>
            </>
          }
        />
        <Card accent="finding" className="px-4 py-3.5 flex flex-col gap-2">
          <Label tone="finding">VERIFICATION QUERY FAILED</Label>
          <Prose>
            The verification query failed. No missing-row conclusion can be drawn from this
            response, and no proposal or verdict is available until the query succeeds.
          </Prose>
          <Prose size="xs" className="text-dim">
            Error details, response body and stack are withheld. Retry the data source before
            interpreting this finding.
          </Prose>
          <Button onClick={fixQ.retry}>Retry verification</Button>
        </Card>
      </Page>
    );
  }

  if (!finding) {
    return (
      <Page>
        <ScreenHeader title={!jobId ? "No run with findings in the last 50"
          : explicitFinding ? "Selected finding not found" : "No findings returned for this job"} />
        <Card accent="withheld" className="px-4 py-3.5">
          <Prose>
            {!jobId ? "No job could be selected from the returned runs."
              : explicitFinding ? <>Finding <Mono>{findingId}</Mono> was not returned for job <Mono>{jobId}</Mono>. This does not mean the job has no other findings.</>
              : <>The findings query returned no findings for job <Mono>{jobId}</Mono>.</>}
            {" "}Select a job and finding with <Mono>?job=&lt;id&gt;&amp;finding=&lt;id&gt;</Mono>.
          </Prose>
        </Card>
      </Page>
    );
  }

  if (rowMismatch) return <Page>
    <ScreenHeader title="Verification selection mismatch" />
    <Prose>The returned verification does not belong to this job and finding. No proposal or verdict is shown.</Prose>
    <Button onClick={fixQ.retry}>Retry verification</Button>
  </Page>;

  const confGap = sourceGap("configuration", confQ);
  const stagesGap = sourceGap("stages", stagesQ);
  const transGap = sourceGap("transitions", transQ);
  const missingStage = { vacant: true as const, reason: finding.stage_id < 0
    ? "this finding is job-level — no stage check applies"
    : "no stage row returned for this finding — stage check unavailable" };
  const dependencyNotices = <>
    {([
      ["configuration", confQ], ["stages", stagesQ], ["transitions", transQ],
    ] as const).filter(([, q]) => q.loading || q.error).map(([source, q]) => (
      <Card key={source} accent="withheld" className="p-3 flex flex-col gap-2">
        <Prose>{sourceGap(source, q)?.reason}</Prose>
        {q.error && <Button onClick={q.retry}>Retry {source}</Button>}
      </Card>
    ))}
  </>;

  // Every guardrail that does NOT need a verification row is computed from data
  // the console already has, so the gates stay visible even when the verify lane
  // has written nothing. The noise floor is the exception: it compares a
  // PREDICTED saving against a MEASURED floor, and both live on that row.
  const assessment = !stagesGap && !confGap && stage ? assessStage(stage, conf) : null;

  /**
   * The proposal, read off the row rather than typed into this screen.
   *
   * `apex.fix_verifications.proposed_config` is a conf overlay; the recorded
   * run predates that column and carries a unified diff. parseProposal names
   * each outcome, so only a complete valid overlay receives config checks.
   */
  const proposal = v ? parseProposal(v.proposed_diff) : null;
  const overlay = proposal?.kind === "overlay" ? proposal.config : null;
  const proposalKeys = overlay ? Object.keys(overlay) : [];
  const nonConfKeys = proposalKeys.filter((k) => !k.startsWith("spark."));

  const guardrails: Guardrail[] = [
    {
      name: "bound analysis",
      rule: "rule 1",
      // The real verdict for THIS stage, not a sentence about another one.
      verdict: stagesGap ?? confGap ?? assessment?.ruleOne ?? missingStage,
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
      verdict: confGap ?? (
        readSlots(conf) === null
          ? { vacant: true, reason: "spark.executor.instances absent from job_conf — no width is assumed" }
          : { held: true, reason: `${readSlots(conf)} slots resolved from job_conf` }),
    },
    {
      name: "reshape check",
      rule: "rule 7",
      verdict: stagesGap ?? confGap ?? (!stage ? missingStage :
        configured !== null
          ? ruleSevenReshaped(stage, configured)
          : { vacant: true, reason: "spark.sql.shuffle.partitions not captured — reshape undecidable" }),
    },
    {
      name: "skew absence",
      rule: "rule 5",
      verdict: transGap ?? ruleFiveSkewAbsence(transQ.data ?? []),
    },
    {
      name: "safety",
      rule: "policy",
      // ESTABLISHED, not asserted. "config-only change, no data path touched"
      // used to be a constant string printed beside every proposal, including
      // ones this console had never read. Every key in the overlay being a
      // spark.* conf key is something the console can actually check, and it
      // says whose check it is: verify's own `safe` / `safety_verdict` columns
      // are not selected by FIX_VERIFICATIONS, so this is not that lane's
      // verdict and must not borrow its authority.
      verdict: !v
        ? { vacant: true, reason: "no verification row — nothing proposed to check" }
        : !overlay
          ? {
              vacant: true,
              reason:
                "proposal is not a valid conf overlay; verify's own safe/safety_verdict " +
                "columns are not read by this console",
            }
          : nonConfKeys.length === 0
            ? {
                held: true,
                reason:
                  `local namespace check: ${proposalKeys.length} proposed ${proposalKeys.length === 1 ? "key is" : "keys are"} under spark.*. ` +
                  "This does not validate values, establish broader safety, and does not inspect data paths; " +
                  "verify's safe/safety_verdict columns are not read here",
              }
            : {
                held: false,
                reason: `proposal names a non-conf key: ${nonConfKeys.join(", ")}`,
              },
    },
  ];

  // The proposal itself lives on the verification row. Without one there is no
  // proposed config, so the no-op gate has nothing to gate and the noise floor
  // has no predicted saving to resolve — both are added only alongside `v`.
  const recomputedFloor = v ? measureNoiseFloorPct(v.replay_durations_ms) : null;
  const measured = v ? recomputedFloor ?? v.noise_floor_pct : null;
  if (v) {
    // ONE GATE PER PROPOSED KEY, each read off the row.
    //
    // This was `noOpGate(conf, "spark.sql.shuffle.partitions", "800")` — a key
    // and a value typed into this screen. It gated a proposal no lane had made,
    // so the gate could report a real change while the actual overlay was a
    // no-op, which is the one thing a no-op gate exists to catch.
    const gates: Guardrail[] = overlay
      ? Object.entries(overlay).map(([key, value]) => ({
          name: `no-op gate · ${key.replace(/^spark\.(sql\.)?/, "")}`,
          rule: "conf",
          verdict: confGap ?? noOpGate(conf, key, value),
        }))
      : [{
          name: "no-op gate",
          rule: "conf",
          verdict: {
            vacant: true,
            reason: "proposal is not a valid conf overlay — nothing to gate",
          },
        }];
    guardrails.unshift(...gates);
    guardrails.splice(gates.length + 1, 0, {
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
            The <Mono className="text-body2">apex.fix_verifications</Mono> query returned no row
            for this selection. No proposal or verdict is available. This successful empty response
            does not establish why the row is absent or whether processing is pending.
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

        {dependencyNotices}
        <GuardrailList items={guardrails} />
      </Page>
    );
  }

  return (
    <Page className="!py-0 !px-0">
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0 px-7 py-6 flex flex-col gap-4 border-r border-edge overflow-auto">
          {/* Was: title "Repartition the join input", finding id `f-7c41e9` and
              "confidence 0.94 >= 0.75" — the recorded run's proposal, its id and
              its score, printed over every row. The 0.75 was not a contract
              number either: the engine cuts tiers at 0.60 and 0.85 and gates
              escalation at 0.60, so no threshold is claimed here at all. */}
          <ScreenHeader
            title={`Proposed fix · ${finding.type}`}
            subtitle={
              <span className="flex items-center gap-2.5 flex-wrap">
                <span>
                  for <Mono className="text-body2">{finding.finding_id}</Mono> ·{" "}
                  {finding.stage_id < 0 ? "job-level" : `stage ${finding.stage_id}`}
                </span>
                <SeverityBadge severity={finding.severity} />
                <ConfidencePill
                  confidence={finding.confidence}
                  score={finding.confidence_score}
                />
              </span>
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

          {/* Rendered as WHAT IT IS. The header read "conf/spark-defaults.conf ·
              2 hunks" over both shapes — naming a file and a hunk count that the
              JSON overlay the live column actually stores does not have. */}
          <div className="bg-raised border border-edge rounded-sm overflow-hidden">
            <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-edge font-mono text-[11px] text-sub">
              <span>{
                proposal?.kind === "overlay" ? "proposed_config · valid JSON overlay"
                  : proposal?.kind === "diff" ? "proposed_diff · unified diff"
                    : proposal?.kind === "invalid-json" ? "proposed_config · invalid JSON"
                      : proposal?.kind === "invalid-overlay" ? "proposed_config · invalid overlay"
                        : "proposal · unknown format"
              }</span>
              <span className="text-muted">
                {overlay
                  ? `${proposalKeys.length} conf ${proposalKeys.length === 1 ? "key" : "keys"}`
                  : "original text shown verbatim"}
              </span>
            </div>
            <div className="p-3.5">
              {overlay ? (
                <div className="flex flex-col gap-1.5">
                  {Object.entries(overlay).map(([k, val]) => (
                    <Metric key={k} label={k} value={val} />
                  ))}
                </div>
              ) : (
                <Diff text={v.proposed_diff} />
              )}
              <pre aria-label="Original proposal" role="region" className="mt-3 overflow-x-auto whitespace-pre font-mono text-[11.5px] text-muted">
                {v.proposed_diff}
              </pre>
            </div>
          </div>

          <DualVerdictPanel v={v} />

          {dependencyNotices}
          <GuardrailList items={guardrails} />

          <div className="flex items-center justify-between gap-6 mt-auto pt-2">
            <Prose size="xs" className="text-dim max-w-[520px]">
              {proposal?.kind === "diff" ? (
                <>Apply it yourself: review this unified diff, then <Mono className="text-body">git apply</Mono>.</>
              ) : proposal?.kind === "overlay" ? (
                <>This is a configuration overlay, not a patch: copy the original proposal and apply its keys manually.</>
              ) : (
                <>This proposal format is not actionable here; inspect or copy the original text without executing it.</>
              )} The console never executes a proposal.
            </Prose>
            {/* `open PR body` and `replay again` are gone. The paragraph beside
                them says Apex "opens no PR" and the console is read-only by
                construction, so a button offering to open one contradicted the
                sentence it sat next to, and one offering to re-run the verify
                lane offered something this side cannot do. `copy diff` is the
                only one of the three the console can honestly perform, so it
                does — on the text already on screen. */}
            <div className="flex gap-2">
              <Button onClick={copyProposal}>{copied ? "original proposal copied ✓" : "copy original proposal"}</Button>
            </div>
          </div>
        </div>

        <aside className="w-[352px] shrink-0 bg-[#1a1d1e] px-5 py-6 flex flex-col gap-5 overflow-auto">
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <Label tone="memory">PLAN MEMORY</Label>
              <Mono className="text-[10px] text-muted">
                {runQ.loading ? "run context loading"
                  : runQ.error ? "run context unavailable"
                  : !runQ.data ? "run context returned no row"
                  : !runQ.data.plan_fingerprint ? "run has no fingerprint"
                  : shapeQ.loading ? "plan memory loading"
                  : shapeQ.error ? "plan memory unavailable"
                  : shapeRuns.length === 0 ? "no shape rows returned"
                  : otherShapeRuns.length === 0 ? "selected run only"
                  : `other indexed shape runs · ${otherShapeRuns.length}`}
              </Mono>
            </div>
            {runQ.loading ? (
              <Prose size="xs" className="text-dim">
                Loading the selected run context before consulting plan memory. The available
                proposal and verdicts remain independent of this sidebar source.
              </Prose>
            ) : runQ.error ? (
              <>
                <Prose size="xs" className="text-dim">
                  The selected run context is unavailable, so no plan fingerprint or history can be
                  stated. This is not an empty memory result.
                </Prose>
                <Button onClick={runQ.retry}>Retry run context</Button>
              </>
            ) : !runQ.data ? (
              <Prose size="xs" className="text-dim">
                The run query returned no row for this selection. No plan fingerprint was available
                to consult, so plan memory is unknown rather than empty.
              </Prose>
            ) : !runQ.data.plan_fingerprint ? (
              <Prose size="xs" className="text-dim">
                The selected run has no plan fingerprint. The sidebar did not query plan memory and
                does not infer a shape for this finding.
              </Prose>
            ) : (
              <>
                <Prose size="xs" className="text-dim">
                  Consulted run fingerprint <Mono>{runQ.data.plan_fingerprint}</Mono>. It is the
                  selected run&apos;s {runQ.data.shape_count > 1 ? "dominant-shape choice" : "run-level shape"};
                  this screen does not establish it as the selected finding&apos;s shape.
                </Prose>
                {shapeQ.loading ? (
                  <Prose size="xs" className="text-dim">
                    Loading plan memory for this fingerprint. No history conclusion is available yet.
                  </Prose>
                ) : shapeQ.error ? (
                  <>
                    <Prose size="xs" className="text-dim">
                      Plan memory is unavailable for this fingerprint. The failed request is not an
                      empty history.
                    </Prose>
                    <Button onClick={shapeQ.retry}>Retry plan memory</Button>
                  </>
                ) : shapeRuns.length === 0 ? (
                  <Prose size="xs" className="text-dim">
                    Plan memory returned no indexed runs for this fingerprint. That successful empty
                    response does not identify a shape for this finding.
                  </Prose>
                ) : otherShapeRuns.length === 0 ? (
                  <Prose size="xs" className="text-dim">
                    The memory response contains only the selected run. It is current context, not
                    other run context, so there are no other indexed outcomes to show.
                  </Prose>
                ) : (
                  <>
                    <Prose>Other indexed outcomes on this consulted shape, not opinions:</Prose>
                    {otherShapeRuns.slice(0, 4).map((r) => (
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
              {/* Three colours were fixed here: mechanism green, certified red,
                  verdict amber — regardless of the values. On the live store
                  mechanism_confirmed is null, so "null" rendered in the green of
                  a confirmed mechanism. */}
              <div>
                <span className="text-dim">mechanism_confirmed</span>{" "}
                <span className={
                  v.mechanism_confirmed === null ? "text-withheld"
                  : v.mechanism_confirmed ? "text-certified" : "text-finding"
                }>
                  {fmt.verdict(v.mechanism_confirmed)}
                </span>
              </div>
              <div>
                <span className="text-dim">runtime_certified</span>{" "}
                <span className={v.runtime_certified ? "text-certified" : "text-withheld"}>
                  {String(v.runtime_certified)}
                </span>
              </div>
              <div>
                <span className="text-dim">runtime_verdict</span>{" "}
                <span className={
                  v.runtime_verdict === "unresolved" ? "text-withheld"
                  : v.runtime_verdict === "improved" ? "text-certified" : "text-finding"
                }>
                  {v.runtime_verdict}
                </span>
              </div>
              {/* The label used to read "(measured, not stored)" on BOTH paths.
                  Against the live store the replay durations are never stored,
                  so it is always the fallback that is on screen. */}
              <div>
                <span className="text-dim">noise_floor_pct</span> {fmt.pctOrDash(measured)}{" "}
                <span className="text-muted">
                  ({recomputedFloor !== null ? "measured here from the replays" : "as verify stored it"})
                </span>
              </div>
              <div><span className="text-dim">replays</span> {v.replay_count} per arm</div>
              <div>
                <span className="text-dim">cluster_slots</span>{" "}
                <span className="text-muted">{v.cluster_slots ?? "not captured"}</span>
              </div>
            </div>
            <Prose size="xs" className="text-dim">
              The mechanism field and runtime evidence remain separate claims. Neither is inferred
              from the other, and the runtime query does not attribute a measured change to this proposal.
            </Prose>
          </div>
        </aside>
      </div>
    </Page>
  );
}
