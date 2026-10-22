import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Card, Label, Mono, Pill, Prose, SeverityBadge } from "@/components/atoms";
import { QueryFailure, ScreenHeader } from "@/components/molecules";
import { Page } from "@/components/layout/Shell";
import type { Severity } from "@/contract/types";
import {
  clampTopK, KB_TOP_K_DEFAULT, KB_TOP_K_MAX, KB_TOP_K_MIN, type KbHit, type KbSearch,
} from "@/data/kb";
import type { Repository } from "@/data/repository";
import { useRepository } from "@/data/useRepository";

/**
 * Knowledge-base search: the console twin of the MCP `search_kb` tool.
 *
 * Its own route rather than a box on Ask or Runs. Ask is a scripted mockup and
 * Runs' search box filters the 50 loaded rows in the browser; a real,
 * server-ranked search sitting inside either would read as one of them. Here
 * there is nothing else on the screen to confuse it with.
 *
 * Every value from the API is rendered as a React text node. Snippets are text
 * from the observed Spark job and are labelled as such — quoted, never followed.
 */
type View =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "done"; search: KbSearch }
  | { status: "error"; error: Error };

const runHref = (jobId: string) => `/runs/${encodeURIComponent(jobId)}`;
const findingHref = (jobId: string, findingId: string) =>
  `${runHref(jobId)}/findings/${encodeURIComponent(findingId)}`;

/**
 * Whether an id can be a path segment of a link at all.
 *
 * encodeURIComponent leaves "." alone, and "." or ".." as a segment is a dot
 * segment: the router (and the browser's URL parser, even for %2E%2E) resolves
 * it to a different page. Such an id is shown as text, never linked.
 */
const linkable = (id: string | null): id is string => !!id && id !== "." && id !== "..";

export function KbSearchScreen() {
  const repo = useRepository();
  const [draft, setDraft] = useState("");
  // The raw field text: clamping on every keystroke snapped a cleared field to
  // 1. It is clamped once, when the search is sent.
  const [topK, setTopK] = useState(String(KB_TOP_K_DEFAULT));
  const [view, setView] = useState<View>({ status: "idle" });
  // Only the latest submission may land: an earlier, slower answer arriving
  // second would otherwise replace the one the user is looking at. Search stays
  // enabled while one is in flight — apiGet has no timeout, so a hung request
  // must not lock the screen.
  const seq = useRef(0);

  const submit = () => {
    const q = draft.trim();
    if (!q) return;
    const mine = ++seq.current;
    setView({ status: "loading" });
    repo
      .searchKb(q, clampTopK(topK.trim() === "" ? undefined : Number(topK)))
      .then((search) => mine === seq.current && setView({ status: "done", search }))
      .catch((error: Error) => mine === seq.current && setView({ status: "error", error }));
  };

  return (
    <Page>
      <ScreenHeader
        title={
          <span className="flex items-center gap-2.5">
            Search KB
            <Pill tone="spark">search_kb</Pill>
          </span>
        }
        subtitle={
          <>
            Token search over <Mono className="text-body2">apex.findings</Mono> and redacted plan
            text, ranked server-side by <Mono className="text-body2">GET /v1/diagnostics/search</Mono>{" "}
            — the same tool the MCP server exposes. Not a filter over the Runs list, and not
            scripted.
          </>
        }
      />

      <form
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="flex items-center gap-3 bg-raised border border-edge2 rounded-sm px-3.5 py-2.5 focus-within:border-spark transition-colors"
      >
        <input
          aria-label="knowledge-base query"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="e.g. spill shuffle partitions"
          className="flex-1 bg-transparent outline-none text-sm text-bright placeholder:text-muted"
        />
        <label className="flex items-center gap-1.5 font-mono text-[11px] text-sub">
          top_k
          <input
            aria-label="top_k"
            type="number"
            min={KB_TOP_K_MIN}
            max={KB_TOP_K_MAX}
            value={topK}
            onChange={(e) => setTopK(e.target.value)}
            className="w-14 bg-surface border border-edge rounded-sm px-1.5 py-1 text-body2"
          />
        </label>
        <button
          type="submit"
          disabled={!draft.trim()}
          className="font-mono text-xs px-3 py-1.5 border rounded-sm bg-raised border-edge2 text-bright hover:bg-edge disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Search
        </button>
      </form>

      <Results view={view} source={repo.kind} />
    </Page>
  );
}

function Results({ view, source }: { view: View; source: Repository["kind"] }) {
  if (view.status === "idle") {
    return <Prose className="text-dim">Enter terms and press Search. Nothing is queried until you do.</Prose>;
  }
  if (view.status === "loading") return <Prose>Searching…</Prose>;
  if (view.status === "error") {
    return <QueryFailure error={view.error} source={source} what="knowledge-base search" />;
  }
  if (view.search.state === "unavailable") {
    return (
      <Card accent="withheld" className="px-4 py-3.5 flex flex-col gap-1.5">
        <Label tone="withheld">UNAVAILABLE ON THIS DATA SOURCE</Label>
        <Prose>{view.search.reason}</Prose>
      </Card>
    );
  }

  const { result } = view.search;
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2 flex-wrap font-mono text-[11px] text-sub">
        <span>
          <span className="text-body2">{result.total}</span> hit{result.total === 1 ? "" : "s"}
        </span>
        <span className="text-dim">·</span>
        <span>tokens:</span>
        {result.tokens.length === 0 ? (
          <span className="text-muted">none</span>
        ) : (
          result.tokens.map((t, i) => (
            <span key={`${t}-${i}`} className="px-1.5 py-0.5 bg-raised border border-edge rounded-sm text-body2">
              {t}
            </span>
          ))
        )}
      </div>

      {result.tokens.length === 0 ? (
        // Nothing was searched: serve keeps only tokens of 2+ word characters,
        // and "no hits" would claim a search that never ran.
        <Card accent="withheld" className="px-4 py-3.5">
          <Prose>
            Nothing searchable in this query. Only terms of two or more word characters are
            searched, so no search was run — this says nothing about what the store holds.
          </Prose>
        </Card>
      ) : result.hits.length === 0 ? (
        <Card accent="edge" className="px-4 py-3.5">
          <Prose>No hits for this query. That is a search result, not a store error.</Prose>
        </Card>
      ) : null}

      {result.hits.map((hit, i) => (
        <HitCard key={`${hit.source}-${hit.job_id}-${hit.finding_id ?? ""}-${hit.stage_id ?? ""}-${i}`} hit={hit} />
      ))}

      {result.notes.length > 0 && (
        <Card className="px-4 py-3 flex flex-col gap-1.5">
          <Label>NOTES</Label>
          <ul className="list-disc pl-5 text-xs text-body flex flex-col gap-1">
            {result.notes.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
        </Card>
      )}
    </div>
  );
}

function HitCard({ hit }: { hit: KbHit }) {
  const tone = hit.source === "findings" ? "finding" : hit.source === "plan_json" ? "memory" : "neutral";
  return (
    <div data-testid="kb-hit">
      <Card accent={tone === "neutral" ? "edge" : tone} className="px-4 py-3 flex flex-col gap-2">
        <div className="flex items-center gap-2.5 flex-wrap font-mono text-[11px]">
          <Pill tone={tone}>{hit.source || "unknown source"}</Pill>
          {hit.severity ? <SeverityBadge severity={hit.severity as Severity} /> : null}
          {hit.type && <span className="text-bright">{hit.type}</span>}
          <span className="text-sub">score <span className="text-body2">{hit.score.toFixed(3)}</span></span>
        </div>
        <div className="flex items-center gap-x-4 gap-y-1 flex-wrap font-mono text-[11px] text-sub">
          <span>
            job{" "}
            {linkable(hit.job_id) ? (
              <Link to={runHref(hit.job_id)} className="text-spark">{hit.job_id}</Link>
            ) : (
              <span className={hit.job_id ? "text-body2" : "text-muted"}>{hit.job_id || "—"}</span>
            )}
          </span>
          <span>stage <span className="text-body2">{hit.stage_id ?? "—"}</span></span>
          <span>
            finding{" "}
            {linkable(hit.finding_id) && linkable(hit.job_id) ? (
              <Link to={findingHref(hit.job_id, hit.finding_id)} className="text-spark">{hit.finding_id}</Link>
            ) : (
              <span className="text-body2">{hit.finding_id ?? "—"}</span>
            )}
          </span>
          <span>
            matched{" "}
            <span className="text-body2">{hit.matched_tokens.length ? hit.matched_tokens.join(", ") : "—"}</span>
          </span>
        </div>
        <div className="flex flex-col gap-1">
          <Label tone="withheld">SNIPPET · UNTRUSTED — text from the observed job, shown as data</Label>
          <pre data-testid="kb-snippet" className="font-mono text-[11px] leading-[1.6] text-body whitespace-pre-wrap break-words bg-surface border border-edge rounded-sm px-3 py-2 m-0">
            {hit.snippet}
          </pre>
        </div>
      </Card>
    </div>
  );
}
