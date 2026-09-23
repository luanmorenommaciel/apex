/**
 * The Apex API client.
 *
 * This is the exit `clickhouse.ts` named: "swap ClickHouseRepository for an
 * HTTP client against serve/ — the Repository interface is the seam". What
 * changes underneath is WHAT the browser holds. Against ClickHouse it carries
 * a database credential and sends SQL; against this it carries an API token
 * and sends a path. A token can be scoped, rotated and revoked per consumer,
 * and it cannot read a table nobody exposed a route for.
 *
 * The token still reaches the browser — that is unavoidable for a client-side
 * console — so it is a credential for the API and never for the store, and the
 * API is what decides what it may see.
 */
import { runtimeConfig } from "./runtimeConfig";

/** Set by the API when a listing came back at its cap. */
const TRUNCATED_HEADER = "x-apex-truncated";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly detail: string,
    readonly path: string,
  ) {
    super(`apex api ${status} on ${path}: ${detail}`);
    this.name = "ApiError";
  }
}

/**
 * An unauthenticated or wrongly-authenticated call.
 *
 * Distinguished from every other failure because the caller must NOT treat it
 * as "the API is unavailable, fall back". Falling back to ClickHouse on a 401
 * would silently restore the browser-side database credential this layer
 * exists to remove.
 */
export class ApiAuthError extends ApiError {
  constructor(detail: string, path: string) {
    super(401, detail, path);
    this.name = "ApiAuthError";
  }
}

const base = (): string => runtimeConfig.apiUrl.replace(/\/+$/, "");

const headers = (): HeadersInit => {
  const h: Record<string, string> = { Accept: "application/json" };
  // Omitted rather than sent empty: an empty bearer is a malformed credential,
  // and the API's refusal should say "no token", not "bad token".
  if (runtimeConfig.apiToken) h.Authorization = `Bearer ${runtimeConfig.apiToken}`;
  return h;
};

const url = (path: string, params?: Record<string, string | number | undefined>): string => {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== undefined) search.set(key, String(value));
  }
  const query = search.toString();
  return `${base()}${path}${query ? `?${query}` : ""}`;
};

export interface ApiResult<T> {
  data: T;
  /** True when the API reported the page came back at its cap. */
  truncated: boolean;
}

/**
 * One GET against the API.
 *
 * 404 is returned as `null` rather than thrown: the API uses it for "no run
 * with that id", which several callers turn into a null of their own, and an
 * exception would make a normal absence look like a fault.
 */
export async function apiGet<T>(
  path: string,
  params?: Record<string, string | number | undefined>,
): Promise<ApiResult<T | null>> {
  const target = url(path, params);
  let response: Response;
  try {
    response = await fetch(target, { headers: headers() });
  } catch (cause) {
    throw new ApiError(0, `the API could not be reached (${String(cause)})`, path);
  }

  if (response.status === 401) {
    throw new ApiAuthError(
      "the console's API token was rejected. Check APEX_API_TOKEN for this deployment.",
      path,
    );
  }
  if (response.status === 404) {
    return { data: null, truncated: false };
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string; error?: string };
      detail = body.detail ?? body.error ?? detail;
    } catch {
      // A non-JSON error body is still a failure; the status carries it.
    }
    throw new ApiError(response.status, detail, path);
  }

  return {
    data: (await response.json()) as T,
    truncated: response.headers.get(TRUNCATED_HEADER) === "true",
  };
}

/**
 * Whether an Apex API answers at the configured base — the probe `auto` uses.
 *
 * With no apiUrl this asks the SAME ORIGIN (`/v1/health`), which is the
 * supported deployment: the dev server and nginx forward `/v1`, so the bundle
 * never learns where the API lives and an empty apiUrl says nothing about
 * whether one exists.
 *
 * Two answers count as "an API is there":
 *   - 200 with `{"status": "ok"}` — the API's own liveness body. A bare 200 is
 *     not enough: a static host with an SPA fallback answers every unknown path
 *     with index.html and a 200, which would make `auto` pick an API that
 *     is not there.
 *   - 401 — /v1/health needs no token, so a 401 means something in front of
 *     the API is gating it. The API exists and refused us; `auto` must select
 *     it and let the refusal surface, never fall back to the browser-side
 *     database credential this layer exists to remove.
 * Anything else — a refused connection, a 502 from a proxy whose upstream is
 * absent, a non-API body — is "no API here".
 */
export async function apiPing(signal?: AbortSignal): Promise<boolean> {
  try {
    const response = await fetch(`${base()}/v1/health`, { signal });
    if (response.status === 401) return true;
    if (!response.ok) return false;
    const body = (await response.json()) as { status?: unknown } | null;
    return body?.status === "ok";
  } catch {
    return false;
  }
}
