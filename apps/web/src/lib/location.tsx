import { createContext, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { api, bumpAnchorVersion, closeGate, onPlacementSignal, openGate, setAnchor } from './api';
import tzCities from './tz-cities.json';

export type UserPosition = { latitude: number; longitude: number; accuracy: number; timestamp: number };
/** Approximate (2 dp) area the demo stores are laid out around. */
export type RegionAnchor = { latitude: number; longitude: number; source: 'precise' | 'ip' | 'saved' | 'timezone'; label: string };
/** Server-reported layout of the demo stores for this viewer. */
export type DemoPlacement = { mode: 'relocated' | 'original'; reason: string; placed?: number; total?: number } | null;
type LocationState = { position: UserPosition | null; permission: PermissionState | 'unavailable'; locating: boolean;
  error: string; request: () => Promise<UserPosition | null>; clear: () => void; anchor: RegionAnchor; placement: DemoPlacement;
  /** False until the viewer's demo-store layout is known (boot gate); data requests for stores wait for it. */ ready: boolean };
const Context = createContext<LocationState | null>(null);
const ANCHOR_KEY = 'pf.anchor.v1';
const IP_KEY = 'pf.ip.v1';
const GATE_MS = 12000;
const round2 = (n: number) => Math.round(n * 100) / 100;

function browserZone() {
  try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch { return ''; }
}
function zoneLabel(zone: string) {
  const city = zone.split('/').pop() || '';
  return city && city !== 'UTC' ? city.replace(/_/g, ' ') : 'your area';
}
function savedAnchor(): { latitude: number; longitude: number } | null {
  try {
    const raw = JSON.parse(localStorage.getItem(ANCHOR_KEY) || 'null');
    if (raw && Number.isFinite(raw.latitude) && Number.isFinite(raw.longitude) && Math.abs(raw.latitude) <= 85 && Math.abs(raw.longitude) <= 180) return raw;
  } catch { /* storage unavailable or corrupt: fall back to the time zone */ }
  return null;
}
function cachedIp(): IpArea {
  try {
    const raw = JSON.parse(localStorage.getItem(IP_KEY) || 'null');
    if (raw && Number.isFinite(raw.latitude) && Number.isFinite(raw.longitude)) return raw;
  } catch { /* ignore */ }
  return null;
}
function persistAnchor(value: { latitude: number; longitude: number }) {
  try { localStorage.setItem(ANCHOR_KEY, JSON.stringify(value)); } catch { /* optional convenience only */ }
}
type IpArea = { latitude: number; longitude: number; city?: string; country?: string } | null;
/** Anchor candidates, best first: shared position, IP-derived city, last shared position, time-zone city. */
function buildCandidates(position: UserPosition | null, ip: IpArea): RegionAnchor[] {
  const list: RegionAnchor[] = [];
  if (position) list.push({ latitude: round2(position.latitude), longitude: round2(position.longitude), source: 'precise', label: 'your location' });
  if (ip) list.push({ latitude: round2(ip.latitude), longitude: round2(ip.longitude), source: 'ip', label: ip.city || ip.country || 'your area' });
  const saved = savedAnchor();
  if (saved) list.push({ ...saved, source: 'saved', label: 'your last location' });
  const zone = browserZone();
  const city = (tzCities as unknown as Record<string, [number, number]>)[zone];
  // Last resort (unknown zone): the original demo area, which the API treats as the unmoved catalogue.
  list.push(city ? { latitude: city[0], longitude: city[1], source: 'timezone', label: zoneLabel(zone) }
    : { latitude: 37.78, longitude: -122.41, source: 'timezone', label: 'the demo area' });
  return list.filter((x, i) => list.findIndex(y => y.latitude === x.latitude && y.longitude === x.longitude) === i);
}

export function LocationProvider({ children }: { children: ReactNode }) {
  const [position, setPosition] = useState<UserPosition | null>(null);
  const [permission, setPermission] = useState<LocationState['permission']>('prompt');
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef<Promise<UserPosition | null> | null>(null);
  const generation = useRef(0);
  const [ip, setIp] = useState<IpArea>(null);
  const ipRef = useRef<IpArea>(null);
  const [skip, setSkip] = useState({ key: '', n: 0 });
  const list = useMemo(() => buildCandidates(position, ip), [position, ip]);
  const key = list.map(x => `${x.latitude},${x.longitude}`).join('|');
  const step = skip.key === key ? Math.min(skip.n, list.length - 1) : 0;
  const anchor = list[step];
  const [placement, setPlacement] = useState<DemoPlacement>(null);
  const [ipResolved, setIpResolved] = useState(false);
  const [ready, setReady] = useState(false);
  const [nonce, setNonce] = useState(0);
  const polling = useRef(false);
  // The header must change BEFORE any state that triggers a fetch: set it synchronously at the source of every change.
  const initial = useRef(false);
  if (!initial.current) { initial.current = true; openGate(); setAnchor(anchor); }
  const release = () => { closeGate(); setReady(true); };
  useEffect(() => {  // boot: 1) IP city (3 s cap; cached IP only if the live lookup fails) 2) placement for it 3) release the gate
    let alive = true;
    const cap = window.setTimeout(() => { if (alive) release(); }, GATE_MS);
    const abort = new AbortController();
    const timeout = window.setTimeout(() => abort.abort(), 3000);
    api<IpArea>('/demo/ip-anchor', { signal: abort.signal }).then(value => {
      if (value) { try { localStorage.setItem(IP_KEY, JSON.stringify(value)); } catch { /* optional */ } }
      return value || cachedIp();
    }).catch(() => cachedIp()).then(value => {
      window.clearTimeout(timeout);
      if (!alive) return;
      ipRef.current = value; setIp(value); setIpResolved(true);
    });
    return () => { alive = false; window.clearTimeout(cap); window.clearTimeout(timeout); abort.abort(); };
  }, []);
  useLayoutEffect(() => {  // runs before children's fetch effects in the same commit
    if (!ipResolved) return;
    setAnchor(anchor);
    if (anchor.source === 'precise') persistAnchor(anchor);
    let alive = true;
    api<NonNullable<DemoPlacement> & { reason: string }>('/demo/placement').then(value => {
      if (!alive) return;
      // No land found around this anchor: try the next-best area (IP city, cached IP, last location, time-zone city) before accepting San Francisco.
      if (value.mode === 'original' && value.reason !== 'pending' && step < list.length - 1) { setSkip({ key, n: step + 1 }); return; }
      setPlacement(value); release();
    }).catch(() => { if (alive) { setPlacement(null); release(); } });
    return () => { alive = false; };
  }, [anchor, key, step, list.length, ipResolved]);
  // Self-healing: while the layout is not 'relocated', poll until it is, then re-fetch everything (no manual refresh needed).
  useEffect(() => { onPlacementSignal(state => { if (state === 'pending' && !polling.current) setNonce(n => n + 1); }); return () => onPlacementSignal(null); }, []);
  useEffect(() => {
    if (!ready || placement?.mode === 'relocated') return;
    let alive = true;
    polling.current = true;
    const until = Date.now() + 120000;
    (async () => {
      while (alive && Date.now() < until) {
        await new Promise(resolve => window.setTimeout(resolve, 1500));
        if (!alive) break;
        try {
          const value = await api<NonNullable<DemoPlacement>>('/demo/placement');
          if (alive && value.mode === 'relocated') { setPlacement(value); bumpAnchorVersion(); break; }
        } catch { /* keep trying until the deadline */ }
      }
      polling.current = false;
    })();
    return () => { alive = false; polling.current = false; };
  }, [ready, placement?.mode, key, step, nonce]);
  useEffect(() => {
    let status: PermissionStatus | undefined;
    let alive = true;
    if (!navigator.geolocation) { setPermission('unavailable'); return; }
    navigator.permissions?.query({ name: 'geolocation' }).then(next => {
      if (!alive) return;
      status = next;
      const update = () => {
        setPermission(next.state);
        if (next.state === 'denied') { generation.current++; setAnchor(buildCandidates(null, ipRef.current)[0]); setPosition(null); setLocating(false); }
      };
      next.onchange = update; update();
    }).catch(() => { /* Browsers without Permissions API still use the native prompt. */ });
    return () => { alive = false; if (status) status.onchange = null; };
  }, []);

  const request = () => {
    if (pending.current) return pending.current;
    if (!navigator.geolocation || !window.isSecureContext) {
      setError('Location needs HTTPS or localhost and a browser with geolocation support.');
      return Promise.resolve(null);
    }
    setLocating(true); setError('');
    const current = ++generation.current;
    pending.current = new Promise<UserPosition | null>(resolve => navigator.geolocation.getCurrentPosition(value => {
      const next = { latitude: value.coords.latitude, longitude: value.coords.longitude,
        accuracy: value.coords.accuracy, timestamp: value.timestamp };
      if (current === generation.current) {
        setAnchor(buildCandidates(next, ipRef.current)[0]);  // new header first, then the state that triggers refetches
        setPlacement(null);  // the previous area's placement no longer applies until the new one arrives
        setPosition(next); setPermission('granted');
      }
      resolve(current === generation.current ? next : null);
    }, issue => {
      if (current === generation.current) {
        setError(issue.code === 1 ? 'Location blocked. Open the site settings beside your browser address bar, allow Location, then try again.'
          : issue.code === 3 ? 'Location timed out. Try again or browse the demo area.' : 'Your device could not determine its location. Try again or browse the demo area.');
        if (issue.code === 1) { setPermission('denied'); setAnchor(buildCandidates(null, ipRef.current)[0]); setPosition(null); }
      }
      resolve(null);
    }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 })).finally(() => {
      pending.current = null; setLocating(false);
    });
    return pending.current;
  };
  return <Context.Provider value={{ position, permission, locating, error, request,
    clear: () => { generation.current++; setAnchor(buildCandidates(null, ipRef.current)[0]); setPosition(null); setError(''); setLocating(false); }, anchor, placement, ready }}>{children}</Context.Provider>;
}

export function useUserLocation() {
  const value = useContext(Context);
  if (!value) throw new Error('LocationProvider is required');
  return value;
}

export function straightLineKm(a: Pick<UserPosition, 'latitude' | 'longitude'>, b: { latitude: number; longitude: number }) {
  const radians = Math.PI / 180;
  const dLat = (b.latitude - a.latitude) * radians, dLng = (b.longitude - a.longitude) * radians;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.latitude * radians) * Math.cos(b.latitude * radians) * Math.sin(dLng / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(Math.min(1, h)));
}
