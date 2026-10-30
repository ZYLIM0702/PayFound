import { ArrowUpRight, Car, LocateFixed, Navigation, RefreshCw } from 'lucide-react';
import { useUserLocation } from '../lib/location';
import { formatDistance, formatDuration, googleDirections } from '../lib/directions';
import type { useDrivingRoute } from '../lib/use-driving-route';
import { ErrorLine } from './Shared';

export function DirectionsPanel({ destination, driving }: { destination: { latitude: number; longitude: number; name?: string };
  driving: ReturnType<typeof useDrivingRoute> }) {
  const location = useUserLocation();
  const route = driving.route;
  const time = (value: string) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return <div className="flex flex-col gap-3">
    <div className="flex flex-wrap gap-2">
      <button className="pf-btn sm flex-1" disabled={driving.busy || location.locating} onClick={() => void driving.load()}><Navigation size={15} />{driving.busy ? 'Finding route…' : location.locating ? 'Locating…' : route ? 'Refresh route' : 'Show driving route'}</button>
      <a className="pf-btn sm outline flex-1" href={googleDirections(destination, location.position)} target="_blank" rel="noreferrer">Google Maps<ArrowUpRight size={14} /></a>
    </div>
    {!location.position && <p className="flex items-center gap-1.5 text-xs text-muted"><LocateFixed size={13} className="shrink-0" />Allow location when prompted to get your distance and route.</p>}
    <ErrorLine message={driving.error || location.error} />
    {route && <div className="rounded-[var(--pf-r-md)] bg-canvas p-4" data-testid="driving-route-result">
      <dl className="grid grid-cols-3 gap-3">
        <div><dt className="text-xs text-muted flex items-center gap-1"><Car size={13} />Driving</dt><dd className="font-display text-2xl font-semibold tracking-tight tabular">{formatDuration(route.duration_seconds)}</dd></div>
        <div><dt className="text-xs text-muted">By road</dt><dd className="font-display text-2xl font-semibold tracking-tight tabular">{formatDistance(route.distance_m / 1000)}</dd></div>
        <div><dt className="text-xs text-muted">Arrive</dt><dd className="font-display text-2xl font-semibold tracking-tight tabular">{time(route.arrival_at)}</dd></div>
      </dl>
      <p className="flex items-center gap-2 text-xs text-muted mt-3"><span className={`w-1.5 h-1.5 rounded-full ${route.traffic_aware ? 'bg-ok' : 'bg-subtle'}`} /><strong className="font-semibold text-ink-2">{route.traffic_aware ? 'Traffic-aware ETA' : 'Without live traffic'}</strong><span>Updated {time(route.fetched_at)}</span>{driving.busy && <RefreshCw size={12} className="animate-spin" />}</p>
      <p className="text-xs text-muted mt-1.5">{route.traffic_aware ? 'Includes Google Maps traffic conditions. Refreshes every minute while this page is visible.' : 'Road-network estimate; traffic conditions are not included.'}</p>
      {route.provider === 'google' && <span className="pf-google-attribution block mt-2" translate="no">Google Maps</span>}
      <details className="mt-3 border-t border-line pt-3 text-[13px]"><summary className="cursor-pointer font-semibold">Route directions ({route.steps.length})</summary>
        <ol className="mt-3 max-h-56 overflow-auto flex flex-col gap-2.5">{route.steps.map((step, i) => <li key={i} className="flex gap-3"><span className="w-5 text-subtle tabular shrink-0">{i + 1}</span><p className="flex-1">{step.instruction}<small className="block text-xs text-muted">{formatDistance(step.distance_m / 1000)}</small></p></li>)}</ol>
      </details>
    </div>}
  </div>;
}
