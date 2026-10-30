import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { cash } from '../../../lib/api';
import { Chip } from '../../../components/Shared';
import type { Forecast } from '../overviewTypes';
import { askState } from '../OverviewSections';
import { BarList, ColumnChart, DataTable, EmptyState, Metric, MetricGrid, ReportSection, TrendChart } from './parts';
import { Showcase } from './Showcase';
import type { ReportPackData } from './types';

const money = (c: number, cur: string) => cash(c, cur);
const short = (iso: string) => new Date(iso + 'T12:00:00').toLocaleDateString([], { month: 'short', day: 'numeric' });
const hour = (h: number) => `${String(h).padStart(2, '0')}:00`;
const pct = (n: number, d: number) => (d ? `${Math.round((100 * n) / d)}%` : '0%');

export function ReportPack({ pack, forecast, forecastError }: { pack: ReportPackData; forecast: Forecast | null; forecastError: string }) {
  const s = pack.summary, f = pack.funnel, name = pack.store_name;
  const headline = forecast?.insights[0];
  const multi = pack.summary.by_currency.length > 1;
  return <div className="flex flex-col gap-5">
    <ReportSection id="summary" title="Executive summary" description={`${short(pack.start_date)} to ${short(pack.end_date)} · ${pack.days} days`}
      csv={{ name: `${name} summary`, columns: ['Currency', 'Captured amount', 'Orders', 'Average basket'], rows: s.by_currency.map(c => [c.currency, (c.captured_amount_cents / 100).toFixed(2), c.orders, (c.average_basket_cents / 100).toFixed(2)]) }}>
      {s.by_currency.length ? <MetricGrid>
        {s.by_currency.flatMap(c => [<Metric key={`a${c.currency}`} label={multi ? `Captured (${c.currency})` : 'Captured revenue'} value={money(c.captured_amount_cents, c.currency)} hint={`${c.orders.toLocaleString()} captured orders`} />,
          <Metric key={`b${c.currency}`} label={multi ? `Average basket (${c.currency})` : 'Average basket'} value={money(c.average_basket_cents, c.currency)} />])}
        <Metric label="Orders placed" value={s.orders_in_range.toLocaleString()} hint="all statuses" />
        <Metric label="Pickup completion" value={s.pickup_completion_pct === null ? 'No data' : `${s.pickup_completion_pct}%`} hint="paid orders collected" tone={s.pickup_completion_pct !== null && s.pickup_completion_pct < 90 ? 'warn' : undefined} />
        <Metric label="Low or out of stock" value={s.stock_attention_count} hint={`${s.out_of_stock} out · ${s.low_stock} low`} tone={s.stock_attention_count ? 'warn' : 'ok'} />
        <Metric label="Forecast headline" value={<span className="text-base font-semibold leading-snug font-text block">{headline ? headline.title : forecastError ? 'Unavailable' : 'Loading…'}</span>} hint={headline?.body} />
      </MetricGrid> : <EmptyState title="No captured orders in this range">Try 90 days, or take a first order from the storefront. Amounts appear here as soon as a payment is captured.</EmptyState>}
      <p className="text-xs text-muted">{pack.note}</p>
    </ReportSection>

    <Showcase pack={pack} />

    <ReportSection id="trend" title="Sales trend" description="Captured amount per day, each currency on its own scale"
      csv={{ name: `${name} daily sales`, columns: ['Date', 'Currency', 'Captured amount', 'Orders'], rows: Object.entries(pack.sales_trend.by_currency).flatMap(([cur, rows]) => rows.map(r => [r.date, cur, (r.amount_cents / 100).toFixed(2), r.orders])) }}>
      {Object.entries(pack.sales_trend.by_currency).some(([, rows]) => rows.some(r => r.amount_cents > 0)) ? Object.entries(pack.sales_trend.by_currency).map(([cur, rows]) => <div key={cur}>
        {multi && <h3 className="text-sm font-semibold mb-1">{cur}</h3>}
        <TrendChart label={`Daily captured amount in ${cur}`} points={rows.map(r => ({ label: short(r.date), value: r.amount_cents / 100 }))} format={n => cash(Math.round(n * 100), cur).replace(/\.00$/, '')} /></div>)
        : <EmptyState title="No sales to chart yet">Captured payments will draw this line. Use the 90-day range for a longer view.</EmptyState>}
    </ReportSection>

    <ReportSection id="mix" title="Sales by category and branch" description="Captured amounts, by currency"
      csv={{ name: `${name} sales by category`, columns: ['Category', 'Currency', 'Units', 'Captured amount'], rows: pack.categories.map(c => [c.category, c.currency, c.units, (c.amount_cents / 100).toFixed(2)]) }}>
      {pack.categories.length || pack.branches.length ? <div className="grid gap-6 xl:grid-cols-2">
        <div className="flex flex-col gap-4">
          <BarList label="Captured amount by category" rows={pack.categories.slice(0, 8).map(c => ({ label: `${c.category}${multi ? ` (${c.currency})` : ''}`, value: c.amount_cents, display: money(c.amount_cents, c.currency).replace(/\.00$/, '') }))} />
          <DataTable name={`${name} categories`} title="By category" columns={['Category', 'Currency', 'Units', 'Captured amount']} numeric={[2, 3]} rows={pack.categories.map(c => [c.category, c.currency, c.units, money(c.amount_cents, c.currency)])} />
        </div>
        <div className="flex flex-col gap-4">
          <BarList ink label="Captured amount by branch" rows={pack.branches.map(b => ({ label: b.branch, value: b.amount_cents, display: money(b.amount_cents, b.currency).replace(/\.00$/, '') }))} />
          <DataTable name={`${name} branches`} title="By branch" columns={['Branch', 'Currency', 'Orders', 'Captured amount']} numeric={[2, 3]} rows={pack.branches.map(b => [b.branch, b.currency, b.orders, money(b.amount_cents, b.currency)])} />
        </div>
      </div> : <EmptyState title="No category or branch sales yet">Sales are grouped from captured orders. Make sure products have a category under Inventory.</EmptyState>}
    </ReportSection>

    <ReportSection id="products" title="Top products" description="Ranked by units, with captured revenue alongside"
      csv={{ name: `${name} top products`, columns: ['Product', 'Units', 'Currency', 'Captured amount'], rows: pack.top_products.by_units.map(p => [p.name, p.units, p.currency, (p.amount_cents / 100).toFixed(2)]) }}>
      {pack.top_products.by_units.length ? <div className="grid gap-6 xl:grid-cols-2">
        <div className="flex flex-col gap-3"><h3 className="text-sm font-semibold">By units sold</h3><BarList label="Top products by units" rows={pack.top_products.by_units.slice(0, 8).map(p => ({ label: p.name, value: p.units, display: p.units.toLocaleString() }))} /></div>
        <div className="flex flex-col gap-3"><h3 className="text-sm font-semibold">By captured revenue</h3><BarList ink label="Top products by revenue" rows={pack.top_products.by_revenue.slice(0, 8).map(p => ({ label: p.name, value: p.amount_cents, display: money(p.amount_cents, p.currency).replace(/\.00$/, '') }))} /></div>
        <div className="xl:col-span-2"><DataTable name={`${name} top products`} title="Top 10" columns={['Product', 'Units', 'Currency', 'Captured amount']} numeric={[1, 3]} rows={pack.top_products.by_units.map(p => [p.name, p.units, p.currency, money(p.amount_cents, p.currency)])} /></div>
      </div> : <EmptyState title="No product sales yet">Top products rank once orders are paid. Check that products are active under Inventory.</EmptyState>}
    </ReportSection>

    <ReportSection id="funnel" title="Orders funnel" description="How reservations move through payment and pickup"
      csv={{ name: `${name} orders funnel`, columns: ['Stage', 'Orders'], rows: Object.entries(f).map(([k, v]) => [k, v]) }}>
      {f.reserved ? <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <BarList label="Orders by stage" rows={([['Reserved', f.reserved], ['Paid', f.paid], ['Prepared', f.prepared], ['Collected', f.collected]] as [string, number][]).map(([l, v]) => ({ label: l, value: v, display: `${v.toLocaleString()} · ${pct(v, f.reserved)}` }))} />
        <div className="grid grid-cols-3 gap-3 content-start"><Metric label="Cancelled" value={f.cancelled} /><Metric label="Refunded" value={f.refunded} tone={f.refunded ? 'warn' : undefined} /><Metric label="Expired" value={f.expired} /></div>
      </div> : <EmptyState title="No orders in this range">The funnel fills as shoppers reserve and pay. Try a longer range.</EmptyState>}
    </ReportSection>

    <ReportSection id="stock" title="Stock health" description={`Low means ${pack.stock_health.threshold} or fewer available. Counts are listed quantities, not POS-authoritative.`}
      csv={{ name: `${name} stock attention`, columns: ['Product', 'Available', 'State'], rows: pack.stock_health.attention.map(r => [r.name, r.available, r.state]) }}>
      <MetricGrid><Metric label="In stock" value={pack.stock_health.in_stock} tone="ok" /><Metric label="Low" value={pack.stock_health.low} tone={pack.stock_health.low ? 'warn' : undefined} /><Metric label="Out of stock" value={pack.stock_health.out} tone={pack.stock_health.out ? 'bad' : undefined} /><Metric label="Stale count" value={pack.stock_health.stale} hint="not counted in 24 h" /></MetricGrid>
      {pack.stock_health.attention.length ? <DataTable name={`${name} stock attention`} title="Needs a count or a reorder" columns={['Product', 'Available', 'State']} numeric={[1]} rows={pack.stock_health.attention.slice(0, 25).map(r => [r.name, r.available, r.state === 'out' ? 'Out of stock' : r.state === 'low' ? 'Low' : 'Stale count'])} />
        : <EmptyState title="Nothing needs attention">Every active product is counted and above its low-stock level.</EmptyState>}
    </ReportSection>

    <ReportSection id="pickup" title="Pickup utilisation" description="Collected orders by branch and hour, plus booked places in upcoming pickup windows"
      csv={{ name: `${name} pickup by branch`, columns: ['Branch', 'Currency', 'Collected', 'Orders'], rows: pack.pickup.by_branch.map(b => [b.branch, b.currency, b.collected, b.orders]) }}>
      {pack.pickup.by_branch.length ? <div className="grid gap-6 xl:grid-cols-2">
        <div className="flex flex-col gap-3"><h3 className="text-sm font-semibold">Collected orders by hour</h3>
          <ColumnChart label="Collected orders by hour of day" points={pack.pickup.collected_by_hour.filter(h => h.hour >= 7 && h.hour <= 21).map(h => ({ label: hour(h.hour).slice(0, 2), value: h.orders }))} /></div>
        <DataTable name={`${name} pickup by branch`} title="By branch" columns={['Branch', 'Collected', 'Orders']} numeric={[1, 2]} rows={pack.pickup.by_branch.map(b => [b.branch, b.collected, b.orders])} />
        <div className="xl:col-span-2"><SlotGrid pack={pack} /></div>
      </div> : <EmptyState title="No pickups yet">Collected orders appear here. Add pickup windows under Pickup so shoppers can book one.</EmptyState>}
    </ReportSection>

    <ReportSection id="recs" title="Recommendations" description="Next steps drawn from the sections above"
      csv={{ name: `${name} recommendations`, columns: ['Recommendation', 'Detail'], rows: pack.recommendations.map(r => [r.title, r.detail]) }}>
      <ul className="flex flex-col divide-y divide-line">{pack.recommendations.map(r => <li key={r.title} className="py-3 flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0"><p className="font-semibold text-sm">{r.title}</p><p className="text-sm text-muted">{r.detail}</p></div>
        <div className="no-print flex gap-2"><Link className="pf-btn sm outline" to={r.to}>{r.action}</Link><Link className="pf-btn sm ghost" to="/merchant/assistant" state={askState(`${r.title}. ${r.detail} What should I do about it?`)}><Sparkles size={14} />Ask assistant</Link></div></li>)}</ul>
      {forecast?.insights.length ? <div className="flex flex-wrap gap-2">{forecast.insights.slice(0, 3).map(i => <Chip key={i.title} kind="blue">{i.title}</Chip>)}</div> : null}
    </ReportSection>
  </div>;
}

function SlotGrid({ pack }: { pack: ReportPackData }) {
  const cells = pack.pickup.slots;
  if (!cells.length) return <EmptyState title="No upcoming pickup windows">Create windows under Pickup to see booked places by branch and hour.</EmptyState>;
  const branches = [...new Set(cells.map(c => c.branch))], hours = [...new Set(cells.map(c => c.hour))].sort((a, b) => a - b);
  const at = (b: string, h: number) => cells.find(c => c.branch === b && c.hour === h);
  return <div className="pf-keep"><h3 className="text-sm font-semibold mb-1.5">Upcoming pickup windows: booked share by branch and hour{pack.pickup.slot_utilisation_pct !== null && <span className="text-muted font-normal"> · {pack.pickup.slot_utilisation_pct}% overall ({pack.pickup.slot_booked} of {pack.pickup.slot_capacity})</span>}</h3>
    <div className="overflow-x-auto"><table className="pf-rt"><thead><tr><th>Branch</th>{hours.map(h => <th key={h} className="num">{String(h).padStart(2, '0')}</th>)}</tr></thead>
      <tbody>{branches.map(b => <tr key={b}><td className="whitespace-nowrap">{b}</td>{hours.map(h => { const c = at(b, h); return <td key={h} className="num" style={c ? { background: `rgba(0,87,255,${Math.min(0.55, c.utilisation_pct / 180)})` } : undefined} title={c ? `${c.booked} of ${c.capacity} booked` : 'No window'}>{c ? `${c.utilisation_pct}%` : ''}</td>; })}</tr>)}</tbody></table></div></div>;
}
