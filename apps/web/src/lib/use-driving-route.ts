import { useCallback, useEffect, useRef, useState } from 'react';
import { api, messageOf } from './api';
import { useUserLocation } from './location';
import type { DrivingRoute } from './directions';

export function useDrivingRoute(productId?: string) {
  const location = useUserLocation();
  const [route, setRoute] = useState<DrivingRoute | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const controller = useRef<AbortController | null>(null);
  const version = useRef(0);
  const clear = useCallback(() => { version.current++; controller.current?.abort(); setRoute(null); setError(''); setBusy(false); }, []);
  useEffect(() => { clear(); return () => { version.current++; controller.current?.abort(); }; }, [productId, clear]);
  useEffect(() => { if (!location.position) clear(); }, [location.position, clear]);
  const load = useCallback(async () => {
    if (!productId) return;
    // Invalidate before the permission prompt: the selected product may change
    // while native geolocation is pending. A late grant must not route to it.
    const current = ++version.current;
    controller.current?.abort();
    const origin = location.position || await location.request();
    if (!origin || current !== version.current) return;
    const abort = new AbortController(); controller.current = abort;
    setBusy(true); setError('');
    try {
      const value = await api<DrivingRoute>('/routing/route', { method: 'POST', signal: abort.signal,
        body: JSON.stringify({ product_id: productId, origin_latitude: origin.latitude, origin_longitude: origin.longitude }) });
      if (current === version.current) setRoute(value);
    } catch (issue) { if (!abort.signal.aborted && current === version.current) { setError(messageOf(issue)); setRoute(null); } }
    finally { if (current === version.current) setBusy(false); }
  }, [productId, location]);
  useEffect(() => {
    if (!route?.traffic_aware) return;
    const timer = window.setInterval(() => { if (document.visibilityState === 'visible') void load(); }, 60000);
    return () => window.clearInterval(timer);
  }, [route?.traffic_aware, load]);
  return { route, busy, error, load, clear };
}
