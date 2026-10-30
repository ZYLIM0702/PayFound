import { addDays, zonedToUtc } from './tz';

/** Demo rota only: staff come from the merchant's memberships (padded with fictional colleagues); shifts are generated, not stored. */
export type RotaStaff = { id: string; name: string; role: string; real: boolean };
export type Shift = { id: string; resourceId: string; name: string; startDate: string; endDate: string; kind: 'desk' | 'pack'; readOnly: true; branchName: string };

const PAD = [['Priya S.', 'staff'], ['Marcus L.', 'staff'], ['Sofia R.', 'manager'], ['Tom H.', 'staff'], ['Amara O.', 'staff']] as const;
const nice = (subject: string) => subject === 'demo-merchant' ? 'Demo owner' : subject.replace(/^(auth0|demo)[|-]/, '').slice(0, 18);

export function rotaStaff(memberships: { id: string; subject: string; role: string; active: boolean }[] | undefined): RotaStaff[] {
  const real = (memberships || []).filter(m => m.active !== false).map<RotaStaff>(m => ({ id: m.id, name: nice(m.subject), role: m.role, real: true }));
  const out = [...real];
  for (const [name, role] of PAD) { if (out.length >= 6) break; out.push({ id: `demo-rota-${name}`, name, role, real: false }); }
  return out;
}
// [desk start, desk end, pack start, pack end] in branch hours; null = day off
const PATTERNS: ([number, number, number, number] | null)[] = [[8, 14, 14, 17], [14, 20, 11, 14], [11, 17, 8, 11], [9, 15, 15, 19], null, [12, 20, 8, 12]];

export function buildRota(staff: RotaStaff[], days: string[], tz: string, branches: string[]): Shift[] {
  const out: Shift[] = [];
  staff.forEach((s, i) => days.forEach((day, d) => {
    const p = PATTERNS[(i * 2 + d) % PATTERNS.length];
    if (!p) return;
    const branchName = branches[(i + d) % Math.max(1, branches.length)] || '';
    const mk = (kind: 'desk' | 'pack', a: number, b: number) => out.push({ id: `shift-${s.id}-${day}-${kind}`, resourceId: s.id, name: kind === 'desk' ? 'Pickup desk' : 'Packing', kind, startDate: zonedToUtc(day, a, 0, tz).toISOString(), endDate: zonedToUtc(day, b, 0, tz).toISOString(), readOnly: true, branchName });
    mk('desk', p[0], p[1]); mk('pack', p[2] === p[1] ? p[2] : p[2], p[3]);
  }));
  return out;
}
/** Desk cover per branch-hour of one day. */
export function deskCover(shifts: Shift[], dayKey: string, tz: string) {
  const cover: number[] = Array(24).fill(0);
  for (const s of shifts) {
    if (s.kind !== 'desk') continue;
    for (let h = 0; h < 24; h++) {
      const a = zonedToUtc(dayKey, h, 0, tz).getTime();
      if (Date.parse(s.startDate) <= a && Date.parse(s.endDate) >= a + 3600000) cover[h]++;
    }
  }
  return cover;
}
export { addDays };
