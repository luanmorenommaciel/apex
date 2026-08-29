import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Card, Diff, Label, Metric, Mono, Pill, Prose, SeverityBadge } from "@/components/atoms";
import {
  Button, LayerTabs, RefusalTable, SignalStrip, StageNode, WithheldPanel,
  type Layer, type NodeTone, type Withholding,
} from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import {
  assessStage, breakEvenSlots, fmt, isVacant, ratioOf, readConfiguredPartitions,
  readSlots, ruleFiveSkewAbsence,
} from "@/contract/rules";
import { useAsync, useRepository } from "@/data/useRepository";
import { PLAN_FINGERPRINT, REDACTED_PLAN } from "@/data/fixtures";

/** The nine stages the DAG draws, laid out in three columns. */
const LAYOUT: Record<number, { col: number; row: number }> = {
  1: { col: 0, row: 0 }, 4: { col: 0, row: 2 },
  6: { col: 1, row: 0 }, 11: { col: 1, row: 2 },
  29: { col: 2, row: 1 },
  25: { col: 3, row: 0 }, 33: { col: 3, row: 2 },
  31: { col: 4, row: 0 }, 34: { col: 4, row: 2 },
};

export function RunDetailScreen() {
  const { jobId = "" } = useParams();
  const repo = useRepository();
  const navigate = useNavigate();
  const [layer, setLayer] = useState<Layer>("stage_dag");
  const [selected, setSelected] = useState(25);

  const runQ = useAsync(() => repo.run(jobId), [repo, jobId]);
  const stagesQ = useAsync(() => repo.stages(jobId), [repo, jobId]);
  const confQ = useAsync(() => repo.jobConf(jobId), [repo, jobId]);
  const findingsQ = useAsync(() => repo.findings(jobId), [repo, jobId]);
  const transQ = useAsync(() => repo.transitions(jobId), [repo, jobId]);

  const run = runQ.data ?? null;
  const stages = useMemo(() => stagesQ.data ?? [], [stagesQ.data]);
  const conf = useMemo(() => confQ.data ?? [], [confQ.data]);
  const findings = findingsQ.data ?? [];
  const transitions = transQ.data ?? [];

  const slots = readSlots(conf);
  const configured = readConfiguredPartitions(conf);
  const appName = stages[0]?.app_name ?? "";

  // Wall clock is the run's own field, the same one the runs list reads. Summing
  // stage durations is a DIFFERENT quantity — it counts concurrent stages twice —
  // and showing it under this label made one run report two durations. Against
  // the live contract the field is null: nothing stores a run's duration.
  const wall = run ? fmt.durationOrDash(run.wall_clock_ms) : "—";

  const refusedCount = useMemo(
    () =>
      [...stages]
        .sort((a, b) => ratioOf(b) - ratioOf(a))
        .slice(0, 5)
        .filter((s) => assessStage(s, conf).refusal !== null).length,
    [stages, conf],
  );

  const graphStages = useMemo(
    () => stages.filter((s) => s.stage_id in LAYOUT),
    [stages],
  );

  const current = stages.find((s) => s.stage_id === selected) ?? stages[0];
  const assessment = current ? assessStage(current, conf) : null;
  const finding = findings.find((f) => f.stage_id === selected) ?? null;

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
  if (finding?.type === "SPILL") {
    withheld.push({
      code: "runtime_unresolved",
      text: (
        <>
          The measured noise floor on this plan shape is{" "}
          <Mono className="text-withheld">17.4%</Mono>; a predicted saving of 11% cannot be separated
          from it. No percentage is shown. <Link to="/verify">See both verdicts</Link>.
        </>
      ),
    });
  }
  const rule5 = ruleFiveSkewAbsence(transitions);
  if (isVacant(rule5)) {
    withheld.push({ code: "skew_absence_not_evidence", text: rule5.reason });
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
            {findings.some((f) => f.severity === "critical") ? (
              <Pill tone="finding" solid>DEGRADED</Pill>
            ) : (
              <Pill tone="withheld">WARNING</Pill>
            )}
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
            <span>{refusedCount} refused</span>
            <span className="text-edge2">·</span>
            <span>llm_calls <span className="text-certified">0</span></span>
            <span className="text-edge2">·</span>
            <span>spark 4.0 · standalone</span>
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
            {layer === "stage_dag" && (
              <div className="flex items-center gap-4 font-mono text-[10px] text-sub">
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-finding not-italic" />finding</span>
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-withheld not-italic" />aqe reshaped</span>
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] border border-muted not-italic" />tail, refused</span>
                <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-edge not-italic" />clean</span>
              </div>
            )}
            {layer !== "stage_dag" && (
              <span className="font-mono text-[10px] text-sub">
                {layer === "plan_operators"
                  ? "redacted in-JVM before egress · every column is none#N"
                  : "where this evidence came from · nothing lost, nothing invented"}
              </span>
            )}
          </div>

          {layer === "stage_dag" && (
            <div className="relative bg-[#1a1d1e] border border-edge rounded-sm p-4">
              <div className="grid grid-cols-5 gap-x-9 gap-y-4" style={{ gridTemplateRows: "auto auto auto" }}>
                {graphStages.map((s) => {
                  const pos = LAYOUT[s.stage_id];
                  const a = assessStage(s, conf);
                  return (
                    <div
                      key={s.stage_id}
                      style={{ gridColumn: pos.col + 1, gridRow: pos.row + 1 }}
                      className="flex items-center"
                    >
                      <StageNode
                        assessment={a}
                        tone={toneFor(s.stage_id)}
                        selected={selected === s.stage_id}
                        onClick={() => setSelected(s.stage_id)}
                        detail={
                          s.stage_id === 25
                            ? `spill ${fmt.bytes(s.spill_mem_bytes + s.spill_disk_bytes)}`
                            : s.stage_id === 29
                              ? `skew_split ×1 · post-AQE`
                              : undefined
                        }
                      />
                    </div>
                  );
                })}
              </div>
              <div className="mt-3 font-mono text-[10px] text-muted">
                latest attempt per stage · argMax(col, ts) · {graphStages.length} of {stages.length} stages
                on the critical path
              </div>
            </div>
          )}

          {layer === "plan_operators" && (
            <div className="bg-[#1a1d1e] border border-edge rounded-sm p-4 flex gap-5">
              <div className="flex-1 font-mono text-xs leading-[1.85] text-body">
                {REDACTED_PLAN.map((line, i) => (
                  <div
                    key={i}
                    className={
                      i === 1
                        ? "bg-finding/[0.12] shadow-[inset_3px_0_0_#fb4934] pl-2 -ml-2 text-bright"
                        : i === 3
                          ? "bg-withheld/[0.10] pl-2 -ml-2"
                          : ""
                    }
                  >
                    {line}
                    {i === 1 && <span className="text-finding"> ← stage 25 · spill</span>}
                    {i === 3 && <span className="text-withheld"> ← stage 29 · split</span>}
                  </div>
                ))}
              </div>
              <div className="w-[270px] flex flex-col gap-2.5 border-l border-edge pl-5">
                <Label>FINGERPRINT</Label>
                <div className="font-mono text-[11px] text-body2 break-all leading-relaxed">
                  {PLAN_FINGERPRINT}
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

          {layer === "pipeline_lanes" && <PipelineLanes stageCount={stages.length} findingCount={findings.length} />}

          <div className="bg-raised border border-edge rounded-sm p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <Label>ALL {stages.length} STAGES AGAINST THE MEASURABILITY FLOOR</Label>
              <span className="text-xs text-dim">log axis · bytes/task</span>
            </div>
            <SignalStrip stages={stages} conf={conf} findings={findings} />
          </div>

          <RefusalTable stages={stages} conf={conf} onSelect={setSelected} />

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
                  <Pill tone="certified">{finding.confidence} · {finding.confidence_score.toFixed(2)}</Pill>
                </>
              ) : (
                <Pill tone="neutral">EVALUATED · REFUSED</Pill>
              )}
            </div>
            <Prose>
              {finding
                ? "The join spills because the build side does not fit the executor's execution memory, not because the data is skewed. Both measurements below are from the same attempt."
                : assessment?.refusal?.text}
            </Prose>
            {!finding && assessment?.caveat && (
              <Prose size="xs" className="text-withheld">{assessment.caveat}</Prose>
            )}
          </div>

          <div className="p-5 border-b border-edge flex flex-col gap-2.5">
            <Label>MEASURED</Label>
            <div className="flex flex-col gap-1.5">
              <Metric label="task_count" value={current.task_count} note={`${fmt.bytes(assessment!.bytesPerTask)}/task`} />
              <Metric label="shuffle_read_bytes" value={fmt.bytes(current.shuffle_read_bytes)} />
              <Metric label="spill_mem_bytes" value={fmt.bytes(current.spill_mem_bytes)} tone={current.spill_mem_bytes > 0 ? "finding" : "body2"} />
              <Metric label="spill_disk_bytes" value={fmt.bytes(current.spill_disk_bytes)} />
              <Metric label="peak_execution_mem" value={fmt.bytes(current.peak_execution_mem_bytes)} />
              <Metric label="p99 / p50" value={fmt.ratio(assessment!.ratio)} note={assessment!.ratio < 2 ? "not a tail" : "tail present"} />
              <Metric label="gc_time_ms" value={current.gc_time_ms.toLocaleString()} />
            </div>
          </div>

          <div className="p-5 border-b border-edge flex flex-col gap-2.5">
            <Label>RULE CHAIN</Label>
            <div className="flex flex-col gap-2">
              {[
                { n: "rule 6 · distribution", v: assessment!.ruleSix },
                { n: "rule 1 · tail-bound bar", v: assessment!.ruleOne },
                { n: "rule 7 · reshape", v: assessment!.ruleSeven },
              ].map((r) => {
                // bound to a const so isVacant() narrows the union on the else branch
                const v = r.v;
                const vacant = isVacant(v);
                return (
                  <div key={r.n} className="flex gap-2 items-start">
                    <Mono className={`text-[11px] ${vacant ? "text-withheld" : v.held ? "text-certified" : "text-dim"}`}>
                      {vacant ? "∅" : v.held ? "✓" : "·"}
                    </Mono>
                    <div className="flex-1">
                      <Mono className="text-[11px] text-body2">{r.n}</Mono>
                      <Prose size="xs" className="text-sub">{v.reason}</Prose>
                    </div>
                  </div>
                );
              })}
              <div className="flex gap-2 items-start">
                <Mono className={`text-[11px] ${assessment!.aboveVolumeFloor ? "text-certified" : "text-withheld"}`}>
                  {assessment!.aboveVolumeFloor ? "✓" : "∅"}
                </Mono>
                <div className="flex-1">
                  <Mono className="text-[11px] text-body2">volume floor · 1 MiB/task</Mono>
                  <Prose size="xs" className="text-sub">
                    {fmt.bytesExact(assessment!.bytesPerTask)} B/task ·{" "}
                    {((assessment!.bytesPerTask / (1024 * 1024)) * 100).toFixed(0)}% of the floor
                  </Prose>
                </div>
              </div>
            </div>
          </div>

          {finding && (
            <div className="p-5 border-b border-edge flex flex-col gap-2.5">
              <Label>RECOMMENDED FIX</Label>
              <Diff text={`- spark.sql.shuffle.partitions      ${configured}
+ spark.sql.shuffle.partitions      800
+ spark.memory.fraction             0.75`} />
              <Prose size="xs" className="text-sub">
                {fmt.bytes(assessment!.bytesPerTask)}/task against{" "}
                {fmt.bytes(current.peak_execution_mem_bytes)} of execution memory shared by cores is
                the constraint. Four-fold more partitions puts each task under the limit without new
                hardware.
              </Prose>
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
              <Button onClick={() => navigate("/verify")}>propose fix</Button>
            </div>
          </div>
        </aside>
      </div>
    </Page>
  );
}

function PipelineLanes({ stageCount, findingCount }: { stageCount: number; findingCount: number }) {
  const lanes = [
    { name: "dev", role: "generate", note: "submitted ✓" },
    { name: "jar", role: "capture", note: `${stageCount} events` },
    { name: "collect", role: "transport", note: `${stageCount + 2} spans` },
    { name: "infra", role: "store", note: `${stageCount} rows` },
    { name: "engine", role: "reason", note: `${findingCount} findings`, hot: true },
    { name: "serve", role: "answer", note: "read-only ✓" },
  ];
  return (
    <div className="bg-[#1a1d1e] border border-edge rounded-sm p-5 flex flex-col gap-4">
      <div className="grid grid-cols-6 gap-2.5">
        {lanes.map((l) => (
          <div
            key={l.name}
            className={`bg-raised border rounded-sm p-2.5 flex flex-col gap-1 ${
              l.hot ? "border-spark border-t-2 border-t-spark" : "border-edge2 border-t-2 border-t-certified"
            }`}
          >
            <Mono className={`text-[11px] ${l.hot ? "text-spark" : "text-bright"}`}>{l.name}</Mono>
            <span className="text-[11px] text-dim">{l.role}</span>
            <Mono className={`text-[11px] mt-auto ${l.hot ? "text-spark" : "text-certified"}`}>{l.note}</Mono>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2.5">
        <Card accent="memory" className="px-3 py-2.5 flex justify-between items-center">
          <Mono className="text-[11px] text-memory">memory · recall</Mono>
          <Mono className="text-[11px] text-body">7 prior runs on this fingerprint</Mono>
        </Card>
        <Card accent="finding" className="px-3 py-2.5 flex justify-between items-center">
          <Mono className="text-[11px] text-finding">verify · refute</Mono>
          <Mono className="text-[11px] text-body">1 prediction pending replay</Mono>
        </Card>
      </div>
      <Prose size="xs" className="text-sub">
        {stageCount + 2} spans decompose exactly: {stageCount}{" "}
        <Mono className="text-body2">apex.stage</Mono> + 1{" "}
        <Mono className="text-body2">apex.plan_transition</Mono> + 1{" "}
        <Mono className="text-body2">apex.job_conf</Mono>. Every span accounted for.
      </Prose>
    </div>
  );
}
