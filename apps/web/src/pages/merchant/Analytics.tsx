import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronDown, FileDown, Save, Send, Sparkles, Trash2 } from 'lucide-react';
import '../../styles/report-print.css';
import { messageOf, post, remove, scoped } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { ErrorLine, Notice, PageHeader, Skeleton, Spinner } from '../../components/Shared';
import { useMerchant } from './context';
import { askState } from './OverviewSections';
import type { Forecast } from './overviewTypes';
import { exportPdf } from './reports/parts';
import { ReportCardBody, recipeQuery } from './reports/ReportCardView';
import { ReportPack } from './reports/ReportPack';
import type { CardRecipe, ReportCardData, ReportPackData, SavedReport } from './reports/types';

const AdvancedBuilder = lazy(() => import('./AdvancedBuilder'));
const RANGES = [7, 30, 90] as const;
const SUGGESTIONS = ['Build a 30-day sales report by category and branch', 'Make a stock health report for the products I should reorder', 'Create a pickup report for the last 14 days'];
type NavState = { report?: CardRecipe; print?: boolean } | null;

export function AnalyticsPage() {
  const { merchantId } = useMerchant();
  const location = useLocation();
  const navigate = useNavigate();
  const incoming = (location.state as NavState)?.report || null;
  const [days, setDays] = useState<(typeof RANGES)[number]>(30);
  const [open, setOpen] = useState<CardRecipe | null>(incoming);
  const [seen, setSeen] = useState(location.key);
  if (location.key !== seen) { setSeen(location.key); if (incoming) setOpen(incoming); }
  const pack = useResource<ReportPackData>(open ? null : scoped(`/merchant/report-pack?days=${days}`, merchantId));
  const forecast = useResource<Forecast>(open ? null : scoped('/merchant/forecast', merchantId), 300000);
  const saved = useResource<{ reports: SavedReport[] }>(scoped('/merchant/report-cards', merchantId));
  const [info, setInfo] = useState('');
  const [error, setError] = useState('');
  const [ask, setAsk] = useState('');
  const send = (text: string) => { const q = text.trim(); if (q) navigate('/merchant/assistant', { state: askState(q) }); };
  const shownPack = pack.data;

  return <div className="pf-report flex flex-col gap-5 pf-enter">
    <div className="no-print"><PageHeader title="Analytics" description="Ready-made reports for your store, filled from your live orders, stock and pickups. Export any report as PDF or CSV, or ask the assistant to build a new one." right={!open && <>
      <div className="pf-segmented" role="group" aria-label="Date range">{RANGES.map(d => <button key={d} aria-pressed={days === d} onClick={() => setDays(d)}>{d} days</button>)}</div>
      <button type="button" className="pf-btn accent" disabled={!shownPack} onClick={() => exportPdf()}><FileDown size={16} />Export full pack PDF</button></>} /></div>

    <form className="no-print pf-card p-4 sm:p-5 flex flex-col gap-3" onSubmit={e => { e.preventDefault(); send(ask); }} aria-label="Ask the assistant to build a report">
      <div className="flex items-center gap-2"><Sparkles size={16} className="text-accent" /><h2 className="pf-subtitle">Ask the assistant to build a report</h2></div>
      <div className="flex flex-col sm:flex-row gap-2"><input className="pf-input flex-1" aria-label="Describe the report you want" value={ask} maxLength={300} onChange={e => setAsk(e.target.value)} placeholder="e.g. Weekly sales by category for the Marina branch" />
        <button className="pf-btn accent" type="submit" disabled={!ask.trim()}><Send size={15} />Build report</button></div>
      <div className="flex flex-wrap gap-2">{SUGGESTIONS.map(s => <button key={s} type="button" className="pf-chip !whitespace-normal !h-auto !py-1.5 text-left" onClick={() => send(s)}>{s}</button>)}</div>
    </form>

    <ErrorLine message={error || saved.error} />{info && <div className="no-print"><Notice tone="green">{info}</Notice></div>}
    {!open && <section className="no-print" aria-label="Saved reports"><h2 className="pf-subtitle mb-2">Saved reports</h2>
      <ul className="flex flex-wrap gap-2">
        <li className="flex items-center pf-card !rounded-full px-4 py-1.5"><button type="button" className="text-sm font-semibold" onClick={() => document.querySelector('[data-report-section="showcase"]')?.scrollIntoView({ behavior: 'smooth' })}>Store performance showcase</button></li>
        {saved.data?.reports.map(r => <li key={r.id} className="flex items-center gap-1 pf-card !rounded-full pl-4 pr-1 py-1">
          <button type="button" className="text-sm font-semibold" onClick={() => setOpen({ kind: r.kind, days: r.days, focus: r.focus, title: r.name })}>{r.name}<span className="text-muted font-normal"> · {r.days}d</span></button>
          <button type="button" className="pf-btn sm ghost icon" aria-label={`Delete ${r.name}`} onClick={async () => { try { await remove(`/merchant/report-cards/${r.id}`); await saved.refresh(); } catch (e) { setError(messageOf(e)); } }}><Trash2 size={14} /></button></li>)}</ul>
      {!saved.loading && !saved.data?.reports.length && <p className="text-sm text-muted mt-2">No reports of your own saved yet. Ask the assistant to build one above, then choose Save report and it will be listed here.</p>}</section>}
    {open ? <OpenCard merchantId={merchantId} recipe={open} onBack={() => { setOpen(null); navigate('/merchant/analytics', { replace: true, state: null }); }}
        autoPrint={Boolean((location.state as NavState)?.print)} onSaved={async () => { await saved.refresh(); setInfo('Saved. It now appears under Saved reports.'); }} onError={setError} />
      : pack.error ? <ErrorLine message={pack.error} retry={pack.refresh} />
      : !shownPack ? <div className="flex flex-col gap-5" aria-busy="true"><Spinner label="Building your report pack…" inline />{[0, 1, 2].map(i => <Skeleton key={i} className="h-48 !rounded-[var(--pf-r-lg)]" />)}</div>
      : <><div className="pf-report-print-header"><div><h1>{shownPack.store_name}: report pack</h1><p>{shownPack.start_date} to {shownPack.end_date} ({shownPack.days} days) · {shownPack.timezone}</p></div><p>Generated {new Date(shownPack.generated_at).toLocaleString()}</p></div>
        <ReportPack pack={shownPack} forecast={forecast.data} forecastError={forecast.error} /></>}

    <details className="no-print pf-card group" data-testid="advanced-builder">
      <summary className="flex items-center justify-between gap-3 p-4 sm:px-5 cursor-pointer list-none"><span><span className="pf-subtitle block">Advanced: custom chart</span><span className="text-sm text-muted">Build and save your own charts with the AG Studio report builder.</span></span><ChevronDown size={18} className="transition-transform group-open:rotate-180" /></summary>
      <div className="p-4 sm:p-5 pt-0"><AdvancedWhenOpen /></div>
    </details>
  </div>;
}

/** Mount the heavy builder only once the section is opened. */
function AdvancedWhenOpen() {
  const [armed, setArmed] = useState(false);
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => { const d = host.current?.closest('details'); if (!d) return; const on = () => setArmed(a => a || d.open); d.addEventListener('toggle', on); on(); return () => d.removeEventListener('toggle', on); }, []);
  return <div ref={host}>{armed && <Suspense fallback={<Spinner label="Loading builder…" />}><AdvancedBuilder /></Suspense>}</div>;
}

function OpenCard({ merchantId, recipe, onBack, onSaved, onError, autoPrint }: { merchantId: string; recipe: CardRecipe; onBack: () => void; onSaved: () => Promise<void>; onError: (m: string) => void; autoPrint: boolean }) {
  const res = useResource<ReportCardData>(scoped(`/merchant/report-cards/preview?${recipeQuery(recipe)}`, merchantId));
  const navigate = useNavigate();
  const [name, setName] = useState(recipe.title || '');
  const printed = useRef(false);
  const card = res.data;
  useEffect(() => {
    if (!autoPrint || !card || printed.current) return;
    printed.current = true;
    navigate('/merchant/analytics', { replace: true, state: { report: recipe } });
    const t = window.setTimeout(() => exportPdf(), 600);
    return () => window.clearTimeout(t);
  }, [autoPrint, card, navigate, recipe]);
  if (res.error) return <><button className="pf-btn sm outline w-fit" onClick={onBack}><ArrowLeft size={14} />Back to report pack</button><ErrorLine message={res.error} retry={res.refresh} /></>;
  if (!card) return <Spinner label="Building your report…" />;
  const save = async () => { try { await post('/merchant/report-cards', { merchant_id: merchantId, name: name.trim() || card.title, kind: recipe.kind, days: recipe.days, focus: recipe.focus || null }); await onSaved(); } catch (e) { onError(messageOf(e)); } };
  return <ReportCardBody card={card} extra={<div className="no-print flex flex-wrap items-center gap-2">
    <button className="pf-btn sm outline" onClick={onBack}><ArrowLeft size={14} />Back to report pack</button>
    <input className="pf-input sm !w-56" aria-label="Report name" value={name} maxLength={120} placeholder={card.title} onChange={e => setName(e.target.value)} />
    <button className="pf-btn sm" onClick={() => void save()}><Save size={14} />Save report</button>
    <button className="pf-btn sm accent" onClick={() => exportPdf()}><FileDown size={14} />Export PDF</button>
    <Link className="pf-link text-sm" to="/merchant/assistant" state={askState(`Explain this ${card.title.toLowerCase()} for the last ${card.days} days and what I should do next.`)}>Ask the assistant about it</Link></div>} />;
}
