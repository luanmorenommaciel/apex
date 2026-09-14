/**
 * Deployment configuration, resolved at RUNTIME rather than baked at build.
 *
 * Vite inlines every `import.meta.env.VITE_*` reference into the bundle, so an
 * image built once could otherwise only ever reach one database, as one user,
 * in one mode — a new endpoint, a renamed database or a rotated credential all
 * meant rebuilding and republishing the assets. The production image writes
 * `/config.js` from its own environment at container start
 * (`docker-entrypoint.d/30-apex-console-config.sh`) and `index.html` loads it as
 * a classic script, which runs before the deferred module bundle. One image
 * therefore serves every deployment.
 *
 * Resolution order, first DEFINED wins:
 *   1. `window.__APEX_CONFIG__` — what the container was started with
 *   2. `import.meta.env.VITE_*` — the dev server and a plain `npm run build`
 *   3. the defaults below
 *
 * A key the deployment did not set is OMITTED by the entrypoint rather than
 * written empty, so `""` stays a real value: `apex_ro` is created IDENTIFIED
 * WITH no_password and its empty password must not fall through to a default.
 *
 * This changes WHO sets the credential, not who can read it. It still ships to
 * every browser, which is why `contract/01-readonly-user.sql` grants SELECT and
 * nothing else. See the README — "Querying ClickHouse from the browser".
 */
const DATA_SOURCES = ["auto", "clickhouse", "fixtures"] as const;

export type DataSource = (typeof DATA_SOURCES)[number];

export interface RuntimeConfig {
  database: string;
  user: string;
  password: string;
  dataSource: DataSource;
}

declare global {
  interface Window {
    __APEX_CONFIG__?: {
      database?: string;
      user?: string;
      password?: string;
      dataSource?: string;
    };
  }
}

/**
 * `window` is absent under vitest, which runs in node and imports this module
 * transitively through the repository. Guarding here keeps the read side
 * environment-agnostic instead of making every caller check.
 */
const deployed = typeof window === "undefined" ? undefined : window.__APEX_CONFIG__;

/** An unrecognised value behaves as "auto", which pings and falls back rather
 *  than committing to a store it has not reached. */
const asDataSource = (v: string | undefined): DataSource =>
  (DATA_SOURCES as readonly string[]).includes(v ?? "") ? (v as DataSource) : "auto";

export const runtimeConfig: RuntimeConfig = {
  database: deployed?.database ?? import.meta.env.VITE_CLICKHOUSE_DB ?? "apex",
  user: deployed?.user ?? import.meta.env.VITE_CLICKHOUSE_USER ?? "apex_ro",
  password: deployed?.password ?? import.meta.env.VITE_CLICKHOUSE_PASSWORD ?? "",
  dataSource: asDataSource(deployed?.dataSource ?? import.meta.env.VITE_DATA_SOURCE),
};
