interface ImportMetaEnv {
  readonly VITE_CLICKHOUSE_URL?: string;
  readonly VITE_CLICKHOUSE_DB?: string;
  readonly VITE_CLICKHOUSE_USER?: string;
  readonly VITE_CLICKHOUSE_PASSWORD?: string;
  readonly VITE_DATA_SOURCE?: "auto" | "clickhouse" | "fixtures";
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
