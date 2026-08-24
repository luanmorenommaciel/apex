import type { ReactNode } from "react";
import type { Confidence, Severity } from "@/contract/types";

export function Pill({
  children, tone = "neutral", solid = false,
}: {
  children: ReactNode;
  tone?: "neutral" | "finding" | "withheld" | "certified" | "spark" | "memory";
  solid?: boolean;
}) {
  const solidTone = {
    neutral: "bg-muted text-surface", finding: "bg-finding text-surface",
    withheld: "bg-withheld text-surface", certified: "bg-certified text-surface",
    spark: "bg-spark text-surface", memory: "bg-memory text-surface",
  }[tone];
  const outlineTone = {
    neutral: "border-edge2 text-body", finding: "border-finding text-finding",
    withheld: "border-withheld text-withheld", certified: "border-edge2 text-certified",
    spark: "border-spark text-spark", memory: "border-memory text-memory",
  }[tone];
  return (
    <span
      className={
        solid
          ? `font-mono text-[10px] tracking-[.1em] font-bold px-[7px] py-[3px] rounded-sm ${solidTone}`
          : `font-mono text-[10px] tracking-[.1em] px-[7px] py-[2px] rounded-sm border ${outlineTone}`
      }
    >
      {children}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  if (severity === "critical") return <Pill tone="finding" solid>CRITICAL</Pill>;
  if (severity === "warning") return <Pill tone="withheld">WARNING</Pill>;
  return <Pill tone="neutral">INFO</Pill>;
}

/**
 * Shows the coarse tier AND the raw score, because ranking happens on the raw
 * score and a UI that hides it invites the wrong comparison.
 */
export function ConfidencePill({
  confidence, score,
}: {
  confidence: Confidence;
  score: number;
}) {
  return (
    <Pill tone={confidence === "HIGH" ? "certified" : "neutral"}>
      {confidence} · {score.toFixed(2)}
    </Pill>
  );
}

export function StatusPill({ status }: { status: string }) {
  if (status === "degraded" || status === "failed")
    return <Pill tone="finding" solid>{status.toUpperCase()}</Pill>;
  if (status === "warning") return <Pill tone="withheld">WARNING</Pill>;
  return <Pill tone="certified">HEALTHY</Pill>;
}
