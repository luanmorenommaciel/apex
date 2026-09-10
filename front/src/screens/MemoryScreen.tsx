import { useSearchParams } from "react-router-dom";
import { Card, Label, Mono, Prose } from "@/components/atoms";
import { KpiCard, ScreenHeader } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import { canonicaliseConfValue, distinctConfigCount, fmt, ruleThreeAttributableToTuning } from "@/contract/rules";
import { useAsync, useRepository } from "@/data/useRepository";
import type { ShapeRun } from "@/data/repository";

/**
 * Plan memory: outcomes, not opinions.
 *
 * Reads apex.plan_memory for what a shape IS — its operator mix, structurally —
 * and apex.run_outcomes for what happened when it ran. Neither table stores an
 * opinion, and this screen adds none: rule 3 decides what may be credited to
 * tuning, and where the config was never captured it credits nothing.
 *
 * The four ZEST-typed knobs are the ones rule 3 reasons over. `conf_extra` holds
 * the rest verbatim; it is not read here because a key present in one run and
 * absent in another is not two configurations, and telling those apart needs the
 * per-key history this screen does not yet show.
 */
const TUNABLES = [
  { key: "spark.sql.shuffle.partitions", field: "conf_shuffle_partitions" },
  { key: "spark.executor.instances", field: "conf_executor_instances" },
  { key: "spark.executor.cores", field: "conf_executor_cores" },
  { key: "spark.executor.memory", field: "conf_executor_memory_mb" },
] as const;

export function MemoryScreen() {
  const repo = useRepository();
  const [params] = useSearchParams();

  const shapesQ = useAsync(() => repo.planShapes(), [repo]);
  const shapes = shapesQ.data ?? [];
  // Default to the most-run shape: the one with history worth reading.
  const fingerprint = params.get("shape") ?? shapes[0]?.plan_fingerprint ?? "";
  const shape = shapes.find((s) => s.plan_fingerprint === fingerprint) ?? null;

  const runsQ = useAsync(
    () => (fingerprint ? repo.shapeRuns(fingerprint) : Promise.resolve([])),
    [repo, fingerprint],
  );
  const runs = runsQ.data ?? [];

  if (shapesQ.loading) return <Page><Prose>Loading plan memory…</Prose></Page>;
  if (!shape) {
    return (
      <Page>
        <ScreenHeader title="Plan memory" subtitle="nothing indexed yet" />
        <Card accent="withheld" className="px-4 py-3.5">
          <Prose>
            No plan shape has been indexed. <Mono className="text-body2">apex.plan_memory</Mono> is
            written by the memory lane, not by the console — until that lane runs over a job, there
            is no history to recall, and this screen shows none rather than a placeholder.
          </Prose>
        </Card>
      </Page>
    );
  }

  const maxMs = Math.max(1, ...runs.map((r) => r.task_time_ms));
  const captured = runs.filter((r) => r.config_source !== "unknown").length;

  return (
    <Page>
      <ScreenHeader
        title="Plan memory"
        subtitle={
          <>
            we have seen this plan shape before · <Mono className="text-body2">{shape.run_count} runs</Mono> on{" "}
            <Mono className="text-body2">{fingerprint.slice(0, 12)}…</Mono>
            {shapes.length > 1 && <> · {shapes.length} shapes indexed</>}
          </>
        }
      />

      <div className="grid grid-cols-4 gap-3">
        <KpiCard label="PLAN SHAPES KNOWN" value={shapes.length} note="literal-normalized fingerprints" accent="memory" />
        <KpiCard label="RUNS ON THIS SHAPE" value={shape.run_count} note={`first seen ${shape.first_run.slice(0, 10)}`} accent="edge" />
        {/* Config coverage, not "fixes confirmed": a confirmed fix is a
            fix_verifications row, and that lane has written none here. Counting
            zero rows as zero confirmed fixes would report an absence of evidence
            as evidence of failure. */}
        <KpiCard
          label="RUNS WITH CONFIG"
          value={`${captured}/${runs.length}`}
          note={captured === 0 ? "no job_conf captured on this shape" : "jar emitted job_conf"}
          accent={captured === 0 ? "withheld" : "certified"}
          tone={captured === 0 ? "withheld" : "certified"}
        />
        <KpiCard label="RUNTIME CERTIFIED" value="—" note="verify lane has written no row" accent="withheld" tone="withheld" />
      </div>

      <Card className="p-4 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <Label tone="memory">TASK TIME PER RUN ON THIS SHAPE</Label>
          <div className="flex items-center gap-4 font-mono text-[10px] text-sub">
            <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-finding not-italic" />carries a finding</span>
            <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-withheld not-italic" />warning only</span>
            <span className="flex items-center gap-1.5"><i className="w-2 h-2 rounded-[1px] bg-edge2 not-italic" />clean</span>
          </div>
        </div>
        <div className="flex items-end gap-4 h-[132px]">
          {runs.map((r) => (
            <div key={r.job_id} className="flex-1 flex flex-col items-center gap-1.5 justify-end">
              <Mono className="text-[10px] text-dim">{fmt.duration(r.task_time_ms)}</Mono>
              <div
                className={`w-full rounded-[1px] ${
                  r.severity_rank >= 3 ? "bg-finding" : r.finding_count > 0 ? "bg-withheld" : "bg-edge2"
                }`}
                style={{ height: Math.max(4, Math.round((r.task_time_ms / maxMs) * 96)) }}
                title={r.job_id}
              />
              <Mono className="text-[10px] text-dim">{r.job_id.slice(-4)}</Mono>
            </div>
          ))}
        </div>
        <Prose size="xs" className="text-dim">
          Height is <Mono className="text-body">task_time_ms</Mono> — sum of task_count x p50 —
          against the largest run ({fmt.duration(maxMs)}), on a linear scale. It is NOT a wall clock:
          the contract stores none, and this lane's own wall_clock_ms is a per-shape timestamp span
          its DDL calls context rather than a cost metric.
        </Prose>
      </Card>

      <div className="grid grid-cols-2 gap-4 flex-1 min-h-0">
        <div className="bg-raised border border-edge rounded-sm overflow-hidden flex flex-col">
          <div className="px-3.5 py-2.5 border-b border-edge">
            <span className="font-mono text-xs text-bright">Configuration history · rule 3</span>
          </div>
          {TUNABLES.map((t) => (
            <TunableRow key={t.key} label={t.key} runs={runs} field={t.field} />
          ))}
          <div className="px-3.5 py-3 mt-auto bg-surface border-t border-edge">
            <Prose size="xs" className="text-dim">
              Rule 3 credits a delta to tuning only above <Mono className="text-body">2 distinct
              configurations</Mono>, canonicalised first so <Mono className="text-body">'5.0'</Mono>{" "}
              and <Mono className="text-body">'5'</Mono> count once. Below that, any difference
              between these runs is run-to-run variance.
            </Prose>
          </div>
        </div>

        <div className="bg-raised border border-edge rounded-sm overflow-hidden flex flex-col">
          <div className="px-3.5 py-2.5 border-b border-edge">
            <span className="font-mono text-xs text-bright">This shape, structurally</span>
          </div>
          <div className="px-3.5 py-3 grid grid-cols-2 gap-x-5 gap-y-2">
            {[
              ["nodes", shape.node_count], ["max depth", shape.max_depth],
              ["joins", shape.join_count], ["aggregates", shape.agg_count],
              ["exchanges", shape.exchange_count], ["scans", shape.scan_count],
            ].map(([label, v]) => (
              <div key={String(label)} className="flex justify-between font-mono text-xs border-b border-edge pb-1.5">
                <span className="text-sub">{label}</span>
                <span className="text-body2">{v}</span>
              </div>
            ))}
          </div>
          <div className="px-3.5 py-3 mt-auto bg-surface border-t border-edge">
            <Prose size="xs" className="text-dim">
              From <Mono className="text-body">apex.plan_memory</Mono>, the memory lane's structural
              index. It describes the SHAPE — what the query is made of — and carries no timing, so
              two runs of it can be compared knowing the work was the same.
            </Prose>
          </div>
        </div>
      </div>

      <Card accent="withheld" className="px-4 py-3.5 flex flex-col gap-1.5">
        <Label tone="withheld">WHAT THIS MEMORY IS NOT</Label>
        <Prose>
          A single-environment corpus. Counts are directional: they say “this worked on this bench”,
          never “this works”.{" "}
          {captured === 0 && (
            <>
              And on this shape the jar captured no configuration at all, so rule 3 credits nothing
              to tuning — not because the changes failed, but because there is nothing to attribute.{" "}
            </>
          )}
          Fingerprint <Mono className="text-body2">{fingerprint.slice(0, 24)}…</Mono>
        </Prose>
      </Card>
    </Page>
  );
}

/** One tunable across the shape's history, judged by rule 3. */
function TunableRow({
  label, runs, field,
}: {
  label: string;
  runs: ShapeRun[];
  field: "conf_shuffle_partitions" | "conf_executor_instances" | "conf_executor_cores" | "conf_executor_memory_mb";
}) {
  // null is NOT a value: a run that never reported the key is not a run that
  // set it to something. canonicaliseConfValue then folds '5.0' onto '5'.
  const values = runs.map((r) => (r[field] === null ? null : String(r[field])));
  const observed = values.filter((v): v is string => v !== null);
  const distinct = distinctConfigCount(values);
  const verdict = ruleThreeAttributableToTuning(values);
  const attributable = "held" in verdict && verdict.held;

  const shown = Array.from(new Set(observed.map(canonicaliseConfValue)))
    .filter((v): v is string => v !== null);

  return (
    <div className="px-3.5 py-3 border-b border-edge flex flex-col gap-1.5">
      <div className="flex items-center justify-between gap-2">
        <Mono className="text-xs text-bright">{label}</Mono>
        <Mono className={`text-[10px] ${observed.length === 0 ? "text-muted" : "text-body2"}`}>
          {observed.length}/{runs.length} runs reported it
        </Mono>
      </div>
      <Prose size="xs" className="text-sub">
        {observed.length === 0
          ? "Never captured on this shape — the jar emitted no job_conf for these runs."
          : `Values seen: ${shown.join(" · ")}`}
      </Prose>
      <div className="flex items-center gap-2 font-mono text-[10px]">
        <span className={`px-1.5 py-0.5 border rounded-sm ${attributable ? "border-edge2 text-certified" : "border-withheld text-withheld"}`}>
          rule 3 · {distinct} distinct config{distinct === 1 ? "" : "s"}
        </span>
        {!attributable && <span className="text-withheld">not attributable to tuning</span>}
      </div>
    </div>
  );
}
