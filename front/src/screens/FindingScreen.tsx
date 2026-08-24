import { Link, useParams } from "react-router-dom";
import { Bar, Card, FLOOR_PX, KeyValue, Label, Mono, Pill, Prose, SeverityBadge } from "@/components/atoms";
import { ScreenHeader } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import { assessStage, fmt, noOpGate, ratioOf, VOLUME_FLOOR_BYTES_PER_TASK } from "@/contract/rules";
import { attributionIsAvailable } from "@/contract/rules";
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

  const finding = (findingsQ.data ?? []).find((f) => f.finding_id === findingId);
  const stages = stagesQ.data ?? [];
  const conf = confQ.data ?? [];
  const transition = (transQ.data ?? [])[0];

  if (findingsQ.loading) return <Page><Prose>Loading finding…</Prose></Page>;
  if (!finding) return <Page><Prose>No finding <Mono>{findingId}</Mono>.</Prose></Page>;

  const gate = noOpGate(conf, "spark.sql.adaptive.skewJoin.enabled", "true");
  const ranked = [...stages].sort((a, b) => ratioOf(b) - ratioOf(a)).slice(0, 5);

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
            <Pill tone="certified">{finding.confidence} · {finding.confidence_score.toFixed(2)}</Pill>
          </span>
        }
      />

      <div className="flex gap-5 flex-1 min-h-0">
        <div className="flex-1 min-w-0 flex flex-col gap-4 overflow-auto pr-1">
          <Prose size="base" className="max-w-[760px]">
            This finding is not a heuristic. It is Spark's own runtime re-planning decision, captured
            from <Mono className="text-body2">SparkListenerSQLAdaptiveExecutionUpdate</Mono> and
            diffed per execution. It sits at job level because contract v0.4 keys transitions by{" "}
            <Mono className="text-body2">(job_id, execution_id)</Mono> and carries no execution→stage
            map. Attributing it to a stage would be a fabrication
            {!attributionIsAvailable() && " — the map arrives in v0.5"}.
          </Prose>

          <div className="grid grid-cols-2 gap-3.5">
            <Card className="p-4 flex flex-col gap-2.5">
              <Label>GROUND TRUTH CAPTURED</Label>
              <div className="flex flex-col gap-1.5 font-mono text-xs">
                <div className="flex justify-between"><span className="text-sub">transition_type</span><span className="text-withheld">{transition?.transition_type ?? "—"}</span></div>
                <div className="flex justify-between"><span className="text-sub">execution_id</span><span className="text-body2">{transition?.execution_id ?? "—"}</span></div>
                <div className="flex justify-between"><span className="text-sub">detail</span><span className="text-body2">{transition?.detail ?? "—"}</span></div>
                <div className="flex justify-between"><span className="text-sub">before → after</span><span className="text-body2">{transition ? `${transition.before} → ${transition.after}` : "—"}</span></div>
                <div className="flex justify-between"><span className="text-sub">confidence</span><span className="text-certified">{transition?.confidence ?? "—"}</span></div>
              </div>
              <Prose size="xs" className="text-dim">
                Cost to produce: <Mono className="text-certified">$0</Mono>. No LLM was called for
                this finding.
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
                      {c.key.replace("spark.sql.", "")} = <span className="text-certified">{c.value}</span>
                      {c.key.endsWith("skewJoin.enabled") && (
                        <span className="text-withheld"> ← already on</span>
                      )}
                    </div>
                  ))}
                <div className="text-body2">
                  spark.executor.instances = <span className="text-finding">absent</span>
                </div>
              </div>
              <Prose size="xs" className="text-sub">{gate.reason}</Prose>
            </Card>
          </div>

          <Card accent="certified" className="p-4 flex flex-col gap-2">
            <Label>FIX AS WRITTEN</Label>
            <div className="font-mono text-sm text-bright">
              Keep <span className="text-certified">skewJoin.enabled=true</span>, then remove the
              skew at the source.
            </div>
            <Prose size="xs" className="text-sub">
              Salt the join key, or pre-aggregate the hot key upstream. AQE is already doing what it
              can — and rule 5 means a quiet transition log would license no claim either way.
            </Prose>
          </Card>

          <Card className="p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <Label tone="withheld">WHY THE LOUDEST NUMBER IS NOT HERE</Label>
              <span className="text-xs text-dim">
                {ranked.length} stages carried a tail · zero were reported as skew
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
                    {ranked.map((s) => {
                      const a = assessStage(s, conf);
                      return (
                        <Bar
                          key={s.stage_id}
                          bytesPerTask={a.bytesPerTask}
                          tone={a.refusal?.code === "post_intervention" ? "withheld" : "refused"}
                          label={String(s.stage_id)}
                        />
                      );
                    })}
                  </div>
                </div>
                <Prose size="xs" className="text-dim">
                  Bar height is bytes/task on a log scale. Stage 11 clears the floor but has 2 tasks
                  — rule 6 makes rule 1 vacant, so the stage is excluded, not cleared.
                </Prose>
              </div>

              <div className="flex-1 min-w-0 flex flex-col gap-2.5">
                {ranked.slice(0, 2).map((s) => {
                  const a = assessStage(s, conf);
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
              <KeyValue k="hot_key" v={<span className="text-muted">""</span>} />
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

          <Card accent="memory" className="p-3 flex flex-col gap-1.5">
            <Mono className="text-xs text-memory">7 runs · same fingerprint</Mono>
            <Prose size="xs" className="text-sub">
              Salting the join key cleared it twice. Raising{" "}
              <Mono className="text-body2">skewedPartitionFactor</Mono> did nothing, three times.
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
