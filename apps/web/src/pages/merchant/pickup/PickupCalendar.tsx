import { forwardRef, useEffect, useMemo, useRef, useState } from 'react';
import { BryntumCalendar, type BryntumCalendarProps } from '@bryntum/calendar-react';
import type { EventModel } from '@bryntum/calendar';
import { esc, timeRange, toneOf, utilisationOf, type BranchInfo, type PickupEvent } from './model';

type Ctx = { eventRecord: EventModel; renderData: { cls: object; iconCls: unknown } };
const TONE_LABEL = { low: 'Quiet', mid: 'Filling', high: 'Nearly full' } as const;

/** One readable block per branch per hour: big remaining/capacity, a fill bar, an orders chip. Colour = utilisation, stripe = branch. */
function eventRenderer({ eventRecord, renderData }: Ctx) {
  const cls = renderData.cls as Record<string, boolean>;
  const get = <T,>(field: string) => eventRecord.get(field) as T | undefined;
  const capacity = get<number>('capacity') || 0; const remaining = get<number>('remaining') ?? 0; const orders = get<number>('orders') || 0;
  const used = utilisationOf({ capacity, remaining }); const tone = toneOf(used);
  const full = remaining === 0 && capacity > 0;
  renderData.iconCls = '';
  cls['pf-ev'] = true; cls[`pf-tone-${tone}`] = true; cls['pf-ev-full'] = full;
  const branch = get<number>('branchIdx');
  if (get<string>('scope') === 'branch' && branch !== undefined) cls[`pf-br-${branch % 6}`] = true;
  return [
    { class: 'pf-ev-row', children: [
      { tag: 'b', class: 'pf-ev-big', text: full ? 'Full' : String(remaining) },
      { tag: 'span', class: 'pf-ev-of', text: full ? `${capacity}/${capacity}` : `of ${capacity} left` },
      ...(orders ? [{ tag: 'span', class: 'pf-ev-orders', text: `${orders} order${orders > 1 ? 's' : ''}` }] : []),
    ] },
    { class: 'pf-ev-fill-track', children: [{ class: 'pf-ev-fill', style: { width: `${Math.round(used * 100)}%` } }] },
  ];
}

const HOURS = { dayStartTime: 7, dayEndTime: 21, hourHeight: 68, minEventHeight: 40, visibleStartTime: 7 };
export type CalendarHandlers = Pick<BryntumCalendarProps, 'onDateChange' | 'onDateRangeChange' | 'onViewPaint' | 'onBeforeDragCreate' | 'onBeforeDragCreateEnd' | 'onActiveItemChange'>;
type TimeRange = { id: string; name: string; startDate: Date; endDate: Date; cls: string };

export const PickupCalendar = forwardRef<BryntumCalendar, { events: PickupEvent[]; branches: BranchInfo[]; date: Date; timeZone: string; timeRanges: TimeRange[] } & CalendarHandlers>(function PickupCalendar({ events, branches, date, timeZone, timeRanges, ...handlers }, ref) {
  const names = useMemo(() => Object.fromEntries(branches.map(b => [String(b.idx), b.short])), [branches]);
  const namesRef = useRef(names);
  useEffect(() => { namesRef.current = names; }, [names]);
  const [props] = useState<BryntumCalendarProps>(() => {
    const tooltip = ({ eventRecord }: { eventRecord: EventModel }) => {
      const get = (f: string) => eventRecord.get(f) as unknown;
      const capacity = Number(get('capacity')) || 0; const remaining = Number(get('remaining')) || 0; const booked = capacity - remaining;
      const used = utilisationOf({ capacity, remaining }); const tone = toneOf(used);
      const when = timeRange(eventRecord.startDate as Date, eventRecord.endDate as Date);
      const lines = String(get('orderLines') || '').split('|').filter(Boolean);
      const orders = Number(get('orders')) || 0;
      const windows = String(get('windows') || '').split('|').filter(Boolean);
      const parts = String(get('breakdown') || '').split('|').filter(Boolean).map(p => { const [i, v] = p.split(':'); return `<li><span>${esc(namesRef.current[i] || 'Branch')}</span><b>${esc(v)}</b></li>`; }).join('');
      return `<div class="pf-tip"><div class="pf-tip-kicker">${get('scope') === 'all' ? 'All branches' : 'Pickup capacity'} · <span class="pf-tip-pill pf-tone-${tone}">${TONE_LABEL[tone]}</span></div>
        <div class="pf-tip-title">${remaining} of ${capacity} spaces left</div>
        <div class="pf-ev-fill-track pf-tip-bar pf-tone-${tone}"><div class="pf-ev-fill" style="width:${Math.round(used * 100)}%"></div></div>
        <dl><dt>Booked</dt><dd>${booked} (${Math.round(used * 100)}%)</dd><dt>Remaining</dt><dd>${remaining}</dd><dt>Hour</dt><dd>${esc(when)}</dd>${orders ? `<dt>Order pickups</dt><dd>${orders}</dd>` : ''}</dl>
        ${parts ? `<ul class="pf-tip-list pf-tip-split">${parts}</ul>` : ''}
        ${lines.length ? `<div class="pf-tip-sub">Orders in this hour</div><ul class="pf-tip-list">${lines.map(l => `<li>${esc(l)}</li>`).join('')}${orders > lines.length ? `<li>+${orders - lines.length} more</li>` : ''}</ul>` : ''}
        ${windows.length > 1 ? `<div class="pf-tip-sub">${windows.length} windows</div><ul class="pf-tip-list">${windows.map(w => `<li>${esc(w)}</li>`).join('')}</ul>` : ''}
        <p class="pf-tip-note">Published windows are managed by the server.</p></div>`;
    };
    return {
      height: '100%', mode: 'dayresource', cls: 'pf-bryntum', hideNonWorkingDays: false, timeZone,
      modeDefaults: { eventRenderer },
      modes: { dayresource: { title: 'Branches', range: '1d', ...HOURS }, day: HOURS, week: { ...HOURS, hourHeight: 56 }, month: true, agenda: true, year: false },
      sidebar: false,
      tbar: { items: { prevButton: { ariaLabel: 'Previous calendar period' }, nextButton: { ariaLabel: 'Next calendar period' } } },
      eventEditFeature: false, eventMenuFeature: false, eventCopyPasteFeature: false,
      eventTooltipFeature: { renderer: tooltip, align: 'l-r' },
      timeRangesFeature: { showCurrentTimeLine: true, showHeaderElements: false },
    };
  });
  const resources = useMemo(() => branches.map(b => ({ id: b.id, name: b.short, eventColor: b.colour, cls: `pf-br pf-br-${b.idx % 6}` })), [branches]);
  const resourceRanges = useMemo(() => branches.flatMap(b => timeRanges.map(r => ({ id: `${r.id}-${b.id}`, resourceId: b.id, name: r.name, startDate: r.startDate, endDate: r.endDate, cls: r.cls }))), [branches, timeRanges]);
  return <BryntumCalendar ref={ref} {...props} {...handlers} date={date} events={events} resources={resources} timeRanges={timeRanges} resourceTimeRanges={resourceRanges} />;
});
