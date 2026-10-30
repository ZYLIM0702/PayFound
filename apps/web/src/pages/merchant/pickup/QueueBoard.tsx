import { useMemo, useRef } from 'react';
import type { AgGridReact, CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { PFGrid } from '../../../components/Tables';
import { orderStatusCell, paymentCell, shortId } from '../../../components/grid-cells';
import { OrderActions } from '../OrderActions';
import type { Order } from '../../../lib/api';

type Ctx = { busy: boolean; run: (path: string, body?: object) => Promise<void>; requestRefund: (o: Order) => void };
const slotStart = (o: Order) => o.pickup_window?.start_at || '';

/** Today's pickups in collection order, with the existing fulfilment actions inline. */
export function QueueBoard({ orders, tz, busy, run, requestRefund }: { orders: Order[]; tz: string; busy: boolean; run: Ctx['run']; requestRefund: Ctx['requestRefund'] }) {
  const grid = useRef<AgGridReact<Order>>(null);
  const context = useMemo<Ctx>(() => ({ busy, run, requestRefund }), [busy, run, requestRefund]);
  const cols = useMemo<ColDef<Order>[]>(() => [
    { colId: 'time', headerName: 'Pickup', valueGetter: p => slotStart(p.data!), sort: 'asc', minWidth: 120, flex: 0.8, valueFormatter: p => p.value ? new Date(p.value).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', timeZone: tz }) : '', cellClass: 'font-semibold tabular' },
    { field: 'buyer_name', headerName: 'Customer', minWidth: 140, flex: 1.2 },
    { field: 'product_name', headerName: 'Items', minWidth: 180, flex: 2 },
    { field: 'status', headerName: 'Status', cellRenderer: orderStatusCell, minWidth: 130, flex: 1 },
    { field: 'payment_status', headerName: 'Payment', cellRenderer: paymentCell, minWidth: 120, flex: 1 },
    { field: 'id', headerName: 'Order', minWidth: 130, flex: 1, valueFormatter: p => p.value ? shortId(p.value) : '' },
    { headerName: 'Actions', colId: 'actions', pinned: 'right', width: 150, sortable: false, filter: false, cellRenderer: ({ data, context: c }: CustomCellRendererProps<Order, unknown, Ctx>) => data ? <OrderActions order={data} busy={c.busy} run={c.run} requestRefund={c.requestRefund} showView /> : null },
  ], [tz]);
  return <PFGrid<Order> gridRef={grid} height="calc(100dvh - 330px)" className="min-h-[420px]" rowData={orders} columnDefs={cols} context={context} getRowId={p => p.data.id}
    rowClassRules={{ 'pf-row-attention': p => p.data?.status === 'READY' }} statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }] }} overlayNoRowsTemplate="No pickups scheduled for this day" />;
}
