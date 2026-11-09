import {
  createContext, useContext, useEffect, useState, type ReactNode,
} from "react";
import {
  FixtureRepository, resolveRepository, StoreUnreachableError, type Repository,
} from "./repository";
import { StoreUnreachable } from "@/components/molecules/StoreUnreachable";

const RepoContext = createContext<Repository>(new FixtureRepository());

export function RepositoryProvider({ children }: { children: ReactNode }) {
  const [repo, setRepo] = useState<Repository | null>(null);
  const [unreachable, setUnreachable] = useState<StoreUnreachableError | null>(null);
  useEffect(() => {
    let live = true;
    resolveRepository().then(
      (r) => live && setRepo(r),
      (error: unknown) => {
        if (!live) return;
        // Only the named failure is rendered; anything else is a bug and
        // stays an unhandled rejection rather than a screen that guesses.
        if (error instanceof StoreUnreachableError) setUnreachable(error);
        else throw error;
      },
    );
    return () => {
      live = false;
    };
  }, []);
  // No store answered: the app does not mount over a recording. The failure
  // takes the page and names what was asked.
  if (unreachable) return <StoreUnreachable probed={unreachable.probed} />;
  if (!repo) return null;
  return <RepoContext.Provider value={repo}>{children}</RepoContext.Provider>;
}

export const useRepository = () => useContext(RepoContext);

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

/**
 * One read of the repository, named by its method and arguments.
 *
 * `["stages", jobId]` is the key RunDetail, Finding and Compare all use for
 * the same rows, so the three share one request and one cached answer.
 * The trailing AbortSignal every Repository method accepts is supplied here.
 */
export type ReadMethod = Exclude<keyof Repository, "kind">;
export type ReadSpec<M extends ReadMethod> = [M, ...Parameters<Repository[M]>];
type ReadResult<M extends ReadMethod> = Awaited<ReturnType<Repository[M]>>;
/** The cache's view of a spec: the method name and whatever arguments followed. */
type AnySpec = [ReadMethod, ...unknown[]];

/**
 * How long a settled read answers from memory. Proposed and open for review:
 * the console is read-only and new runs arrive on the order of minutes, so
 * thirty seconds covers a visit that walks Runs -> RunDetail -> Finding
 * without refetching the rows the previous screen just read, and is short
 * enough that a reload after a new run lands shows it.
 */
export const READ_TTL_MS = 30_000;

interface Entry {
  promise: Promise<unknown>;
  controller: AbortController;
  /** Set once the promise resolved; absent while in flight. */
  settledAt?: number;
  value?: unknown;
  /** Mounted hooks reading this entry. Zero and unsettled means nobody wants it. */
  subscribers: number;
}

/**
 * The cache belongs to the repository INSTANCE - a WeakMap keyed on it - so a
 * swap of repositories (a test, a future re-resolution) cannot serve rows that
 * came through another door, and it is collected with the instance.
 */
const CACHES = new WeakMap<Repository, Map<string, Entry>>();

const cacheOf = (repo: Repository): Map<string, Entry> => {
  let cache = CACHES.get(repo);
  if (!cache) {
    cache = new Map();
    CACHES.set(repo, cache);
  }
  return cache;
};

const keyOf = (spec: AnySpec): string => JSON.stringify(spec);

/** The entry for a key: the live one, the fresh settled one, or a new request. */
function acquire(repo: Repository, spec: AnySpec): Entry {
  const cache = cacheOf(repo);
  const key = keyOf(spec);
  const existing = cache.get(key);
  if (existing && (existing.settledAt === undefined || Date.now() - existing.settledAt < READ_TTL_MS)) {
    return existing;
  }
  const controller = new AbortController();
  const [method, ...args] = spec;
  const call = repo[method] as (...a: unknown[]) => Promise<unknown>;
  const entry: Entry = { promise: Promise.resolve(), controller, subscribers: 0 };
  entry.promise = call.call(repo, ...args, controller.signal).then(
    (value) => {
      entry.value = value;
      entry.settledAt = Date.now();
      return value;
    },
    (error: unknown) => {
      // A failure is not cached: the next mount asks again.
      if (cache.get(key) === entry) cache.delete(key);
      throw error;
    },
  );
  cache.set(key, entry);
  return entry;
}

/**
 * Release one subscriber. An in-flight request nobody is waiting for is
 * aborted at the fetch - but one tick later, not synchronously: React
 * StrictMode unmounts and remounts every effect in development, and an
 * immediate abort would turn that into two requests per read.
 */
function release(repo: Repository, spec: AnySpec, entry: Entry): void {
  entry.subscribers -= 1;
  setTimeout(() => {
    if (entry.subscribers > 0 || entry.settledAt !== undefined) return;
    entry.controller.abort();
    const cache = cacheOf(repo);
    if (cache.get(keyOf(spec)) === entry) cache.delete(keyOf(spec));
  }, 0);
}

const settled = <T,>(entry: Entry | null): AsyncState<T> =>
  entry && entry.settledAt !== undefined
    ? { data: entry.value as T, loading: false, error: null }
    : { data: null, loading: entry !== null, error: null };

/**
 * Read from the repository with dedupe, a short cache and cancellation.
 *
 * A `null` spec is a read the screen does not need yet (no fingerprint to
 * ask about, no finding selected): it issues nothing and reports no data,
 * not loading. Concurrent hooks on one spec share one request; a spec that
 * settled within READ_TTL_MS is answered from memory; an unmounted hook
 * whose request is still in flight aborts it.
 */
export function useRead<M extends ReadMethod>(
  repo: Repository,
  spec: ReadSpec<M> | null,
): AsyncState<ReadResult<M>> {
  const any = spec as AnySpec | null;
  const key = any ? keyOf(any) : null;
  // Answer from the cache on the first render when it can, so a screen that
  // navigates to rows the previous screen just read never flashes "loading".
  const [state, setState] = useState<AsyncState<ReadResult<M>>>(() =>
    settled(any ? cacheOf(repo).get(keyOf(any)) ?? null : null),
  );

  useEffect(() => {
    if (!any) {
      setState({ data: null, loading: false, error: null });
      return;
    }
    const entry = acquire(repo, any);
    entry.subscribers += 1;
    let live = true;
    if (entry.settledAt !== undefined) {
      setState({ data: entry.value as ReadResult<M>, loading: false, error: null });
    } else {
      setState((s) => ({ ...s, loading: true, error: null }));
      entry.promise.then(
        (data) => live && setState({ data: data as ReadResult<M>, loading: false, error: null }),
        (error: Error) => live && setState({ data: null, loading: false, error }),
      );
    }
    return () => {
      live = false;
      release(repo, any, entry);
    };
    // The key is the spec, serialised; the array identity changes every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repo, key]);

  return state;
}
