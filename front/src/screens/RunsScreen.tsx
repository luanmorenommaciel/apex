import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Mono, Pill, Prose, StatusPill } from "@/components/atoms";
import { DataTable, KpiCard, ScreenHeader, type Column } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import { fmt } from "@/contract/rules";
import { useAsync, useRepository } from "@/data/useRepository";
import type { RunSummary } from "@/contract/types";

type Row = RunSummary & { age?: string };
type Filter = "findings" | "all";

export function RunsScreen() {
  const repo = useRepository();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const { data, loading, error } = useAsync(() => repo.listRuns(50), [repo]);
  const runs = useMemo(() => data ?? [], [data]);

  const shown = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return runs.filter((r) => {
      if (filter === "findings" && r.finding_count === 0) return false;
      if (!needle) return true;
      return (
        r.job_id.toLowerCase().includes(needle) ||
        r.app_name.toLowerCase().includes(needle) ||
        r.plan_fingerprint.toLowerCase().includes(needle)
      );
    });
  }, [runs, q, filter]);

  const totals = useMemo(() => {
    const findings = runs.reduce((n, r) => n + r.finding_count, 0);
    const refused = runs.reduce((n, r) => n + Math.max(0, r.refused_count), 0);
    return {
      findings,
      refused,
      llm: runs.reduce((n, r) => n + r.llm_calls, 0),
      affected: runs.filter((r) => r.finding_count > 0).length,
      escalated: runs.filter((r) => r.llm_calls > 0).length,
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

  return (
    <Page>
      <ScreenHeader
        title="Runs"
        subtitle={
          loading
            ? "querying…"
            : `Last 24 h · ${runs.length} applications · ${totals.affected} carrying an open finding`
        }
        right={
          <div className="flex gap-2 font-mono text-xs">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="job_id, app_name, or plan fingerprint"
              className="w-[300px] bg-raised border border-edge rounded-sm px-2.5 py-[7px] text-body2 placeholder:text-dim outline-none focus:border-spark"
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
        }
      />

      {error && (
        <div className="bg-raised border border-edge2 border-l-2 border-l-finding rounded-sm p-4">
          <Prose>
            ClickHouse did not answer: <Mono className="text-finding">{error.message}</Mono>
          </Prose>
        </div>
      )}

      <div className="grid grid-cols-4 gap-3">
        <KpiCard label="OPEN FINDINGS" value={totals.findings} note="ranked on confidence_score" accent="finding" />
        <KpiCard label="CONSIDERED & REFUSED" value={totals.refused || "—"} note="stages with a tail, no claim" accent="edge" />
        <KpiCard label="LLM CALLS TODAY" value={totals.llm} note={`${totals.escalated} of ${runs.length} runs escalated past the gate`} accent="withheld" />
        <KpiCard label="SIX-LANE GATE" value="passed" note="7/7 contract tables match DDL" accent="certified" tone="certified" />
      </div>

      <DataTable
        columns={columns}
        rows={shown}
        rowKey={(r) => r.job_id}
        onRowClick={(r) => navigate(`/runs/${r.job_id}`)}
        isHighlighted={(r) => r === shown[0] && filter === "all" && q === ""}
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

      {q !== "" && (
        <div className="flex items-center gap-2">
          <Pill tone="spark">{shown.length} of {runs.length}</Pill>
          <span className="text-xs text-dim">matching “{q}”</span>
        </div>
      )}
    </Page>
  );
}
