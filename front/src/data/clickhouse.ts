/**
 * ClickHouse HTTP client — queried straight from the browser.
 *
 * Two things make this safe enough for a bench and unsafe for a shared
 * deployment; both are stated in the README rather than hidden here:
 *
 *  1. The credential ships to the browser. It MUST be a read-only user
 *     (see `contract/01-readonly-user.sql`). Anything a visitor can read,
 *     they can read all of.
 *  2. Same-origin is achieved with a proxy (Vite in dev, nginx in prod), so
 *     ClickHouse itself never needs add_http_cors_header.
 *
 * When the deployment stops being a bench, swap ClickHouseRepository for an
 * HTTP client against serve/ — the Repository interface is the seam.
 */

const BASE = "/clickhouse";

export interface ClickHouseConfig {
  database: string;
  user: string;
  password: string;
}

export const chConfig: ClickHouseConfig = {
  database: import.meta.env.VITE_CLICKHOUSE_DB ?? "apex",
  user: import.meta.env.VITE_CLICKHOUSE_USER ?? "apex_ro",
  password: import.meta.env.VITE_CLICKHOUSE_PASSWORD ?? "",
};

export class ClickHouseError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
    this.name = "ClickHouseError";
  }
}

interface JsonResponse<T> {
  data: T[];
  meta: { name: string; type: string }[];
  rows: number;
  statistics?: { elapsed: number; rows_read: number; bytes_read: number };
}

/**
 * ClickHouse QUOTES 64-bit integers in JSON: an Int64 byte count arrives as
 * "4398046511104" while an Int32 task_count arrives as 4398046511104. Screens
 * that call .toFixed() on the former throw at render, and comparisons against a
 * threshold compare strings.
 *
 * The obvious fix — output_format_json_quote_64bit_integers=0 — is unavailable:
 * apex_ro runs with readonly=1, which forbids modifying ANY setting, so the
 * request is rejected outright. Instead this reads the `meta` block ClickHouse
 * already returns and converts by DECLARED TYPE, which is stricter than sniffing
 * values: a String column holding "200" stays the string it is.
 *
 * Precision bound: values above 2^53 (~9.0e15) cannot survive as JS numbers.
 * Nothing the contract stores approaches it — the largest is a per-stage byte
 * count — and a value that did would be wrong in every consumer, not just here.
 */
const NUMERIC = /^(Nullable\()?(U?Int(8|16|32|64|128|256)|Float(32|64)|Decimal)/;

function coerceNumerics<T>(json: JsonResponse<T>): T[] {
  const numericCols = (json.meta ?? [])
    .filter((m) => NUMERIC.test(m.type))
    .map((m) => m.name);
  if (numericCols.length === 0) return json.data;

  return json.data.map((row) => {
    const out = { ...(row as Record<string, unknown>) };
    for (const c of numericCols) {
      const v = out[c];
      // null stays null: a Nullable column's absence is a fact, not a zero.
      if (typeof v === "string" && v !== "") out[c] = Number(v);
    }
    return out as T;
  });
}

/**
 * Run a SELECT. Parameters are passed as ClickHouse query parameters
 * ({name:String}) rather than interpolated, so a job id from the URL cannot
 * become SQL.
 */
export async function query<T>(
  sql: string,
  params: Record<string, string | number> = {},
  signal?: AbortSignal,
): Promise<T[]> {
  const url = new URL(BASE, window.location.origin);
  url.searchParams.set("database", chConfig.database);
  url.searchParams.set("default_format", "JSON");
  // Read-only at the session level too: belt and braces.
  url.searchParams.set("readonly", "1");
  for (const [k, v] of Object.entries(params)) {
    url.searchParams.set(`param_${k}`, String(v));
  }

  const headers: Record<string, string> = {
    "Content-Type": "text/plain; charset=utf-8",
    "X-ClickHouse-User": chConfig.user,
  };
  if (chConfig.password) headers["X-ClickHouse-Key"] = chConfig.password;

  const res = await fetch(url.toString(), {
    method: "POST",
    headers,
    body: sql,
    signal,
  });

  if (!res.ok) {
    throw new ClickHouseError(
      `ClickHouse ${res.status}: ${(await res.text()).slice(0, 300)}`,
      res.status,
    );
  }

  const json = (await res.json()) as JsonResponse<T>;
  return coerceNumerics(json);
}

export async function ping(signal?: AbortSignal): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/ping`, { signal });
    return res.ok;
  } catch {
    return false;
  }
}
