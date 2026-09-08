/**
 * "stage dag" was a promise the contract cannot keep. Nothing in v0.5 carries a
 * stage-to-stage edge: spark_events is keyed by (job_id, stage_id, attempt) and
 * plan_json is a tree-string its own DDL forbids parsing. The layer showed nine
 * hand-placed nodes from the recorded run and drew no edges between them. It is
 * named for what it is now — the stages, ordered by id.
 */
export type Layer = "stages" | "plan_operators" | "pipeline_lanes";

const LABELS: Record<Layer, string> = {
  stages: "stages",
  plan_operators: "plan operators",
  pipeline_lanes: "pipeline lanes",
};

export function LayerTabs({
  value, onChange,
}: {
  value: Layer;
  onChange: (l: Layer) => void;
}) {
  return (
    <div className="flex border border-edge rounded-sm overflow-hidden font-mono text-[11px]">
      {(Object.keys(LABELS) as Layer[]).map((l, i) => (
        <button
          key={l}
          type="button"
          onClick={() => onChange(l)}
          className={`px-3.5 py-[7px] transition-colors ${i > 0 ? "border-l border-edge" : ""} ${
            value === l ? "bg-edge text-bright" : "text-sub hover:text-body2"
          }`}
        >
          {LABELS[l]}
        </button>
      ))}
    </div>
  );
}
