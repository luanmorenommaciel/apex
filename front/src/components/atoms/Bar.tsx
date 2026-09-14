/**
 * One bar of the log-scale signal strip. Height is derived from bytes/task, so
 * the geometry cannot drift from the number it claims to show.
 */
export const LOG_PX_PER_DECADE = 14.28;

export function logHeight(bytesPerTask: number): number {
  if (bytesPerTask <= 1) return 4;
  return Math.max(4, Math.round(LOG_PX_PER_DECADE * Math.log10(bytesPerTask)));
}

/** The dashed floor sits at exactly log10(1 MiB) decades. */
export const FLOOR_PX = Math.round(LOG_PX_PER_DECADE * Math.log10(1024 * 1024));

export type BarTone = "finding" | "withheld" | "refused" | "clean";

export function Bar({
  bytesPerTask, tone, label,
}: {
  bytesPerTask: number;
  tone: BarTone;
  label?: string;
}) {
  const bg = {
    finding: "bg-spark", withheld: "bg-withheld",
    refused: "bg-muted", clean: "bg-edge",
  }[tone];
  return (
    <div className="flex-1 flex flex-col items-center gap-1.5 justify-end">
      <div
        className={`w-full rounded-[1px] ${bg}`}
        style={{ height: logHeight(bytesPerTask) }}
        title={`${Math.round(bytesPerTask).toLocaleString()} B/task`}
      />
      {label && <span className="font-mono text-[9px] text-dim">{label}</span>}
    </div>
  );
}
