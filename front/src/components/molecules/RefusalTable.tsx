import { useMemo } from "react";
import { Label, Mono, Prose } from "@/components/atoms";
import {
  assessStage, breakEvenSlots, fmt, isVacant, ratioOf, readSlots, TAIL_SAMPLE, tailBoundBar,
} from "@/contract/rules";
import type { JobConfRow, SparkEventRow } from "@/contract/types";

/**
 * "Considered and refused" — the screen a ratio-ranking tool cannot ship.
 *
 * The BAR column is rule 1's COMPUTED threshold, (n-1)/(slots-1), per stage.
 * There is no 5x or 10x anywhere: a fixed threshold is the thing the contract
 * says is wrong. When cluster width is absent from job_conf the bar cannot be
 * computed, so the column reports the break-even width instead of inventing one.
 */
export function RefusalTable({
  stages, conf, onSelect,
}: {
  stages: SparkEventRow[];
  conf: JobConfRow[];
  onSelect?: (stageId: number) => void;
}) {
  const slots = readSlots(conf);

  const rows = useMemo(
    () =>
      [...stages]
        .sort((a, b) => ratioOf(b) - ratioOf(a))
        .slice(0, TAIL_SAMPLE)
        .map((s) => ({ s, a: assessStage(s, conf) }))
        .filter((r) => r.a.refusal !== null),
    [stages, conf],
  );

  const ruleLabel: Record<string, string> = {
    not_a_distribution: "rule 6",
    below_volume_floor: "floor",
    post_intervention: "rule 7",
    cluster_width_unknown: "rule 1",
    work_bound: "rule 1",
  };

  return (
    <div className="bg-raised border border-edge rounded-sm overflow-hidden">
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-edge">
        <div className="flex items-center gap-2.5">
          <span className="font-mono text-xs text-bright">Considered and refused</span>
          <span className="font-mono text-[10px] font-bold bg-muted text-surface px-1.5 py-0.5 rounded-sm">
            {rows.length}
          </span>
        </div>
        <span className="text-xs text-dim">
          the {TAIL_SAMPLE} loudest p99/p50 ratios, evaluated for a tail claim · none produced one
        </span>
      </div>

      <div className="grid grid-cols-[64px_70px_104px_56px_112px_1fr] px-3.5 py-2 bg-surface border-b border-edge font-mono text-[10px] tracking-[.12em] text-muted">
        <span>STAGE</span>
        <span className="text-right">RATIO</span>
        <span className="text-right">BYTES/TASK</span>
        <span className="text-right">TASKS</span>
        <span className="text-right">BAR (n-1)/(s-1)</span>
        <span className="pl-4">WHY NOT REPORTED</span>
      </div>

      {rows.map(({ s, a }) => {
        const bar = slots === null ? null : tailBoundBar(s.task_count, slots);
        const vacant = isVacant(a.ruleOne) || isVacant(a.ruleSix);
        return (
          <div
            key={s.stage_id}
            onClick={() => onSelect?.(s.stage_id)}
            className={`grid grid-cols-[64px_70px_104px_56px_112px_1fr] px-3.5 py-2.5 border-b border-edge last:border-b-0 items-center font-mono text-[11px] text-body2 ${
              onSelect ? "cursor-pointer hover:bg-edge/40" : ""
            } ${a.refusal?.code === "post_intervention" ? "bg-withheld/[0.06]" : ""}`}
          >
            <span className={a.refusal?.code === "post_intervention" ? "text-withheld" : ""}>
              {s.stage_id}
            </span>
            <span className="text-right text-body">{fmt.ratio(a.ratio)}</span>
            <span className="text-right">{fmt.bytesExact(a.bytesPerTask)}</span>
            <span className="text-right">{s.task_count}</span>
            <span className="text-right">
              {bar !== null ? (
                <span className={a.ratio > bar ? "text-certified" : "text-dim"}>
                  {fmt.ratio(bar)}
                </span>
              ) : vacant && isVacant(a.ruleSix) ? (
                <span className="text-muted">vacant</span>
              ) : (
                <span className="text-withheld">
                  &gt;{breakEvenSlots(s.task_count, a.ratio).toFixed(1)} slots
                </span>
              )}
            </span>
            <span className="pl-4">
              <Prose size="xs" className="text-sub">
                <Mono className="text-dim">[{ruleLabel[a.refusal!.code]}]</Mono>{" "}
                {a.refusal!.text}
                {a.caveat && (
                  <>
                    {" "}
                    <span className="text-withheld">{a.caveat}</span>
                  </>
                )}
              </Prose>
            </span>
          </div>
        );
      })}

      <div className="px-3.5 py-2.5 bg-surface border-t border-edge flex flex-col gap-1">
        <Label>HOW THE BAR IS SET</Label>
        <Prose size="xs" className="text-dim">
          Rule 1 computes the tail-bound threshold per stage as{" "}
          <Mono className="text-body">(n_tasks − 1) / (slots − 1)</Mono>. A fixed 5× or 10× cut is
          wrong because the bar depends on cluster width.{" "}
          {slots === null && (
            <>
              <Mono className="text-body2">spark.executor.instances</Mono> is absent from job_conf,
              so no width is assumed — each row reports the width above which its ratio would clear.
            </>
          )}
        </Prose>
      </div>
    </div>
  );
}
