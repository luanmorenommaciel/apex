import { Label, Mono, Prose } from "@/components/atoms";
import type { RuleVerdict } from "@/contract/rules";
import { isVacant } from "@/contract/rules";

export interface Guardrail {
  name: string;
  rule: string;
  verdict: RuleVerdict;
}

/** Every gate the engine ran before a proposal was allowed on screen. */
export function GuardrailList({ items }: { items: Guardrail[] }) {
  return (
    <div className="bg-raised border border-edge rounded-sm p-4 flex flex-col gap-2.5">
      <Label>GUARDRAILS RUN BEFORE THIS WAS SHOWN</Label>
      <div className="grid grid-cols-2 gap-x-5 gap-y-2">
        {items.map((g) => {
          // bound to a const so isVacant() narrows the union on the else branch
          const verdict = g.verdict;
          const passed = !isVacant(verdict) && verdict.held;
          return (
            <div key={g.name} className="flex gap-2 text-[13px] leading-snug">
              <Mono className={passed ? "text-certified" : "text-withheld"}>
                {passed ? "✓" : "!"}
              </Mono>
              <Prose size="sm">
                <span className="text-bright">{g.name}</span>{" "}
                <Mono className="text-dim text-[11px]">{g.rule}</Mono> — {g.verdict.reason}
              </Prose>
            </div>
          );
        })}
      </div>
    </div>
  );
}
