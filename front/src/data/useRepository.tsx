import {
  createContext, useContext, useEffect, useRef, useState, type ReactNode,
} from "react";
import { FixtureRepository, resolveRepository, type Repository } from "./repository";

const RepoContext = createContext<Repository>(new FixtureRepository());

export function RepositoryProvider({ children }: { children: ReactNode }) {
  const [repo, setRepo] = useState<Repository | null>(null);
  useEffect(() => {
    let live = true;
    resolveRepository().then((r) => live && setRepo(r));
    return () => {
      live = false;
    };
  }, []);
  if (!repo) return null;
  return <RepoContext.Provider value={repo}>{children}</RepoContext.Provider>;
}

export const useRepository = () => useContext(RepoContext);

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

/** Minimal async hook — no data-fetching library, so the deps list stays honest. */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: true, error: null });
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fnRef
      .current()
      .then((data) => live && setState({ data, loading: false, error: null }))
      .catch((error: Error) => live && setState({ data: null, loading: false, error }));
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
