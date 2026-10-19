/**
 * The container entrypoint's boot decision: which deployments start, and which
 * are refused with a named error.
 *
 * The script is run for real under `sh`, with only the environment a container
 * would have. Two modes exist (D-api-only): http, which warns when no API is
 * configured, and fixtures, which needs nothing; anything else is refused by
 * name. The image defaults the API upstream to an unroutable address (nginx
 * needs some value to render its template), so that address means "not
 * configured" here too.
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
    // No inherited environment: the host's own APEX_* must not leak in.
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
  it("boots when the same-origin API upstream is set", () => {
    // The supported deployment: the browser holds an API token and no
    // database credential.
    const r = boot({
      DATA_SOURCE: "http",
      APEX_API_UPSTREAM: "http://apex-api:8000",
      APEX_API_TOKEN: "tok",
    });
    expect(r.status).toBe(0);
    expect(r.stderr).toBe("");
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
    // Not fatal: the operator may be about to attach the upstream, and the
    // bundle renders "no store answered" until then.
    const r = boot({ DATA_SOURCE: "http" });
    expect(r.status).toBe(0);
    expect(r.stderr).toContain("APEX_API_UPSTREAM");
    expect(r.stderr).toContain("no store answered");
  });
});

describe("data source fixtures", () => {
  it("needs no upstream at all", () => {
    const r = boot({ DATA_SOURCE: "fixtures" });
    expect(r.status).toBe(0);
    expect(r.stderr).toBe("");
  });
});

describe("the default and the refusal", () => {
  it("is http when DATA_SOURCE is unset", () => {
    const r = boot({ APEX_API_UPSTREAM: "http://apex-api:8000" });
    expect(r.status).toBe(0);
    expect(r.stderr).toBe("");
    // Unset emits no key: the bundle's own default, http, applies.
    expect(r.config).not.toContain("dataSource");
  });

  it("refuses an unrecognised DATA_SOURCE by name, rendering nothing", () => {
    for (const value of ["clikhouse", "clickhouse", "auto"]) {
      const r = boot({ DATA_SOURCE: value, APEX_API_UPSTREAM: "http://apex-api:8000" });
      expect(r.status, value).toBe(1);
      expect(r.stderr).toContain(`DATA_SOURCE='${value}' is not a data source`);
      expect(r.config).toBeNull();
    }
  });

  it("writes no database key into config.js, whatever the environment carries", () => {
    const r = boot({
      APEX_API_UPSTREAM: "http://apex-api:8000", APEX_API_TOKEN: "t",
      CLICKHOUSE_USER: "leak", CLICKHOUSE_PASSWORD: "leak", CLICKHOUSE_DB: "leak",
    });
    expect(r.status).toBe(0);
    expect(r.config).not.toMatch(/database|user|password/);
    expect(r.config).toContain('apiToken: "t"');
  });
});
