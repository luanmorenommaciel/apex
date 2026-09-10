import { fmt } from "@/contract/rules";
import type { StageAssessment } from "@/contract/rules";

export type NodeTone = "finding" | "reshaped" | "refused" | "clean";

export function StageNode({
  assessment, tone, selected, onClick, detail,
}: {
  assessment: StageAssessment;
  tone: NodeTone;
  selected: boolean;
  onClick: () => void;
  detail?: string;
}) {
  const s = assessment.stage;
  const shell = {
    finding: "bg-finding/[0.12] border-finding",
    reshaped: "bg-withheld/[0.10] border-withheld",
    refused: "bg-raised border-dashed border-muted",
    clean: "bg-raised border-edge",
  }[tone];

  const ring = selected
    ? tone === "finding"
      ? "shadow-[inset_3px_0_0_#fb4934,0_0_0_2px_#e25a1c]"
      : "shadow-[0_0_0_2px_#e25a1c]"
    : tone === "finding"
      ? "shadow-[inset_3px_0_0_#fb4934,0_0_0_3px_rgba(251,73,52,.14)]"
      : "";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-[148px] text-left border rounded-sm px-2.5 py-2 flex flex-col gap-1 transition-shadow ${shell} ${ring}`}
    >
      <div className="flex justify-between font-mono text-[10px] text-dim">
        <span className={tone === "finding" ? "text-finding font-semibold" : ""}>
          stage {s.stage_id}
        </span>
        <span className={tone === "reshaped" ? "text-withheld" : ""}>{s.task_count} t</span>
      </div>
      <div
        className={`font-mono text-xs truncate ${tone === "reshaped" ? "text-withheld" : tone === "finding" ? "text-bright" : "text-body2"}`}
      >
        {/* The contract carries no stage name; the id is the honest label. */}
        {s.stage_name ?? `stage ${s.stage_id}`}
      </div>
      <div className="font-mono text-[10px] text-sub truncate">
        {detail ?? (
          <>
            {fmt.bytes(assessment.bytesPerTask)}/task ·{" "}
            <span className="text-body">{fmt.ratio(assessment.ratio)}</span>
          </>
        )}
      </div>
    </button>
  );
}
