import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, MonitorSmartphone } from 'lucide-react';
import type { ColDef } from 'ag-grid-community';
import { cash, localDateKey, scoped, type Order } from '../../lib/api';
import { useApp } from '../../lib/app-context';
import { useResource } from '../../lib/use-resource';
import type { PosState } from '../../lib/pos';
import { Chip, Empty, OrderStatus, PageHeader, Panel, Stat } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';
import { dateTimeFormatter, moneyFormatter, orderStatusCell, orderIdColumn } from '../../components/grid-cells';
import { LOW_STOCK_AT, useMerchant } from './context';
import { ReservationsToPrepare } from './Notifications';
import type { Analytics, Forecast } from './overviewTypes';
import { AlertsPanel, ChartsGrid, EventsPanel, ForecastPanel, InsightsPanel, PrepPanel, StoreStrip } from './OverviewSections';

const DAYS = 14;
const lastDays = (n: number) => Array.from({ length: n }, (_, i) => { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - (n - 1 - i)); return d; });

export function Overview() {
  const { dashboard: data, merchantId } = useMerchant();
  const { demo } = useApp();
  const analytics = useResource<Analytics>(scoped('/merchant/analytics?days=30', merchantId), 60000);
  const forecastRes = useResource<Forecast>(scoped('/merchant/forecast', merchantId), 300000);
  const data2 = analytics.data;
  const alerts = useMemo(() => [...(data2?.alerts || []), ...(forecastRes.data?.weather_risk ? [forecastRes.data.weather_risk] : [])], [data2, forecastRes.data]);
  const currency = data.orders[0]?.currency || 'USD';
  const days = useMemo(() => lastDays(DAYS), []);
  const statusRows = useMemo(() => {
    const groups = new Map<string, { status: string; orders: number; revenue: number; trend: number[] }>();
    for (const o of data.orders) {
      const row = groups.get(o.status) || { status: o.status, orders: 0, revenue: 0, trend: days.slice(-7).map(() => 0) };
      row.orders += 1; if (o.payment_status === 'CAPTURED') row.revenue += o.amount_cents;
      const idx = days.slice(-7).findIndex(d => localDateKey(d) === localDateKey(new Date(o.created_at))); if (idx >= 0) row.trend[idx] += 1;
      groups.set(o.status, row);
    }
    return [...groups.values()].sort((a, b) => b.orders - a.orders);
  }, [data.orders, days]);
  const statusCols = useMemo<ColDef<(typeof statusRows)[number]>[]>(() => [
    { field: 'status', headerName: 'Status', flex: 1.2, cellRenderer: ({ value }: { value: string }) => <OrderStatus order={{ status: value }} />, filter: false },
    { field: 'orders', headerName: 'Orders', width: 90, type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', filter: false },
    { field: 'revenue', headerName: 'Captured', flex: 1, cellClass: 'pf-num', headerClass: 'pf-num', valueFormatter: p => cash(p.value, currency), filter: false },
    { field: 'trend', headerName: '7 days', flex: 1.2, sortable: false, filter: false, cellRenderer: 'agSparklineCellRenderer', cellRendererParams: { sparklineOptions: { type: 'area', stroke: '#0057ff', strokeWidth: 2, fill: 'rgba(0,87,255,0.12)', padding: { top: 14, bottom: 14 }, axis: { stroke: 'transparent' }, marker: { enabled: false } } } },
  ], [currency]);

  const recent = useMemo(() => data.orders.slice(0, 8), [data.orders]);
  const recentCols = useMemo<ColDef<Order>[]>(() => [
    { ...orderIdColumn, minWidth: 150, cellRenderer: undefined, cellRendererParams: undefined, valueFormatter: p => p.value ? `${String(p.value).slice(0, 8)}…` : '' },
    { field: 'product_name', headerName: 'Items', flex: 2, minWidth: 180 },
    { headerName: 'Total', field: 'amount_cents', valueFormatter: moneyFormatter, type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 110 },
    { field: 'status', headerName: 'Status', cellRenderer: orderStatusCell, minWidth: 140 },
    { field: 'created_at', headerName: 'Placed', valueFormatter: dateTimeFormatter, minWidth: 150 },
  ], []);

  return <div className="space-y-5 pf-enter">
    <PageHeader title="Overview" description={demo ? 'Sample records. Stock freshness is shown per product; simulated payments move no funds.' : 'Stock, payments and pickup at a glance.'} />
    {data2 && <StoreStrip store={data2.store} />}
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
      <Stat label="Captured revenue" value={cash(data.revenue_cents, currency)} />
      <Stat label="Orders" value={data.order_count} />
      <Stat label="Awaiting pickup" value={data.pending_count} tone={data.pending_count ? 'blue' : undefined} />
      <Stat label="Low stock" value={data.low_stock_count} tone={data.low_stock_count ? 'amber' : undefined} hint={`${LOW_STOCK_AT} or fewer available`} />
      <Stat label="Products" value={data.product_count} />
    </div>
    <ChartsGrid data={data2} loading={analytics.loading} />
    <div className="grid xl:grid-cols-5 gap-5">
      <div className="xl:col-span-2"><AlertsPanel alerts={alerts} loading={analytics.loading} /></div>
      <div className="xl:col-span-3"><ForecastPanel forecast={forecastRes.data} loading={forecastRes.loading} /></div>
    </div>
    <div className="grid lg:grid-cols-2 gap-5"><PrepPanel forecast={forecastRes.data} loading={forecastRes.loading} /><InsightsPanel forecast={forecastRes.data} loading={forecastRes.loading} /></div>
    <EventsPanel forecast={forecastRes.data} />
    <ReservationsToPrepare />
    <div className="grid xl:grid-cols-3 gap-5">
      <Panel className="xl:col-span-2" title="Recent orders" actions={<Link className="pf-link text-sm inline-flex items-center gap-1" to="/merchant/orders">All orders<ArrowRight size={14} /></Link>} flush>
        {recent.length ? <PFGrid height={44 + recent.length * 56 + 2} rowData={recent} columnDefs={recentCols} getRowId={p => p.data.id} suppressCellFocus /> : <Empty title="No orders yet" description="Orders appear here as shoppers reserve and pay." />}
      </Panel>
      <div className="space-y-5">
        <Panel title="Orders by status" description="Count, captured value and 7-day trend" flush><PFGrid height={Math.max(270, 44 + statusRows.length * 56 + 2)} rowData={statusRows} columnDefs={statusCols} rowHeight={56} suppressCellFocus defaultColDef={{ sortable: true, resizable: false, flex: 1, minWidth: 70 }} getRowId={p => p.data.status} overlayNoRowsTemplate="No orders yet" /></Panel>
        {demo && <PosBridge merchantId={merchantId} />}
      </div>
    </div>
  </div>;
}

function PosBridge({ merchantId }: { merchantId: string }) {
  const pos = useResource<PosState>(scoped('/pos-simulator/state', merchantId), 10000);
  const completed = pos.data?.receipts.filter(receipt => receipt.status === 'COMPLETED') || [];
  return <section className="pf-card p-5 bg-navy !border-navy text-white">
    <div className="flex items-center gap-2 text-white/70 text-xs font-semibold"><MonitorSmartphone size={15} />POS add-on <Chip kind="blue">Simulation</Chip></div>
    <h2 className="font-display text-xl font-semibold mt-3 tracking-tight">Your counter, connected</h2>
    <p className="text-sm text-white/65 mt-1.5">{pos.data?.connected ? `${completed.length} simulated counter sales · ${pos.data.pending_count} queued stock updates · ${pos.data.conflict_count} conflicts` : 'Try a register that syncs catalog, stock and online orders with PayFound.'}</p>
    <Link className="pf-btn sm mt-4 !bg-white !text-ink" to="/pos/sync">{pos.data?.connected ? 'View POS connection' : 'Explore the POS simulator'}<ArrowRight size={14} /></Link>
  </section>;
}
