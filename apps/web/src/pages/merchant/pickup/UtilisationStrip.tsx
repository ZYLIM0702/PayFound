import type { PickupSlot } from '../../../lib/api';
import { hourIn } from './tz';
import { toneOf, type BranchInfo } from './model';

const HOURS = Array.from({ length: 14 }, (_, i) => i + 7); // 07:00-20:00
const label = (h: number) => `${h % 12 || 12}${h < 12 ? 'a' : 'p'}`;

/** Capacity planning for today: totals, per-branch utilisation, and hour-by-hour coverage gaps (full / empty / no desk cover). */
export function UtilisationStrip({ slots, orderPickups, loading, branches, tz, cover }: { slots: PickupSlot[]; orderPickups: number; loading: boolean; branches: BranchInfo[]; tz: string; cover: number[] | null }) {
  const capacity = slots.reduce((sum, s) => sum + s.capacity, 0);
  const remaining = slots.reduce((sum, s) => sum + s.remaining, 0);
  const booked = capacity - remaining;
  const used = capacity ? booked / capacity : 0;
  const perHour = HOURS.map(h => {
    const mine = slots.filter(s => hourIn(new Date(s.start_at), tz) === h);
    const cap = mine.reduce((n, s) => n + s.capacity, 0); const bk = cap - mine.reduce((n, s) => n + s.remaining, 0);
    const u = cap ? bk / cap : 0;
    const flag = !cap ? 'closed' : u > 0.9 ? 'tight' : bk === 0 ? 'empty' : cover && (cover[h] ?? 0) === 0 && u > 0.4 ? 'nocover' : 'ok';
    return { h, cap, bk, u, flag };
  });
  const gaps = perHour.filter(x => ['tight', 'empty', 'nocover'].includes(x.flag));
  const perBranch = branches.map(b => { const mine = slots.filter(s => s.location_id === b.id); const cap = mine.reduce((n, s) => n + s.capacity, 0); const bk = cap - mine.reduce((n, s) => n + s.remaining, 0); return { b, cap, bk, u: cap ? bk / cap : 0 }; });
  const cells: [string, string | number, string?][] = [['Windows today', slots.length], ['Capacity', capacity], ['Booked', booked], ['Remaining', remaining, remaining === 0 && capacity > 0 ? 'text-bad' : ''], ['Order pickups', orderPickups]];
  return <section aria-label="Today's pickup capacity" className="pf-util">
    <div className="pf-util-top">
      <div className="pf-util-cells">{cells.map(([name, value, tone]) => <div key={name} className="pf-util-cell"><span className="pf-stat-label">{name}</span><strong className={`pf-stat-number ${tone || ''}`}>{loading ? '–' : value}</strong></div>)}</div>
      <div className="pf-util-meter" role="img" aria-label={`${Math.round(used * 100)}% of today's capacity booked`}><div className="flex justify-between text-[13px]"><span className="pf-muted">Utilisation today</span><strong className="tabular">{Math.round(used * 100)}%</strong></div><div className={`pf-meter pf-tone-${toneOf(used)}`}><i style={{ width: `${Math.round(used * 100)}%` }} /></div>
        <div className="pf-branch-chips">{perBranch.map(x => <span key={x.b.id} className="pf-branch-chip" style={{ '--pf-branch': x.b.colour } as React.CSSProperties}><i />{x.b.short}<b className={`pf-tone-${toneOf(x.u)}`}>{Math.round(x.u * 100)}%</b></span>)}</div></div>
    </div>
    <div className="pf-cover" data-testid="capacity-planning">
      <div className="pf-cover-head"><strong>Capacity planning</strong><span className="pf-muted">{loading ? 'Loading…' : gaps.length ? `${gaps.length} hour${gaps.length > 1 ? 's' : ''} need attention today` : 'No coverage gaps today'}</span></div>
      <div className="pf-cover-bars" role="list" aria-label="Booked share by hour today">{perHour.map(x => <div key={x.h} role="listitem" className={`pf-cover-col pf-flag-${x.flag}`} title={x.cap ? `${label(x.h)}: ${x.bk}/${x.cap} booked${x.flag === 'tight' ? ' – over 90%' : x.flag === 'empty' ? ' – nothing booked' : x.flag === 'nocover' ? ' – no one on the pickup desk (demo rota)' : ''}` : `${label(x.h)}: closed`}><div className="pf-cover-bar"><i className={`pf-tone-${toneOf(x.u)}`} style={{ height: `${Math.max(x.cap ? 4 : 0, Math.round(x.u * 100))}%` }} /></div><span>{label(x.h)}</span></div>)}</div>
      <div className="pf-cover-legend"><span className="pf-lg tight">Over 90% booked</span><span className="pf-lg empty">Nothing booked</span><span className="pf-lg nocover">Busy, no desk cover (demo rota)</span></div>
    </div>
  </section>;
}
