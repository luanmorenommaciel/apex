import { Card, Label, type CardAccent } from "@/components/atoms";

export function KpiCard({
  label, value, note, accent = "edge", tone = "bright",
}: {
  label: string;
  value: string | number;
  note?: string;
  accent?: CardAccent;
  tone?: "bright" | "certified" | "withheld" | "finding";
}) {
  const color = {
    bright: "text-bright", certified: "text-certified",
    withheld: "text-withheld", finding: "text-finding",
  }[tone];
  return (
    <Card accent={accent} className="px-4 py-3.5 flex flex-col gap-1.5">
      <Label>{label}</Label>
      <div className={`font-mono text-[28px] font-semibold leading-none ${color}`}>{value}</div>
      {note && <div className="text-xs text-dim">{note}</div>}
    </Card>
  );
}
