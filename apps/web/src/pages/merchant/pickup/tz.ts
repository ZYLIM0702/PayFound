/** Branch-time helpers: the demo schedule is authored in the branch's own time zone, so the calendar shows branch time. */
export const DEFAULT_TZ = 'America/Los_Angeles';

function offsetMinutes(at: Date, tz: string) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).formatToParts(at).map(p => [p.type, p.value]));
  const asUtc = Date.UTC(+parts.year, +parts.month - 1, +parts.day, +parts.hour, +parts.minute, +parts.second);
  return Math.round((asUtc - Math.floor(at.getTime() / 1000) * 1000) / 60000);
}
/** Wall-clock y-m-d h:m in `tz` to a real instant. */
export function zonedToUtc(dayKey: string, hour: number, minute: number, tz: string) {
  const [y, m, d] = dayKey.split('-').map(Number);
  const guess = new Date(Date.UTC(y, m - 1, d, hour, minute));
  return new Date(guess.getTime() - offsetMinutes(guess, tz) * 60000);
}
export const dayKeyIn = (at: Date, tz: string) => new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(at);
export const hourIn = (at: Date, tz: string) => Number(new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', hour: '2-digit' }).format(at));
export const addDays = (dayKey: string, n: number) => { const d = new Date(`${dayKey}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
export const weekdayOf = (dayKey: string) => new Date(`${dayKey}T12:00:00Z`).getUTCDay(); // 0 Sun
export const dayBoundsIn = (dayKey: string, tz: string) => ({ start: zonedToUtc(dayKey, 0, 0, tz).toISOString(), end: zonedToUtc(addDays(dayKey, 1), 0, 0, tz).toISOString() });
/** A Date produced by Bryntum with a configured timeZone carries branch wall-clock in its local fields. */
export const wallToUtc = (wall: Date, tz: string) => zonedToUtc(`${wall.getFullYear()}-${String(wall.getMonth() + 1).padStart(2, '0')}-${String(wall.getDate()).padStart(2, '0')}`, wall.getHours(), wall.getMinutes(), tz);
