/**
 * Knowledge-base search — the console twin of the MCP `search_kb` tool.
 *
 * Served by `GET /v1/diagnostics/search`, which dispatches through the same
 * FastMCP tool, so the console and an editor get one answer to one question.
 * The types below mirror `KbHit` / `KbHits` in serve/src/apex_mcp/models.py.
 *
 * Only the API can answer it. The search runs server-side over apex.findings
 * and the redacted plan text; neither the browser-side ClickHouse path nor the
 * recording has a twin of it, and a client-side imitation would rank rows by a
 * scorer nobody else uses. So those sources report `unavailable` rather than
 * an empty hit list — "this source cannot search" is not "nothing matched".
 */

export interface KbHit {
  /**
   * "findings" or "plan_json" per the model. Kept as the API sent it: mapping
   * an unrecognised value onto a known one would name a table the hit may not
   * have come from. Empty when the API sent none.
   */
  source: string;
  job_id: string;
  stage_id: number | null;
  finding_id: string | null;
  type: string;
  severity: string;
  score: number;
  matched_tokens: string[];
  /** UNTRUSTED: text from the observed Spark job. Render as data, never markup. */
  snippet: string;
}

export interface KbHits {
  query: string;
  tokens: string[];
  total: number;
  hits: KbHit[];
  notes: string[];
  untrusted_fields: string[];
}

export type KbSearch =
  | { state: "ok"; result: KbHits }
  | { state: "unavailable"; reason: string };

/** serve clamps top_k to [1, 50] (ch.ReadStore.search); the tool defaults to 5. */
export const KB_TOP_K_MIN = 1;
export const KB_TOP_K_MAX = 50;
export const KB_TOP_K_DEFAULT = 5;

export const clampTopK = (topK: number | undefined): number => {
  if (topK === undefined || !Number.isFinite(topK)) return KB_TOP_K_DEFAULT;
  return Math.min(KB_TOP_K_MAX, Math.max(KB_TOP_K_MIN, Math.trunc(topK)));
};

export const KB_UNAVAILABLE_REASON =
  "Knowledge-base search is available only via the Apex API. It runs server-side as the " +
  "search_kb tool; this data source has no equivalent, and the console does not imitate one.";

const str = (v: unknown): string => (typeof v === "string" ? v : v == null ? "" : String(v));
const strList = (v: unknown): string[] => (Array.isArray(v) ? v.map(str) : []);

/**
 * The API's payload, as values React can render as text.
 *
 * Every field is coerced to the type the model declares: a non-string reaching
 * a React child would either throw (an object) or be read as something it is
 * not. Defaults are the model's own (score 0.0, empty strings and lists), so a
 * field the API omitted reads as serve would have written it.
 */
export const toKbHits = (raw: unknown): KbHits => {
  const r = (raw ?? {}) as Record<string, unknown>;
  const hits = Array.isArray(r.hits) ? r.hits : [];
  return {
    query: str(r.query),
    tokens: strList(r.tokens),
    total: Number(r.total ?? hits.length) || 0,
    notes: strList(r.notes),
    untrusted_fields: strList(r.untrusted_fields),
    hits: hits.map((h): KbHit => {
      const x = (h ?? {}) as Record<string, unknown>;
      // Any value that is not a finite number is no stage — NaN rendered as a
      // stage id is a fabrication.
      const stage = typeof x.stage_id === "number" ? x.stage_id
        : typeof x.stage_id === "string" && x.stage_id.trim() !== "" ? Number(x.stage_id)
        : Number.NaN;
      return {
        source: str(x.source),
        job_id: str(x.job_id),
        stage_id: Number.isFinite(stage) ? stage : null,
        finding_id: x.finding_id ? str(x.finding_id) : null,
        type: str(x.type),
        severity: str(x.severity),
        score: Number(x.score ?? 0) || 0,
        matched_tokens: strList(x.matched_tokens),
        snippet: str(x.snippet),
      };
    }),
  };
};
