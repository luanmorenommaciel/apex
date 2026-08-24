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
      },
    },
  };
});
