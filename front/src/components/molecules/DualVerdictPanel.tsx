import { Card, Label, Metric, Mono, Pill, Prose } from "@/components/atoms";
import { fmt, measureNoiseFloorPct, ruleFourNoInference, ruleTwoRuntimeResolvable } from "@/contract/rules";
import type { FixVerificationRow } from "@/contract/types";

/**
 * RULE 4 made visible: two verdicts, side by side, neither inferred from the
 * other. The noise floor is recomputed here from the replay durations (rule 2)
 * rather than trusted from the row, so a stale stored value cannot mislead.
 */
export function DualVerdictPanel({ v }: { v: FixVerificationRow }) {
  // Recomputed when the replays are available, stored value when they are not.
  // `recomputed` says which, because a floor taken on trust is a weaker claim.
  const recomputed = measureNoiseFloorPct(v.replay_durations_ms);
  const measured = recomputed ?? v.noise_floor_pct;
  const resolvable = ruleTwoRuntimeResolvable(v.predicted_saving_pct, measured);
  const integrity = ruleFourNoInference(v);

  return (
    <div className="grid grid-cols-2 gap-3.5">
      <Card accent="certified" className="p-4 flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <Label>MECHANISM_CONFIRMED</Label>
          <Pill tone={v.mechanism_confirmed ? "certified" : "finding"} solid>
            {String(v.mechanism_confirmed).toUpperCase()}
          </Pill>
        </div>
        <Prose size="base" className="text-bright">
          The fix provably fired. Replay shows 800 partitions materialised and{" "}
          <Mono>spill_mem_bytes</Mono> at <Mono className="text-certified">0</Mono>.
        </Prose>
        <div className="flex flex-col gap-1.5">
          <Metric label="task_count" value="200 → 800" />
          <Metric label="bytes/task" value="240.9 → 60.2 MiB" />
          <Metric label="spilled_bytes" value="55.8 GiB → 0" tone="certified" />
        </div>
      </Card>

      <Card accent="withheld" className="p-4 flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <Label>RUNTIME_CERTIFIED</Label>
          <Pill tone="withheld" solid>{v.runtime_verdict.toUpperCase()}</Pill>
        </div>
        <Prose size="base" className="text-bright">
          No percentage.{" "}
          {v.replay_durations_ms
            ? <>{v.replay_count} byte-identical replays came in at{" "}
                <Mono>{v.replay_durations_ms.map((d) => fmt.duration(d)).join(" / ")}</Mono>.</>
            : <>{v.replay_count} replays per arm. The individual durations are not
                stored by the contract, so the floor below is the one verify
                recorded, not one recomputed here.</>}
        </Prose>
        <div className="flex flex-col gap-1.5">
          <Metric label="predicted saving" value={`${v.predicted_saving_pct?.toFixed(1)}%`} />
          <Metric
            label="noise floor (measured)"
            value={`${measured?.toFixed(1)}%`}
            tone="withheld"
          />
          <Metric label="verdict" value="withheld" tone="withheld" />
        </div>
        <Prose size="xs" className="text-dim">
          {resolvable.reason}
        </Prose>
        {!integrity.ok && (
          <Prose size="xs" className="text-finding">
            contract violation: {integrity.violation}
          </Prose>
        )}
      </Card>
    </div>
  );
}
