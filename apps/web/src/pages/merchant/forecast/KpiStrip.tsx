import { CalendarClock, CloudRain, Gauge, MapPin, PackageCheck, TrendingUp } from 'lucide-react';
import type { Forecast } from '../overviewTypes';

type Kpi = { label: string; value: string; hint: string; icon: React.ReactNode; tone?: 'bad' | 'warn' };

export function KpiStrip({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  if (loading || !forecast) return <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">{[0, 1, 2, 3, 4, 5].map(i => <div key={i} className="pf-skeleton h-24" />)}</div>;
  const s = forecast.summary;
  const items: Kpi[] = [
    { label: 'Demand today', value: String(s.demand_index_today), hint: '100 is a normal day', icon: <Gauge size={16} /> },
    { label: 'Next 7 days', value: String(s.demand_index_avg_7d), hint: s.peak_day ? `Peaks ${new Date(s.peak_day + 'T12:00:00').toLocaleDateString([], { weekday: 'long' })}` : 'Average index', icon: <TrendingUp size={16} /> },
    { label: 'Rain days', value: String(s.rain_days), hint: s.rain_days ? 'Rain chance 40% or more' : 'None above 40% chance', icon: <CloudRain size={16} />, tone: s.rain_days ? 'warn' : undefined },
    { label: 'Events within 3 km', value: String(s.events_nearby), hint: 'Demo events feed', icon: <MapPin size={16} /> },
    { label: 'Paydays and holidays', value: String(s.calendar_ahead), hint: `Next ${forecast.calendar.ahead_days} days, demo calendar`, icon: <CalendarClock size={16} /> },
    { label: 'Pickup capacity risk', value: s.pickup_risk_days ? `${s.pickup_risk_days} day${s.pickup_risk_days > 1 ? 's' : ''}` : 'None', hint: s.pickup_risk_days ? 'Slots tight, full or missing' : 'Slots cover expected orders', icon: <PackageCheck size={16} />, tone: s.pickup_risk_days ? 'bad' : undefined },
  ];
  return <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3" data-testid="forecast-kpis">{items.map(k => <div key={k.label} className="pf-card p-4 min-w-0">
    <div className="flex items-center gap-1.5 text-xs text-muted">{k.icon}<span className="truncate">{k.label}</span></div>
    <div className={`font-display text-3xl font-semibold tabular mt-1 ${k.tone === 'bad' ? 'text-bad' : k.tone === 'warn' ? 'text-warn' : ''}`}>{k.value}</div>
    <div className="text-xs text-muted mt-0.5 truncate">{k.hint}</div>
  </div>)}</div>;
}
