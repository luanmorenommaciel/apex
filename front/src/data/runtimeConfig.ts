/**
 * Deployment configuration, resolved at RUNTIME rather than baked at build.
 *
 * Vite inlines every `import.meta.env.VITE_*` reference into the bundle, so an
 * image built once could otherwise only ever reach one API, with one token,
 * in one mode. The production image writes `/config.js` from its own
 * environment at container start (`docker-entrypoint.d/30-apex-console-config.sh`)
 * and `index.html` loads it as a classic script, which runs before the
 * deferred module bundle. One image therefore serves every deployment.
 *
 * Resolution order, first DEFINED wins:
 *   1. `window.__APEX_CONFIG__` — what the container was started with
 *   2. `import.meta.env.VITE_*` — the dev server and a plain `npm run build`
 *   3. the defaults below
 *
 * The console reads through the Apex API alone (D-api-only, 2026-10-19): the
 * browser carries an API token and never a database user, and no SQL. The
 * token still ships to every visitor — a client-side console cannot hide a
 * credential — but it is a credential for the API, scoped, rotated and
 * revoked per consumer, and it cannot read a table nobody exposed a route for.
 */
const DATA_SOURCES = ["http", "fixtures"] as const;

export type DataSource = (typeof DATA_SOURCES)[number];

export interface RuntimeConfig {
  dataSource: DataSource;
  /** Base URL of the Apex API. Empty means same-origin: /v1 is proxied here. */
  apiUrl: string;
  /** Bearer token for that API. */
  apiToken: string;
}

declare global {
  interface Window {
    __APEX_CONFIG__?: {
      dataSource?: string;
      apiUrl?: string;
      apiToken?: string;
    };
  }
}

/**
 * `window` is absent under vitest, which runs in node and imports this module
 * transitively through the repository. Guarding here keeps the read side
 * environment-agnostic instead of making every caller check.
 */
const deployed = typeof window === "undefined" ? undefined : window.__APEX_CONFIG__;

/** The image entrypoint refuses an unknown value by name; the bundle, which
 *  cannot refuse, reads anything unrecognised as the default, http. */
const asDataSource = (v: string | undefined): DataSource =>
  (DATA_SOURCES as readonly string[]).includes(v ?? "") ? (v as DataSource) : "http";

export const runtimeConfig: RuntimeConfig = {
  dataSource: asDataSource(deployed?.dataSource ?? import.meta.env.VITE_DATA_SOURCE),
  apiUrl: deployed?.apiUrl ?? import.meta.env.VITE_APEX_API_URL ?? "",
  apiToken: deployed?.apiToken ?? import.meta.env.VITE_APEX_API_TOKEN ?? "",
};
