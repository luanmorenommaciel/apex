import type { ReactNode } from "react";

/** One measured row: label left, value right. Value always mono. */
export function Metric({
  label, value, note, tone = "body2",
}: {
  label: string;
  value: ReactNode;
  note?: string;
  tone?: "body2" | "finding" | "withheld" | "certified";
}) {
  const color = {
    body2: "text-body2", finding: "text-finding",
    withheld: "text-withheld", certified: "text-certified",
  }[tone];
  return (
    <div className="flex justify-between font-mono text-xs">
      <span className="text-sub">{label}</span>
      <span className={color}>
        {value}
        {note && <span className="text-dim"> · {note}</span>}
      </span>
    </div>
  );
}

export function KeyValue({ k, v, tone = "body" }: { k: string; v: ReactNode; tone?: string }) {
  return (
    <div className="font-mono text-[10.5px] leading-[1.85]">
      <span className="text-dim">{k}</span>{" "}
      <span className={tone === "body" ? "text-body" : tone}>{v}</span>
    </div>
  );
}
