import { CalendarDays, Landmark, Wallet } from 'lucide-react';
import { Panel } from '../../../components/Shared';
import { AskLink } from '../OverviewSections';
import type { Forecast } from '../overviewTypes';
import { EmptyLine, Skel, shortDate, signed, weekday } from './shared';

export function CalendarPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  return <Panel title="Events, holidays and paydays" description="Nearby events, plus the demo calendar for the store's country" className="h-full">
    <div data-testid="forecast-calendar" className="space-y-5">
      {loading || !forecast ? <Skel h="h-72" /> : <>
        <section aria-label="Local events within 3 km">
          <h3 className="text-sm font-semibold mb-2">Local events within 3 km</h3>
          {forecast.events.length === 0 ? <EmptyLine>No events within 3 km in the next 7 days.</EmptyLine> :
            <ul className="space-y-2" data-testid="overview-events">{forecast.events.slice(0, 6).map(e => <li key={`${e.id}-${e.date}`}>
              <AskLink ask={`The event "${e.name}" is ${e.distance_km} km from my store on ${e.date}. How should I prepare?`} className="flex items-start gap-3 rounded-[10px] bg-sunk p-2.5 hover:bg-line transition-colors">
                <CalendarDays size={16} className="mt-0.5 text-accent shrink-0" /><span className="min-w-0"><span className="block text-sm font-semibold">{e.name}</span><span className="block text-xs text-muted">{weekday(e.date)} {shortDate(e.date)}{e.start ? ` · ${e.start}` : ''} · {e.distance_km} km · {e.footfall.replace('_', ' ')} footfall</span></span></AskLink></li>)}</ul>}
        </section>
        <section aria-label="Holidays and paydays">
          <h3 className="text-sm font-semibold mb-2">Holidays and paydays, {forecast.calendar.country_name}</h3>
          {forecast.calendar.entries.length === 0 && forecast.calendar.paydays.length === 0 ? <EmptyLine>No holidays or paydays in the demo calendar for the next 30 days.</EmptyLine> :
            <ul className="space-y-2">
              {forecast.calendar.entries.slice(0, 5).map(r => <li key={`${r.name}-${r.range_start}`} className="flex items-start gap-3 rounded-[10px] bg-sunk p-2.5">
                <Landmark size={16} className="mt-0.5 text-warn shrink-0" /><span className="min-w-0"><span className="block text-sm font-semibold">{r.name}</span><span className="block text-xs text-muted">{weekday(r.range_start)} {shortDate(r.range_start)}{r.range_end !== r.range_start ? ` to ${shortDate(r.range_end)}` : ''} · {r.kind.replace('_', ' ')} · typical effect {signed(r.effect_pct)}</span></span></li>)}
              {forecast.calendar.paydays.length > 0 && <li className="flex items-start gap-3 rounded-[10px] bg-sunk p-2.5"><Wallet size={16} className="mt-0.5 text-ok shrink-0" /><span className="min-w-0"><span className="block text-sm font-semibold">Paydays</span><span className="block text-xs text-muted">{forecast.calendar.paydays.map(d => `${weekday(d)} ${shortDate(d)}`).join(', ')} · spend is typically higher for about 3 days after</span></span></li>}
            </ul>}
          <p className="text-xs text-muted mt-3">{forecast.calendar.payday_rule} {forecast.calendar.note}</p>
        </section>
      </>}
    </div>
  </Panel>;
}
