import { useMemo, useState } from 'react';
import { BryntumCalendar, type BryntumCalendarProps } from '@bryntum/calendar-react';
import type { EventModel } from '@bryntum/calendar';
import { esc, timeRange } from './model';
import type { RotaStaff, Shift } from './rota';

type Ctx = { eventRecord: EventModel; renderData: { cls: object; iconCls: unknown } };
function renderer({ eventRecord, renderData }: Ctx) {
  const cls = renderData.cls as Record<string, boolean>; renderData.iconCls = '';
  const kind = eventRecord.get('kind') as string;
  cls['pf-ev'] = true; cls['pf-shift'] = true; cls[`pf-shift-${kind}`] = true;
  return [{ class: 'pf-ev-row', children: [{ tag: 'b', class: 'pf-ev-shift', text: eventRecord.get('name') as string }] }, { class: 'pf-ev-meta', text: eventRecord.get('branchName') as string }];
}
const tooltip = ({ eventRecord }: { eventRecord: EventModel }) => `<div class="pf-tip"><div class="pf-tip-kicker">Demo rota</div><div class="pf-tip-title">${esc(eventRecord.get('name'))}</div><dl><dt>Branch</dt><dd>${esc(eventRecord.get('branchName'))}</dd><dt>Shift</dt><dd>${esc(timeRange(eventRecord.startDate as Date, eventRecord.endDate as Date))}</dd></dl><p class="pf-tip-note">${eventRecord.get('kind') === 'desk' ? 'Covers customer pickups at the desk.' : 'Packs and stages orders for collection.'} Generated for the demo; not stored.</p></div>`;

/** Staff as resources, shifts as events: who covers pickup, and when. */
export function RotaCalendar({ staff, shifts, date, timeZone, timeRanges }: { staff: RotaStaff[]; shifts: Shift[]; date: Date; timeZone: string; timeRanges: { id: string; name: string; startDate: Date; endDate: Date; cls: string }[] }) {
  const [props] = useState<BryntumCalendarProps>(() => ({
    height: '100%', mode: 'dayresource', cls: 'pf-bryntum pf-rota', timeZone, sidebar: false,
    modeDefaults: { eventRenderer: renderer },
    modes: { dayresource: { title: 'Staff', range: '1d', dayStartTime: 7, dayEndTime: 21, hourHeight: 52, visibleStartTime: 7 }, day: false, week: false, month: false, agenda: false, year: false },
    eventEditFeature: false, eventMenuFeature: false, eventDragFeature: false, eventResizeFeature: false, eventCopyPasteFeature: false, eventDragCreateFeature: false,
    eventTooltipFeature: { renderer: tooltip, align: 'l-r' },
    timeRangesFeature: { showCurrentTimeLine: true, showHeaderElements: false },
  }));
  const resources = useMemo(() => staff.map(s => ({ id: s.id, name: s.name, eventColor: 'blue', cls: s.real ? 'pf-staff-real' : '' })), [staff]);
  const resourceRanges = useMemo(() => staff.flatMap(m => timeRanges.map(r => ({ id: `${r.id}-${m.id}`, resourceId: m.id, name: r.name, startDate: r.startDate, endDate: r.endDate, cls: r.cls }))), [staff, timeRanges]);
  return <BryntumCalendar {...props} date={date} events={shifts} resources={resources} timeRanges={timeRanges} resourceTimeRanges={resourceRanges} />;
}
