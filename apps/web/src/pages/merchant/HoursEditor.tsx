import { Plus, Trash2 } from 'lucide-react';

export type Period = { start: string; end: string };
export type WeekHours = Record<string, Period[]>;
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const DEFAULT: Period = { start: '09:00', end: '18:00' };

/** Weekly hours editor producing `{ "0": [{start,end}], ... }` (0 = Monday). */
export function WeeklyHours({ value, onChange }: { value: WeekHours; onChange: (next: WeekHours) => void }) {
  const set = (day: number, periods: Period[]) => onChange({ ...value, [String(day)]: periods });
  return <div className="divide-y divide-line border border-line rounded-[var(--pf-r-md)]">{DAYS.map((name, day) => {
    const periods = value[String(day)] || [];
    const open = periods.length > 0;
    return <div key={name} className="flex flex-wrap items-start gap-x-4 gap-y-2 px-4 py-3">
      <label className="pf-check w-36 font-medium h-9"><input type="checkbox" checked={open} onChange={e => set(day, e.target.checked ? [{ ...DEFAULT }] : [])} aria-label={`${name} open`} />{name}</label>
      <div className="flex-1 min-w-[240px] space-y-2">{open ? periods.map((p, i) => <div key={i} className="flex items-center gap-2">
        <input className="pf-input sm !w-32" type="time" aria-label={`${name} opens`} value={p.start} onChange={e => set(day, periods.map((x, j) => j === i ? { ...x, start: e.target.value } : x))} required />
        <span className="text-muted text-sm">to</span>
        <input className="pf-input sm !w-32" type="time" aria-label={`${name} closes`} value={p.end} onChange={e => set(day, periods.map((x, j) => j === i ? { ...x, end: e.target.value } : x))} required />
        {periods.length > 1 && <button type="button" className="pf-btn ghost sm icon" aria-label="Remove period" onClick={() => set(day, periods.filter((_, j) => j !== i))}><Trash2 size={14} /></button>}
        {i === periods.length - 1 && <button type="button" className="pf-btn ghost sm icon" aria-label={`Add period on ${name}`} onClick={() => set(day, [...periods, { start: '12:00', end: '14:00' }])}><Plus size={14} /></button>}
      </div>) : <p className="text-sm text-muted h-9 flex items-center">Closed</p>}</div>
    </div>;
  })}</div>;
}

/** Special dates: each YYYY-MM-DD maps to periods; no periods means closed that day. */
export function SpecialDates({ value, onChange }: { value: WeekHours; onChange: (next: WeekHours) => void }) {
  const entries = Object.entries(value).sort(([a], [b]) => a.localeCompare(b));
  const rename = (from: string, to: string) => { const next: WeekHours = {}; for (const [k, v] of Object.entries(value)) next[k === from ? to : k] = v; onChange(next); };
  return <div className="space-y-3">
    {entries.length === 0 && <p className="text-sm text-muted">No special dates. Add holidays or one-off changes.</p>}
    {entries.map(([date, periods]) => <div key={date} className="flex flex-wrap items-center gap-2 border border-line rounded-[var(--pf-r-md)] px-3 py-2.5">
      <input className="pf-input sm !w-40" type="date" aria-label="Special date" value={date} onChange={e => e.target.value && e.target.value !== date && !(e.target.value in value) && rename(date, e.target.value)} required />
      <label className="pf-check"><input type="checkbox" checked={periods.length === 0} onChange={e => onChange({ ...value, [date]: e.target.checked ? [] : [{ ...DEFAULT }] })} />Closed all day</label>
      {periods.map((p, i) => <span key={i} className="flex items-center gap-2"><input className="pf-input sm !w-28" type="time" aria-label="Opens" value={p.start} onChange={e => onChange({ ...value, [date]: periods.map((x, j) => j === i ? { ...x, start: e.target.value } : x) })} /><span className="text-muted text-sm">to</span><input className="pf-input sm !w-28" type="time" aria-label="Closes" value={p.end} onChange={e => onChange({ ...value, [date]: periods.map((x, j) => j === i ? { ...x, end: e.target.value } : x) })} /></span>)}
      <button type="button" className="pf-btn ghost sm icon ml-auto" aria-label={`Remove ${date}`} onClick={() => { const next = { ...value }; delete next[date]; onChange(next); }}><Trash2 size={14} /></button>
    </div>)}
    <button type="button" className="pf-btn sm outline" onClick={() => { let d = new Date(); for (let i = 0; i < 400; i++) { const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; if (!(key in value)) { onChange({ ...value, [key]: [] }); return; } d = new Date(d.getTime() + 864e5); } }}><Plus size={14} />Add special date</button>
  </div>;
}
