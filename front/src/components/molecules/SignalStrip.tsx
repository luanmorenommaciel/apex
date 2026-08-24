import { useMemo } from "react";
import { Bar, FLOOR_PX, type BarTone } from "@/components/atoms";
import { assessStage, ratioOf } from "@/contract/rules";
import type { FindingRow, JobConfRow, SparkEventRow } from "@/contract/types";

/**
 * 34 stages on a log axis of bytes/task, with the 1 MiB measurability floor
 * drawn where it actually falls. Colour is a claim, not emphasis:
 *   spark  = a finding Apex defends
 *   amber  = the honest near-miss (>= 90% of the floor)
 *   muted  = evaluated for a tail claim and refused
 *   clean  = never a candidate for a tail claim
 */
export function SignalStrip({
  stages, conf, findings, className = "",
}: {
  stages: SparkEventRow[];
  conf: JobConfRow[];
  findings: FindingRow[];
  className?: string;
}) {
  const bars = useMemo(() => {
    const withFinding = new Set(findings.filter((f) => f.stage_id >= 0).map((f) => f.stage_id));
    const ranked = [...stages].sort((a, b) => ratioOf(b) - ratioOf(a)).slice(0, 5);
    const refusedIds = new Set(
      ranked.filter((s) => assessStage(s, conf).refusal !== null).map((s) => s.stage_id),
    );

    return stages.map((s) => {
      const a = assessStage(s, conf);
      let tone: BarTone = "clean";
      if (withFinding.has(s.stage_id)) tone = "finding";
      else if (a.refusal?.code === "post_intervention") tone = "withheld";
      else if (refusedIds.has(s.stage_id)) tone = "refused";
      return { stage: s, tone, bpt: a.bytesPerTask };
    });
  }, [stages, conf, findings]);

  const refusedCount = bars.filter((b) => b.tone === "refused" || b.tone === "withheld").length;
  const claimCount = bars.filter((b) => b.tone === "finding").length;

  return (
    <div className={`flex flex-col gap-2.5 ${className}`}>
      <div className="relative flex items-end gap-[5px] h-[132px] mt-5">
        <div
          className="absolute left-0 right-0 border-t border-dashed border-withheld pointer-events-none"
          style={{ bottom: FLOOR_PX }}
        />
        <div className="absolute left-0 -top-4 font-mono text-[10px] tracking-label text-withheld">
          1 MiB/TASK · MEASURABILITY FLOOR
        </div>
        {bars.map((b) => (
          <Bar key={b.stage.stage_id} bytesPerTask={b.bpt} tone={b.tone} />
        ))}
      </div>
      <div className="h-px bg-edge" />
      <div className="flex gap-6 font-mono text-[11px] text-dim">
        <span>{stages.length} stages · log axis, bytes/task</span>
        <span>{refusedCount} tails considered</span>
        <span>
          <span className="text-spark">{claimCount}</span> claims made
        </span>
        <span>
          llm_calls <span className="text-certified">0</span>
        </span>
      </div>
    </div>
  );
}
