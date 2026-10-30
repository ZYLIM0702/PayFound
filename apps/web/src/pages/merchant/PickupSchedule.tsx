import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { BryntumCalendar } from '@bryntum/calendar-react';
import { CalendarPlus } from 'lucide-react';
import '@bryntum/calendar/fontawesome/css/fontawesome.css';
import '@bryntum/calendar/fontawesome/css/solid.css';
import '@bryntum/calendar/calendar.css';
import '@bryntum/calendar/svalbard-light.css';
import '../../styles/bryntum-theme.css';
import { scoped, type MerchantLocation, type Order, type PickupSlot } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { ErrorLine, Notice } from '../../components/Shared';
import { PickupCalendar } from './pickup/PickupCalendar';
import { RotaCalendar } from './pickup/RotaCalendar';
import { QueueBoard } from './pickup/QueueBoard';
import { WindowSheet, type WindowDraft } from './pickup/WindowSheet';
import { UtilisationStrip } from './pickup/UtilisationStrip';
import { branchColour, branchInfos, branchTimezone, buildEvents, daysAround, rushRanges } from './pickup/model';
import { buildRota, deskCover, rotaStaff } from './pickup/rota';
import { addDays, dayBoundsIn, dayKeyIn, wallToUtc } from './pickup/tz';
import { useMerchant } from './context';

type Slots = { slots: PickupSlot[]; truncated: boolean };
type StaffList = { memberships: { id: string; subject: string; role: string; active: boolean }[] };
type View = 'capacity' | 'rota' | 'queue';
const slotsPath = (merchantId: string, start: string, end: string) => scoped(`/merchant/pickup-slots?start_at=${encodeURIComponent(start)}&end_at=${encodeURIComponent(end)}`, merchantId);
const SNAP_MS = 5 * 60000;
const VIEWS: [View, string][] = [['capacity', 'Capacity'], ['rota', 'Staff rota'], ['queue', 'Queue board']];

export function PickupSchedule({ merchantId, orders }: { merchantId: string; orders: Order[] }) {
  const { busy, run, requestRefund } = useMerchant();
  const locations = useResource<MerchantLocation[]>(scoped('/merchant/locations', merchantId));
  const staffRes = useResource<StaffList>(scoped('/merchant/staff', merchantId));
  const tz = useMemo(() => branchTimezone(locations.data), [locations.data]);
  const [view, setView] = useState<View>('capacity');
  const [dayKey, setDayKey] = useState<string | null>(null);
  const todayKey = useMemo(() => dayKeyIn(new Date(), tz), [tz]);
  const date = dayKey || todayKey;
  const [wall, setWall] = useState<{ start: number; end: number } | null>(null);
  const fallback = useMemo(() => ({ start: dayBoundsIn(addDays(date, -1), tz).start, end: dayBoundsIn(addDays(date, 8), tz).end }), [date, tz]);
  const range = useMemo(() => wall ? { start: new Date(wallToUtc(new Date(wall.start), tz).getTime() - 86400000).toISOString(), end: new Date(wallToUtc(new Date(wall.end), tz).getTime() + 86400000).toISOString() } : null, [wall, tz]);
  const visible = range || fallback;
  const slots = useResource<Slots>(slotsPath(merchantId, visible.start, visible.end), 15000);
  const todayBounds = useMemo(() => dayBoundsIn(todayKey, tz), [todayKey, tz]);
  const today = useResource<Slots>(slotsPath(merchantId, todayBounds.start, todayBounds.end), 30000);
  const [draft, setDraft] = useState<WindowDraft | null>(null);
  const [notice, setNotice] = useState('');
  const calendarDate = useMemo(() => { const [y, m, d] = date.split('-').map(Number); return new Date(y, m - 1, d, 12); }, [date]);
  const allBranches = useMemo(() => branchInfos(locations.data), [locations.data]);
  // Branches that publish no pickup windows (e.g. connector-created stores) would only add empty lanes.
  const branches = useMemo(() => { const withSlots = new Set([...(slots.data?.slots || []), ...(today.data?.slots || [])].map(s => s.location_id)); const kept = allBranches.filter(b => withSlots.has(b.id)); return (kept.length ? kept : allBranches).map((b, idx) => ({ ...b, idx, colour: branchColour(idx) })); }, [allBranches, slots.data, today.data]);
  const events = useMemo(() => buildEvents(slots.data?.slots || [], orders, branches.map(b => b.id), tz), [slots.data, orders, branches, tz]);
  const [mode, setMode] = useState('dayresource');
  const cal = useRef<BryntumCalendar>(null);
  // Send only the event set for the active view: per-branch blocks in Branches, all-branch blocks elsewhere.
  const shownEvents = useMemo(() => events.filter(e => (mode === 'dayresource') === (e.scope === 'branch')), [events, mode]);
  const days = useMemo(() => daysAround(date, 3, 10), [date]);
  const timeRanges = useMemo(() => rushRanges(days, tz), [days, tz]);
  const staff = useMemo(() => rotaStaff(staffRes.data?.memberships), [staffRes.data]);
  const shifts = useMemo(() => buildRota(staff, days, tz, branches.map(b => b.short)), [staff, days, tz, branches]);
  const cover = useMemo(() => deskCover(shifts, todayKey, tz), [shifts, todayKey, tz]);
  const dayOrders = useMemo(() => orders.filter(o => o.pickup_window && dayKeyIn(new Date(o.pickup_window.start_at), tz) === date).sort((a, b) => a.pickup_window!.start_at.localeCompare(b.pickup_window!.start_at)), [orders, date, tz]);
  const todayOrders = useMemo(() => orders.filter(o => o.pickup_window && dayKeyIn(new Date(o.pickup_window.start_at), tz) === todayKey).length, [orders, todayKey, tz]);
  const [dayLabel, setDayLabel] = useState('');
  useEffect(() => { setDayLabel(new Date(`${date}T12:00:00Z`).toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' })); }, [date]);

  const syncRange = useCallback((start?: Date, end?: Date) => {
    if (!start || !end || Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return;
    const next = { start: start.getTime(), end: end.getTime() };
    setWall(current => current?.start === next.start && current.end === next.end ? current : next);
  }, []);
  const refreshAll = useCallback(async () => { await Promise.all([slots.refresh(), today.refresh()]); setNotice('Pickup window published.'); }, [slots, today]);
  const openNew = () => { const start = new Date(Math.ceil((Date.now() + 3600000) / 3600000) * 3600000); setDraft({ start, end: new Date(start.getTime() + 7200000) }); };

  return <div className="pf-pickup flex flex-col gap-4">
    <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3">
      <div className="min-w-0"><h1 className="pf-heading">Pickup schedule</h1><p className="pf-muted text-[14px] mt-1.5">Times in branch time ({tz.replace('_', ' ')}). Drag across empty time to open a new window; capacity is enforced by the server.</p></div>
      <div className="flex items-center gap-3 flex-wrap">
        <div className="pf-segmented" role="group" aria-label="Pickup view">{VIEWS.map(([v, l]) => <button key={v} aria-pressed={view === v} onClick={() => setView(v)} data-testid={`pickup-view-${v}`}>{l}</button>)}</div>
        <button className="pf-btn accent" onClick={openNew} data-testid="new-pickup-window"><CalendarPlus size={16} />New pickup window</button>
      </div>
    </div>
    <UtilisationStrip slots={today.data?.slots || []} orderPickups={todayOrders} loading={today.loading} branches={branches} tz={tz} cover={cover} />
    <ErrorLine message={slots.error || locations.error} />
    {notice && <Notice tone="green">{notice}</Notice>}
    {slots.data?.truncated && <Notice>This period exceeds 5,000 windows. Choose a shorter calendar view to see a complete schedule.</Notice>}
    {!locations.data && !locations.error && <p className="text-sm text-muted">Loading branches…</p>}
    {locations.data && view === 'capacity' && <>
      <div className="pf-legend" aria-label="Legend">
        {branches.map(b => <span key={b.id} className="pf-branch-chip" style={{ '--pf-branch': b.colour } as React.CSSProperties}><i />{b.name}</span>)}
        <span className="pf-lg-sep" /><span className="pf-lg low">Under 50%</span><span className="pf-lg mid">50–85%</span><span className="pf-lg high">Over 85%</span><span className="pf-lg rush">Expected rush</span>
      </div>
      <div className="pf-pickup-cal" aria-busy={slots.refreshing}>
        <PickupCalendar ref={cal} events={shownEvents} branches={branches} date={calendarDate} timeZone={tz} timeRanges={timeRanges}
          onActiveItemChange={e => setMode(String((e.source as unknown as { mode?: string }).mode || 'dayresource'))}
          onDateChange={({ date: next }) => setDayKey(`${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, '0')}-${String(next.getDate()).padStart(2, '0')}`)}
          onDateRangeChange={({ new: next }) => syncRange(next.startDate, next.endDate)}
          onViewPaint={({ source: v }) => {
            if ('isVisible' in v && v.isVisible === false) return;
            setMode(String(cal.current?.instance?.mode || 'dayresource'));
            if ('startDate' in v && 'endDate' in v && v.startDate instanceof Date && v.endDate instanceof Date) syncRange(v.startDate, v.endDate);
          }}
          onBeforeDragCreate={({ date: at }) => at.getTime() + 60000 >= Date.now()}
          onBeforeDragCreateEnd={({ newStartDate, newEndDate, resourceRecord }) => {
            const start = wallToUtc(new Date(Math.round(newStartDate.getTime() / SNAP_MS) * SNAP_MS), tz);
            const end = new Date(Math.max(wallToUtc(new Date(Math.round(newEndDate.getTime() / SNAP_MS) * SNAP_MS), tz).getTime(), start.getTime() + SNAP_MS));
            setDraft({ locationId: resourceRecord ? String(resourceRecord.id) : undefined, start, end });
            return false;
          }} />
      </div>
    </>}
    {locations.data && view === 'rota' && <>
      <p className="text-[13px] text-muted">Demo rota: staff come from your team (padded with fictional colleagues) and shifts are generated for the demo, not stored. {dayLabel && <span>Showing {dayLabel}.</span>}</p>
      <div className="pf-pickup-cal"><RotaCalendar staff={staff} shifts={shifts} date={calendarDate} timeZone={tz} timeRanges={timeRanges} /></div>
    </>}
    {view === 'queue' && <section className="pf-card flat !p-0 overflow-hidden" data-testid="pickup-queue">
      <div className="px-5 py-3.5 border-b border-line flex flex-wrap items-center justify-between gap-2"><strong className="font-display text-[17px]">Pickup queue</strong><span className="text-[13px] text-muted">{dayLabel} · {dayOrders.length} pickup{dayOrders.length === 1 ? '' : 's'} · actions use the same fulfilment endpoints as Orders</span></div>
      <QueueBoard orders={dayOrders} tz={tz} busy={busy} run={run} requestRefund={requestRefund} />
    </section>}
    <WindowSheet draft={draft} merchantId={merchantId} locations={locations.data || []} onClose={() => setDraft(null)} onSaved={refreshAll} />
  </div>;
}
