import type { ReactNode } from "react";

/** The small tracked caps that title every panel. */
export function Label({
  children, tone = "dim",
}: {
  children: ReactNode;
  tone?: "dim" | "withheld" | "spark" | "finding" | "memory";
}) {
  const color = {
    dim: "text-dim", withheld: "text-withheld", spark: "text-spark",
    finding: "text-finding", memory: "text-memory",
  }[tone];
  return (
    <div className={`font-mono text-[10px] tracking-label ${color}`}>{children}</div>
  );
}
