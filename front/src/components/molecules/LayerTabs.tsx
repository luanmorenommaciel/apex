export type Layer = "stage_dag" | "plan_operators" | "pipeline_lanes";

const LABELS: Record<Layer, string> = {
  stage_dag: "stage dag",
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
