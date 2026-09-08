import { Card, Label, Metric, Mono, Pill, Prose, VerdictPill } from "@/components/atoms";
import {
  fmt, measureNoiseFloorPct, parseProposal, ruleFourNoInference, ruleTwoRuntimeResolvable,
} from "@/contract/rules";
import type { FixVerificationRow } from "@/contract/types";

/**
 * RULE 4 made visible: two verdicts side by side, neither inferred from the
 * other. Everything on screen is read off the row.
 *
 * What was removed matters more than what stayed. This panel used to assert a
 * mechanism in prose — "replay shows 800 partitions materialised and
 * spill_mem_bytes at 0" — over a metric block reading 200 -> 800 tasks,
 * 240.9 -> 60.2 MiB/task and 55.8 GiB -> 0 spilled. None of those six numbers
 * exist in the contract. `apex.fix_verifications` stores a proposal, the two
 * arms' medians, a floor and a replay count, and NO per-stage before/after at
 * all. They were the recorded run's numbers, printed over every row that
 * reached this component.
 *
 * The mechanism pill is the other half: `mechanism_confirmed` has no source in
 * v0.5 and arrives null from the live store. Rendering `String(null)` in a red
 * pill convicted every fix of not firing on the strength of a column that does
 * not exist — deriving one verdict from the absence of the other, which is the
 * single thing rule 4 forbids.
 */
export function DualVerdictPanel({ v }: { v: FixVerificationRow }) {
  // Recomputed when the replay set is available, the stored value when it is
  // not. WHICH one is on screen is labelled, because a floor taken on trust is
  // a weaker claim than one measured here.
  const recomputed = measureNoiseFloorPct(v.replay_durations_ms);
  const measured = recomputed ?? v.noise_floor_pct;
  const resolvable = ruleTwoRuntimeResolvable(v.predicted_saving_pct, measured);
  const integrity = ruleFourNoInference(v);
  const proposal = parseProposal(v.proposed_diff);

  const runtimeTone = v.runtime_verdict === "unresolved"
    ? "withheld"
    : v.runtime_certified
      ? "certified"
      : "finding";

  return (
    <div className="grid grid-cols-2 gap-3.5">
      <Card
        accent={
          v.mechanism_confirmed === null
            ? "withheld"
            : v.mechanism_confirmed
              ? "certified"
              : "finding"
        }
        className="p-4 flex flex-col gap-2.5"
      >
        <div className="flex items-center justify-between">
          <Label>MECHANISM_CONFIRMED</Label>
          <VerdictPill value={v.mechanism_confirmed} label="NOT STORED" />
        </div>
        <Prose size="base" className="text-bright">
          {v.mechanism_confirmed === null ? (
            <>
              Not stored. Nothing in contract v0.5 records whether the fix fired:
              the nearest columns say something was executed safely, which is a
              different claim. Deriving this from the runtime verdict beside it
              is precisely what rule 4 forbids.
            </>
          ) : v.mechanism_confirmed ? (
            <>The verify lane recorded that the fix demonstrably fired.</>
          ) : (
            <>The verify lane recorded that the fix did not fire.</>
          )}
        </Prose>

        <div className="flex flex-col gap-1.5">
          <Label>WHAT WAS EVALUATED</Label>
          {proposal ? (
            Object.entries(proposal).map(([k, val]) => (
              <Metric key={k} label={k} value={val} />
            ))
          ) : (
            <Prose size="xs" className="text-dim">
              The proposal could not be read as a conf overlay, so no key is
              listed rather than one being inferred from the text.
            </Prose>
          )}
        </div>

        <Prose size="xs" className="text-dim">
          No before/after appears here because the row carries none:{" "}
          <Mono className="text-body2">apex.fix_verifications</Mono> stores the
          proposal, the two arms&rsquo; medians, the floor and the replay count.
        </Prose>
      </Card>

      <Card accent="withheld" className="p-4 flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <Label>RUNTIME_CERTIFIED</Label>
          <Pill tone={runtimeTone} solid>{v.runtime_verdict.toUpperCase()}</Pill>
        </div>
        <Prose size="base" className="text-bright">
          {v.replay_durations_ms ? (
            <>
              {v.replay_count} byte-identical replays per arm came in at{" "}
              <Mono>{v.replay_durations_ms.map((d) => fmt.duration(d)).join(" / ")}</Mono>.
            </>
          ) : (
            <>
              {v.replay_count} replays per arm. The individual durations are not
              stored by the contract — only the two arms&rsquo; medians — so the
              floor below is the one verify recorded, not one recomputed here.
            </>
          )}
        </Prose>
        <div className="flex flex-col gap-1.5">
          <Metric label="predicted saving" value={fmt.pctOrDash(v.predicted_saving_pct)} />
          {/* The label names its own provenance. It read "(measured)" even on
              the fallback path, where nothing had been measured here at all. */}
          <Metric
            label={recomputed !== null ? "noise floor · measured here" : "noise floor · as stored"}
            value={fmt.pctOrDash(measured)}
            tone="withheld"
          />
          <Metric label="runtime_verdict" value={v.runtime_verdict} tone={runtimeTone} />
        </div>
        <Prose size="xs" className="text-dim">{resolvable.reason}</Prose>
        {!integrity.ok && (
          <Prose size="xs" className="text-finding">
            contract violation: {integrity.violation}
          </Prose>
        )}
      </Card>
    </div>
  );
}
