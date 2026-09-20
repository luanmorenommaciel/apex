interface ImportMetaEnv {
  readonly VITE_CLICKHOUSE_URL?: string;
  readonly VITE_CLICKHOUSE_DB?: string;
  readonly VITE_CLICKHOUSE_USER?: string;
  readonly VITE_CLICKHOUSE_PASSWORD?: string;
  readonly VITE_DATA_SOURCE?: "auto" | "clickhouse" | "fixtures" | "http";
  /** Base URL of the Apex API, e.g. http://127.0.0.1:8000 — used by DATA_SOURCE=http. */
  readonly VITE_APEX_API_URL?: string;
  /** Bearer token for that API. A credential for the API, never for the store. */
  readonly VITE_APEX_API_TOKEN?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
