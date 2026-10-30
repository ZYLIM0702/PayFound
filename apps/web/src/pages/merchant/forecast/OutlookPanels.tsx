import { Chip, Panel, type Tone } from '../../../components/Shared';
import { AskLink } from '../OverviewSections';
import type { Forecast, PickupDay } from '../overviewTypes';
import { EmptyLine, Skel, shortDate } from './shared';

const FLAG: Record<PickupDay['flag'], [Tone, string]> = { ok: ['green', 'OK'], tight: ['amber', 'Tight'], capped: ['red', 'Capped'], none: ['default', 'No slots'] };

export function PickupOutlook({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  return <Panel title="Pickup capacity outlook" description="Published pickup slots against expected orders" className="h-full">
    <div data-testid="forecast-pickup">
      {loading || !forecast ? <Skel h="h-56" /> : forecast.pickup_outlook.days.length === 0 ? <EmptyLine>No pickup data yet. Publish pickup slots to see capacity.</EmptyLine> : <>
        <ul className="divide-y divide-line -my-2">{forecast.pickup_outlook.days.map(d => {
          const pct = d.slots_capacity ? Math.min(100, 100 * d.expected_orders / d.slots_capacity) : 0;
          const bookedPct = d.slots_capacity ? Math.min(100, 100 * d.booked / d.slots_capacity) : 0;
          return <li key={d.date} className="py-2.5 grid grid-cols-[3.5rem_1fr_auto] items-center gap-3">
            <span className="text-sm"><span className="font-semibold">{d.weekday}</span><span className="block text-xs text-muted">{shortDate(d.date)}</span></span>
            <span className="min-w-0"><span className="block h-2 rounded-full bg-sunk relative overflow-hidden" role="img" aria-label={`${d.booked} booked, ${d.expected_orders} expected, ${d.slots_capacity} slots`}>
              <span className={`absolute inset-y-0 left-0 rounded-full ${d.flag === 'capped' ? 'bg-bad/40' : d.flag === 'tight' ? 'bg-warn/40' : 'bg-accent/30'}`} style={{ width: `${pct}%` }} />
              <span className="absolute inset-y-0 left-0 rounded-full bg-accent" style={{ width: `${bookedPct}%` }} /></span>
              <span className="block text-xs text-muted mt-1 truncate">{d.booked} booked · {d.expected_orders} expected · {d.free} of {d.slots_capacity} free{d.rain_uplift_pct ? ` · rain +${d.rain_uplift_pct}%` : ''}</span></span>
            <Chip kind={FLAG[d.flag][0]}>{FLAG[d.flag][1]}</Chip>
          </li>;
        })}</ul>
        {forecast.pickup_outlook.days.some(d => d.note) && <ul className="mt-4 pt-3 border-t border-line space-y-1">{forecast.pickup_outlook.days.filter(d => d.note).slice(0, 3).map(d => <li key={d.date} className="text-[13px]"><AskLink ask={`${d.note} (${d.date}). What should I do about pickup slots?`} className="hover:underline"><strong>{d.weekday}:</strong> {d.note}</AskLink></li>)}</ul>}
        <p className="text-xs text-muted mt-3">{forecast.pickup_outlook.note}</p>
      </>}
    </div>
  </Panel>;
}

export function StockCover({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  const tone: Record<string, Tone> = { out: 'red', low: 'amber', ok: 'green' };
  return <Panel title="Stock risk by category" description="Days of cover at the forecast pace" className="h-full">
    <div data-testid="forecast-stock">
      {loading || !forecast ? <Skel h="h-56" /> : forecast.stock_cover.categories.length === 0 ? <EmptyLine>No active products yet. Add products to see stock cover.</EmptyLine> : <>
        <ul className="divide-y divide-line -my-2">{forecast.stock_cover.categories.slice(0, 8).map(c => <li key={c.category} className="py-2.5">
          <AskLink ask={`${c.category} has ${c.days_of_cover ?? 'unknown'} days of cover${c.out_of_stock_products.length ? ` and ${c.out_of_stock_products.join(', ')} is out of stock` : ''}. What should I reorder?`} className="flex items-center gap-3 group">
            <span className="min-w-0 flex-1"><span className="block text-sm font-semibold group-hover:underline">{c.category}</span>
              <span className="block text-xs text-muted truncate">{c.available_units} units · {c.expected_units_7d} expected in 7 days{c.out_of_stock_products.length ? ` · out: ${c.out_of_stock_products.join(', ')}` : ''}</span></span>
            <span className="text-sm tabular font-semibold shrink-0">{c.days_of_cover != null ? `${c.days_of_cover} d` : '–'}</span>
            <Chip kind={tone[c.status]}>{c.status === 'ok' ? 'Covered' : c.status === 'low' ? 'Watch' : 'Out'}</Chip>
          </AskLink>
          {c.note && <p className="text-xs text-muted mt-1">{c.suppressed_days} out-of-stock days. {c.note}</p>}
        </li>)}</ul>
        {forecast.stock_cover.suppressed_products.length > 0 && <div className="mt-4 pt-3 border-t border-line" data-testid="forecast-suppressed">
          <h3 className="text-sm font-semibold mb-1">Sales held down by stock-outs</h3>
          <ul className="text-[13px] space-y-0.5">{forecast.stock_cover.suppressed_products.slice(0, 4).map(p => <li key={p.product_id}>{p.product}: {p.suppressed_days} days out of stock. Counted at {p.rate_per_day}/day, not {p.naive_rate_per_day}/day.</li>)}</ul>
        </div>}
        <p className="text-xs text-muted mt-3">{forecast.stock_cover.note}</p>
      </>}
    </div>
  </Panel>;
}
