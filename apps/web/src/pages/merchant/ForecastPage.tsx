import { PageHeader } from '../../components/Shared';
import { useResource } from '../../lib/use-resource';
import { scoped } from '../../lib/api';
import { useApp } from '../../lib/app-context';
import { InsightsPanel, PrepPanel } from './OverviewSections';
import { CalendarPanel } from './forecast/CalendarPanel';
import { DemandPanel } from './forecast/DemandPanel';
import { DriversTable } from './forecast/DriversTable';
import { KpiStrip } from './forecast/KpiStrip';
import { PickupOutlook, StockCover } from './forecast/OutlookPanels';
import { StockUpPanel } from './forecast/StockUpPanel';
import { MethodPanel, ScenarioPanel } from './forecast/ScenarioPanel';
import type { Forecast } from './overviewTypes';

/** Forecasting: next-7-day demand and the drivers behind it, on a full-width 12-column grid. */
export function ForecastPage({ merchantId }: { merchantId: string }) {
  const { demo } = useApp();
  const forecast = useResource<Forecast>(scoped('/merchant/forecast', merchantId), 300000);
  const f = forecast.data, loading = forecast.loading;
  return <div className="space-y-5 pf-enter w-full min-w-0" data-testid="forecast-page">
    <PageHeader title="Forecast" description="Next 7 days of demand, the drivers behind it and what to prepare. Weather, stock and pickup slots are live; events and the holiday calendar are demo data."
      right={demo ? <span className="pf-chip" title={f?.label}>Model</span> : undefined} />
    {forecast.error && !f && <p className="text-sm text-bad" role="alert">The forecast could not be loaded. Try again shortly.</p>}
    <KpiStrip forecast={f} loading={loading} />
    <div className="grid grid-cols-12 gap-5">
      <div className="col-span-12"><DemandPanel forecast={f} loading={loading} /></div>
      <div className="col-span-12 xl:col-span-8 min-w-0"><DriversTable forecast={f} loading={loading} /></div>
      <div className="col-span-12 xl:col-span-4 min-w-0"><CalendarPanel forecast={f} loading={loading} /></div>
      <div className="col-span-12 lg:col-span-6 min-w-0"><PrepPanel forecast={f} loading={loading} /></div>
      <div className="col-span-12 lg:col-span-6 min-w-0"><InsightsPanel forecast={f} loading={loading} /></div>
      <div className="col-span-12 lg:col-span-6 min-w-0"><PickupOutlook forecast={f} loading={loading} /></div>
      <div className="col-span-12 lg:col-span-6 min-w-0"><StockCover forecast={f} loading={loading} /></div>
      <div className="col-span-12 min-w-0"><StockUpPanel merchantId={merchantId} /></div>
      <div className="col-span-12 xl:col-span-8 min-w-0"><ScenarioPanel forecast={f} loading={loading} /></div>
      <div className="col-span-12 xl:col-span-4 min-w-0"><MethodPanel forecast={f} loading={loading} /></div>
    </div>
  </div>;
}
