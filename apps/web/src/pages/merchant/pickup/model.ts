import type { MerchantLocation, Order, PickupSlot } from '../../../lib/api';
import { addDays, DEFAULT_TZ, weekdayOf, zonedToUtc } from './tz';

export type PickupScope = 'branch' | 'all';

/** Plain event data handed to Bryntum. One block per branch per hour (scope 'branch') or per hour across branches (scope 'all'). */
export type PickupEvent = {
  id: string; resourceId?: string; name: string; startDate: string; endDate: string; readOnly: true; scope: PickupScope;
  capacity: number; remaining: number; count: number; windows: string; orders: number; orderLines: string; branchIdx?: number; branchName?: string; breakdown?: string;
};

export const utilisationOf = (slot: Pick<PickupSlot, 'capacity' | 'remaining'>) => slot.capacity > 0 ? Math.min(1, Math.max(0, (slot.capacity - slot.remaining) / slot.capacity)) : 0;
/** green below 50%, amber 50-85%, red above 85%. */
export const toneOf = (utilisation: number) => utilisation >= 0.85 ? 'high' : utilisation >= 0.5 ? 'mid' : 'low';

export const BRANCH_COLOURS = ['#0057ff', '#0d9488', '#7c3aed', '#db2777', '#ea580c', '#0891b2'];
export const branchColour = (idx: number) => BRANCH_COLOURS[idx % BRANCH_COLOURS.length];
const HOUR = 3600000;
const fmt = (iso: string, tz: string) => new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', timeZone: tz });

/** "Northside Electronics Marina" -> "Marina": drop the merchant prefix so branch names stay readable in narrow headers. */
export function shortBranch(name: string, all: string[]) {
  if (all.length < 2) return name.replace(/ Main$/, '') || name;
  const words = all.map(n => n.split(' '));
  let common = 0;
  while (words.every(w => w[common] && w[common] === words[0][common])) common++;
  const out = name.split(' ').slice(common).join(' ');
  return out || 'Main';
}

function orderLine(o: Order) { return `${o.buyer_name || 'Customer'} · ${o.product_name}${o.quantity > 1 ? ` ×${o.quantity}` : ''} · ${o.status}`; }

export function buildEvents(slots: PickupSlot[], orders: Order[], branchIds: string[], tz: string): PickupEvent[] {
  const idx = new Map(branchIds.map((id, i) => [id, i]));
  const pickups = orders.filter(o => o.pickup_window);
  const byHour = new Map<string, PickupSlot[]>();
  for (const s of slots) {
    const hour = Math.floor(Date.parse(s.start_at) / HOUR);
    const key = `${s.location_id || ''}|${hour}`;
    byHour.set(key, [...(byHour.get(key) || []), s]);
  }
  const branch: PickupEvent[] = [];
  const all = new Map<number, { capacity: number; remaining: number; count: number; orders: number; parts: Map<number, [number, number]> }>();
  for (const [key, group] of byHour) {
    const [loc, hourText] = key.split('|');
    const hour = Number(hourText);
    const capacity = group.reduce((n, g) => n + g.capacity, 0); const remaining = group.reduce((n, g) => n + g.remaining, 0);
    const here = pickups.filter(o => o.location_id === loc && Math.floor(Date.parse(o.pickup_window!.start_at) / HOUR) === hour);
    const bi = idx.get(loc) ?? 0;
    branch.push({ id: `b-${loc}-${hour}`, resourceId: loc || undefined, name: `${remaining}/${capacity}`, startDate: new Date(hour * HOUR).toISOString(), endDate: new Date((hour + 1) * HOUR).toISOString(),
      readOnly: true, scope: 'branch', capacity, remaining, count: group.length, orders: here.length, orderLines: here.slice(0, 6).map(orderLine).join('|'), branchIdx: bi,
      windows: group.sort((a, b) => Date.parse(a.start_at) - Date.parse(b.start_at)).map(g => `${fmt(g.start_at, tz)}–${fmt(g.end_at, tz)} (${g.capacity - g.remaining}/${g.capacity} booked)`).join('|') });
    const agg = all.get(hour) || { capacity: 0, remaining: 0, count: 0, orders: 0, parts: new Map() };
    agg.capacity += capacity; agg.remaining += remaining; agg.count += group.length; agg.orders += here.length;
    const part = agg.parts.get(bi) || [0, 0]; agg.parts.set(bi, [part[0] + capacity - remaining, part[1] + capacity]);
    all.set(hour, agg);
  }
  const names = (i: number) => String(i);
  const aggregated = [...all].map<PickupEvent>(([hour, a]) => ({ id: `a-${hour}`, name: `${a.remaining}/${a.capacity}`, startDate: new Date(hour * HOUR).toISOString(), endDate: new Date((hour + 1) * HOUR).toISOString(),
    readOnly: true, scope: 'all', capacity: a.capacity, remaining: a.remaining, count: a.count, orders: a.orders, orderLines: '', windows: '',
    breakdown: [...a.parts].sort((x, y) => x[0] - y[0]).map(([bi, [b, c]]) => `${names(bi)}:${b}/${c}`).join('|') }));
  return [...branch, ...aggregated];
}

export type BranchInfo = { id: string; name: string; short: string; idx: number; colour: string };
export function branchInfos(locations: MerchantLocation[] | null | undefined): BranchInfo[] {
  const active = (locations || []).filter(l => l.active !== false);
  return active.map((l, idx) => ({ id: l.id, name: l.name, short: shortBranch(l.name, active.map(a => a.name)), idx, colour: branchColour(idx) }));
}
export const branchTimezone = (locations: MerchantLocation[] | null | undefined) => locations?.find(l => l.active !== false)?.timezone || DEFAULT_TZ;

/** Expected rush periods, drawn as Bryntum time ranges in branch time. */
export function rushRanges(dayKeys: string[], tz: string) {
  const out: { id: string; name: string; startDate: Date; endDate: Date; cls: string }[] = [];
  for (const day of dayKeys) {
    const weekend = [0, 6].includes(weekdayOf(day));
    const spans: [string, number, number, number, number][] = weekend ? [['Weekend peak', 10, 0, 15, 0]] : [['Lunch rush', 11, 30, 13, 30], ['After-work rush', 17, 0, 19, 0]];
    for (const [name, h1, m1, h2, m2] of spans) out.push({ id: `rush-${day}-${h1}`, name, startDate: zonedToUtc(day, h1, m1, tz), endDate: zonedToUtc(day, h2, m2, tz), cls: 'pf-rush' });
  }
  return out;
}
export const daysAround = (centre: string, before = 1, after = 7) => Array.from({ length: before + after + 1 }, (_, i) => addDays(centre, i - before));

/** yyyy-MM-ddTHH:mm in the browser's local zone, as <input type="datetime-local"> expects. */
export function toLocalInput(date: Date) {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}T${p(date.getHours())}:${p(date.getMinutes())}`;
}

export const esc = (value: unknown) => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!);
export const timeRange = (start: Date, end: Date) => `${start.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}, ${start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })} – ${end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
