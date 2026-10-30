import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BadgeCheck, CalendarDays, CloudRain, Sparkles, Star } from 'lucide-react';
import type { AgChartOptions } from 'ag-charts-community';
import { cash } from '../../lib/api';
import { Chip, Empty, Panel } from '../../components/Shared';
import { ChartBox } from '../../components/ChartBox';
import type { Analytics, Forecast, OverviewAlert, StoreBlock } from './overviewTypes';

const INK = '#0a0a0b', BLUE = '#0057ff', MUTED = '#62656d', GRID = '#eff0f2';
const axisText = { color: MUTED, fontFamily: 'Inter', fontSize: 12 };
const base = { background: { fill: 'transparent' }, legend: { enabled: false }, padding: { top: 8, right: 8, bottom: 0, left: 0 } };
const money = (cents: number, cur: string) => cash(Math.round(cents), cur).replace(/\.00$/, '');
const short = (iso: string) => new Date(iso + 'T12:00:00').toLocaleDateString([], { month: 'short', day: 'numeric' });
const weekday = (iso: string) => new Date(iso + 'T12:00:00').toLocaleDateString([], { weekday: 'short' });
const opts = (o: object) => o as unknown as AgChartOptions;
const trunc = (s: string, n = 22) => (s.length > n ? s.slice(0, n - 1) + '…' : s);

/** Link into the merchant assistant with the item as the opening question. */
export const askState = (ask: string) => ({ ask, fresh: true });
export function AskLink({ ask, children, className = '', label }: { ask: string; children: React.ReactNode; className?: string; label?: string }) {
  return <Link to="/merchant/assistant" state={askState(ask)} className={className} aria-label={label ?? `Ask the assistant about this: ${ask}`} title="Ask the assistant about this">{children}</Link>;
}

export function StoreStrip({ store }: { store: StoreBlock }) {
  const open = store.is_open;
  return <section className="pf-card p-4 sm:px-5 flex flex-wrap items-center gap-x-6 gap-y-3" data-testid="store-strip" aria-label="Business information">
    <div className="min-w-0 flex items-center gap-2.5">
      <h2 className="font-display text-xl font-semibold tracking-tight truncate">{store.name}</h2>
      {store.verified && <span className="inline-flex items-center gap-1 text-accent text-xs font-semibold" title="Verified business"><BadgeCheck size={16} />Verified</span>}
      <Chip kind={open ? 'green' : 'red'}>{open ? 'Open now' : 'Closed'}{store.status_override !== 'auto' ? ' (manual)' : ''}</Chip>
    </div>
    <dl className="flex flex-wrap gap-x-6 gap-y-2 text-sm flex-1 min-w-0">
      <Fact label="Today" value={store.hours_today} />
      <Fact label="Branches" value={String(store.branch_count)} />
      <Fact label="Rating" value={store.rating ? <span className="inline-flex items-center gap-1"><Star size={13} className="fill-ink text-ink" />{store.rating.toFixed(1)} <span className="text-muted">({store.review_count})</span></span> : 'No reviews yet'} />
      <Fact label="Time zone" value={store.timezone.replace('_', ' ')} />
    </dl>
    <div className="flex flex-wrap gap-2">
      <Link className="pf-btn sm outline" to={`/stores/${store.slug}`} data-testid="view-store-page">View store page</Link>
      <Link className="pf-btn sm outline" to="/merchant/settings">Edit store</Link>
    </div>
  </section>;
}
function Fact({ label, value }: { label: string; value: React.ReactNode }) {
  return <div className="min-w-0"><dt className="text-xs text-muted">{label}</dt><dd className="font-semibold tabular">{value}</dd></div>;
}

const SEV = { high: ['red', 'Urgent'], medium: ['amber', 'Soon'], low: ['blue', 'Info'] } as const;
export function AlertsPanel({ alerts, loading }: { alerts: OverviewAlert[]; loading: boolean }) {
  const sorted = [...alerts].sort((a, b) => ['high', 'medium', 'low'].indexOf(a.severity) - ['high', 'medium', 'low'].indexOf(b.severity));
  return <Panel title="Alerts" description="Click an alert to ask the assistant about it" className="h-full" actions={<Chip kind={sorted.some(a => a.severity === 'high') ? 'red' : 'ink'}>{sorted.length}</Chip>}>
    <div data-testid="overview-alerts">
      {loading ? <div className="space-y-3">{[0, 1, 2].map(i => <div key={i} className="pf-skeleton h-14" />)}</div>
        : sorted.length === 0 ? <p className="text-sm text-muted py-4">Nothing needs attention right now.</p>
        : <ul className="divide-y divide-line -my-2">{sorted.map(a => <li key={a.id} className="flex items-center gap-3 py-3" data-testid={`alert-${a.id}`}>
          <AskLink ask={a.ask} className="flex items-center gap-3 min-w-0 flex-1 group" label={`${a.title}. Ask the assistant about this`}>
            <span className={`min-w-9 h-9 px-2 rounded-full grid place-items-center shrink-0 text-sm font-semibold tabular ${a.severity === 'high' ? 'bg-bad-soft text-bad' : a.severity === 'medium' ? 'bg-warn-soft text-warn' : 'bg-accent-soft text-accent'}`}>{a.kind === 'weather' ? <CloudRain size={16} /> : a.count}</span>
            <span className="min-w-0"><span className="block text-sm font-semibold group-hover:underline">{a.title}</span><span className="block text-xs text-muted truncate">{SEV[a.severity][1]} · {a.detail}</span></span>
          </AskLink>
          <Link className="pf-btn sm outline shrink-0" to={a.to}>{a.action}</Link>
        </li>)}</ul>}
    </div>
  </Panel>;
}

function DemoBadge({ label }: { label: string }) { return <p className="text-xs text-muted flex items-center gap-1.5"><Sparkles size={13} />{label}</p>; }

export function ForecastPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  const chart = useMemo(() => {
    if (!forecast) return null;
    const palette = [BLUE, INK, '#7a8ca8', '#b5bcc8', '#2f6fed'];
    const cats = forecast.demand_index;
    const data = (cats[0]?.days || []).map((d, i) => ({ day: weekday(d.date), ...Object.fromEntries(cats.map(c => [`c${cats.indexOf(c)}`, c.days[i].demand_index])) }));
    return opts({ ...base, legend: { enabled: cats.length > 1, position: 'bottom', item: { label: { color: MUTED, fontFamily: 'Inter', fontSize: 12 } } }, data,
      series: cats.map((c, i) => ({ type: 'line', xKey: 'day', yKey: `c${i}`, yName: c.category, stroke: palette[i % palette.length], strokeWidth: 2.5, marker: { size: 6, fill: palette[i % palette.length], stroke: '#fff' } })),
      axes: { x: { type: 'category', line: { enabled: false }, tick: { enabled: false }, label: axisText }, y: { type: 'number', min: 60, gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: axisText, title: { text: 'Demand index (100 = normal)', ...axisText } } } });
  }, [forecast]);
  return <Panel title="Next 7 days" description="Demand forecast with weather and local events" className="h-full">
    <div data-testid="overview-forecast" className="space-y-4">
      {loading || !forecast ? <div className="pf-skeleton h-72" /> : <>
        <div className="grid grid-cols-7 gap-1.5 sm:gap-2" aria-label="Weather and events by day">{(forecast.weather.days.length ? forecast.weather.days : forecast.demand_index[0]?.days.map(d => ({ date: d.date, summary: '', temp_max_c: null, rain_chance_pct: null, code: 0 })) || []).slice(0, 7).map(d => {
          const ev = forecast.events.filter(e => e.date === d.date);
          return <div key={d.date} className="rounded-[10px] bg-sunk px-1.5 sm:px-2.5 py-2 text-center min-w-0" title={`${d.summary} ${ev.map(e => e.name).join(', ')}`}>
            <p className="text-xs font-semibold">{weekday(d.date)}</p>
            <p className="text-[11px] text-muted truncate">{d.temp_max_c != null ? `${Math.round(d.temp_max_c)}°` : '–'}{d.rain_chance_pct != null && d.rain_chance_pct >= 40 ? ` · ${d.rain_chance_pct}%` : ''}</p>
            <p className={`text-[11px] mt-0.5 ${ev.length ? 'text-accent font-semibold' : 'text-subtle'}`}>{ev.length ? `${ev.length} event${ev.length > 1 ? 's' : ''}` : 'quiet'}</p>
          </div>;
        })}</div>
        {chart && <ChartBox options={chart} height={250} label="Forecast demand index by category for the next 7 days" />}
        <p className="text-xs text-muted">{forecast.weather.source === 'Open-Meteo' ? 'Weather: Open-Meteo.' : 'Weather is unavailable, so weather factors are neutral.'} Events: fictional demo feed. {forecast.method}.</p>
        <DemoBadge label={forecast.label} />
      </>}
    </div>
  </Panel>;
}

export function PrepPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  const driverChip = { weather: ['blue', 'Weather'], event: ['amber', 'Event'], trend: ['ink', 'Trend'], payday: ['green', 'Payday'], holiday: ['amber', 'Holiday'], weekday: ['ink', 'Weekday'] } as const;
  return <Panel title="What to prep" description="Suggested extra units for the next 3 days">
    <div data-testid="overview-prep">
      {loading || !forecast ? <div className="pf-skeleton h-40" /> : forecast.prep.length === 0 ? <p className="text-sm text-muted py-3">Stock covers the forecast. Nothing extra to prepare.</p>
        : <ul className="divide-y divide-line -my-2">{forecast.prep.slice(0, 6).map(p => <li key={p.product_id}>
          <AskLink ask={`Why should I prepare ${p.suggested_quantity} more ${p.product}? ${p.reason}. I currently have ${p.available} available.`} className="flex items-center gap-3 py-3 group">
            <span className="w-12 h-9 rounded-full bg-accent-soft text-accent grid place-items-center text-sm font-semibold tabular shrink-0">+{p.suggested_quantity}</span>
            <span className="min-w-0 flex-1"><span className="block text-sm font-semibold truncate group-hover:underline">{p.headline ?? p.product}</span><span className="block text-xs text-muted truncate">{p.reason} · {p.available} on hand</span></span>
            <Chip kind={driverChip[p.driver][0]}>{driverChip[p.driver][1]}</Chip>
          </AskLink></li>)}</ul>}
    </div>
  </Panel>;
}

export function InsightsPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  return <Panel title="Insights" description="Plain-language read of the next week">
    <div data-testid="overview-insights">
      {loading || !forecast ? <div className="pf-skeleton h-40" /> : <ul className="divide-y divide-line -my-2">{forecast.insights.map(i => <li key={i.title}>
        <AskLink ask={i.ask} className="block py-3 group"><span className="flex items-start gap-2"><span className="min-w-0 flex-1"><span className="block text-sm font-semibold group-hover:underline">{i.title}</span><span className="block text-[13px] text-muted mt-0.5">{i.body}</span></span><span className="inline-flex items-center gap-1 text-xs text-accent font-semibold shrink-0 mt-0.5"><Sparkles size={13} />Ask</span></span></AskLink></li>)}</ul>}
      {forecast && forecast.stock_risks.length > 0 && <div className="mt-4 pt-4 border-t border-line">
        <h3 className="text-sm font-semibold mb-1">Stock at risk</h3>
        <ul className="divide-y divide-line">{forecast.stock_risks.slice(0, 4).map(r => <li key={r.product_id}><AskLink ask={`${r.product} may run out soon: ${r.reason}. What should I reorder and when?`} className="flex items-center gap-2 py-2 group">
          <span className={`w-2 h-2 rounded-full shrink-0 ${r.severity === 'high' ? 'bg-bad' : 'bg-warn'}`} /><span className="text-sm flex-1 min-w-0 truncate group-hover:underline">{r.product}</span><span className="text-xs text-muted shrink-0">{r.reason}</span></AskLink></li>)}</ul>
      </div>}
    </div>
  </Panel>;
}

export function EventsPanel({ forecast }: { forecast: Forecast | null }) {
  if (!forecast?.events.length) return null;
  return <Panel title="Local events nearby" description="Fictional demo feed within 3 km">
    <ul className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3" data-testid="overview-events">{forecast.events.slice(0, 8).map(e => <li key={`${e.id}-${e.date}`}>
      <AskLink ask={`The event "${e.name}" is ${e.distance_km} km from my store on ${e.date}. How should I prepare?`} className="flex items-start gap-3 rounded-[10px] bg-sunk p-3 hover:bg-line transition-colors h-full">
        <CalendarDays size={16} className="mt-0.5 text-accent shrink-0" /><span className="min-w-0"><span className="block text-sm font-semibold">{e.name}</span><span className="block text-xs text-muted">{weekday(e.date)} {short(e.date)}{e.start ? ` · ${e.start}` : ''} · {e.distance_km} km · {e.footfall.replace('_', ' ')} footfall</span></span></AskLink></li>)}</ul>
  </Panel>;
}

export function ChartsGrid({ data, loading }: { data: Analytics | null; loading: boolean }) {
  const [range, setRange] = useState<7 | 30>(7);
  const [cur, setCur] = useState('');
  const currencies = data ? Object.keys(data.revenue) : [];
  const currency = cur && currencies.includes(cur) ? cur : data?.currency && currencies.includes(data.currency) ? data.currency : currencies[0] || 'USD';
  const revenue = useMemo(() => {
    if (!data) return null;
    const rows = (data.revenue[currency] || []).slice(-range).map(r => ({ day: short(r.date), revenue: r.amount_cents / 100, orders: r.orders }));
    return opts({ ...base, data: rows, series: [{ type: 'bar', xKey: 'day', yKey: 'revenue', yName: 'Captured amount', fill: BLUE, cornerRadius: 4, tooltip: { renderer: ({ datum }: { datum: { day: string; revenue: number; orders: number } }) => ({ heading: datum.day, data: [{ label: 'Captured', value: money(datum.revenue * 100, currency) }, { label: 'Paid orders', value: String(datum.orders) }] }) } }],
      axes: { x: { type: 'category', line: { enabled: false }, tick: { enabled: false }, label: { ...axisText, avoidCollisions: true } }, y: { type: 'number', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: { ...axisText, formatter: ({ value }: { value: number }) => money(value * 100, currency) } } } });
  }, [data, range, currency]);
  const hours = useMemo(() => {
    if (!data) return null;
    const peak = Math.max(1, ...data.orders_by_hour.map(h => h.orders));
    return opts({ ...base, data: data.orders_by_hour.map(h => ({ hour: `${String(h.hour).padStart(2, '0')}`, orders: h.orders })), series: [{ type: 'bar', xKey: 'hour', yKey: 'orders', yName: 'Orders', cornerRadius: 3,
      itemStyler: ({ datum }: { datum: { orders: number } }) => ({ fill: datum.orders === 0 ? '#e7e8eb' : `rgba(0,87,255,${0.25 + 0.75 * (datum.orders / peak)})` }), tooltip: { renderer: ({ datum }: { datum: { hour: string; orders: number } }) => ({ heading: `${datum.hour}:00`, data: [{ label: 'Orders', value: String(datum.orders) }] }) } }],
    axes: { x: { type: 'category', line: { enabled: false }, tick: { enabled: false }, label: { ...axisText, interval: { step: 3 } } }, y: { type: 'number', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: axisText, interval: { minSpacing: 30 } } } });
  }, [data]);
  const top = (key: 'top_by_quantity' | 'top_by_revenue') => {
    if (!data) return null;
    const rev = key === 'top_by_revenue';
    return opts({ ...base, data: data[key].map(t => ({ name: trunc(t.name), value: rev ? t.value / 100 : t.value })).reverse(), series: [{ type: 'bar', direction: 'horizontal', xKey: 'name', yKey: 'value', yName: rev ? 'Revenue' : 'Units', fill: rev ? INK : BLUE, cornerRadius: 3,
      tooltip: { renderer: ({ datum }: { datum: { name: string; value: number } }) => ({ heading: datum.name, data: [{ label: rev ? 'Revenue' : 'Units', value: rev ? money(datum.value * 100, currency) : String(datum.value) }] }) } }],
    axes: { x: { type: 'category', position: 'left', line: { enabled: false }, tick: { enabled: false }, label: axisText }, y: { type: 'number', position: 'bottom', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: { ...axisText, formatter: ({ value }: { value: number }) => rev ? money(value * 100, currency) : String(value) } } } });
  };
  const qty = useMemo(() => top('top_by_quantity'), [data]);
  const rev = useMemo(() => top('top_by_revenue'), [data, currency]);
  const donut = useMemo(() => {
    if (!data) return null;
    const h = data.stock_health;
    return opts({ ...base, legend: { enabled: true, position: 'bottom', item: { label: { color: MUTED, fontFamily: 'Inter', fontSize: 12 } } }, data: [{ s: 'In stock', n: h.in_stock }, { s: 'Low', n: h.low }, { s: 'Out', n: h.out }, { s: 'Stale count', n: h.stale }].filter(x => x.n > 0),
      series: [{ type: 'donut', angleKey: 'n', legendItemKey: 's', calloutLabelKey: 's', innerRadiusRatio: 0.62, fills: [INK, '#d97706', '#d92d20', '#b5bcc8'], strokeWidth: 2, calloutLabel: { enabled: false }, sectorLabelKey: 'n', sectorLabel: { color: '#fff', fontFamily: 'Inter', fontSize: 12, fontWeight: 600 } }] });
  }, [data]);
  const pickup = useMemo(() => {
    if (!data) return null;
    return opts({ ...base, legend: { enabled: true, position: 'bottom', item: { label: { color: MUTED, fontFamily: 'Inter', fontSize: 12 } } }, data: data.pickup_utilisation.map(p => ({ day: weekday(p.date) + ' ' + short(p.date).split(' ')[1], booked: p.booked, free: p.capacity - p.booked })),
      series: [{ type: 'bar', xKey: 'day', yKey: 'booked', yName: 'Booked', stacked: true, fill: BLUE }, { type: 'bar', xKey: 'day', yKey: 'free', yName: 'Free', stacked: true, fill: '#dbe6ff', cornerRadius: 3 }],
      axes: { x: { type: 'category', line: { enabled: false }, tick: { enabled: false }, label: axisText }, y: { type: 'number', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: axisText, interval: { minSpacing: 30 } } } });
  }, [data]);
  const sk = <div className="pf-skeleton h-60" />;
  const none = (text: string) => <Empty title="No data yet" description={text} />;
  return <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-6" data-testid="overview-charts">
    <Panel className="md:col-span-2 xl:col-span-4" title="Captured amounts by day" description={data?.revenue_note || 'Recorded captured amounts, not profit.'}
      actions={<>{currencies.length > 1 && <select className="pf-select sm !w-auto" aria-label="Currency" value={currency} onChange={e => setCur(e.target.value)}>{currencies.map(c => <option key={c}>{c}</option>)}</select>}
        <div className="pf-segmented" role="group" aria-label="Revenue range">{([7, 30] as const).map(d => <button key={d} aria-pressed={range === d} onClick={() => setRange(d)}>{d} days</button>)}</div></>}>
      {loading || !revenue ? sk : <ChartBox options={revenue} height={260} label={`Captured amounts per day, last ${range} days, ${currency}`} />}
    </Panel>
    <Panel className="xl:col-span-2" title="Stock health" description={`Low means ${data?.stock_health.threshold ?? 3} or fewer available`}>
      {loading || !donut ? sk : data && Object.values(data.stock_health).slice(0, 4).every(n => n === 0) ? none('Add products to see stock health.') : <ChartBox options={donut} height={260} label="Stock health: in stock, low, out and stale counts" />}
    </Panel>
    <Panel className="xl:col-span-3" title="Orders by hour of day" description="Last 30 days, store time. Darker is busier">
      {loading || !hours ? sk : <ChartBox options={hours} height={230} label="Orders by hour of day" />}
    </Panel>
    <Panel className="xl:col-span-3" title="Pickup slot utilisation" description="Booked and free slots per day">
      {loading || !pickup ? sk : data?.pickup_utilisation.length ? <ChartBox options={pickup} height={230} label="Pickup slot utilisation per day" /> : none('Create pickup slots to see utilisation.')}
    </Panel>
    <Panel className="xl:col-span-3" title="Top products by units" description="Paid orders, last 30 days">
      {loading || !qty ? sk : data?.top_by_quantity.length ? <ChartBox options={qty} height={230} label="Top products by units sold" /> : none('Paid orders will rank products here.')}
    </Panel>
    <Panel className="xl:col-span-3" title="Top products by revenue" description="Captured amounts, last 30 days">
      {loading || !rev ? sk : data?.top_by_revenue.length ? <ChartBox options={rev} height={230} label="Top products by captured revenue" /> : none('Paid orders will rank products here.')}
    </Panel>
  </div>;
}

export function SeeAll({ to, children }: { to: string; children: React.ReactNode }) { return <Link className="pf-link text-sm inline-flex items-center gap-1" to={to}>{children}<ArrowRight size={14} /></Link>; }
