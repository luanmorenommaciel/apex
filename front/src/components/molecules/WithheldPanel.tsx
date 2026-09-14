import type { ReactNode } from "react";
import { Label, Mono, Prose } from "@/components/atoms";

export interface Withholding {
  code: string;
  text: ReactNode;
}

/**
 * What Apex will not claim, and why. This panel is never empty on a finding —
 * if there is nothing to withhold, the finding says so explicitly.
 */
export function WithheldPanel({ items }: { items: Withholding[] }) {
  return (
    <div className="p-4 border-b border-edge flex flex-col gap-2.5 bg-withheld/[0.04]">
      <div className="flex items-center gap-2">
        <Label tone="withheld">WITHHELD</Label>
        <span className="font-mono text-[10px] text-dim">{items.length}</span>
      </div>
      {items.map((w) => (
        <Prose key={w.code} size="sm">
          <Mono className="text-withheld">{w.code}</Mono> — {w.text}
        </Prose>
      ))}
    </div>
  );
}
