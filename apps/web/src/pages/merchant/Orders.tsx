import { useCallback, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Download, Search } from 'lucide-react';
import type { AgGridReact, CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef, RowClickedEvent } from 'ag-grid-community';
import { cash, orderItems, type Order } from '../../lib/api';
import { Chip, OrderStatus, PageHeader, Panel, Sheet, statusLabel } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';
import { dateTimeFormatter, orderIdColumn, orderRowClass, orderStatusCell, paymentCell, shortId, statusSetFilter } from '../../components/grid-cells';
import { FULFILMENT_NEXT, useMerchant } from './context';
import { OrderActions } from './OrderActions';
import { OrderMasterDetail } from './OrderMasterDetail';
import { SalesPivot } from './SalesPivot';

type Segment = 'all' | 'action' | 'active' | 'done';
const DONE = ['COLLECTED', 'REFUNDED', 'CANCELLED', 'EXPIRED'];
const needsAction = (o: Order) => (o.confirmation_status === 'PENDING' && o.status === 'RESERVED') || (Boolean(FULFILMENT_NEXT[o.status]) && o.payment_status === 'CAPTURED');
const inSegment = (o: Order, s: Segment) => s === 'all' || (s === 'action' ? needsAction(o) : s === 'done' ? DONE.includes(o.status) : !DONE.includes(o.status));
const pickupOf = (o: Order) => o.pickup_window || o.pickup_slot || o.pickup || null;
type GridContext = { busy: boolean; run: (path: string, body?: object) => Promise<void>; requestRefund: (order: Order) => void };

export function OrdersPage() {
  const { dashboard, busy, run, requestRefund } = useMerchant();
  const grid = useRef<AgGridReact<Order>>(null);
  const [segment, setSegment] = useState<Segment>('all');
  const segmentRef = useRef<Segment>('all');
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState<'orders' | 'sales'>('orders');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const orders = useMemo(() => dashboard.orders.filter(o => !o.id.startsWith('seed-')), [dashboard.orders]);
  const counts = useMemo(() => ({ all: orders.length, action: orders.filter(o => inSegment(o, 'action')).length, active: orders.filter(o => inSegment(o, 'active')).length, done: orders.filter(o => inSegment(o, 'done')).length }), [orders]);
  const selected = orders.find(o => o.id === selectedId) || null;
  const context = useMemo<GridContext>(() => ({ busy, run, requestRefund }), [busy, run, requestRefund]);

  const columns = useMemo<ColDef<Order>[]>(() => [
    { ...orderIdColumn, flex: 1.1, minWidth: 150 },
    { field: 'buyer_name', headerName: 'Customer', flex: 1.3, minWidth: 140, tooltipField: 'buyer_name', floatingFilter: true, valueFormatter: p => p.value || 'Guest' },
    { field: 'product_name', headerName: 'Items', flex: 2, minWidth: 180, tooltipValueGetter: p => p.data?.product_name, valueGetter: p => p.data ? (p.data.items?.length ?? 0) > 1 ? `${p.data.product_name} + ${(p.data.items?.length ?? 1) - 1} more` : p.data.product_name : '' },
    { headerName: 'Total', colId: 'total', valueGetter: p => p.data ? p.data.amount_cents / 100 : 0, valueFormatter: p => p.data ? cash(p.data.amount_cents, p.data.currency) : '', filter: 'agNumberColumnFilter', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', flex: 0.8, minWidth: 110, enableValue: true, aggFunc: 'sum', chartDataType: 'series' },
    { field: 'payment_status', headerName: 'Payment', cellRenderer: paymentCell, ...statusSetFilter, flex: 1, minWidth: 130 },
    { field: 'status', headerName: 'Fulfilment', cellRenderer: orderStatusCell, ...statusSetFilter, flex: 1, minWidth: 130, chartDataType: 'category' },
    { headerName: 'Pickup', colId: 'pickup', valueGetter: p => p.data ? pickupOf(p.data)?.start_at ?? null : null, valueFormatter: dateTimeFormatter, filter: 'agDateColumnFilter', flex: 1.1, minWidth: 140, hide: true },
    { field: 'created_at', headerName: 'Placed', valueFormatter: dateTimeFormatter, filter: 'agDateColumnFilter', sort: 'desc', flex: 1.2, minWidth: 150 },
    { headerName: 'Actions', colId: 'actions', pinned: 'right', width: 300, minWidth: 260, sortable: false, filter: false, suppressColumnsToolPanel: true, cellRenderer: ({ data, context }: CustomCellRendererProps<Order, unknown, GridContext>) => data ? <OrderActions order={data} busy={context.busy} run={context.run} requestRefund={context.requestRefund} showView /> : null },
  ], []);

  const onRowClicked = useCallback((e: RowClickedEvent<Order>) => {
    const target = e.event?.target as HTMLElement | undefined;
    if (!e.data || target?.closest('button, a, .ag-group-expanded, .ag-group-contracted, .ag-cell[col-id="actions"]')) return;
    setSelectedId(e.data.id);
  }, []);
  const pick = (value: Segment) => { setSegment(value); segmentRef.current = value; grid.current?.api.onFilterChanged(); };
  const segments: [Segment, string][] = [['all', 'All'], ['action', 'Needs action'], ['active', 'In progress'], ['done', 'Completed']];

  return <div className="space-y-5 pf-enter">
    <PageHeader title="Orders" description="Confirm physical stock before payment when a source cannot hold it. Fulfilment requires a verified capture." right={<>
      <button className="pf-btn sm outline" onClick={() => grid.current?.api.exportDataAsCsv({ fileName: 'payfound-orders.csv' })}><Download size={14} />CSV</button>
      <button className="pf-btn sm outline" onClick={() => grid.current?.api.exportDataAsExcel({ fileName: 'payfound-orders.xlsx' })}><Download size={14} />Excel</button></>} />
    <div className="pf-tabs" role="tablist" aria-label="Order views">{([['orders', 'Orders'], ['sales', 'Sales report']] as const).map(([id, label]) => <button key={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)} data-testid={`orders-tab-${id}`}>{label}</button>)}</div>
    {tab === 'sales' && <Panel flush><SalesPivot orders={orders} /></Panel>}
    {tab === 'orders' && <Panel flush>
      <div className="flex flex-wrap items-center gap-3 px-5 py-3.5 border-b border-line">
        <div className="relative flex-1 min-w-[220px] max-w-md"><Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" /><input className="pf-input sm !pl-10 !rounded-full" type="search" placeholder="Search orders, customers, items" aria-label="Search orders" value={search} onChange={e => { setSearch(e.target.value); grid.current?.api.setGridOption('quickFilterText', e.target.value); }} /></div>
        <div className="pf-segmented" role="group" aria-label="Order view">{segments.map(([value, label]) => <button key={value} aria-pressed={segment === value} onClick={() => pick(value)}>{label}<span className="ml-1.5 text-subtle tabular">{counts[value]}</span></button>)}</div>
      </div>
      <PFGrid<Order> gridRef={grid} height="calc(100dvh - 330px)" className="min-h-[460px]" rowData={orders} columnDefs={columns} defaultColDef={{ flex: 1 }} context={context} getRowId={p => p.data.id}
        masterDetail detailCellRenderer={OrderMasterDetail} detailRowAutoHeight rowClassRules={{ 'pf-row-attention': p => Boolean(orderRowClass(p.data)) }}
        onRowClicked={onRowClicked} cellSelection enableCharts sideBar={{ toolPanels: ['columns', 'filters'], hiddenByDefault: true }}
        isExternalFilterPresent={() => segmentRef.current !== 'all'} doesExternalFilterPass={node => Boolean(node.data) && inSegment(node.data as Order, segmentRef.current)}
        statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }, { statusPanel: 'agAggregationComponent', align: 'right', statusPanelParams: { aggFuncs: ['count', 'sum'] } }] }}
        pagination paginationPageSize={25} paginationPageSizeSelector={[25, 50, 100]} overlayNoRowsTemplate="No orders match" />
    </Panel>}
    <p className="text-xs text-muted">Click a row for details. Expand a row to see its items. Select cells to total them in the status bar, or right-click a selection to chart it.</p>
    <Sheet open={Boolean(selected)} onClose={() => setSelectedId(null)} title={selected ? `Order ${shortId(selected.id)}` : 'Order'} description={selected ? `${selected.buyer_name || 'Customer'} · ${new Date(selected.created_at).toLocaleString()}` : undefined}
      footer={selected && <><Link className="pf-btn outline" to={`/checkout/${selected.id}`}>Open receipt</Link></>}>
      {selected && <OrderDetail order={selected} busy={busy} run={run} requestRefund={o => { setSelectedId(null); requestRefund(o); }} />}
    </Sheet>
  </div>;
}

function OrderDetail({ order, busy, run, requestRefund }: { order: Order; busy: boolean; run: GridContext['run']; requestRefund: (o: Order) => void }) {
  const pickup = pickupOf(order);
  const rows: [string, React.ReactNode][] = [
    ['Fulfilment', <OrderStatus key="s" order={order} />], ['Payment', <Chip key="p" kind={order.payment_status === 'CAPTURED' ? 'green' : 'amber'} dot>{statusLabel(order.payment_status)}</Chip>],
    ['Stock confirmation', order.confirmation_status ? statusLabel(order.confirmation_status) : '—'], ['Pickup', pickup ? `${new Date(pickup.start_at).toLocaleString([], { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}` : 'Not scheduled'],
    ['Store', order.merchant_name], ['Order ID', <span key="i" className="break-all text-xs font-mono">{order.id}</span>],
  ];
  return <div className="space-y-6">
    <dl className="divide-y divide-line">{rows.map(([k, v]) => <div key={k} className="flex items-center justify-between gap-4 py-3 text-sm"><dt className="text-muted">{k}</dt><dd className="font-medium text-right">{v}</dd></div>)}</dl>
    <div><h3 className="pf-subtitle mb-3">Items</h3><ul className="divide-y divide-line border border-line rounded-[var(--pf-r-md)]">{orderItems(order).map((item, i) => <li key={`${item.product_id}-${i}`} className="flex items-center justify-between gap-3 px-4 py-3 text-sm"><span className="min-w-0 truncate">{item.product_name || item.name || item.product_id}<span className="text-muted"> × {item.quantity}</span></span>{(item.amount_cents ?? item.unit_price_cents ?? item.price_cents) != null && <span className="tabular font-medium">{cash((item.amount_cents ?? (item.unit_price_cents ?? item.price_cents ?? 0) * item.quantity), order.currency)}</span>}</li>)}</ul>
      <div className="flex justify-between mt-3 text-sm"><span className="text-muted">Total</span><strong className="tabular font-display text-lg">{cash(order.amount_cents, order.currency)}</strong></div></div>
    <div><h3 className="pf-subtitle mb-3">Actions</h3><OrderActions order={order} busy={busy} run={run} requestRefund={requestRefund} />{!orderHasActions(order) && <p className="text-sm text-muted">No actions available for this order.</p>}</div>
  </div>;
}
const orderHasActions = (o: Order) => (o.confirmation_status === 'PENDING' && o.status === 'RESERVED') || (Boolean(FULFILMENT_NEXT[o.status]) && o.payment_status === 'CAPTURED') || (o.payment_status === 'CAPTURED' && o.status !== 'COLLECTED');
