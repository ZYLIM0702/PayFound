import { useMemo } from 'react';
import type { AgChartOptions } from 'ag-charts-community';
import { ChartBox } from '../../../components/ChartBox';
import { Panel } from '../../../components/Shared';
import type { Forecast } from '../overviewTypes';
import { EmptyLine, Skel, shortDate, weekday } from './shared';

const INK = '#0a0a0b', BLUE = '#0057ff', MUTED = '#62656d', GRID = '#eff0f2';
const PALETTE = ['#7a8ca8', INK, '#2f6fed', '#b5bcc8', '#4b5563', '#93a8d6', '#1f3a8a'];
const axisText = { color: MUTED, fontFamily: 'Inter', fontSize: 12 };

export function DemandPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  const chart = useMemo(() => {
    if (!forecast || !forecast.demand_index.length) return null;
    const cats = forecast.demand_index;
    const data = forecast.daily.map((d, i) => ({ day: `${weekday(d.date)} ${shortDate(d.date).split(' ')[1]}`, store: d.demand_index, ...Object.fromEntries(cats.map((c, k) => [`c${k}`, c.days[i]?.demand_index])) }));
    const opts = {
      background: { fill: 'transparent' }, padding: { top: 8, right: 12, bottom: 0, left: 0 }, data,
      legend: { enabled: true, position: 'bottom', item: { label: { color: MUTED, fontFamily: 'Inter', fontSize: 12 } } },
      series: [
        ...cats.map((c, k) => ({ type: 'line', xKey: 'day', yKey: `c${k}`, yName: c.category, stroke: PALETTE[k % PALETTE.length], strokeWidth: 1.5, strokeOpacity: 0.8, marker: { size: 4, fill: PALETTE[k % PALETTE.length], stroke: '#fff' } })),
        { type: 'line', xKey: 'day', yKey: 'store', yName: 'Whole store', stroke: BLUE, strokeWidth: 3.5, marker: { size: 8, fill: BLUE, stroke: '#fff' } },
      ],
      axes: { x: { type: 'category', line: { enabled: false }, tick: { enabled: false }, label: axisText },
        y: { type: 'number', gridLine: { style: [{ stroke: GRID, lineDash: [] }] }, label: axisText, title: { text: 'Demand index (100 = normal)', ...axisText } } },
    };
    return opts as unknown as AgChartOptions;
  }, [forecast]);

  return <Panel title="Next 7 days" description="Demand index by category. 100 is a normal day for this store" className="h-full"
    actions={forecast && <span className="text-xs text-muted hidden sm:inline">Weather: {forecast.weather.source === 'Open-Meteo' ? 'Open-Meteo' : 'unavailable (neutral)'}</span>}>
    <div className="space-y-4" data-testid="forecast-demand">
      {loading || !forecast ? <Skel h="h-80" /> : !chart ? <EmptyLine>Add products and take a few orders to see demand by category.</EmptyLine> : <>
        <ChartBox options={chart} height={320} label="Demand index by category and for the whole store for the next 7 days" />
        <WeatherStrip forecast={forecast} />
        <BranchSplit forecast={forecast} />
      </>}
    </div>
  </Panel>;
}

function WeatherStrip({ forecast }: { forecast: Forecast }) {
  const wx = new Map(forecast.weather.days.map(d => [d.date, d]));
  return <div className="grid grid-cols-7 gap-1.5 sm:gap-2" aria-label="Weather, events and calendar by day" data-testid="forecast-weather-strip">{forecast.daily.map((d, i) => {
    const w = wx.get(d.date);
    const ev = forecast.events.filter(e => e.date === d.date).length;
    const cal = forecast.calendar.horizon[i];
    const tag = cal?.holidays[0] ?? cal?.payday_label ?? null;
    const rainy = (w?.rain_chance_pct ?? 0) >= 40;
    return <div key={d.date} className="rounded-[10px] bg-sunk px-1 sm:px-2.5 py-2 text-center min-w-0" title={`${w?.summary ?? ''} ${tag ?? ''}`}>
      <p className="text-xs font-semibold">{weekday(d.date)}</p>
      <p className="font-display text-lg font-semibold tabular leading-tight">{d.demand_index}</p>
      <p className="text-[11px] text-muted truncate">{w?.temp_max_c != null ? `${Math.round(w.temp_max_c)}°` : '–'}<span className={rainy ? ' text-accent font-semibold' : ''}>{w?.rain_chance_pct != null ? ` ${w.rain_chance_pct}%` : ''}</span></p>
      <p className={`text-[11px] truncate ${ev ? 'text-accent font-semibold' : 'text-subtle'}`}>{ev ? `${ev} event${ev > 1 ? 's' : ''}` : 'quiet'}</p>
      <p className="text-[11px] truncate text-muted hidden sm:block">{tag ?? ' '}</p>
    </div>;
  })}</div>;
}

function BranchSplit({ forecast }: { forecast: Forecast }) {
  const b = forecast.branches;
  if (b.length < 2) return <p className="text-xs text-muted">Single-branch store: no branch split.</p>;
  return <div data-testid="forecast-branches">
    <h3 className="text-sm font-semibold mb-2">Expected units by branch</h3>
    <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">{b.map(x => <div key={x.location_id} className="rounded-[10px] border border-line p-3 min-w-0">
      <div className="flex items-baseline justify-between gap-2"><span className="text-sm font-semibold truncate">{x.name}</span><span className="text-xs text-muted tabular shrink-0">{x.share_pct}% of recent sales</span></div>
      <div className="font-display text-2xl font-semibold tabular">{Math.round(x.expected_units_7d)} <span className="text-xs text-muted font-normal font-text">units, 7 days</span></div>
      <div className="flex items-end gap-0.5 h-8 mt-1" aria-hidden>{x.expected_units.map((u, i) => <span key={i} className="flex-1 bg-accent/70 rounded-sm" style={{ height: `${Math.max(8, 100 * u / Math.max(1, ...x.expected_units))}%` }} />)}</div>
      <div className="text-xs text-muted mt-1">Pickup slots next 7 days: {x.pickup_booked_7d} of {x.pickup_capacity_7d} booked</div>
    </div>)}</div>
    <p className="text-xs text-muted mt-2">Split uses each branch's share of the last 28 days of orders.</p>
  </div>;
}
