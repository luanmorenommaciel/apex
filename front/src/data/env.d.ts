interface ImportMetaEnv {
  readonly VITE_CLICKHOUSE_URL?: string;
  readonly VITE_CLICKHOUSE_DB?: string;
  readonly VITE_CLICKHOUSE_USER?: string;
  readonly VITE_CLICKHOUSE_PASSWORD?: string;
  readonly VITE_DATA_SOURCE?: "auto" | "clickhouse" | "fixtures" | "http";
  /**
   * Where the DEV SERVER forwards /v1. Server-side only: it never reaches the
   * bundle, so setting it cannot push the browser off its origin.
   */
  readonly VITE_APEX_API_PROXY_TARGET?: string;
  /**
   * An ABSOLUTE base for the browser to call directly, bypassing the proxy.
   * Leave unset for the normal same-origin path; setting it makes requests
   * cross-origin, which the API does not currently allow (no CORS).
   */
  readonly VITE_APEX_API_URL?: string;
  /** Bearer token for that API. A credential for the API, never for the store. */
  readonly VITE_APEX_API_TOKEN?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
