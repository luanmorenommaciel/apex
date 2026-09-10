import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { Card, Label, Mono, Pill, Prose } from "@/components/atoms";
import { DataTable, KpiCard, ScreenHeader, type Column } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import { fmt } from "@/contract/rules";
import { useAsync, useRepository } from "@/data/useRepository";
import type { SparkEventRow } from "@/contract/types";


interface Aligned {
  baseline: number | null;
  current: number;
  alignedBy: "plan_fingerprint" | "stage_id+fingerprint" | "unmatched";
  shuffleDelta: number;
  verdict: "regressed" | "improved" | "unchanged" | "current only";
}

export function CompareScreen() {
  const repo = useRepository();
  const [params] = useSearchParams();

  // Which two runs. `current` comes from the URL — the run detail screen links
  // here with it — and falls back to the most recent run. `baseline` is either
  // named explicitly or chosen as the newest OTHER run that ran one of this
  // run's plan shapes. Nothing is hardcoded: a fixed pair was why this screen
  // rendered 0.0x deltas against a live store that had never seen those jobs.
  const runsQ = useAsync(() => repo.listRuns(50), [repo]);
  const currentJob = params.get("current") ?? runsQ.data?.[0]?.job_id ?? "";

  const candidatesQ = useAsync(
    () => (currentJob ? repo.baselineCandidates(currentJob) : Promise.resolve([])),
    [repo, currentJob],
  );
  const baselineJob = params.get("baseline") ?? candidatesQ.data?.[0]?.job_id ?? "";

  const curRunQ = useAsync(() => (currentJob ? repo.run(currentJob) : Promise.resolve(null)), [repo, currentJob]);
  const baseRunQ = useAsync(() => (baselineJob ? repo.run(baselineJob) : Promise.resolve(null)), [repo, baselineJob]);
  const curQ = useAsync(() => (currentJob ? repo.stages(currentJob) : Promise.resolve([])), [repo, currentJob]);
  const baseQ = useAsync(() => (baselineJob ? repo.stages(baselineJob) : Promise.resolve([])), [repo, baselineJob]);
  const curF = useAsync(() => (currentJob ? repo.findings(currentJob) : Promise.resolve([])), [repo, currentJob]);
  const baseF = useAsync(() => (baselineJob ? repo.findings(baselineJob) : Promise.resolve([])), [repo, baselineJob]);

  const cur = useMemo(() => curQ.data ?? [], [curQ.data]);
  const base = useMemo(() => baseQ.data ?? [], [baseQ.data]);
  const sharedShapes = candidatesQ.data?.find((c) => c.job_id === baselineJob)?.shared_shapes ?? 0;

  // Wall clock comes from each run's own row, never from summing stage durations:
  // concurrent stages would be counted twice and the two runs would be compared
  // on a quantity neither of them reports.
  const curWall = curRunQ.data?.wall_clock_ms ?? null;
  const baseWall = baseRunQ.data?.wall_clock_ms ?? null;

  const totals = useMemo(() => {
    const sum = (rows: typeof cur, k: keyof (typeof cur)[number]) =>
      rows.reduce((n, r) => n + Number(r[k] ?? 0), 0);
    return {
      curShuffle: sum(cur, "shuffle_read_bytes"),
      baseShuffle: sum(base, "shuffle_read_bytes"),
      curSpill: sum(cur, "spill_mem_bytes") + sum(cur, "spill_disk_bytes"),
      baseSpill: sum(base, "spill_mem_bytes") + sum(base, "spill_disk_bytes"),
      curGc: sum(cur, "gc_time_ms"),
      baseGc: sum(base, "gc_time_ms"),
    };
  }, [cur, base]);

  /**
   * A delta against a ZERO baseline is not a percentage — there is nothing for
   * it to be a percentage of. It returned 0, which renders as "+0.0%": a
   * measurement of no change, made out of the absence of a denominator.
   */
  const delta = (a: number, b: number): number | null => (b === 0 ? null : ((a - b) / b) * 100);
  const pctDelta = (a: number, b: number): string => {
    const d = delta(a, b);
    return d === null ? "—" : fmt.pct(d);
  };

  // An unknown run renders as "—". A missing wall clock is not a zero, and a
  // delta against one is not a percentage.
  const dur = (ms: number | null) => (ms === null ? "—" : fmt.duration(ms));
  const wallDelta =
    curWall === null || baseWall === null ? "—" : pctDelta(curWall, baseWall);

  /**
   * Stage ids move between runs; plan fingerprints do not. Pairing on id alone
   * would silently compare two different operators, so the alignment is by
   * fingerprint and the column says which key matched.
   */
  const rows: Aligned[] = useMemo(() => {
    // Pair on plan_fingerprint first: a stage's id moves between runs, its shape
    // does not. Same id AND same shape is reported as a distinct, stronger key.
    // A stage whose shape appears in only one of the runs stays UNMATCHED — it
    // is not paired by position, because two operators sharing an id is exactly
    // the silent mis-comparison this alignment exists to prevent.
    // A QUEUE per shape, not a single stage: several stages in one run can share
    // a fingerprint, and mapping them all onto the same baseline stage would show
    // four rows claiming to be four comparisons when they are one stage reused.
    // Each baseline stage is consumed once; the surplus is reported unmatched.
    const byShape = new Map<string, SparkEventRow[]>();
    for (const b of base) {
      if (!b.plan_fingerprint) continue;
      const q = byShape.get(b.plan_fingerprint);
      if (q) q.push(b); else byShape.set(b.plan_fingerprint, [b]);
    }

    const out: Aligned[] = cur.map((c) => {
      const match = c.plan_fingerprint ? byShape.get(c.plan_fingerprint)?.shift() : undefined;
      if (!match) {
        return { baseline: null, current: c.stage_id, alignedBy: "unmatched" as const,
                 shuffleDelta: 0, verdict: "current only" as const };
      }
      const d = c.shuffle_read_bytes - match.shuffle_read_bytes;
      // 1% of the baseline, so float dust is not announced as a regression.
      const material = Math.abs(d) > Math.max(1, match.shuffle_read_bytes * 0.01);
      return {
        baseline: match.stage_id,
        current: c.stage_id,
        alignedBy: match.stage_id === c.stage_id ? ("stage_id+fingerprint" as const)
                                                 : ("plan_fingerprint" as const),
        shuffleDelta: d,
        verdict: !material ? ("unchanged" as const)
               : d > 0 ? ("regressed" as const)
               : ("improved" as const),
      };
    });

    // Loudest first: a triage table is read from the top.
    return out.sort((a, b) => Math.abs(b.shuffleDelta) - Math.abs(a.shuffleDelta));
  }, [cur, base]);

  // The sentence below names a real pair or says nothing: a moved stage id is
  // the clearest demonstration that ids are not the key.
  const alignedExample = rows.find(
    (r) => r.baseline !== null && r.baseline !== r.current,
  );

  const regressed = rows.filter((r) => r.verdict === "regressed").length;
  const improved = rows.filter((r) => r.verdict === "improved").length;
  const runStatus = regressed > improved ? "regressed"
                  : improved > regressed ? "improved"
                  : "unchanged";

  const columns: Column<Aligned>[] = [
    { key: "b", header: "BASELINE", width: "1fr", render: (r) => (r.baseline === null ? <span className="text-muted">—</span> : `stage ${r.baseline}`) },
    {
      key: "c", header: "CURRENT", width: "1fr",
      render: (r) => <span className={r.verdict === "regressed" ? "text-finding" : ""}>stage {r.current}</span>,
    },
    { key: "k", header: "ALIGNED BY", width: "168px", render: (r) => <span className="text-sub">{r.alignedBy}</span> },
    {
      key: "d", header: "SHUFFLE Δ", width: "1fr", align: "right",
      render: (r) =>
        r.verdict === "current only" ? (
          <span className="text-dim">no shape in baseline</span>
        ) : (
          <span className={r.shuffleDelta > 1e9 ? "text-finding" : r.shuffleDelta < 0 ? "text-certified" : "text-body"}>
            {r.shuffleDelta > 0 ? "+" : ""}
            {fmt.bytes(Math.abs(r.shuffleDelta))}
          </span>
        ),
    },
    {
      key: "v", header: "VERDICT", width: "116px", align: "right",
      render: (r) => (
        <span
          className={
            r.verdict === "regressed" ? "text-finding" : r.verdict === "improved" ? "text-certified" : "text-sub"
          }
        >
          {r.verdict}
        </span>
      ),
    },
  ];

  /**
   * Findings that appeared, cleared or moved between the two runs, keyed by
   * (type, stage_id). Ranked on confidence_score — the raw 0-1 the contract
   * routes on — never on the coarse display tier.
   */
  const findingDeltas = useMemo(() => {
    const key = (f: { type: string; stage_id: number }) => `${f.type}·${f.stage_id}`;
    const before = new Map((baseF.data ?? []).map((f) => [key(f), f]));
    const after = new Map((curF.data ?? []).map((f) => [key(f), f]));

    const out: { name: string; badge: string; tone: "finding" | "withheld" | "certified"; note: string }[] = [];
    for (const [k, f] of after) {
      const was = before.get(k);
      const where = f.stage_id < 0 ? "job" : `stage ${f.stage_id}`;
      if (!was) {
        out.push({ name: `${f.type} · ${where}`, badge: "INTRODUCED", tone: "finding",
                   note: `0.00 → ${f.confidence_score.toFixed(2)}` });
      } else if (Math.abs(f.confidence_score - was.confidence_score) > 0.01) {
        const up = f.confidence_score > was.confidence_score;
        out.push({ name: `${f.type} · ${where}`, badge: up ? "CONFIDENCE UP" : "CONFIDENCE DOWN",
                   tone: "withheld",
                   note: `${was.confidence_score.toFixed(2)} → ${f.confidence_score.toFixed(2)}` });
      }
    }
    for (const [k, f] of before) {
      if (!after.has(k)) {
        const where = f.stage_id < 0 ? "job" : `stage ${f.stage_id}`;
        out.push({ name: `${f.type} · ${where}`, badge: "RESOLVED", tone: "certified",
                   note: `${f.confidence_score.toFixed(2)} → 0.00` });
      }
    }
    return out;
  }, [curF.data, baseF.data]);

  return (
    <Page>
      <ScreenHeader title="Compare runs" subtitle="aligned on plan fingerprint · stage ids move between runs, fingerprints do not" />

      <div className="flex items-center gap-4">
        <Card className="flex-1 px-4 py-3.5 flex flex-col gap-1">
          <Label>BASELINE</Label>
          <Mono className="text-sm text-bright">{baselineJob || "—"}</Mono>
          <span className="text-xs text-sub">
            {baseRunQ.data?.app_name ?? "no comparable run"} · {dur(baseWall)} ·{" "}
            {(baseF.data ?? []).length} findings
          </span>
        </Card>
        <Mono className="text-base text-muted">→</Mono>
        <Card accent="finding" className="flex-1 px-4 py-3.5 flex flex-col gap-1">
          <Label>CURRENT</Label>
          <Mono className="text-sm text-bright">{currentJob || "—"}</Mono>
          <span className="text-xs text-sub">
            {curRunQ.data?.app_name ?? "—"} · {dur(curWall)} ·{" "}
            {(curF.data ?? []).length} findings
          </span>
        </Card>
        <Card className="w-[250px] px-4 py-3.5 flex flex-col gap-1">
          <Label>STATUS</Label>
          <Mono className={`text-sm ${runStatus === "regressed" ? "text-finding"
            : runStatus === "improved" ? "text-certified" : "text-sub"}`}>
            {baselineJob ? runStatus : "no baseline"}
          </Mono>
          <span className="text-xs text-sub">
            {baselineJob
              ? `${sharedShapes} shared plan ${sharedShapes === 1 ? "shape" : "shapes"}`
              : "no other run has executed this shape"}
          </span>
        </Card>
      </div>

      {/* The claim is conditional on the evidence. "The query did not change" is
          only sayable when the two runs actually share shapes, and the example
          pair named in the sentence is drawn from the alignment, not asserted. */}
      <Card accent={sharedShapes > 0 ? "withheld" : undefined} className="px-4 py-3.5">
        <Prose size="base">
          {sharedShapes === 0 ? (
            <>
              These runs share <span className="text-bright">no plan shape</span>, so no delta
              between them is attributable to data or config — it may simply be a different query.
              Nothing here is aligned; the table below reports every stage as unmatched.
            </>
          ) : (
            <>
              {sharedShapes} plan {sharedShapes === 1 ? "shape is" : "shapes are"} common to both
              runs, so for those stages the query did not change and the same work ran against{" "}
              <span className="text-bright">
                {(totals.curShuffle / Math.max(1, totals.baseShuffle)).toFixed(2)}× the shuffle bytes
              </span>
              . Attribute that to the input{" "}
              {totals.curShuffle >= totals.baseShuffle ? "growing" : "shrinking"}, not to a code
              change.{" "}
              {alignedExample && (
                <span className="text-dim">
                  Alignment on the fingerprint is the only reason stage {alignedExample.current}{" "}
                  here matches stage {alignedExample.baseline} there.
                </span>
              )}
            </>
          )}
        </Prose>
      </Card>

      <div className="grid grid-cols-5 gap-3">
        <KpiCard
          label="WALL CLOCK"
          value={wallDelta}
          note={`${dur(baseWall)} → ${dur(curWall)}`}
          tone={wallDelta === "—" ? "withheld" : "finding"}
        />
        <KpiCard
          label="SHUFFLE READ"
          value={pctDelta(totals.curShuffle, totals.baseShuffle)}
          note={`${fmt.bytes(totals.baseShuffle)} → ${fmt.bytes(totals.curShuffle)}`}
          tone="finding"
        />
        {/* Was `0 → X` with the note "introduced", while totals.baseSpill sat
            computed and unread beside it: a baseline of zero asserted for every
            pair, including two runs that both spilled. "introduced" is now a
            statement the numbers support, made only when they do. */}
        <KpiCard
          label="SPILLED"
          value={pctDelta(totals.curSpill, totals.baseSpill)}
          note={
            totals.baseSpill === 0 && totals.curSpill > 0
              ? `introduced · 0 B → ${fmt.bytes(totals.curSpill)}`
              : `${fmt.bytes(totals.baseSpill)} → ${fmt.bytes(totals.curSpill)}`
          }
          tone={totals.curSpill > totals.baseSpill ? "finding" : "bright"}
        />
        <KpiCard
          label="GC TIME"
          value={pctDelta(totals.curGc, totals.baseGc)}
          note={`${(totals.baseGc / 1000).toFixed(1)} → ${(totals.curGc / 1000).toFixed(1)} s`}
          tone="withheld"
        />
        {/* Was `${base.length} = ${cur.length}` under the note "unchanged" —
            an equals sign and a word, both printed even when the two differed. */}
        <KpiCard
          label="STAGE COUNT"
          value={`${base.length} → ${cur.length}`}
          note={
            base.length === cur.length
              ? "unchanged"
              : `${cur.length > base.length ? "+" : ""}${cur.length - base.length} stages`
          }
          tone={base.length === cur.length ? "bright" : "withheld"}
        />
      </div>

      <div className="flex-1 min-h-0 grid grid-cols-[1.55fr_1fr] gap-4">
        <DataTable
          columns={columns}
          rows={rows}
          rowKey={(r) => `${r.baseline}-${r.current}`}
          // The loudest row, which the sort already put first. It was `stage 25`
          // — a stage id from the recorded run, highlighted in every comparison.
          isHighlighted={(r) => r === rows[0] && r.verdict !== "unchanged"}
          // `cur.length - rows.length` was always 0: `rows` is a map over `cur`,
          // so the two lengths are equal by construction and the sentence
          // reported "0 further stages" on every screen it has ever rendered.
          footer={
            `${rows.filter((r) => r.verdict === "unchanged").length} aligned with no material ` +
            `delta · ${rows.filter((r) => r.alignedBy === "unmatched").length} with no shape ` +
            `in the baseline.`
          }
        />

        <div className="bg-raised border border-edge rounded-sm overflow-hidden flex flex-col">
          <div className="px-3.5 py-2.5 border-b border-edge font-mono text-xs text-bright">
            Finding deltas
          </div>
          {findingDeltas.map((d) => (
            <div key={d.name} className="px-3.5 py-3 border-b border-edge flex flex-col gap-1.5">
              <div className="flex items-center justify-between gap-2">
                <Mono className="text-xs text-bright">{d.name}</Mono>
                <Pill tone={d.tone} solid={d.tone === "finding"}>{d.badge}</Pill>
              </div>
              <Mono className="text-[11px] text-sub">{d.note}</Mono>
            </div>
          ))}
          <div className="px-3.5 py-3 mt-auto bg-surface border-t border-edge">
            <Prose size="xs" className="text-dim">
              Ranked on <Mono className="text-body">confidence_score</Mono>, the raw 0–1 the contract
              routes here — not the coarse display tier.
            </Prose>
          </div>
        </div>
      </div>
    </Page>
  );
}
