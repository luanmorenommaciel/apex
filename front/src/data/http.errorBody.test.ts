/**
 * What an ApiError says, for each error body the Apex API actually sends.
 *
 * The bodies below are copied from the API, not written to suit the client:
 * a store failure and a refusal are `{error, detail}` with `detail` a string,
 * but FastAPI's request validation answers 422 with `detail` as a LIST of
 * pydantic errors. The client typed `detail` as a string and interpolated it,
 * so a 422 became "apex api 422 on /v1/runs: [object Object]".
 */
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("./runtimeConfig", () => ({
  runtimeConfig: { apiUrl: "", apiToken: "tok", dataSource: "http", database: "apex", user: "", password: "" },
}));

import { ApiError, apiGet } from "./http";

const reply = (status: number, statusText: string, body: string) =>
  vi.stubGlobal("fetch", () =>
    Promise.resolve(new Response(body, { status, statusText, headers: { "content-type": "application/json" } })),
  );

const failure = async (): Promise<ApiError> => {
  try {
    await apiGet("/v1/runs", { limit: Number.NaN });
  } catch (err) {
    return err as ApiError;
  }
  throw new Error("expected apiGet to throw");
};

afterEach(() => vi.unstubAllGlobals());

describe("ApiError detail", () => {
  it("is a readable string for a FastAPI validation error, whose detail is a list", async () => {
    reply(
      422,
      "Unprocessable Entity",
      '{"detail":[{"type":"int_parsing","loc":["query","limit"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"NaN"}]}',
    );
    const err = await failure();
    expect(err.status).toBe(422);
    expect(typeof err.detail).toBe("string");
    expect(err.message).not.toContain("[object Object]");
  });

  it("still carries the sanitized store code for a store failure", async () => {
    reply(
      502,
      "Bad Gateway",
      '{"error":"store_error","detail":"clickhouse_unavailable: the Apex store did not answer. Check the CLICKHOUSE_* environment of the MCP server."}',
    );
    const err = await failure();
    expect(err.detail).toMatch(/^clickhouse_unavailable:/);
  });

  it("falls back to the error key, then the status text", async () => {
    reply(500, "Internal Server Error", '{"error":"internal_error"}');
    expect((await failure()).detail).toBe("internal_error");
    reply(502, "Bad Gateway", "");
    expect((await failure()).detail).toBe("Bad Gateway");
  });
});
