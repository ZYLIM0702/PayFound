import { Chip, type Tone } from '../../../components/Shared';
import type { Confidence } from '../overviewTypes';

export const weekday = (iso: string) => new Date(iso + 'T12:00:00').toLocaleDateString([], { weekday: 'short' });
export const shortDate = (iso: string) => new Date(iso + 'T12:00:00').toLocaleDateString([], { month: 'short', day: 'numeric' });
export const signed = (n: number) => `${n > 0 ? '+' : ''}${n}%`;

const CONF: Record<Confidence, [Tone, string, string]> = {
  observed: ['green', 'Observed', 'Measured from this store\'s own data'],
  modelled: ['blue', 'Modelled', 'Real input data with an assumed effect size'],
  demo: ['amber', 'Demo', 'Demo-only input (fictional feed or demo calendar)'],
  not_modelled: ['default', 'Not modelled', 'A real driver we have no data for yet'],
  unavailable: ['default', 'Unavailable', 'Data could not be loaded'],
};
export function ConfidenceChip({ value }: { value: Confidence }) {
  const [kind, label, title] = CONF[value] ?? CONF.demo;
  return <span title={title}><Chip kind={kind}>{label}</Chip></span>;
}

export function Skel({ h = 'h-40' }: { h?: string }) { return <div className={`pf-skeleton ${h}`} />; }
export function EmptyLine({ children }: { children: React.ReactNode }) { return <p className="text-sm text-muted py-4">{children}</p>; }
