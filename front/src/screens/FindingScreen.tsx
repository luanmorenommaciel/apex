import { Link, useParams } from "react-router-dom";
import {
  Bar, Card, ConfidencePill, FLOOR_PX, KeyValue, Label, Mono, Pill, Prose, SeverityBadge,
} from "@/components/atoms";
import { ScreenHeader } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import {
  assessStage, fmt, noOpGate, parseProposal, ratioOf, TAIL_SAMPLE,
  VOLUME_FLOOR_BYTES_PER_TASK,
} from "@/contract/rules";
import { attributionIsAvailable } from "@/contract/rules";
import { CONTRACT_VERSION } from "@/contract/types";
import { useAsync, useRepository } from "@/data/useRepository";

/** UNTRUSTED per the contract: written by the observed job, rendered as data. */
const UNTRUSTED = ["evidence", "impact", "fix", "hot_key", "plan_transitions[].detail"];

export function FindingScreen() {
  const { jobId = "", findingId = "" } = useParams();
  const repo = useRepository();

  const findingsQ = useAsync(() => repo.findings(jobId), [repo, jobId]);
  const stagesQ = useAsync(() => repo.stages(jobId), [repo, jobId]);
  const confQ = useAsync(() => repo.jobConf(jobId), [repo, jobId]);
  const transQ = useAsync(() => repo.transitions(jobId), [repo, jobId]);

  // The verification row carries the only PROPOSAL the contract stores, and
  // the shape history is what plan memory actually knows about this run. Both
  // used to be prose typed into this screen.
  const fixQ = useAsync(() => repo.fixVerification(findingId), [repo, findingId]);

  const finding = (findingsQ.data ?? []).find((f) => f.finding_id === findingId);
  const stages = stagesQ.data ?? [];
  const conf = confQ.data ?? [];
  const transitions = transQ.data ?? [];

  const fingerprint = stages.find((s) => s.plan_fingerprint)?.plan_fingerprint ?? "";
  const shapeQ = useAsync(
    () => (fingerprint ? repo.shapeRuns(fingerprint) : Promise.resolve([])),
    [repo, fingerprint],
  );

  if (findingsQ.loading) return <Page><Prose>Loading finding…</Prose></Page>;
  if (!finding) return <Page><Prose>No finding <Mono>{findingId}</Mono>.</Prose></Page>;

  const shapeHistory = shapeQ.data ?? [];
  const v = fixQ.data;
  const proposal = v ? parseProposal(v.proposed_diff) : null;

  // The AQE transition is only THIS finding's ground truth when this finding is
  // the AQE one. `transitions[0]` was rendered under that heading for every
  // finding, including a SPILL that no re-plan produced.
  const transition = finding.type === "AQE_REPLAN" ? transitions[0] : undefined;

  const ranked = [...stages].sort((a, b) => ratioOf(b) - ratioOf(a)).slice(0, TAIL_SAMPLE);
  const rankedAssessed = ranked.map((s) => ({ s, a: assessStage(s, conf) }));
  // "zero were reported as skew" was a constant. This is the count.
  const rankedWithFinding = ranked.filter((s) =>
    (findingsQ.data ?? []).some((f) => f.stage_id === s.stage_id),
  ).length;
  // A stage that CLEARS the volume floor and is still excluded is the sharpest
  // illustration of rule 6, so the caption names whichever one that is — it
  // used to name stage 11 unconditionally.
  const clearsFloorButExcluded = rankedAssessed.find(
    ({ a }) => a.aboveVolumeFloor && a.refusal?.code === "not_a_distribution",
  );

  return (
    <Page>
      <ScreenHeader
        title={
          <span className="flex items-center gap-2.5">
            {finding.type}
            {finding.stage_id < 0 && <Pill tone="withheld">stage_id −1 · job-level</Pill>}
          </span>
        }
        subtitle={
          <span className="flex items-center gap-2.5">
            <Link to={`/runs/${jobId}`}>{fmt.shortJob(jobId)}</Link>
            <span className="text-edge2">/</span>
            <Mono>{finding.finding_id}</Mono>
            <SeverityBadge severity={finding.severity} />
            {/* Was a hardcoded `certified` (green) pill: a LOW-confidence
                finding wore the colour of a passed check. */}
            <ConfidencePill confidence={finding.confidence} score={finding.confidence_score} />
          </span>
        }
      />

      <div className="flex gap-5 flex-1 min-h-0">
        <div className="flex-1 min-w-0 flex flex-col gap-4 overflow-auto pr-1">
          {/* One paragraph used to assert AQE provenance for EVERY finding: a
              SPILL raised by the memory watcher was described as Spark's own
              re-planning decision, captured from a listener that had nothing to
              do with it. The claim is now made only for the type that has it.
              The version is read from the contract module too — this said v0.4,
              and promised a map "in v0.5" that v0.5 does not carry. */}
          <Prose size="base" className="max-w-[760px]">
            {finding.type === "AQE_REPLAN" ? (
              <>
                This finding is not a heuristic. It is Spark&rsquo;s own runtime re-planning
                decision, captured from{" "}
                <Mono className="text-body2">SparkListenerSQLAdaptiveExecutionUpdate</Mono> and
                diffed per execution.
              </>
            ) : (
              <>
                Raised by <Mono className="text-body2">{finding.detected_by}</Mono> over the
                contract rows for this run. Everything below is the stored row and what this
                console can derive from it; no part of the verdict is re-decided here.
              </>
            )}{" "}
            {finding.stage_id < 0 && (
              <>
                It sits at job level because contract v{CONTRACT_VERSION} keys transitions by{" "}
                <Mono className="text-body2">(job_id, execution_id)</Mono> and carries no
                execution→stage map. Attributing it to a stage would be a fabrication
                {!attributionIsAvailable() && ", and that map is still not in the contract"}.
              </>
            )}
          </Prose>

          <div className="grid grid-cols-2 gap-3.5">
            <Card className="p-4 flex flex-col gap-2.5">
              <Label>{transition ? "GROUND TRUTH CAPTURED" : "AQE TRANSITION LOG"}</Label>
              {transition ? (
                <div className="flex flex-col gap-1.5 font-mono text-xs">
                  <div className="flex justify-between"><span className="text-sub">transition_type</span><span className="text-withheld">{transition.transition_type}</span></div>
                  <div className="flex justify-between"><span className="text-sub">execution_id</span><span className="text-body2">{transition.execution_id}</span></div>
                  <div className="flex justify-between"><span className="text-sub">detail</span><span className="text-body2">{transition.detail}</span></div>
                  <div className="flex justify-between"><span className="text-sub">before → after</span><span className="text-body2">{transition.before} → {transition.after}</span></div>
                  <div className="flex justify-between"><span className="text-sub">confidence</span><span className="text-certified">{transition.confidence}</span></div>
                </div>
              ) : (
                <Prose size="sm" className="text-sub">
                  {transitions.length === 0
                    ? "Spark logged no AQE re-plan for this run at all."
                    : `${transitions.length} re-plan${transitions.length === 1 ? " was" : "s were"} logged for this run, but none is this finding's evidence: contract v${CONTRACT_VERSION} carries no execution→stage map, so a transition cannot be tied to a ${finding.type} on a stage.`}
                </Prose>
              )}
              <Prose size="xs" className="text-dim">
                {/* Was "Cost to produce: $0. No LLM was called for this finding."
                    Nothing in the contract counts model invocations, so that was
                    a claim this console had no row to support. */}
                No contract table counts model invocations, so no LLM cost is
                claimed for this finding.
              </Prose>
            </Card>

            <Card className="p-4 flex flex-col gap-2.5">
              <Label>THE NO-OP GATE</Label>
              <div className="font-mono text-xs leading-[1.75] text-body">
                <div>captured job_conf ({conf.length} keys):</div>
                {conf
                  .filter((c) => c.key.includes("adaptive"))
                  .map((c) => (
                    <div key={c.key} className="text-body2">
                      {c.key.replace("spark.sql.", "")} ={" "}
                      <span className={c.value === "true" ? "text-certified" : "text-body2"}>
                        {c.value}
                      </span>
                      {/* Printed beside skewJoin.enabled whatever its value —
                          including `false`, where "already on" is backwards. */}
                      {c.key.endsWith("skewJoin.enabled") && c.value === "true" && (
                        <span className="text-withheld"> ← already on</span>
                      )}
                    </div>
                  ))}
                {/* Rendered only when the key really is missing. Unconditional,
                    it printed "absent" for a run that had emitted the value. */}
                {!conf.some((c) => c.key === "spark.executor.instances") && (
                  <div className="text-body2">
                    spark.executor.instances = <span className="text-finding">absent</span>
                  </div>
                )}
              </div>
              {/* The gate now runs over the PROPOSAL the verify lane stored, key
                  by key. It used to gate one key and one value written into this
                  screen — skewJoin.enabled -> true — which gates a proposal no
                  lane had necessarily made. */}
              {proposal ? (
                <div className="flex flex-col gap-1">
                  {Object.entries(proposal).map(([k, val]) => (
                    <Prose key={k} size="xs" className="text-sub">
                      <Mono className="text-dim">{k}</Mono> — {noOpGate(conf, k, val).reason}
                    </Prose>
                  ))}
                </div>
              ) : (
                <Prose size="xs" className="text-sub">
                  Nothing to gate:{" "}
                  <Mono className="text-body2">apex.fix_verifications</Mono>{" "}
                  {v
                    ? "carries no readable conf overlay for this finding"
                    : "holds no row for this finding"}
                  , and the fix below is prose rather than a testable set of keys.
                </Prose>
              )}
            </Card>
          </div>

          {/* The STORED fix, not a sentence about the recorded run's fix. It is
              UNTRUSTED — authored by the engine about the observed job — so it is
              rendered as data and never parsed into something to run. */}
          <Card accent={finding.fix ? "certified" : "withheld"} className="p-4 flex flex-col gap-2">
            <Label>FIX AS WRITTEN</Label>
            <div className="font-mono text-sm text-bright">
              {finding.fix || "No fix text was stored with this finding."}
            </div>
            <Prose size="xs" className="text-sub">
              Prose, not a configuration. Turning it into a testable overlay is the verify
              lane&rsquo;s job — and rule 5 means a quiet transition log licenses no claim either
              way in the meantime.
            </Prose>
          </Card>

          <Card className="p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <Label tone="withheld">WHY THE LOUDEST NUMBER IS NOT HERE</Label>
              {/* "zero were reported as skew" was a constant beside a count. */}
              <span className="text-xs text-dim">
                the {ranked.length} loudest p99/p50 ratios ·{" "}
                {rankedWithFinding === 0
                  ? "none produced a finding"
                  : `${rankedWithFinding} produced a finding`}
              </span>
            </div>
            <div className="flex gap-5">
              <div className="w-[330px] shrink-0 flex flex-col gap-2">
                <div className="relative bg-surface border border-edge rounded-sm p-3 h-[150px]">
                  <div
                    className="absolute left-3 right-3 border-t border-dashed border-withheld"
                    style={{ bottom: FLOOR_PX + 18 }}
                  />
                  <div className="absolute right-3.5 font-mono text-[9px] text-withheld" style={{ bottom: FLOOR_PX + 22 }}>
                    1 MiB/task floor
                  </div>
                  <div className="h-full flex items-end gap-4 pb-[18px]">
                    {rankedAssessed.map(({ s, a }) => (
                      <Bar
                        key={s.stage_id}
                        bytesPerTask={a.bytesPerTask}
                        tone={a.refusal?.code === "post_intervention" ? "withheld" : "refused"}
                        label={String(s.stage_id)}
                      />
                    ))}
                  </div>
                </div>
                {/* Named stage 11 and "2 tasks" unconditionally. The caption now
                    finds whichever stage actually demonstrates the point, and
                    says something weaker when none does. */}
                <Prose size="xs" className="text-dim">
                  Bar height is bytes/task on a log scale.{" "}
                  {clearsFloorButExcluded ? (
                    <>
                      Stage {clearsFloorButExcluded.s.stage_id} clears the floor but has{" "}
                      {clearsFloorButExcluded.s.task_count} tasks — rule 6 makes rule 1 vacant, so
                      the stage is excluded, not cleared.
                    </>
                  ) : (
                    <>
                      A bar above the line is not a claim: rule 6 excludes a stage whose task count
                      cannot describe a distribution, whatever its volume.
                    </>
                  )}
                </Prose>
              </div>

              <div className="flex-1 min-w-0 flex flex-col gap-2.5">
                {rankedAssessed.slice(0, 2).map(({ s, a }) => {
                  return (
                    <Prose key={s.stage_id}>
                      <Mono className="text-bright">stage {s.stage_id} · {fmt.ratio(a.ratio)}</Mono> —{" "}
                      {a.refusal?.text}
                      {a.caveat && <span className="text-withheld"> {a.caveat}</span>}
                    </Prose>
                  );
                })}
                <Prose className="text-sub">
                  The floor is a measurability bound, not a tunable threshold — and it is shared
                  verbatim by engine, verify and serve so no two lanes can disagree about which
                  stages a ratio may describe. Rule 7 is the remedy for the near-miss: a reshaped
                  stage is detected by comparing task_count against{" "}
                  <Mono className="text-body2">spark.sql.shuffle.partitions</Mono>, so the console can
                  say the floor measured a healed state. Softening the floor would not.
                </Prose>
                <div className="mt-auto font-mono text-[10px] text-muted">
                  contract rule 7 · floor = {VOLUME_FLOOR_BYTES_PER_TASK.toLocaleString()} B/task
                </div>
              </div>
            </div>
          </Card>
        </div>

        <aside className="w-[330px] shrink-0 flex flex-col gap-5 overflow-auto">
          <div className="flex flex-col gap-2.5">
            <Label>ROW AS STORED</Label>
            <div className="bg-surface border border-edge rounded-sm p-3">
              <KeyValue k="finding_id" v={finding.finding_id} />
              <KeyValue k="job_id" v={fmt.shortJob(finding.job_id)} />
              <KeyValue k="stage_id" v={<span className="text-withheld">{finding.stage_id}</span>} />
              <KeyValue k="type" v={finding.type} />
              <KeyValue k="severity" v={finding.severity} />
              <KeyValue k="confidence" v={finding.confidence} />
              <KeyValue k="confidence_score" v={finding.confidence_score.toFixed(2)} />
              <KeyValue k="detected_by" v={finding.detected_by} />
              {/* Was the literal string `""`, so a finding that named a hot key
                  showed none. */}
              <KeyValue
                k="hot_key"
                v={finding.hot_key
                  ? <span className="text-body2">{finding.hot_key}</span>
                  : <span className="text-muted">not set</span>}
              />
            </div>
          </div>

          <div className="flex flex-col gap-2.5">
            <Label tone="finding">UNTRUSTED FIELDS</Label>
            <div className="font-mono text-[11px] leading-[1.9] text-body">
              {UNTRUSTED.map((f) => <div key={f}>{f}</div>)}
            </div>
            <Prose size="xs" className="text-dim">
              Written by the observed Spark job, not by Apex. Rendered as data — never evaluated,
              never re-emitted as instructions.
            </Prose>
          </div>

          {/* Was "7 runs · same fingerprint" over two sentences about salting a
              join key and raising skewedPartitionFactor — an outcome history
              this console had never queried, printed beside every finding. */}
          <Card
            accent={shapeHistory.length > 0 ? "memory" : "withheld"}
            className="p-3 flex flex-col gap-1.5"
          >
            <Mono className="text-xs text-memory">
              {shapeHistory.length > 0
                ? `${shapeHistory.length} run${shapeHistory.length === 1 ? "" : "s"} · same fingerprint`
                : "no history on this shape"}
            </Mono>
            <Prose size="xs" className="text-sub">
              {shapeHistory.length === 0 ? (
                <>
                  <Mono className="text-body2">apex.run_outcomes</Mono> holds no run of this plan
                  shape, so there is nothing to recall — and rule 3 credits nothing to tuning below
                  two distinct configurations.
                </>
              ) : (
                <>
                  {shapeHistory.filter((r) => r.finding_count === 0).length} of them ran clean, and
                  configuration was captured on{" "}
                  {shapeHistory.filter((r) => r.config_source !== "unknown").length} of them — which
                  is all rule 3 has to reason over. <Link to="/memory">Open plan memory</Link>.
                </>
              )}
            </Prose>
            <Mono className="text-[10px] text-muted">
              single-environment corpus · magnitude uncertain
            </Mono>
          </Card>
        </aside>
      </div>
    </Page>
  );
}
