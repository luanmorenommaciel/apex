import { useState } from "react";
import { Link } from "react-router-dom";
import { Card, Diff, Label, Metric, Mono, Pill, Prose } from "@/components/atoms";
import { ScreenHeader } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";

/**
 * Natural-language in, STRUCTURED DIAGNOSTIC out — verdict, evidence,
 * mechanism, recommendation, and what will not be claimed. Prose appears only
 * where prose is the answer.
 *
 * The console and the MCP server read the same tables and return the same four
 * tool results; this screen is one of two front doors, not a second product.
 */
type Turn =
  | { role: "user"; text: string }
  | { role: "apex"; kind: "claim" }
  | { role: "apex"; kind: "refusal" };

const SCRIPT: Turn[] = [
  { role: "user", text: "spill" },
  { role: "apex", kind: "claim" },
  { role: "user", text: "stage6" },
  { role: "apex", kind: "refusal" },
];

const SUGGESTIONS = [
  "what regressed since Monday?",
  "is this skew or spill?",
  "has anything fixed this before?",
];

export function AskScreen() {
  const [turns, setTurns] = useState<Turn[]>(SCRIPT.slice(0, 2));
  const [draft, setDraft] = useState("");
  const [thinking, setThinking] = useState(false);

  const send = (text: string) => {
    if (!text.trim() || thinking) return;
    setDraft("");
    setTurns((t) => [...t, { role: "user", text }]);
    setThinking(true);
    // A mockup: the second answer is the scripted refusal, because a console
    // that only ever agrees is the thing this product is arguing against.
    window.setTimeout(() => {
      setTurns((t) => [...t, { role: "apex", kind: t.length >= 3 ? "refusal" : "claim" }]);
      setThinking(false);
    }, 900);
  };

  return (
    <Page className="!py-0 !px-0">
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0 flex flex-col border-r border-edge">
          <div className="px-7 pt-6 pb-2 shrink-0">
            <ScreenHeader
              title="Ask Apex"
              subtitle={
                <>
                  scope <Mono className="text-body2">app-20260803014217-0071</Mono> · 4 tools ·
                  read-only
                </>
              }
            />
          </div>

          <div className="flex-1 min-h-0 overflow-auto px-7 py-5 flex flex-col gap-5">
            {turns.map((t, i) =>
              t.role === "user" ? (
                <div key={i} className="flex justify-end">
                  <div className="max-w-[720px] bg-raised border border-edge2 rounded-sm px-4 py-3 text-sm leading-relaxed text-bright">
                    {t.text === "spill" ? (
                      <>
                        I have a problem with job{" "}
                        <Mono className="text-spark">…14217-0071</Mono> — it went from 11 to 18
                        minutes and stage 25 keeps spilling. Can you recommend something?
                      </>
                    ) : t.text === "stage6" ? (
                      <>But stage 6 shows 10.97× in the Spark UI. Isn't that the real problem?</>
                    ) : (
                      t.text
                    )}
                  </div>
                </div>
              ) : t.kind === "claim" ? (
                <ClaimCard key={i} />
              ) : (
                <RefusalCard key={i} />
              ),
            )}
            {thinking && (
              <div className="flex items-center gap-2.5 font-mono text-[11px] text-dim">
                <span className="w-1.5 h-1.5 rounded-full bg-spark animate-pulse" />
                querying spark_events, findings, job_conf…
              </div>
            )}
          </div>

          <div className="shrink-0 px-7 pt-4 pb-5 border-t border-edge flex flex-col gap-2.5">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(draft);
              }}
              className="flex items-center gap-3 bg-raised border border-edge2 rounded-sm px-3.5 py-3 focus-within:border-spark transition-colors"
            >
              <Mono className="text-sm text-spark">^</Mono>
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Ask by job ID, or in plain language — “why did the rollup get slower this week?”"
                className="flex-1 bg-transparent outline-none text-sm text-bright placeholder:text-muted"
              />
              <Mono className="text-[10px] text-muted">⏎ send</Mono>
            </form>
            <div className="flex items-center justify-between gap-4">
              <div className="flex gap-2 font-mono text-[11px]">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => send(s)}
                    className="px-2.5 py-1.5 bg-surface border border-edge rounded-sm text-sub hover:text-body2 hover:border-edge2 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
              <span className="text-[11px] text-muted">
                Answers are backed by measurements. Text from your job is quoted as data, never
                followed.
              </span>
            </div>
          </div>
        </div>

        <aside className="w-[318px] shrink-0 bg-[#1a1d1e] px-5 py-6 flex flex-col gap-6 overflow-auto">
          <div className="flex flex-col gap-2.5">
            <Label>CITED EVIDENCE</Label>
            {[
              { accent: "finding" as const, t: "findings · f-7c41e9", s: "SPILL · stage 25 · 0.94" },
              { accent: "edge" as const, t: "spark_events · stage 25", s: "attempt 1 · argMax(col, ts)" },
              { accent: "edge" as const, t: "job_conf · 8 keys", s: "shuffle.partitions = 200" },
              { accent: "memory" as const, t: "plan_memory · 7 runs", s: "same fingerprint" },
            ].map((e) => (
              <Card key={e.t} accent={e.accent} className="px-3 py-2.5 flex flex-col gap-1">
                <Mono className="text-[11px] text-bright">{e.t}</Mono>
                <span className="text-xs text-sub">{e.s}</span>
              </Card>
            ))}
          </div>

          <div className="flex flex-col gap-2.5">
            <Label>SCOPE</Label>
            <Metric label="job" value="…14217-0071" />
            <Metric label="baseline" value="…31455-0069" />
            <Metric label="window" value="7 d" />
          </div>

          <Card className="p-3 mt-auto flex flex-col gap-2">
            <Label tone="withheld">SAME ANSWER IN YOUR EDITOR</Label>
            <div className="font-mono text-[10.5px] leading-[1.7] text-body">
              claude mcp add --scope project \
              <br />
              &nbsp;&nbsp;apex -- uvx apex-mcp
            </div>
            <Prose size="xs" className="text-dim">
              The console and the MCP server read the same tables and return the same four tool
              results.
            </Prose>
          </Card>
        </aside>
      </div>
    </Page>
  );
}

function ClaimCard() {
  return (
    <div className="flex gap-3.5">
      <img src="/apex-star.png" alt="" className="w-5 h-5 mt-1 shrink-0 object-contain" />
      <div className="flex-1 min-w-0 flex flex-col gap-3.5">
        <div className="flex items-center gap-2 flex-wrap font-mono text-[10px]">
          <span className="text-muted">resolved:</span>
          {[
            ["analyze_run · 34 stages", "text-certified"],
            ["compare_runs · …55-0069", "text-certified"],
            ["search_kb · 7 hits", "text-certified"],
            ["recall · 7 prior runs", "text-memory"],
          ].map(([t, c]) => (
            <span key={t} className={`px-1.5 py-0.5 bg-raised border border-edge rounded-sm ${c}`}>
              {t}
            </span>
          ))}
          <span className="text-muted">
            · llm_calls <span className="text-certified">1</span> · 2.4 s
          </span>
        </div>

        <Card accent="finding" className="overflow-hidden">
          <div className="p-4 flex flex-col gap-2.5 border-b border-edge">
            <div className="flex items-center gap-2.5 flex-wrap">
              <Label>VERDICT</Label>
              <Pill tone="finding" solid>CRITICAL</Pill>
              <Pill tone="certified">HIGH · 0.94</Pill>
              <Mono className="text-[11px] text-sub">SPILL · stage 25</Mono>
            </div>
            <div className="text-base leading-snug text-bright">
              Stage 25 is memory-bound, not skewed. Its build side no longer fits execution memory
              after the input grew 1.9×.
            </div>
          </div>

          <div className="grid grid-cols-2">
            <div className="p-4 border-r border-b border-edge flex flex-col gap-2.5">
              <Label>EVIDENCE · MEASURED</Label>
              <Metric label="spill_mem / disk" value="48.2 / 7.6 GiB" tone="finding" />
              <Metric label="peak_exec_mem" value="16.0 GiB = limit" />
              <Metric label="bytes/task" value="240.6 MiB" />
              <Metric label="p99/p50" value="1.42×" note="balanced" />
              <Metric label="shuffle_read Δ vs 0069" value="+1.9×" tone="finding" />
            </div>
            <div className="p-4 border-b border-edge flex flex-col gap-2.5">
              <Label>MECHANISM</Label>
              <Prose>
                Plan fingerprint is <span className="text-bright">unchanged</span> from the 11-minute
                run, so this is not a query regression — the same work met more data. Every task
                moves ~241 MiB against 16 GiB shared by cores, so tasks spill in lockstep. That is
                why the ratio is flat at 1.42×.
              </Prose>
            </div>
          </div>

          <div className="p-4 flex flex-col gap-3 border-b border-edge">
            <Label>RECOMMENDATION</Label>
            <Diff text={"- spark.sql.shuffle.partitions      200\n+ spark.sql.shuffle.partitions      800\n+ spark.memory.fraction             0.75"} />
            <div className="flex items-center gap-2.5 font-mono text-[10px]">
              <span className="px-1.5 py-0.5 bg-raised border border-edge2 rounded-sm text-withheld">
                requires_human_approval: true
              </span>
              <span className="px-1.5 py-0.5 bg-raised border border-edge2 rounded-sm text-certified">
                applied: false
              </span>
              <span className="text-muted">no file written · no git · no PR</span>
            </div>
          </div>

          <div className="p-4 flex flex-col gap-2 bg-withheld/[0.05]">
            <Label tone="withheld">WHAT I WILL NOT CLAIM</Label>
            <Prose>
              A runtime saving. Predicted effect is 11%; the measured noise floor on this plan shape
              is <Mono className="text-withheld">17.4%</Mono>, so the delta is{" "}
              <Mono className="text-withheld">runtime_unresolved</Mono> — unresolvable, which is not
              the same as zero.
            </Prose>
            <Prose>
              That skew is your problem. Five stages carried a tail; none is a distribution above the
              volume floor. <Link to="/runs/app-20260803014217-0071">See the five refusals</Link>.
            </Prose>
          </div>
        </Card>
      </div>
    </div>
  );
}

function RefusalCard() {
  return (
    <div className="flex gap-3.5">
      <img src="/apex-star.png" alt="" className="w-5 h-5 mt-1 shrink-0 object-contain" />
      <Card accent="edge" className="flex-1 min-w-0 p-4 flex flex-col gap-2.5">
        <div className="flex items-center gap-2.5">
          <Label>VERDICT</Label>
          <Pill tone="neutral">NO CLAIM</Pill>
          <Mono className="text-[11px] text-sub">stage 6 · 50 tasks</Mono>
        </div>
        <div className="text-[15px] leading-snug text-bright">
          No. Stage 6 moves <Mono className="text-spark">427 bytes per task</Mono>.
        </div>
        <Prose>
          At that volume p99/p50 measures JVM warm-up and scheduler dispatch, not a data
          distribution. The ratio is real; the skew it implies is not. Rule 1's computed bar would
          need a cluster of more than 5.5 slots for the ratio to clear at all — and even then the
          volume floor refuses it. Stage 6's total contribution to wall-clock is 0.4%.
        </Prose>
        <Mono className="text-[10px] text-muted">
          a ratio-ranking tool would have led with this stage · floor shared by engine · verify ·
          serve
        </Mono>
      </Card>
    </div>
  );
}
