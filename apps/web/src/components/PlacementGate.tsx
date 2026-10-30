import type { ReactNode } from 'react';
import { Monogram } from './Brand';
import { Spinner } from './Shared';
import { useUserLocation } from '../lib/location';

/** Holds the routed content until the viewer's demo stores are laid out near them, so the first screen is never the wrong city. */
export function PlacementGate({ children }: { children: ReactNode }) {
  const { ready, anchor } = useUserLocation();
  if (ready) return <>{children}</>;
  const near = anchor.source === 'ip' || anchor.source === 'precise' ? anchor.label : 'you';
  return <main className="pf-container min-h-[60vh] grid place-items-center" data-testid="placement-gate" aria-busy="true">
    <div className="flex flex-col items-center gap-5 text-center">
      <Monogram size={44} />
      <Spinner inline label={`Finding stores near ${near}…`} />
    </div>
  </main>;
}
