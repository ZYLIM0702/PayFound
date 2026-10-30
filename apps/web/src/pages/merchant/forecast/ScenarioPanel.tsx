import { Panel } from '../../../components/Shared';
import { AskLink } from '../OverviewSections';
import type { Forecast } from '../overviewTypes';
import { ConfidenceChip, EmptyLine, Skel, signed } from './shared';

export function ScenarioPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  return <Panel title="What if" description={forecast?.scenarios.label ?? 'Demo scenarios'} className="h-full" actions={<ConfidenceChip value="demo" />}>
    <div data-testid="forecast-scenarios">
      {loading || !forecast ? <Skel h="h-48" /> : forecast.scenarios.items.length === 0 ? <EmptyLine>Add products to compare scenarios.</EmptyLine> :
        <div className="grid md:grid-cols-2 gap-4">{forecast.scenarios.items.map(s => <div key={s.id} className="rounded-[10px] border border-line p-4 min-w-0">
          <h3 className="text-sm font-semibold">{s.title}</h3>
          <div className="flex items-baseline gap-2 mt-2"><span className="font-display text-3xl font-semibold tabular">{s.delta_units_7d > 0 ? '+' : ''}{Math.round(s.delta_units_7d)}</span><span className="text-sm text-muted">units over 7 days ({signed(s.delta_pct)})</span></div>
          <p className="text-[13px] mt-1">{s.summary}</p>
          {s.extra_prep.length > 0 && <ul className="mt-2 text-[13px] space-y-0.5">{s.extra_prep.map(x => <li key={x.product_id} className="flex justify-between gap-2"><span className="truncate">{x.product}</span><span className="tabular shrink-0">+{x.extra_units}{x.short ? ' · restock first' : ''}</span></li>)}</ul>}
          <p className="text-xs text-muted mt-2">{s.assumption}</p>
          <AskLink ask={s.ask} className="pf-link text-sm mt-2 inline-block">Ask the assistant</AskLink>
        </div>)}</div>}
    </div>
  </Panel>;
}

export function MethodPanel({ forecast, loading }: { forecast: Forecast | null; loading: boolean }) {
  return <Panel title="How this forecast works" description="How the numbers are built" className="h-full">
    <div data-testid="forecast-method" className="space-y-3">
      {loading || !forecast ? <Skel h="h-48" /> : <>
        <p className="text-[13px] leading-relaxed">{forecast.method_note}</p>
        <ul className="divide-y divide-line">{forecast.confidence.parts.map(p => <li key={p.name} className="py-2 flex items-start gap-2 justify-between">
          <span className="min-w-0"><span className="block text-sm font-semibold">{p.name}</span><span className="block text-xs text-muted">{p.detail}</span></span><span className="shrink-0"><ConfidenceChip value={p.status} /></span></li>)}</ul>
      </>}
    </div>
  </Panel>;
}
