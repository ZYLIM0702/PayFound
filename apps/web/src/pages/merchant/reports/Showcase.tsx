import { useMemo, useState } from 'react';
import type { AgChartOptions } from 'ag-charts-community';
import { cash } from '../../../lib/api';
import { ChartBox } from '../../../components/ChartBox';
import { EmptyState, ReportSection } from './parts';
import type { ReportPackData } from './types';

const INK = '#0a0a0b', BLUE = '#0057ff', MUTED = '#62656d', GRID = '#eff0f2';
const axisText = { color: MUTED, fontFamily: 'Inter', fontSize: 12 };
const base = { background: { fill: 'transparent' }, padding: { top: 8, right: 8, bottom: 0, left: 0 } };
const opts = (o: object) => o as unknown as AgChartOptions;
const short = (iso: string) => new Date(iso + 'T12:00:00').toLocaleDateString([], { month: 'short', day: 'numeric' });

/** "Store performance showcase": AG Charts combo, branch-linked donut and an intensity-coloured hour chart. */
export function Showcase({ pack }: { pack: ReportPackData }) {
  const currencies = Object.keys(pack.sales_trend.by_currency);
  const [cur, setCur] = useState(currencies[0] || 'USD');
  const branches = useMemo(() => ['All branches', ...[...new Set(pack.category_by_branch.map(r => r.branch))].sort()], [pack]);
  const [branch, setBranch] = useState('All branches');
  const [cat, setCat] = useState<string | null>(null);   // cross-filter: clicking a donut slice filters the other charts' caption
  const fmt = (n: number) => cash(Math.round(n * 100), cur).replace(/\.00$/, '');

  const combo = useMemo(() => {
    const rows = pack.sales_trend.by_currency[cur] || [];
    const data = rows.map((r, i) => { const w = rows.slice(Math.max(0, i - 6), i + 1); return { day: short(r.date), revenue: r.amount_cents / 100, avg7: Math.round(w.reduce((a, b) => a + b.amount_cents, 0) / w.length) / 100 }; });
    return opts({ ...base, data, legend: { enabled: true, position: 'bottom', item: { label: { color: MUTED, fontFamily: 'Inter', fontSize: 12 } } },
      series: [{ type: 'bar', xKey: 'day', yKey: 'revenue', yName: 'Daily captured', fill: '#b9cfff', cornerRadius: 2 }, { type: 'line', xKey: 'day', yKey: 'avg7', yName: '7-day average', stroke: INK, strokeWidth: 2.5, marker: { enabled: false } }],
      axes: { x: { type: 'category', line: { enabled: false }, label: { ...axisText, avoidCollisions: true }, tick: { enabled: false } }, y: { type: 'number', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: { ...axisText, formatter: ({ value }: { value: number }) => fmt(value) } } } });
  }, [pack, cur]);

  const donutRows = useMemo(() => {
    const m = new Map<string, number>();
    pack.category_by_branch.filter(r => r.currency === cur && (branch === 'All branches' || r.branch === branch)).forEach(r => m.set(r.category, (m.get(r.category) || 0) + r.amount_cents));
    return [...m].map(([category, cents]) => ({ category, amount: cents / 100 })).sort((a, b) => b.amount - a.amount);
  }, [pack, cur, branch]);
  const donut = useMemo(() => opts({ ...base, data: donutRows, legend: { enabled: true, position: 'right', item: { label: { color: MUTED, fontFamily: 'Inter', fontSize: 12 } } },
    series: [{ type: 'donut', angleKey: 'amount', legendItemKey: 'category', calloutLabelKey: 'category', innerRadiusRatio: 0.6, calloutLabel: { enabled: false }, fills: [BLUE, INK, '#4d8bff', '#8a8f98', '#9dbcff', '#c9ccd2', '#2f343c'],
      highlightStyle: { item: { fill: undefined } }, listeners: { nodeClick: (e: { datum: { category: string } }) => setCat(c => (c === e.datum.category ? null : e.datum.category)) },
      tooltip: { renderer: ({ datum }: { datum: { category: string; amount: number } }) => ({ heading: datum.category, data: [{ label: 'Captured', value: fmt(datum.amount) }] }) } }] }), [donutRows, cur]);

  const hours = useMemo(() => {
    const data = pack.pickup.orders_by_hour.filter(h => h.hour >= 6 && h.hour <= 22).map(h => ({ hour: `${String(h.hour).padStart(2, '0')}:00`, orders: h.orders }));
    const max = Math.max(1, ...data.map(d => d.orders));
    return opts({ ...base, data, legend: { enabled: false },
      series: [{ type: 'bar', xKey: 'hour', yKey: 'orders', yName: 'Captured orders', cornerRadius: 3, itemStyler: ({ datum }: { datum: { orders: number } }) => ({ fill: `rgba(0,87,255,${0.15 + 0.85 * (datum.orders / max)})` }) }],
      axes: { x: { type: 'category', line: { enabled: false }, tick: { enabled: false }, label: axisText }, y: { type: 'number', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: axisText } } });
  }, [pack]);

  const total = donutRows.reduce((a, b) => a + b.amount, 0);
  const picked = cat ? donutRows.find(r => r.category === cat) : null;
  if (!currencies.length || !pack.category_by_branch.length) return <ReportSection id="showcase" title="Store performance showcase"><EmptyState title="No sales to chart yet">The showcase fills once payments are captured.</EmptyState></ReportSection>;
  return <ReportSection id="showcase" title="Store performance showcase" description="Daily revenue with a 7-day average, categories linked to a branch selector, and orders by hour"
    csv={{ name: `${pack.store_name} showcase`, columns: ['Category', 'Branch', 'Currency', 'Captured amount'], rows: pack.category_by_branch.map(r => [r.category, r.branch, r.currency, (r.amount_cents / 100).toFixed(2)]) }}>
    <div className="no-print flex flex-wrap items-center gap-2">
      <label className="text-sm text-muted" htmlFor="sc-branch">Branch</label>
      <select id="sc-branch" className="pf-select sm !w-auto" value={branch} onChange={e => { setBranch(e.target.value); setCat(null); }}>{branches.map(b => <option key={b}>{b}</option>)}</select>
      {currencies.length > 1 && <select className="pf-select sm !w-auto" aria-label="Currency" value={cur} onChange={e => setCur(e.target.value)}>{currencies.map(c => <option key={c}>{c}</option>)}</select>}
      {cat && <button className="pf-chip blue" onClick={() => setCat(null)}>Category: {cat} ×</button>}</div>
    <div className="pf-keep"><h3 className="text-sm font-semibold mb-1">Daily captured revenue and 7-day average ({cur})</h3><ChartBox options={combo} height={280} label={`Daily captured revenue in ${cur} with 7-day moving average`} /></div>
    <div className="grid gap-6 xl:grid-cols-2">
      <div className="pf-keep"><h3 className="text-sm font-semibold mb-1">Sales by category: {branch}</h3><ChartBox options={donut} height={260} label={`Captured amount by category for ${branch}`} />
        <p className="text-sm text-muted" aria-live="polite">{picked ? `${picked.category}: ${fmt(picked.amount)} (${Math.round((100 * picked.amount) / (total || 1))}% of ${branch.toLowerCase()}). Click the slice again to clear.` : `${fmt(total)} captured. Click a slice to focus a category.`}</p></div>
      <div className="pf-keep"><h3 className="text-sm font-semibold mb-1">Captured orders by hour (darker is busier)</h3><ChartBox options={hours} height={260} label="Captured orders by hour of day" /></div>
    </div>
  </ReportSection>;
}
