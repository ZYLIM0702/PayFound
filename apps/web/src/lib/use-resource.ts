import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { api, getAnchorVersion, messageOf, subscribeAnchor } from './api';

export function useResource<T>(path: string | null, poll = 0) {
  // Re-fetch when the viewer's area changes: the API lays out the demo stores around it.
  const anchorVersion = useSyncExternalStore(subscribeAnchor, getAnchorVersion);
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(Boolean(path));
  const [refreshing, setRefreshing] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const generation = useRef(0);
  const refresh = useCallback(async () => {
    if (!path) return;
    const current = ++generation.current;
    controller.current?.abort();
    const abort = new AbortController();
    controller.current = abort;
    setRefreshing(true);
    try {
      const value = await api<T>(path, { signal: abort.signal });
      if (current === generation.current) { setData(value); setError(''); }
    } catch (e) {
      if (!abort.signal.aborted && current === generation.current) setError(messageOf(e));
    } finally {
      if (current === generation.current) { setLoading(false); setRefreshing(false); }
    }
  }, [path, anchorVersion]);
  useEffect(() => {
    setData(null); setError(''); setLoading(Boolean(path));
    void refresh();
    const timer = poll ? window.setInterval(() => { if (document.visibilityState === 'visible') void refresh(); }, poll) : undefined;
    return () => { generation.current++; controller.current?.abort(); window.clearInterval(timer); };
  }, [refresh, poll, path, anchorVersion]);
  return { data, error, loading, refreshing, refresh, setData };
}
