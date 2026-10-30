import { useId, type ReactNode } from 'react';
import { Download, FileDown } from 'lucide-react';

/* ---- export helpers ---- */
export function downloadCsv(name: string, columns: string[], rows: (string | number)[][]) {
  const esc = (v: string | number) => { const s = String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const text = [columns, ...rows].map(r => r.map(esc).join(',')).join('\n');
  const url = URL.createObjectURL(new Blob(['﻿' + text], { type: 'text/csv;charset=utf-8' }));
  const a = document.createElement('a');
  a.href = url; a.download = `${name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'report'}.csv`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Export PDF = the browser print dialog, styled by report-print.css. `sectionId` limits the print to one section. */
export function exportPdf(sectionId?: string) {
  const body = document.body;
  const target = sectionId ? document.querySelector<HTMLElement>(`[data-report-section="${sectionId}"]`) : null;
  if (target) { body.classList.add('pf-print-one'); target.classList.add('pf-print-target'); }
  const done = () => { body.classList.remove('pf-print-one'); target?.classList.remove('pf-print-target'); window.removeEventListener('afterprint', done); };
  window.addEventListener('afterprint', done);
  window.print();
}

/* ---- section shell ---- */
export function ReportSection({ id, title, description, children, csv }: { id: string; title: string; description?: ReactNode; children: ReactNode; csv?: { name: string; columns: string[]; rows: (string | number)[][] } }) {
  return <section className="pf-report-section pf-card p-5 sm:p-6 flex flex-col gap-5" data-report-section={id} aria-labelledby={`rs-${id}`}>
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0"><h2 id={`rs-${id}`} className="pf-title">{title}</h2>{description && <p className="text-sm text-muted mt-1">{description}</p>}</div>
      <div className="no-print flex items-center gap-2">
        {csv && csv.rows.length > 0 && <button type="button" className="pf-btn sm ghost" onClick={() => downloadCsv(csv.name, csv.columns, csv.rows)}><Download size={14} />CSV</button>}
        <button type="button" className="pf-btn sm outline" onClick={() => exportPdf(id)}><FileDown size={14} />Export PDF</button>
      </div>
    </div>
    {children}
  </section>;
}

export function EmptyState({ title, children }: { title: string; children: ReactNode }) {
  return <div className="rounded-[var(--pf-r-lg)] border border-dashed border-line-strong bg-sunk p-5 text-sm"><p className="font-semibold">{title}</p><p className="text-muted mt-1">{children}</p></div>;
}

export function Metric({ label, value, hint, tone }: { label: string; value: ReactNode; hint?: ReactNode; tone?: 'warn' | 'bad' | 'ok' }) {
  return <div className="pf-stat !p-4"><span className="pf-stat-label">{label}</span><strong className={`pf-stat-number !text-[28px] ${tone === 'bad' ? 'text-bad' : tone === 'warn' ? 'text-warn' : tone === 'ok' ? 'text-ok' : ''}`}>{value}</strong>{hint && <span className="text-xs text-muted">{hint}</span>}</div>;
}

export function MetricGrid({ children }: { children: ReactNode }) { return <div className="pf-keep grid gap-3 grid-cols-2 lg:grid-cols-4 2xl:grid-cols-6">{children}</div>; }

/* ---- table with its own CSV ---- */
export type Col = { label: string; num?: boolean };
export function DataTable({ title, name, columns, rows, numeric = [] }: { title?: string; name: string; columns: string[]; rows: (string | number)[][]; numeric?: number[] }) {
  const id = useId();
  if (!rows.length) return null;
  return <div className="pf-keep min-w-0">
    <div className="flex items-center justify-between gap-2 mb-1.5">{title && <h3 className="text-sm font-semibold" id={id}>{title}</h3>}
      <button type="button" className="no-print pf-btn sm ghost" aria-label={`Download ${title || name} as CSV`} onClick={() => downloadCsv(name, columns, rows)}><Download size={14} />CSV</button></div>
    <div className="overflow-x-auto"><table className="pf-rt" aria-labelledby={title ? id : undefined}>
      <thead><tr>{columns.map((c, i) => <th key={c} scope="col" className={numeric.includes(i) ? 'num' : ''}>{c}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j} className={numeric.includes(j) ? 'num' : ''}>{typeof v === 'number' ? v.toLocaleString('en-US') : v}</td>)}</tr>)}</tbody></table></div>
  </div>;
}

/* ---- charts: plain SVG/HTML so they scale to the page and print crisp ---- */
export function BarList({ rows, label, ink = false }: { rows: { label: string; value: number; display: string }[]; label: string; ink?: boolean }) {
  const max = Math.max(1, ...rows.map(r => r.value));
  if (!rows.length) return null;
  return <ul className="pf-keep flex flex-col gap-2.5" aria-label={label}>{rows.map(r => <li key={r.label} className="grid grid-cols-[minmax(80px,40%)_1fr_auto] items-center gap-3 text-[13px]">
    <span className="truncate" title={r.label}>{r.label}</span><span className="pf-bar-track" aria-hidden="true"><span className={`pf-bar-fill ${ink ? 'ink' : ''} block`} style={{ width: `${Math.max(2, (r.value / max) * 100)}%` }} /></span><span className="tabular font-semibold">{r.display}</span></li>)}</ul>;
}

export function ColumnChart({ points, label, format = String }: { points: { label: string; value: number }[]; label: string; format?: (n: number) => string }) {
  const max = Math.max(1, ...points.map(p => p.value)), W = 640, H = 170, pad = 22, bw = (W - pad) / Math.max(1, points.length);
  return <figure className="pf-keep m-0"><svg viewBox={`0 0 ${W} ${H + 22}`} role="img" aria-label={label} className="w-full h-auto">
    <line x1={pad} x2={W} y1={H} y2={H} stroke="var(--pf-line)" />
    {points.map((p, i) => { const h = (p.value / max) * (H - 14); const x = pad + i * bw; return <g key={p.label}>
      <rect x={x + bw * 0.15} y={H - h} width={bw * 0.7} height={h} rx={2} fill="var(--pf-blue, #0057ff)"><title>{`${p.label}: ${format(p.value)}`}</title></rect>
      {(points.length <= 14 || i % 2 === 0) && <text x={x + bw / 2} y={H + 14} textAnchor="middle" fontSize="10" fill="var(--pf-muted)">{p.label}</text>}</g>; })}
    <text x={0} y={10} fontSize="10" fill="var(--pf-muted)">{format(max)}</text></svg></figure>;
}

export function TrendChart({ points, label, format }: { points: { label: string; value: number }[]; label: string; format: (n: number) => string }) {
  const W = 760, H = 190, pl = 52, max = Math.max(1, ...points.map(p => p.value)), n = Math.max(1, points.length - 1);
  const x = (i: number) => pl + (i / n) * (W - pl - 6), y = (v: number) => H - (v / max) * (H - 16) - 2;
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(' ');
  const ticks = [0, 0.5, 1].map(t => ({ v: max * t, y: y(max * t) }));
  const every = Math.max(1, Math.ceil(points.length / 8));
  return <figure className="pf-keep m-0"><svg viewBox={`0 0 ${W} ${H + 24}`} role="img" aria-label={label} className="w-full h-auto">
    {ticks.map(t => <g key={t.v}><line x1={pl} x2={W} y1={t.y} y2={t.y} stroke="var(--pf-line)" /><text x={pl - 6} y={t.y + 3} textAnchor="end" fontSize="10" fill="var(--pf-muted)">{format(t.v)}</text></g>)}
    <path d={`${d} L${x(points.length - 1)},${H} L${x(0)},${H} Z`} fill="var(--pf-blue, #0057ff)" opacity="0.08" />
    <path d={d} fill="none" stroke="var(--pf-blue, #0057ff)" strokeWidth="2" strokeLinejoin="round" />
    {points.map((p, i) => i % every === 0 && <text key={p.label} x={x(i)} y={H + 16} textAnchor="middle" fontSize="10" fill="var(--pf-muted)">{p.label}</text>)}</svg></figure>;
}
