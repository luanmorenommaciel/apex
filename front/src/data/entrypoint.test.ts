/**
 * The container entrypoint's boot decision: which deployments start, and which
 * are refused with a named error.
 *
 * The script is run for real under `sh`, with only the environment a container
 * would have. What it decides is: a store the deployment will actually use must
 * be configured, and a store it will not use must not be demanded. The image
 * defaults both upstreams to an unroutable address (nginx needs some value to
 * render its template), so that address means "not configured" here too.
 */
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

const SCRIPT = fileURLToPath(
  new URL("../../docker-entrypoint.d/30-apex-console-config.sh", import.meta.url),
);

/** What the Dockerfile sets when the operator passes nothing. */
const IMAGE_DEFAULTS = {
  CLICKHOUSE_UPSTREAM: "http://127.0.0.1:1",
  APEX_API_UPSTREAM: "http://127.0.0.1:1",
};

const dirs: string[] = [];
afterEach(() => {
  for (const d of dirs.splice(0)) rmSync(d, { recursive: true, force: true });
});

function boot(env: Record<string, string>) {
  const dir = mkdtempSync(join(tmpdir(), "apex-entrypoint-"));
  dirs.push(dir);
  const out = join(dir, "config.js");
  const result = spawnSync("sh", [SCRIPT], {
    // No inherited environment: the host's own CLICKHOUSE_* must not leak in.
    env: { PATH: process.env.PATH ?? "", ...IMAGE_DEFAULTS, ...env, APEX_CONFIG_OUT: out },
    encoding: "utf8",
  });
  let config: string | null = null;
  try {
    config = readFileSync(out, "utf8");
  } catch {
    // Refused to boot: nothing was rendered.
  }
  return { status: result.status, stderr: result.stderr, config };
}

describe("data source http", () => {
  it("boots with no CLICKHOUSE_UPSTREAM when the same-origin API upstream is set", () => {
    // The documented HTTP-only deployment: the browser holds an API token and
    // no database credential, and ClickHouse is never called.
    const r = boot({
      DATA_SOURCE: "http",
      APEX_API_UPSTREAM: "http://apex-api:8000",
      APEX_API_TOKEN: "tok",
    });
    expect(r.status).toBe(0);
    expect(r.stderr).not.toContain("CLICKHOUSE_UPSTREAM");
    expect(r.config).toContain('dataSource: "http"');
    expect(r.config).toContain('apiToken: "tok"');
    // Same-origin: no absolute apiUrl is written, so the bundle calls /v1 relative.
    expect(r.config).not.toContain("apiUrl");
  });

  it("boots against an absolute APEX_API_URL too", () => {
    const r = boot({ DATA_SOURCE: "http", APEX_API_URL: "https://api.example.test" });
    expect(r.status).toBe(0);
    expect(r.config).toContain('apiUrl: "https://api.example.test"');
  });

  it("boots but warns when no API is configured at all", () => {
    // Not a ClickHouse problem, so not the ClickHouse error — and not fatal:
    // the operator may be about to attach the upstream.
    const r = boot({ DATA_SOURCE: "http" });
    expect(r.status).toBe(0);
    expect(r.stderr).toContain("APEX_API_UPSTREAM");
    expect(r.stderr).not.toContain("CLICKHOUSE_UPSTREAM is not set");
  });
});

describe("data source clickhouse", () => {
  it("refuses to start without CLICKHOUSE_UPSTREAM, and names the variable", () => {
    const r = boot({ DATA_SOURCE: "clickhouse" });
    expect(r.status).toBe(1);
    expect(r.stderr).toContain("CLICKHOUSE_UPSTREAM is not set");
    expect(r.config).toBeNull();
  });

  it("refuses even when the API is configured: it will not be used", () => {
    const r = boot({ DATA_SOURCE: "clickhouse", APEX_API_UPSTREAM: "http://apex-api:8000" });
    expect(r.status).toBe(1);
    expect(r.stderr).toContain("CLICKHOUSE_UPSTREAM is not set");
  });

  it("boots once the upstream is given", () => {
    const r = boot({ DATA_SOURCE: "clickhouse", CLICKHOUSE_UPSTREAM: "http://ch:8123" });
    expect(r.status).toBe(0);
  });
});

describe("data source fixtures", () => {
  it("needs no upstream at all", () => {
    const r = boot({ DATA_SOURCE: "fixtures" });
    expect(r.status).toBe(0);
    expect(r.stderr).toBe("");
  });
});

describe("data source auto (the default)", () => {
  it("boots with the API alone: ClickHouse is only the fallback", () => {
    const r = boot({ DATA_SOURCE: "auto", APEX_API_UPSTREAM: "http://apex-api:8000" });
    expect(r.status).toBe(0);
    expect(r.stderr).not.toContain("CLICKHOUSE_UPSTREAM is not set");
    // It says what it will do when the API is down, rather than staying quiet.
    expect(r.stderr).toContain("recorded run");
  });

  it("is what an unset DATA_SOURCE means", () => {
    const r = boot({ APEX_API_UPSTREAM: "http://apex-api:8000" });
    expect(r.status).toBe(0);
    expect(r.config).not.toContain("dataSource");
  });

  it("is what an unrecognised DATA_SOURCE means, as it is in the bundle", () => {
    const r = boot({ DATA_SOURCE: "bogus" });
    expect(r.status).toBe(1);
    expect(boot({ DATA_SOURCE: "bogus", APEX_API_UPSTREAM: "http://a:1000" }).status).toBe(0);
  });

  it("boots with ClickHouse alone, as before", () => {
    const r = boot({ CLICKHOUSE_UPSTREAM: "http://ch:8123" });
    expect(r.status).toBe(0);
    expect(r.stderr).toBe("");
  });

  it("boots with both", () => {
    const r = boot({
      CLICKHOUSE_UPSTREAM: "http://ch:8123",
      APEX_API_UPSTREAM: "http://apex-api:8000",
    });
    expect(r.status).toBe(0);
    expect(r.stderr).toBe("");
  });

  it("refuses with neither configured — there is nothing to probe", () => {
    const r = boot({});
    expect(r.status).toBe(1);
    expect(r.stderr).toContain("CLICKHOUSE_UPSTREAM is not set");
    // The message offers the API path too, not only ClickHouse.
    expect(r.stderr).toContain("APEX_API_UPSTREAM");
    expect(r.stderr).toContain("DATA_SOURCE=fixtures");
  });
});
