import { Card, Mono, Prose } from "@/components/atoms";
import { ApiAuthError, ApiError } from "@/data/http";
import type { Repository } from "@/data/repository";

/** How a failure notice names the source — by the kind that was RESOLVED. */
const SOURCE_NAME: Record<Repository["kind"], string> = {
  clickhouse: "ClickHouse",
  http: "apex-api",
  fixtures: "the recorded run",
};

/**
 * A query that REJECTED, rendered before any empty state.
 *
 * Four screens read only `data` and rendered a rejection as an empty store:
 * with the http source a wrong APEX_API_TOKEN looked like a connected console
 * with nothing in it, and the API's 502 memory_unavailable — "there is no
 * TABLE" — became MemoryScreen's "nothing indexed yet" — "there is no
 * HISTORY". Runs did render its error, labelled "ClickHouse did not answer"
 * whatever the source was.
 *
 * What is shown follows VerifyScreen's caution. An API error carries a status
 * and a detail that ch._sanitize already stripped of connection details
 * server-side, so those are shown. Anything else gets a fixed line: a message
 * from below that layer can carry a response body verbatim, and the
 * VerifyScreen tests exist because one did.
 */
export function QueryFailure({ error, source, what }: {
  error: Error;
  source: Repository["kind"];
  what: string;
}) {
  const name = SOURCE_NAME[source];
  // Only a string is a message. http.ts takes `detail` from the response body,
  // and FastAPI's 422 sends a LIST of validation errors there — rendered as a
  // React child that would throw and take the whole screen down with it, on
  // the one request that was already failing.
  const detail =
    error instanceof ApiError && typeof error.detail === "string" && error.detail
      ? error.detail
      : "no readable detail";
  return (
    <Card accent="finding" className="px-4 py-3.5">
      {error instanceof ApiAuthError ? (
        <Prose>
          {name} rejected the console&rsquo;s token on the{" "}
          <Mono className="text-body2">{what}</Mono> query. Check{" "}
          <Mono className="text-body2">APEX_API_TOKEN</Mono> for this deployment. This is a
          refused credential, not an empty store — nothing below says what the store holds.
        </Prose>
      ) : error instanceof ApiError ? (
        <Prose>
          {name} answered <Mono className="text-finding">{error.status || "nothing"}</Mono> on the{" "}
          <Mono className="text-body2">{what}</Mono> query:{" "}
          <Mono className="text-finding">{detail}</Mono>. No absence conclusion can be
          drawn from what is shown below.
        </Prose>
      ) : (
        <Prose>
          The <Mono className="text-body2">{what}</Mono> query against {name} failed. No absence
          conclusion can be drawn from what is shown below.
        </Prose>
      )}
    </Card>
  );
}
