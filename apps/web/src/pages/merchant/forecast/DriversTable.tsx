import { ArrowDown, ArrowUp, ArrowUpDown, Minus } from 'lucide-react';
import { Panel } from '../../../components/Shared';
import { AskLink } from '../OverviewSections';
import type { Forecast, ForecastDriver } from '../overviewTypes';
import { ConfidenceChip, EmptyLine, Skel, signed, weekday } from './shared';

function Dir({ d }: { d: ForecastDriver['direction'] }) {
  const p = { size: 14, 'aria-hidden': true } as const;
  return d === 'up' ? <ArrowUp {...p} className="text-ok" /> : d === 'down' ? <ArrowDown {...p} className="text-bad" /> : d === 'mixed' ? <ArrowUpDown {...p} className="text-warn" /> : <Minus {...p} className="text-subtle" />;
}

function Spark({ effects, dates }: { effects: number[]; dates: string[] }) {
  const max = Math.max(5, ...effects.map(Math.abs));
  return <div className="flex items-center gap-1" aria-label={`Effect on demand by day: ${effects.map((e, i) => `${weekday(dates[i])} ${signed(e)}`).join(', ')}`}>{effects.map((e, i) => <span key={i} className="w-6 text-center" title={`${weekday(dates[i])} ${signed(e)}`}>
    <span className="block h-6 relative"><span className={`absolute left-1 right-1 rounded-sm ${e >= 0 ? 'bg-ok/70 bottom-1/2' : 'bg-bad/70 top-1/2'}`} style={{ height: `${Math.max(e === 0 ? 0 : 6, 50 * Math.abs(e) / max)}%` }} /><span className="absolute left-0 right-0 top-1/2 h-px bg-line" /></span>
    <span className="block text-[10px] text-subtle">{weekday(dates[i]).slice(0, 2)}</span></span>)}</div>;
}

export function DriversTable({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  const dates = forecast?.daily.map(d => d.date) ?? [];
  return <Panel title="What is moving demand" description="Each driver, its value today and its effect on the demand index for the next 7 days" className="h-full" flush>
    <div data-testid="forecast-drivers">
      {loading || !forecast ? <div className="pf-panel-body"><Skel h="h-72" /></div> : forecast.drivers.length === 0 ? <div className="pf-panel-body"><EmptyLine>No drivers available yet.</EmptyLine></div> : <>
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs text-muted border-b border-line"><th className="font-medium px-5 py-2.5">Driver</th><th className="font-medium py-2.5">Today</th><th className="font-medium py-2.5">Effect, next 7 days</th><th className="font-medium py-2.5 whitespace-nowrap">Avg / peak</th><th className="font-medium py-2.5 pr-5">Confidence</th></tr></thead>
            <tbody className="divide-y divide-line">{forecast.drivers.map(d => <tr key={d.id} className="align-top" data-testid={`driver-${d.id}`}>
              <td className="px-5 py-3 w-[22%]"><AskLink ask={d.ask} className="font-semibold hover:underline">{d.name}</AskLink><p className="text-xs text-muted mt-0.5 truncate max-w-[22ch]" title={d.summary + (d.data ? ` Source: ${d.data}` : '')}>{d.data ?? ''}</p></td>
              <td className="py-3 pr-4 w-[30%]"><span className="text-[13px]">{d.today_value}</span></td>
              <td className="py-3 pr-4"><Spark effects={d.effect_pct} dates={dates} /></td>
              <td className="py-3 pr-4 whitespace-nowrap tabular"><span className="inline-flex items-center gap-1"><Dir d={d.direction} />{signed(d.avg_effect_pct)} / {signed(d.peak_effect_pct)}</span></td>
              <td className="py-3 pr-5"><ConfidenceChip value={d.confidence} /></td>
            </tr>)}</tbody>
          </table>
        </div>
        <ul className="md:hidden divide-y divide-line">{forecast.drivers.map(d => <li key={d.id} className="px-4 py-3 space-y-1.5">
          <div className="flex items-center justify-between gap-2"><AskLink ask={d.ask} className="font-semibold text-sm">{d.name}</AskLink><ConfidenceChip value={d.confidence} /></div>
          <p className="text-[13px]">{d.today_value}</p>
          <div className="flex items-center justify-between gap-2"><Spark effects={d.effect_pct} dates={dates} /><span className="inline-flex items-center gap-1 text-xs tabular text-muted"><Dir d={d.direction} />{signed(d.avg_effect_pct)}</span></div>
        </li>)}</ul>
        <p className="px-5 py-3 text-xs text-muted border-t border-line">Effects are the average change in the demand index across categories. Observed = measured from your data, modelled = real input with an assumed size, demo = demo-only input.</p>
      </>}
    </div>
  </Panel>;
}
