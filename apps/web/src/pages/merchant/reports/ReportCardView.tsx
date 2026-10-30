import '../../../styles/report-print.css';
import { Link } from 'react-router-dom';
import { ArrowUpRight, FileDown } from 'lucide-react';
import { scoped } from '../../../lib/api';
import { useResource } from '../../../lib/use-resource';
import { ErrorLine } from '../../../components/Shared';
import { BarList, ColumnChart, DataTable, EmptyState, Metric, MetricGrid, ReportSection, TrendChart } from './parts';
import type { CardChart, CardRecipe, ReportCardData } from './types';

const idOk = (s?: string) => Boolean(s && /^[a-zA-Z0-9_-]{1,64}$/.test(s));
export const recipeQuery = (r: CardRecipe) => `kind=${encodeURIComponent(r.kind)}&days=${r.days}${r.focus ? `&focus=${encodeURIComponent(r.focus)}` : ''}`;

function ChartFromSpec({ chart }: { chart: CardChart }) {
  const s = chart.series[0];
  if (!s || !chart.labels.length) return null;
  const rows = chart.labels.map((label, i) => ({ label, value: s.values[i] ?? 0 }));
  const fmt = (n: number) => n >= 1000 ? n.toLocaleString('en-US', { maximumFractionDigits: 0 }) : String(Math.round(n * 100) / 100);
  return <div className="flex flex-col gap-2 min-w-0"><h3 className="text-sm font-semibold">{chart.title}</h3>
    {chart.type === 'line' ? <TrendChart points={rows} label={chart.title} format={fmt} />
      : chart.labels.length > 8 ? <ColumnChart points={rows} label={chart.title} format={fmt} /> : <BarList label={chart.title} rows={rows.map(r => ({ ...r, display: fmt(r.value) }))} />}</div>;
}

/** Full report from a validated ReportCard spec: metrics, charts, tables (each with CSV) and Export PDF. */
export function ReportCardBody({ card, extra }: { card: ReportCardData; extra?: React.ReactNode }) {
  return <div className="pf-report flex flex-col gap-5">
    <div className="pf-report-print-header"><div><h1>{card.title}</h1><p>{card.store_name} · {card.start_date} to {card.end_date} ({card.days} days)</p></div><p>Generated {new Date(card.generated_at).toLocaleString()}</p></div>
    {extra}
    {card.sections.map(sec => <ReportSection key={sec.id} id={sec.id} title={sec.title}
      csv={sec.tables[0] ? { name: `${card.title} ${sec.tables[0].title}`, columns: sec.tables[0].columns, rows: sec.tables[0].rows } : undefined}>
      {sec.empty ? <EmptyState title="Nothing to show yet">{sec.empty}</EmptyState> : <>
        {sec.metrics.length > 0 && <MetricGrid>{sec.metrics.map(m => <Metric key={m.label} label={m.label} value={m.value} hint={m.hint} />)}</MetricGrid>}
        {sec.charts.length > 0 && <div className="grid gap-6 xl:grid-cols-2">{sec.charts.map(c => <ChartFromSpec key={c.title} chart={c} />)}</div>}
        {sec.tables.map(t => <DataTable key={t.title} name={`${card.title} ${t.title}`} title={t.title} columns={t.columns} rows={t.rows} numeric={t.columns.map((c, i) => (/units|orders|amount|available|collected|extra/i.test(c) ? i : -1)).filter(i => i >= 0)} />)}</>}
    </ReportSection>)}
    <p className="text-xs text-muted">{card.note}</p>
  </div>;
}

/** Compact in-chat renderer for the OpenUI `ReportCard` component: fetches the spec itself so numbers always come from the server. */
export function ReportCardChatView({ props }: { props: { merchantId?: string; kind?: string; days?: number; focus?: string | null; title?: string | null } }) {
  const id = idOk(props.merchantId) ? props.merchantId! : null;
  const recipe: CardRecipe = { kind: props.kind || 'full', days: Math.min(90, Math.max(1, Math.round(props.days || 30))), focus: props.focus || null };
  const res = useResource<ReportCardData>(id ? scoped(`/merchant/report-cards/preview?${recipeQuery(recipe)}`, id) : null);
  if (!id) return null;
  const card = res.data;
  const state = { report: { ...recipe, title: props.title || undefined } };
  return <section className="pf-ag-card pf-report" aria-label="Report"><h4 className="pf-ag-card-title">{props.title || card?.title || 'Report'}</h4>
    {res.error && <ErrorLine message={res.error} retry={res.refresh} />}
    {res.loading && <div className="pf-skeleton h-24" />}
    {card && <>
      <p className="pf-ag-meta mb-2">{card.store_name} · {card.start_date} to {card.end_date}</p>
      {card.sections.slice(0, 3).map(sec => <div key={sec.id} className="mb-3">
        <p className="font-semibold text-[13px] mb-1">{sec.title}</p>
        {sec.empty ? <p className="text-sm text-muted">{sec.empty}</p> : <>
          {sec.metrics.length > 0 && <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">{sec.metrics.slice(0, 6).map(m => <div key={m.label} className="flex justify-between gap-2 border-b border-line py-1"><dt className="text-muted">{m.label}</dt><dd className="font-semibold tabular">{m.value}</dd></div>)}</dl>}
          {sec.metrics.length === 0 && sec.tables[0] && <DataTable name={sec.tables[0].title} columns={sec.tables[0].columns} rows={sec.tables[0].rows.slice(0, 5)} />}</>}
      </div>)}
      {card.sections.length > 3 && <p className="text-xs text-muted mb-2">{card.sections.length - 3} more sections in Analytics.</p>}
      <p className="text-xs text-muted mb-3">{card.note}</p>
      <div className="flex flex-wrap gap-2">
        <Link className="pf-btn sm accent" to="/merchant/analytics" state={state}><ArrowUpRight size={14} />Open in Analytics</Link>
        <Link className="pf-btn sm outline" to="/merchant/analytics" state={{ ...state, print: true }}><FileDown size={14} />Export PDF</Link>
      </div></>}
  </section>;
}

