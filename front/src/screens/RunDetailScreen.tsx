import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  ConfidencePill, Diff, Label, Metric, Mono, Pill, Prose, SeverityBadge, StatusPill,
} from "@/components/atoms";
import {
  Button, LayerTabs, RefusalTable, SignalStrip, StageNode, WithheldPanel,
  type Layer, type NodeTone, type Withholding,
} from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import {
  assessStage, breakEvenSlots, fmt, isVacant, measureNoiseFloorPct, parseProposal, ratioOf,
  readSlots, ruleFiveSkewAbsence, ruleTwoRuntimeResolvable, TAIL_SAMPLE,
} from "@/contract/rules";
import { severityRank } from "@/contract/types";
import { useAsync, useRepository } from "@/data/useRepository";

export function RunDetailScreen() {
  const { jobId = "" } = useParams();
  const repo = useRepository();
  const navigate = useNavigate();
  const [layer, setLayer] = useState<Layer>("stages");
  // null = "the screen has not been told", so the default can follow the DATA.
  // It was `useState(25)` — a stage id from the recorded run, which on any other
  // run selected nothing and silently fell through to stages[0].
  const [picked, setPicked] = useState<number | null>(null);

  const runQ = useAsync(() => repo.run(jobId), [repo, jobId]);
  const stagesQ = useAsync(() => repo.stages(jobId), [repo, jobId]);
  const confQ = useAsync(() => repo.jobConf(jobId), [repo, jobId]);
  const findingsQ = useAsync(() => repo.findings(jobId), [repo, jobId]);
  const transQ = useAsync(() => repo.transitions(jobId), [repo, jobId]);

  const run = runQ.data ?? null;
  const stages = useMemo(() => stagesQ.data ?? [], [stagesQ.data]);
  const conf = useMemo(() => confQ.data ?? [], [confQ.data]);
  const findings = useMemo(() => findingsQ.data ?? [], [findingsQ.data]);
  const transitions = transQ.data ?? [];

  const byRatio = useMemo(
    () => [...stages].sort((a, b) => ratioOf(b) - ratioOf(a)),
    [stages],
  );

  // Follow the data: the first stage carrying a finding, else the loudest
  // ratio, else whatever exists.
  const defaultStage =
    findings.find((f) => f.stage_id >= 0)?.stage_id ??
    byRatio[0]?.stage_id ??
    stages[0]?.stage_id ??
    null;
  const selected = picked ?? defaultStage;
  const current = stages.find((s) => s.stage_id === selected) ?? stages[0];

  // A stage can carry more than one finding. `find()` returned whichever the
  // query happened to order first; the ladder decides instead, then the raw
  // confidence_score — never the display tier and never array position.
  const finding = useMemo(() => {
    const forStage = findings.filter((f) => f.stage_id === selected);
    if (forStage.length === 0) return null;
    return [...forStage].sort(
      (a, b) =>
        severityRank(b.severity) - severityRank(a.severity) ||
        b.confidence_score - a.confidence_score,
    )[0];
  }, [findings, selected]);

  // The proposal and the floor both live on the verification row, so the
  // withheld panel and the recommended fix are read rather than written here.
  const fixQ = useAsync(
    () => (finding ? repo.fixVerification(finding.finding_id) : Promise.resolve(null)),
    [repo, finding?.finding_id],
  );

  // The run's shape identity, from the run row when the memory lane indexed it,
  // otherwise from a stage that carried a fingerprint.
  const fingerprint =
    run?.plan_fingerprint || stages.find((s) => s.plan_fingerprint)?.plan_fingerprint || "";

  const planQ = useAsync(
    () => (fingerprint ? repo.planSample(fingerprint) : Promise.resolve(null)),
    [repo, fingerprint],
  );
  const shapeQ = useAsync(
    () => (fingerprint ? repo.shapeRuns(fingerprint) : Promise.resolve([])),
    [repo, fingerprint],
  );

  const slots = readSlots(conf);
  const appName = run?.app_name ?? stages[0]?.app_name ?? "";

  // Wall clock is the run's own field, the same one the runs list reads. Summing
  // stage durations is a DIFFERENT quantity — it counts concurrent stages twice.
  // Against the live contract the field is null: nothing stores a run's duration.
  const wall = run ? fmt.durationOrDash(run.wall_clock_ms) : "—";

  const refusedCount = useMemo(
    () =>
      byRatio
        .slice(0, TAIL_SAMPLE)
        .filter((s) => assessStage(s, conf).refusal !== null).length,
    [byRatio, conf],
  );

  // Every stage, ordered by id. There is no layout table any more: LAYOUT
  // hardcoded nine stage ids from the recorded run and `stages.filter(s =>
  // s.stage_id in LAYOUT)` rendered an EMPTY panel for every run whose ids were
  // not those nine.
  const ordered = useMemo(
    () => [...stages].sort((a, b) => a.stage_id - b.stage_id),
    [stages],
  );

  const toneFor = (stageId: number): NodeTone => {
    const s = stages.find((x) => x.stage_id === stageId);
    if (!s) return "clean";
    if (findings.some((f) => f.stage_id === stageId)) return "finding";
    const a = assessStage(s, conf);
    if (a.refusal?.code === "post_intervention") return "reshaped";
    if (a.refusal) return "refused";
    return "clean";
  };

  if (stagesQ.loading) return <Page><Prose>Loading run…</Prose></Page>;
  if (!current) return <Page><Prose>No stage rows for <Mono>{jobId}</Mono>.</Prose></Page>;

  const assessment = assessStage(current, conf);
  const v = fixQ.data;
  const proposal = v ? parseProposal(v.proposed_diff) : null;
  const overlay = proposal?.kind === "overlay" ? proposal.config : null;
  const shapeHistory = shapeQ.data ?? [];

  /**
   * The recommended fix, DERIVED: each proposed key against the value the job
   * actually ran with.
   *
   * This block used to be a literal diff — `shuffle.partitions -> 800`,
   * `memory.fraction -> 0.75` — printed for any finding on any run. Now a hunk
   * exists only where the verify lane proposed a key, and the "before" side is
   * the captured job_conf rather than a number typed here.
   */
  const proposedDiff = overlay
    ? Object.entries(overlay)
        .map(([key, value]) => {
          const currentValue = conf.find((c) => c.key === key)?.value;
          return currentValue === undefined
            ? `+ ${key}  ${value}`
            : `- ${key}  ${currentValue}\n+ ${key}  ${value}`;
        })
        .join("\n")
    : null;

  const withheld: Withholding[] = [];
  if (slots === null) {
    withheld.push({
      code: "cluster_width_unknown",
      text: (
        <>
          <Mono className="text-body2">spark.executor.instances</Mono> is absent from job_conf
          ({conf.length} keys). Rule 1's bar cannot be computed, so no tail claim is made — this
          stage would need more than{" "}
          <Mono className="text-body2">{breakEvenSlots(current.task_count, ratioOf(current)).toFixed(1)}</Mono>{" "}
          slots to be tail-bound.
        </>
      ),
    });
  }
  // Rule 2, READ off the verification row. This was gated on
  // `finding?.type === "SPILL"` and then stated a 17.4% floor against an 11%
  // prediction — the recorded run's two numbers, printed for every SPILL on
  // every run, including runs the verify lane had never touched.
  if (v) {
    const floor = measureNoiseFloorPct(v.replay_durations_ms) ?? v.noise_floor_pct;
    const resolvable = ruleTwoRuntimeResolvable(v.predicted_saving_pct, floor);
    if (isVacant(resolvable) || !resolvable.held) {
      withheld.push({
        code: "runtime_unresolved",
        text: (
          <>
            {resolvable.reason}. No percentage is shown.{" "}
            <Link to={`/verify?job=${encodeURIComponent(jobId)}&finding=${encodeURIComponent(v.finding_id)}`}>
              See both verdicts
            </Link>.
          </>
        ),
      });
    }
  }
  const rule5 = ruleFiveSkewAbsence(transitions);
  if (isVacant(rule5)) {
    withheld.push({ code: "skew_absence_not_evidence", text: rule5.reason });
  }
  // WithheldPanel's own contract: it is never empty on a finding — if there is
  // nothing to withhold, that is stated rather than left as a bare "0". Every
  // entry above is now conditional on data, so reaching zero is possible.
  if (withheld.length === 0) {
    withheld.push({
      code: "nothing_withheld",
      text: "Every gate this screen can run returned a verdict on this stage, so nothing is being held back.",
    });
  }

  return (
    <Page className="!py-0 !px-0">
      <div className="flex items-center justify-between px-6 py-4 border-b border-edge shrink-0">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-3">
            <Link to="/runs" className="font-mono text-xs text-dim no-underline hover:text-body">
              runs /
            </Link>
            <span className="font-mono text-xl font-semibold text-bright">{appName}</span>
            {/* The run's own status, computed once in the repository from the
                finding count and severity. This branch used to read
                `findings.some(f => f.severity === "critical") ? DEGRADED :
                WARNING`, which labelled a run with ZERO findings a warning and
                missed `blocker` entirely. */}
            {run
              ? <StatusPill status={run.status} />
              : <Pill tone="neutral">NO RUN ROW</Pill>}
          </div>
          <div className="flex items-center gap-3.5 font-mono text-[11px] text-sub">
            <span>{jobId}</span>
            <span className="text-edge2">·</span>
            <span>{stages.length} stages</span>
            <span className="text-edge2">·</span>
            <span>{wall}</span>
            <span className="text-edge2">·</span>
            <span>{findings.length} findings</span>
            <span className="text-edge2">·</span>
            {/* The bound is named. It read "{n} refused" beside the finding
                count, as though it covered the run. */}
            <span>{refusedCount} of the {TAIL_SAMPLE} loudest refused</span>
            <span className="text-edge2">·</span>
            {/* Was a hardcoded `llm_calls 0` in certified green. */}
            <span>llm_calls <span className="text-dim">{fmt.countOrDash(run?.llm_calls ?? null)}</span></span>
            <span className="text-edge2">·</span>
            {/* Was "spark 4.0 · standalone". Neither the Spark version nor the
                cluster manager is anywhere in contract v0.5. config_source is,
                and it is the fact that decides whether rule 1 has a width. */}
            <span>config <span className="text-dim">{run?.config_source ?? "unknown"}</span></span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => navigate(`/compare?current=${encodeURIComponent(jobId)}`)}>compare to baseline</Button>
          <Button onClick={() => navigate("/ask")}>ask about this run</Button>
          <Button
            variant="primary"
            onClick={() =>
              navigate(
                `/verify?job=${encodeURIComponent(jobId)}` +
                (finding ? `&finding=${encodeURIComponent(finding.finding_id)}` : ""),
              )
            }
          >
            propose fix
          </Button>
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0 px-5 py-4 flex flex-col gap-4 border-r border-edge overflow-auto">
          <div className="flex items-center justify-between gap-4">
            <LayerTabs value={layer} onChange={setLayer} />
            {layer === "stages" && (
              <div className="flex items-center gap-4 font-mono text-[10px] text-sub">
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-finding not-italic" />finding</span>
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-withheld not-italic" />aqe reshaped</span>
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] border border-muted not-italic" />tail, refused</span>
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-edge not-italic" />clean</span>
              </div>
            )}
            {layer === "plan_operators" && (
              <span className="font-mono text-[10px] text-sub">
                redacted in-JVM before egress · rendered verbatim, never parsed
              </span>
            )}
            {layer === "pipeline_lanes" && (
              <span className="font-mono text-[10px] text-sub">
                what each lane wrote for THIS job, counted from the contract tables
              </span>
            )}
          </div>

          {layer === "stages" && (
            <div className="relative bg-[#1a1d1e] border border-edge rounded-sm p-4">
              <div className="flex flex-wrap gap-2.5">
                {ordered.map((s) => (
                  <StageNode
                    key={s.stage_id}
                    assessment={assessStage(s, conf)}
                    tone={toneFor(s.stage_id)}
                    selected={selected === s.stage_id}
                    onClick={() => setPicked(s.stage_id)}
                    // Derived, not per-stage-id. It read `spill …` for stage 25
                    // and `skew_split ×1 · post-AQE` for stage 29 by number.
                    detail={
                      s.spill_mem_bytes + s.spill_disk_bytes > 0
                        ? `spill ${fmt.bytes(s.spill_mem_bytes + s.spill_disk_bytes)}`
                        : undefined
                    }
                  />
                ))}
              </div>
              <div className="mt-3 font-mono text-[10px] text-muted">
                {stages.length} stages · latest attempt per stage · argMax(col, ts) · ordered by
                stage_id, because contract v0.5 carries no stage-to-stage edge to draw a topology from
              </div>
            </div>
          )}

          {layer === "plan_operators" && (
            <div className="bg-[#1a1d1e] border border-edge rounded-sm p-4 flex gap-5">
              <div className="flex-1 min-w-0 font-mono text-xs leading-[1.85] text-body">
                {/* Was `REDACTED_PLAN` imported straight from the fixture module
                    and rendered even when the repository was ClickHouse, with
                    two lines highlighted by array index. The real source is the
                    memory lane's own exemplar column. */}
                {planQ.loading ? (
                  <Prose size="sm" className="text-dim">Loading plan exemplar…</Prose>
                ) : planQ.data ? (
                  planQ.data.split("\n").map((line, i) => (
                    <div key={i} className="whitespace-pre-wrap break-all">{line}</div>
                  ))
                ) : (
                  <Prose size="sm" className="text-sub">
                    <Mono className="text-body2">apex.plan_memory</Mono> holds no exemplar for this
                    shape. That column is written by the <Mono className="text-body2">memory</Mono>{" "}
                    lane; until it indexes this fingerprint there is no plan text to cite.{" "}
                    <Mono className="text-body2">spark_events.plan_json</Mono> is not read instead —
                    its own DDL marks it a tree-string that is never parsed, and it is stored per
                    stage rather than per shape.
                  </Prose>
                )}
              </div>
              <div className="w-[270px] shrink-0 flex flex-col gap-2.5 border-l border-edge pl-5">
                <Label>FINGERPRINT</Label>
                <div className="font-mono text-[11px] text-body2 break-all leading-relaxed">
                  {fingerprint || "none — no stage on this run carried one"}
                </div>
                <Prose size="xs" className="text-sub">
                  Literal-normalized: the same query with different literals hashes identically,
                  which is the only reason stages align across runs.
                </Prose>
                <div className="mt-auto font-mono text-[10px] text-muted">
                  query_text one-way hashed · file_path dropped · emails/IPs HMAC-SHA256
                </div>
              </div>
            </div>
          )}

          {layer === "pipeline_lanes" && (
            <PipelineLanes
              stageCount={stages.length}
              transitionCount={transitions.length}
              confKeyCount={conf.length}
              findingCount={findings.length}
              shapeRunCount={shapeHistory.length}
              indexed={run?.shaped_stage_count !== null && run?.shaped_stage_count !== undefined}
              verified={v !== null && v !== undefined}
              hasFinding={finding !== null}
            />
          )}

          <div className="bg-raised border border-edge rounded-sm p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <Label>ALL {stages.length} STAGES AGAINST THE MEASURABILITY FLOOR</Label>
              <span className="text-xs text-dim">log axis · bytes/task</span>
            </div>
            <SignalStrip stages={stages} conf={conf} findings={findings} />
          </div>

          <RefusalTable stages={stages} conf={conf} onSelect={setPicked} />

          <div className="bg-raised border border-edge rounded-sm overflow-hidden">
            <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-edge">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-xs text-bright">Resolved config as captured</span>
                <span className="font-mono text-[10px] font-bold bg-muted text-surface px-1.5 py-0.5 rounded-sm">
                  {conf.length} keys
                </span>
              </div>
              <span className="text-xs text-dim">
                from the JVM, not from your repo — this is what the job actually ran with
              </span>
            </div>
            {conf.length === 0 ? (
              <div className="px-3.5 py-4">
                <Prose size="sm" className="text-sub">
                  <Mono className="text-body2">apex.job_conf</Mono> holds no row for this job. The
                  jar emits it once per application; without it rule 1 has no cluster width and
                  rule 7 has no configured partition count, and both say so rather than assuming one.
                </Prose>
              </div>
            ) : (
              <div className="grid grid-cols-2">
                {[conf.slice(0, Math.ceil(conf.length / 2)), conf.slice(Math.ceil(conf.length / 2))].map(
                  (half, i) => (
                    <div key={i} className={`px-3.5 py-2.5 flex flex-col gap-1.5 ${i === 0 ? "border-r border-edge" : ""}`}>
                      {half.map((c) => (
                        <Metric
                          key={c.key}
                          label={c.key.replace("spark.sql.adaptive.", "…adaptive.")}
                          value={c.value ?? "absent"}
                          tone={c.value === null ? "finding" : c.value === "true" ? "certified" : "body2"}
                        />
                      ))}
                      {/* Rendered only when the key really is missing. Hardcoded, it
                          printed "absent" beside the captured value on any run that
                          emitted job_conf — the panel contradicting itself. */}
                      {i === 1 && !conf.some((c) => c.key === "spark.executor.instances") && (
                        <Metric label="spark.executor.instances" value="absent" tone="finding" />
                      )}
                    </div>
                  ),
                )}
              </div>
            )}
            <div className="px-3.5 py-2.5 border-t border-edge bg-surface">
              <Prose size="xs" className="text-dim">
                <Mono className="text-body">spark.sql.adaptive.skewJoin.enabled</Mono> is why a fix
                text may or may not say “enable it”, and{" "}
                <Mono className="text-body">spark.executor.instances</Mono>{" "}
                {conf.some((c) => c.key === "spark.executor.instances")
                  ? "is present, so rule 1 computes a bar instead of declaring itself vacant."
                  : "is absent, which is why cluster width is reported unknown rather than guessed."}
              </Prose>
            </div>
          </div>
        </div>

        <aside className="w-[452px] shrink-0 bg-[#1a1d1e] flex flex-col overflow-auto">
          <div className="p-5 border-b border-edge flex flex-col gap-2.5">
            <div className="flex items-center justify-between">
              <Label>PROBLEM DETAIL · STAGE {current.stage_id}</Label>
              <span className="font-mono text-[10px] text-muted">{finding?.finding_id ?? "no finding"}</span>
            </div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-mono text-[17px] font-semibold text-bright">
                {finding?.type ?? "NO CLAIM"}
              </span>
              {finding ? (
                <>
                  <SeverityBadge severity={finding.severity} />
                  {/* Was a hardcoded `certified` pill regardless of tier. */}
                  <ConfidencePill confidence={finding.confidence} score={finding.confidence_score} />
                </>
              ) : (
                <Pill tone="neutral">EVALUATED · REFUSED</Pill>
              )}
            </div>
            {/* The STORED evidence and impact, marked untrusted. This paragraph
                used to be one sentence about a join spilling because the build
                side did not fit — rendered for every finding of every type, on
                every run, while finding.evidence sat unread. */}
            {finding ? (
              <>
                <Prose>{finding.evidence || "No evidence text was stored with this finding."}</Prose>
                {finding.impact && (
                  <Prose size="xs" className="text-sub">impact: {finding.impact}</Prose>
                )}
                <Mono className="text-[10px] text-muted">
                  evidence and impact are UNTRUSTED — authored about the observed job, rendered as
                  data, never followed
                </Mono>
              </>
            ) : (
              <Prose>{assessment.refusal?.text}</Prose>
            )}
            {!finding && assessment.caveat && (
              <Prose size="xs" className="text-withheld">{assessment.caveat}</Prose>
            )}
          </div>

          <div className="p-5 border-b border-edge flex flex-col gap-2.5">
            <Label>MEASURED</Label>
            <div className="flex flex-col gap-1.5">
              <Metric label="task_count" value={current.task_count} note={`${fmt.bytes(assessment.bytesPerTask)}/task`} />
              <Metric label="shuffle_read_bytes" value={fmt.bytes(current.shuffle_read_bytes)} />
              <Metric label="shuffle_write_bytes" value={fmt.bytes(current.shuffle_write_bytes)} />
              {/* Selected by LATEST_STAGES now, and part of the floor. */}
              <Metric label="input_bytes" value={fmt.bytes(current.input_bytes)} />
              <Metric label="spill_mem_bytes" value={fmt.bytes(current.spill_mem_bytes)} tone={current.spill_mem_bytes > 0 ? "finding" : "body2"} />
              <Metric label="spill_disk_bytes" value={fmt.bytes(current.spill_disk_bytes)} />
              <Metric label="peak_execution_mem" value={fmt.bytes(current.peak_execution_mem_bytes)} />
              <Metric label="p99 / p50" value={fmt.ratio(assessment.ratio)} note={assessment.ratio < 2 ? "not a tail" : "tail present"} />
              <Metric label="gc_time_ms" value={current.gc_time_ms.toLocaleString()} />
            </div>
          </div>

          <div className="p-5 border-b border-edge flex flex-col gap-2.5">
            <Label>RULE CHAIN</Label>
            <div className="flex flex-col gap-2">
              {[
                { n: "rule 6 · distribution", v: assessment.ruleSix },
                { n: "rule 1 · tail-bound bar", v: assessment.ruleOne },
                { n: "rule 7 · reshape", v: assessment.ruleSeven },
              ].map((r) => {
                // bound to a const so isVacant() narrows the union on the else branch
                const verdict = r.v;
                const vacant = isVacant(verdict);
                return (
                  <div key={r.n} className="flex gap-2 items-start">
                    <Mono className={`text-[11px] ${vacant ? "text-withheld" : verdict.held ? "text-certified" : "text-dim"}`}>
                      {vacant ? "∅" : verdict.held ? "✓" : "·"}
                    </Mono>
                    <div className="flex-1">
                      <Mono className="text-[11px] text-body2">{r.n}</Mono>
                      <Prose size="xs" className="text-sub">{verdict.reason}</Prose>
                    </div>
                  </div>
                );
              })}
              <div className="flex gap-2 items-start">
                <Mono className={`text-[11px] ${assessment.aboveVolumeFloor ? "text-certified" : "text-withheld"}`}>
                  {assessment.aboveVolumeFloor ? "✓" : "∅"}
                </Mono>
                <div className="flex-1">
                  <Mono className="text-[11px] text-body2">volume floor · 1 MiB/task</Mono>
                  <Prose size="xs" className="text-sub">
                    {fmt.bytesExact(assessment.bytesPerTask)} B/task ·{" "}
                    {((assessment.bytesPerTask / (1024 * 1024)) * 100).toFixed(0)}% of the floor ·
                    shuffle read + write + input, as the engine sums it
                  </Prose>
                </div>
              </div>
            </div>
          </div>

          {finding && (
            <div className="p-5 border-b border-edge flex flex-col gap-2.5">
              <Label>RECOMMENDED FIX</Label>
              {proposedDiff ? (
                <>
                  <Diff text={proposedDiff} />
                  <Prose size="xs" className="text-sub">
                    Every “before” above is the captured{" "}
                    <Mono className="text-body2">job_conf</Mono> value; every “after” is what the
                    verify lane stored in{" "}
                    <Mono className="text-body2">proposed_config</Mono>. Nothing here is written by
                    this screen.
                  </Prose>
                </>
              ) : (
                <>
                  <Prose size="sm" className="text-body">
                    {finding.fix || "No fix text was stored with this finding."}
                  </Prose>
                  <Prose size="xs" className="text-sub">
                    Prose, not a configuration —{" "}
                    <Mono className="text-body2">apex.fix_verifications</Mono>{" "}
                    {v ? "carries no readable overlay for it" : "holds no row for this finding"}, so
                    there is no diff to show. Turning the sentence into testable keys is the verify
                    lane&rsquo;s job. UNTRUSTED: authored about the observed job.
                  </Prose>
                </>
              )}
            </div>
          )}

          <WithheldPanel items={withheld} />

          <div className="p-5 mt-auto border-t border-edge flex items-center justify-between">
            <span className="font-mono text-[10px] text-muted">
              {finding ? `detected_by ${finding.detected_by}` : "no watcher fired"}
            </span>
            <div className="flex gap-2">
              {finding && (
                <Button variant="outline" onClick={() => navigate(`/runs/${jobId}/findings/${finding.finding_id}`)}>
                  evidence
                </Button>
              )}
              <Button
                onClick={() =>
                  navigate(
                    `/verify?job=${encodeURIComponent(jobId)}` +
                    (finding ? `&finding=${encodeURIComponent(finding.finding_id)}` : ""),
                  )
                }
              >
                propose fix
              </Button>
            </div>
          </div>
        </aside>
      </div>
    </Page>
  );
}

/**
 * What each lane wrote FOR THIS JOB, counted from the contract tables this
 * console already queried.
 *
 * Every number here used to be invented: `${stageCount + 2}` spans for collect,
 * "7 prior runs on this fingerprint", "1 prediction pending replay", and a
 * green tick beside every lane whatever the state of it. Two lanes genuinely
 * cannot be observed from a console that reads the store — collect moves
 * telemetry into it and infra runs it — and those say so instead of scoring
 * themselves.
 */
function PipelineLanes({
  stageCount, transitionCount, confKeyCount, findingCount, shapeRunCount,
  indexed, verified, hasFinding,
}: {
  stageCount: number;
  transitionCount: number;
  confKeyCount: number;
  findingCount: number;
  shapeRunCount: number;
  indexed: boolean;
  verified: boolean;
  hasFinding: boolean;
}) {
  const lanes: {
    name: string; role: string; table: string; note: string;
    state: "present" | "empty" | "unobservable";
  }[] = [
    {
      name: "jar", role: "capture", table: "apex.spark_events",
      note: `${stageCount} stage ${stageCount === 1 ? "row" : "rows"}`,
      state: stageCount > 0 ? "present" : "empty",
    },
    {
      name: "jar", role: "capture", table: "apex.job_conf",
      note: `${confKeyCount} conf ${confKeyCount === 1 ? "key" : "keys"}`,
      state: confKeyCount > 0 ? "present" : "empty",
    },
    {
      name: "jar", role: "capture", table: "apex.plan_transitions",
      note: `${transitionCount} re-plan${transitionCount === 1 ? "" : "s"}`,
      state: transitionCount > 0 ? "present" : "empty",
    },
    {
      name: "collect", role: "transport", table: "—",
      note: "not observable from the store",
      state: "unobservable",
    },
    {
      name: "infra", role: "store", table: "—",
      note: "answering these queries",
      state: "unobservable",
    },
    {
      name: "engine", role: "reason", table: "apex.findings",
      note: `${findingCount} finding${findingCount === 1 ? "" : "s"}`,
      state: findingCount > 0 ? "present" : "empty",
    },
    {
      name: "memory", role: "recall", table: "apex.run_outcomes",
      note: indexed
        ? `indexed · ${shapeRunCount} run${shapeRunCount === 1 ? "" : "s"} on this shape`
        : "this run is not indexed",
      state: indexed ? "present" : "empty",
    },
    {
      name: "verify", role: "refute", table: "apex.fix_verifications",
      note: verified
        ? "a verification exists for the selected finding"
        : hasFinding
          ? "no row for the selected finding"
          : "no finding selected to verify",
      state: verified ? "present" : "empty",
    },
  ];

  const border = {
    present: "border-edge2 border-t-2 border-t-certified",
    empty: "border-edge2 border-t-2 border-t-withheld",
    unobservable: "border-edge border-t-2 border-t-edge2",
  };
  const text = {
    present: "text-certified",
    empty: "text-withheld",
    unobservable: "text-muted",
  };

  return (
    <div className="bg-[#1a1d1e] border border-edge rounded-sm p-5 flex flex-col gap-4">
      <div className="grid grid-cols-4 gap-2.5">
        {lanes.map((l) => (
          <div
            key={`${l.name}-${l.table}`}
            className={`bg-raised border rounded-sm p-2.5 flex flex-col gap-1 ${border[l.state]}`}
          >
            <div className="flex items-baseline justify-between gap-1">
              <Mono className="text-[11px] text-bright">{l.name}</Mono>
              <span className="text-[10px] text-dim">{l.role}</span>
            </div>
            <Mono className="text-[9.5px] text-dim break-all">{l.table}</Mono>
            <Mono className={`text-[10px] mt-auto ${text[l.state]}`}>{l.note}</Mono>
          </div>
        ))}
      </div>
      <Prose size="xs" className="text-sub">
        Amber is an EMPTY table, not a broken lane: a run with no AQE re-plan is a run Spark never
        re-planned, and rule 5 says that licenses no claim in either direction. Grey is a lane this
        console cannot see from where it stands — <Mono className="text-body2">collect</Mono> moves
        telemetry into the store and <Mono className="text-body2">infra</Mono> runs it, and neither
        leaves a per-job row to count.
      </Prose>
    </div>
  );
}
