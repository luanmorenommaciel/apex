import { useCallback, useEffect, useRef, useState } from "react";
import type { Repository } from "@/data/repository";
import type { AsyncState } from "@/data/useRepository";

/** A /verify request belongs to a repository, selection key and retry attempt.
 * Hide the old snapshot during render, before the replacement effect starts.
 * Cleanup also rejects late completions and StrictMode's abandoned attempt.
 * Other screens retain their existing useAsync behavior.
 */
export function useVerifyQuery<T>(repo: Repository, key: string, fn: () => Promise<T>) {
  const [attempt, setAttempt] = useState(0);
  const [snapshot, setSnapshot] = useState<{
    repo: Repository; key: string; attempt: number; state: AsyncState<T>;
  } | null>(null);
  const fnRef = useRef(fn);
  fnRef.current = fn;
  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  useEffect(() => {
    let live = true;
    const request = fnRef.current;
    const save = (state: AsyncState<T>) => {
      if (live) setSnapshot({ repo, key, attempt, state });
    };
    // No old data survives a retry, even while the new request is pending.
    save({ data: null, loading: true, error: null });
    Promise.resolve().then(request).then(
      (data) => save({ data, loading: false, error: null }),
      // Treat rejection as untrusted data; even its name can carry a response body.
      () => save({ data: null, loading: false, error: new Error("Query failed") }),
    );
    return () => { live = false; };
  }, [repo, key, attempt]);

  const state: AsyncState<T> = snapshot?.repo === repo && snapshot.key === key && snapshot.attempt === attempt
    ? snapshot.state : { data: null, loading: true, error: null };
  return { ...state, retry };
}
