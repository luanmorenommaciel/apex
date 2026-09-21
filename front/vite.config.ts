import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react()],
    resolve: {
      alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
      // ClickHouse's HTTP interface is reached through this proxy, so the browser
      // stays same-origin and the database never needs add_http_cors_header.
      proxy: {
        "/clickhouse": {
          target: env.VITE_CLICKHOUSE_URL || "http://127.0.0.1:8123",
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/clickhouse/, ""),
        },
        // Same reason, same shape: with no VITE_APEX_API_URL the console calls
        // /v1 relative and this forwards it, so the API needs no CORS header
        // and the browser never leaves its origin. No rewrite — the API serves
        // /v1 itself, unlike ClickHouse which serves at the root.
        "/v1": {
          // VITE_APEX_API_PROXY_TARGET, deliberately NOT VITE_APEX_API_URL.
          // The latter sets the browser's own apiUrl, so sharing one variable
          // made the documented dev command send the bundle CROSS-ORIGIN and
          // straight past this proxy — which the API, having no CORS header,
          // then refused. The proxy target is a server-side detail; the
          // browser must not learn it.
          target: env.VITE_APEX_API_PROXY_TARGET || "http://127.0.0.1:8099",
          changeOrigin: true,
        },
      },
    },
  };
});
