import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Mono, Pill, StatusPill } from "@/components/atoms";
import { DataTable, KpiCard, ScreenHeader, type Column, QueryFailure } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import { fmt } from "@/contract/rules";
import { RUN_LIST_DEFAULTS, RUN_LIST_MAX_OFFSET, type RunListFilters } from "@/data/repository";
import { useAsync, useRepository } from "@/data/useRepository";
import type { RunSummary } from "@/contract/types";

type Row = RunSummary & { age?: string };
type Filter = "findings" | "all";

/** One page of the list. The store's default, so page 1 is what every door lists. */
export const RUNS_PAGE_SIZE = RUN_LIST_DEFAULTS.limit;
/** Typing settles for this long before the store is asked again. */
export const RUNS_FILTER_DEBOUNCE_MS = 300;

/** `value`, once it has stopped changing for `ms`. */
function useDebounced<T>(value: T, ms: number): T {
  const [settled, setSettled] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setSettled(value), ms);
    return () => clearTimeout(timer);
  }, [value, ms]);
  return settled;
}

export function RunsScreen() {
  const repo = useRepository();
  const navigate = useNavigate();
  const [prefix, setPrefix] = useState("");
  const [fingerprint, setFingerprint] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  // The page belongs to the filters it was turned under: when they change,
  // the key no longer matches and the list starts again from its first page —
  // derived here rather than reset in an effect, which would fetch twice.
  const [page, setPage] = useState({ key: "", offset: 0 });

  // Filtering is SERVER-side (P7.5): the store applies job_id prefix, plan
  // fingerprint and "has findings" before the page is cut, so a match on page
  // 3 is found from page 1. Filtering the 50 returned rows in the browser
  // answered "which of the newest 50 match", which reads as "which runs match".
  const jobIdPrefix = useDebounced(prefix.trim(), RUNS_FILTER_DEBOUNCE_MS);
  const planFingerprint = useDebounced(fingerprint.trim(), RUNS_FILTER_DEBOUNCE_MS);
  const hasFindings = filter === "findings" ? true : undefined;

  const filterKey = JSON.stringify([jobIdPrefix, planFingerprint, hasFindings ?? null]);
  const offset = page.key === filterKey ? page.offset : 0;
  const turn = (to: number) => setPage({ key: filterKey, offset: Math.max(0, to) });

  const filters: RunListFilters = {
    offset,
    jobIdPrefix: jobIdPrefix || undefined,
    planFingerprint: planFingerprint || undefined,
    hasFindings,
  };
  const { data, loading, error } = useAsync(
    () => repo.listRuns(RUNS_PAGE_SIZE, filters),
    [repo, offset, jobIdPrefix, planFingerprint, hasFindings],
  );
  const runs = useMemo(() => data ?? [], [data]);
  const filtered = jobIdPrefix !== "" || planFingerprint !== "" || hasFindings !== undefined;
  // A full page may have a successor; a short one is the last. The store
  // refuses an offset past its cap, so "next" stops where paging can go.
  const hasNext = runs.length >= RUNS_PAGE_SIZE && offset + RUNS_PAGE_SIZE <= RUN_LIST_MAX_OFFSET;

  /**
   * Each total is summed ONLY over the runs that carry the field, and reports
   * how many those were. Summing a sentinel — refused_count is -1 for "not
   * derivable here" — turned "we did not compute it" into a number, and the
   * denominator quietly stayed at 50 either way.
   */
  const totals = useMemo(() => {
    const withRefused = runs.filter((r) => r.refused_count >= 0);
    const withLlm = runs.filter((r) => r.llm_calls !== null);
    return {
      findings: runs.reduce((n, r) => n + r.finding_count, 0),
      affected: runs.filter((r) => r.finding_count > 0).length,
      refused: withRefused.length === 0
        ? null
        : withRefused.reduce((n, r) => n + r.refused_count, 0),
      refusedRuns: withRefused.length,
      llm: withLlm.length === 0 ? null : withLlm.reduce((n, r) => n + (r.llm_calls ?? 0), 0),
      llmRuns: withLlm.length,
      escalated: withLlm.filter((r) => (r.llm_calls ?? 0) > 0).length,
      // Whether the memory lane has been over a run at all. It is the one
      // cross-lane fact this list can actually establish, and it decides
      // whether /compare and /memory have anything to show.
      indexed: runs.filter((r) => r.shaped_stage_count !== null).length,
    };
  }, [runs]);

  const columns: Column<Row>[] = [
    { key: "job", header: "JOB_ID", width: "250px", render: (r) => r.job_id },
    { key: "app", header: "APP_NAME", width: "1fr", render: (r) => <span className="text-body">{r.app_name}</span> },
    { key: "stages", header: "STAGES", width: "92px", align: "right", render: (r) => <span className="text-body">{r.stage_count}</span> },
    { key: "wall", header: "WALL", width: "88px", align: "right", render: (r) => <span className={r.wall_clock_ms === null ? "text-muted" : "text-body"}>{fmt.durationOrDash(r.wall_clock_ms)}</span> },
    {
      key: "findings", header: "FINDINGS", width: "96px", align: "right",
      render: (r) =>
        r.finding_count === 0 ? (
          <span className="text-sub">0</span>
        ) : (
          <span className={r.status === "warning" ? "text-withheld font-semibold" : "text-finding font-semibold"}>
            {r.finding_count}
          </span>
        ),
    },
    {
      key: "refused", header: "REFUSED", width: "108px", align: "right",
      // -1 means the count is not derivable from the list query. It renders as
      // an em dash, never as zero: "we did not compute it" is not "there were none".
      render: (r) => <span className="text-sub">{r.refused_count < 0 ? "—" : r.refused_count}</span>,
    },
    { key: "status", header: "STATUS", width: "132px", align: "center", render: (r) => <StatusPill status={r.status} /> },
    { key: "age", header: "AGE", width: "96px", align: "right", render: (r) => <span className="text-dim">{r.age ?? ""}</span> },
  ];

  // The filters stay on screen in every state, including a failure: a
  // rejected value (an over-long fingerprint, say) must be correctable where
  // it was typed, not on a screen that has replaced the inputs.
  const controls = (
    <div className="flex gap-2 font-mono text-xs">
      <input
        aria-label="job_id prefix"
        value={prefix}
        onChange={(e) => setPrefix(e.target.value)}
        placeholder="job_id prefix"
        className="w-[200px] bg-raised border border-edge rounded-sm px-2.5 py-[7px] text-body2 placeholder:text-dim outline-none focus:border-spark"
      />
      <input
        aria-label="plan fingerprint"
        value={fingerprint}
        onChange={(e) => setFingerprint(e.target.value)}
        placeholder="plan fingerprint (exact)"
        maxLength={64}
        className="w-[220px] bg-raised border border-edge rounded-sm px-2.5 py-[7px] text-body2 placeholder:text-dim outline-none focus:border-spark"
      />
      {(["findings", "all"] as Filter[]).map((f) => (
        <button
          key={f}
          type="button"
          onClick={() => setFilter(f)}
          className={`px-2.5 py-[7px] bg-raised border rounded-sm transition-colors ${
            filter === f ? "border-edge2 text-bright" : "border-edge text-sub hover:text-body2"
          }`}
        >
          {f === "findings" ? "findings only" : "all"}
        </button>
      ))}
    </div>
  );

  // Only stores that apply the window may claim it. The recording is a fixed
  // past snapshot and is listed whole (FixtureRepository.listRuns).
  const windowLabel = repo.kind === "fixtures" ? "from the recording" : "active in the last 7 days";
  const pageLabel = runs.length === 0
    ? (offset === 0 ? "no runs" : `no runs past ${offset}`)
    : `${runs.length} runs · ${offset + 1}–${offset + runs.length}`;

  const pager = (
    <div className="flex items-center gap-2 font-mono text-xs">
      <button
        type="button"
        disabled={loading || offset === 0}
        onClick={() => turn(offset - RUNS_PAGE_SIZE)}
        className="px-2.5 py-[7px] bg-raised border border-edge rounded-sm text-sub hover:text-body2 disabled:opacity-40"
      >
        ← prev
      </button>
      <button
        type="button"
        disabled={loading || !hasNext}
        onClick={() => turn(offset + RUNS_PAGE_SIZE)}
        className="px-2.5 py-[7px] bg-raised border border-edge rounded-sm text-sub hover:text-body2 disabled:opacity-40"
      >
        next →
      </button>
      {!error && filtered && (
        <>
          <Pill tone="spark">{runs.length} on this page</Pill>
          <span className="text-dim">matching the filters, applied by the store</span>
        </>
      )}
    </div>
  );

  // A rejected query is not a store with no runs. This screen used to keep
  // rendering around the error — "0 most recent applications", KPIs at 0,
  // "No rows match this filter" — every one of them a measured-zero claim
  // about a store it had not read.
  if (error) {
    return (
      <Page>
        <ScreenHeader title="Runs" subtitle="query failed" right={controls} />
        <QueryFailure error={error} source={repo.kind} what="runs" />
        {pager}
      </Page>
    );
  }

  return (
    <Page>
      <ScreenHeader
        title="Runs"
        subtitle={
          loading
            ? "querying…"
            // The window is real now: RUN_LIST lists runs with an event in the
            // last 168 hours (P7.5). Totals below are over THIS page.
            : `${pageLabel}, newest started first, ${windowLabel} · ${totals.affected} carrying an open finding`
        }
        right={controls}
      />


      <div className="grid grid-cols-4 gap-3">
        <KpiCard label="OPEN FINDINGS" value={totals.findings} note="ranked on confidence_score" accent="finding" />
        <KpiCard
          label="CONSIDERED & REFUSED"
          value={fmt.countOrDash(totals.refused)}
          note={
            totals.refused === null
              ? "not derivable list-wide — open a run"
              : `stages with a tail, no claim · ${totals.refusedRuns} of ${runs.length} runs`
          }
          accent="edge"
        />
        <KpiCard
          label="LLM CALLS"
          value={fmt.countOrDash(totals.llm)}
          note={
            totals.llm === null
              ? "no contract table counts model invocations"
              : `${totals.escalated} of ${totals.llmRuns} runs escalated past the gate`
          }
          accent="withheld"
          tone={totals.llm === null ? "withheld" : "bright"}
        />
        {/* Replaces a hardcoded "SIX-LANE GATE · passed · 7/7 tables match DDL".
            The console cannot verify a DDL match, and asserting one from a
            screen is the failure mode this product argues against. This is the
            cross-lane fact the list CAN establish. */}
        <KpiCard
          label="INDEXED BY MEMORY"
          value={`${totals.indexed}/${runs.length}`}
          note={
            totals.indexed === 0
              ? "run_outcomes has no row for these runs"
              : "run_outcomes carries a plan shape for these"
          }
          accent={totals.indexed === 0 ? "withheld" : "certified"}
          tone={totals.indexed === 0 ? "withheld" : "certified"}
        />
      </div>

      <DataTable
        columns={columns}
        rows={runs}
        rowKey={(r) => r.job_id}
        onRowClick={(r) => navigate(`/runs/${r.job_id}`)}
        isHighlighted={(r) => r === runs[0] && !filtered && offset === 0}
        footer={
          <div className="flex items-center gap-2.5">
            <Mono className="text-sub">REFUSED</Mono>
            <span>
              counts stages that carried a p99/p50 tail and produced no finding. A rising number is
              the system working, not failing.
            </span>
          </div>
        }
      />

      {pager}
    </Page>
  );
}
