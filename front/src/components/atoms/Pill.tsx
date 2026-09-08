import type { ReactNode } from "react";
import type { FindingConfidence, Severity } from "@/contract/types";

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

/**
 * The contract ladder is info < warning < critical < blocker.
 *
 * `blocker` used to have no branch and fell through to INFO — the loudest rung
 * the engine can raise (an explicit OOM) rendered as the quietest. It is listed
 * first now, and the default names an unrecognised rung instead of colouring it.
 */
export function SeverityBadge({ severity }: { severity: Severity }) {
  switch (severity) {
    case "blocker":
      return <Pill tone="finding" solid>BLOCKER</Pill>;
    case "critical":
      return <Pill tone="finding" solid>CRITICAL</Pill>;
    case "warning":
      return <Pill tone="withheld">WARNING</Pill>;
    case "info":
      return <Pill tone="neutral">INFO</Pill>;
    default:
      return <Pill tone="withheld">{String(severity).toUpperCase()}</Pill>;
  }
}

/**
 * Shows the coarse tier AND the raw score, because ranking happens on the raw
 * score and a UI that hides it invites the wrong comparison.
 */
export function ConfidencePill({
  confidence, score,
}: {
  confidence: FindingConfidence;
  score: number;
}) {
  return (
    <Pill tone={confidence === "HIGH" ? "certified" : "neutral"}>
      {confidence} · {score.toFixed(2)}
    </Pill>
  );
}

/**
 * A verdict the contract may have no source for: true, false, or NOT STORED.
 *
 * Three states, three tones, because rule 4 turns on the difference. Collapsing
 * null onto false — `tone={v ? "certified" : "finding"}` — convicts a fix of
 * not firing on the strength of a column that does not exist.
 */
export function VerdictPill({ value, label }: { value: boolean | null; label?: string }) {
  if (value === null)
    return <Pill tone="withheld" solid>{label ?? "NO SOURCE"}</Pill>;
  return (
    <Pill tone={value ? "certified" : "finding"} solid>
      {String(value).toUpperCase()}
    </Pill>
  );
}

export function StatusPill({ status }: { status: string }) {
  if (status === "degraded" || status === "failed")
    return <Pill tone="finding" solid>{status.toUpperCase()}</Pill>;
  if (status === "warning") return <Pill tone="withheld">WARNING</Pill>;
  return <Pill tone="certified">HEALTHY</Pill>;
}
