import { useMemo, useRef, useState } from 'react';
import { Download } from 'lucide-react';
import type { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { cash, orderItems, type Order } from '../../lib/api';
import { PFGrid } from '../../components/Tables';
import { useMerchant } from './context';

type Line = { id: string; category: string; branch: string; product: string; qty: number; amount: number; day: string; currency: string };

/** Sales by category x branch from captured orders (sums recorded line amounts; no new money logic). Toggle pivot to spread branches across columns. */
export function SalesPivot({ orders }: { orders: Order[] }) {
  const { dashboard } = useMerchant();
  const grid = useRef<AgGridReact<Line>>(null);
  const [pivot, setPivot] = useState(true);
  const categoryOf = useMemo(() => new Map(dashboard.products.map(p => [p.id, p.category])), [dashboard.products]);
  const lines = useMemo<Line[]>(() => orders.filter(o => o.payment_status === 'CAPTURED' && !['CANCELLED', 'REFUNDED'].includes(o.status)).flatMap(o => orderItems(o).map((it, i) => ({
    id: `${o.id}-${i}`, category: categoryOf.get(it.product_id) || 'Other', branch: it.location_name || (o as Order & { location_name?: string | null }).location_name || 'Main branch', product: it.product_name || it.name || it.product_id, qty: it.quantity,
    amount: (it.amount_cents ?? (it.unit_price_cents ?? it.price_cents ?? 0) * it.quantity) / 100, day: o.created_at.slice(0, 10), currency: o.currency }))), [orders, categoryOf]);
  const currencies = useMemo(() => [...new Set(lines.map(l => l.currency))], [lines]);
  const currency = currencies[0] || 'USD';
  const cols = useMemo<ColDef<Line>[]>(() => [
    { field: 'category', headerName: 'Category', rowGroup: true, enableRowGroup: true, enablePivot: true, hide: true },
    { field: 'branch', headerName: 'Branch', pivot: pivot, enablePivot: true, enableRowGroup: true, hide: !pivot },
    { field: 'product', headerName: 'Product', enableRowGroup: true, minWidth: 180 },
    { field: 'day', headerName: 'Day', enableRowGroup: true, enablePivot: true, minWidth: 120 },
    { field: 'qty', headerName: 'Units', type: 'rightAligned', aggFunc: 'sum', enableValue: true, cellClass: 'pf-num', headerClass: 'pf-num', hide: pivot },
    { field: 'amount', headerName: 'Sales', type: 'rightAligned', aggFunc: 'sum', enableValue: true, cellClass: 'pf-num', headerClass: 'pf-num', valueFormatter: p => p.value == null ? '' : cash(Math.round(p.value * 100), currency), minWidth: 130, chartDataType: 'series' },
  ], [pivot, currency]);
  return <div data-testid="sales-pivot">
    <div className="flex flex-wrap items-center gap-3 px-5 py-3.5 border-b border-line">
      <div className="pf-segmented" role="group" aria-label="Report layout"><button aria-pressed={pivot} onClick={() => setPivot(true)}>Pivot: category × branch</button><button aria-pressed={!pivot} onClick={() => setPivot(false)}>Grouped by category</button></div>
      <span className="text-[13px] text-muted">Captured orders only{currencies.length > 1 ? ` · mixed currencies (${currencies.join(', ')}): filter by currency before comparing` : ''}. Drag columns into the side panel to regroup.</span>
      <button className="pf-btn sm outline ml-auto" onClick={() => grid.current?.api.exportDataAsExcel({ fileName: 'payfound-sales-report.xlsx' })}><Download size={14} />Excel</button>
    </div>
    <PFGrid<Line> key={pivot ? 'pivot' : 'group'} gridRef={grid} height="calc(100dvh - 330px)" className="min-h-[460px]" rowData={lines} columnDefs={cols} getRowId={p => p.data.id}
      pivotMode={pivot} autoGroupColumnDef={{ headerName: 'Category', minWidth: 200, pinned: 'left' }} groupDefaultExpanded={1} grandTotalRow="bottom" pivotRowTotals="after" suppressAggFuncInHeader
      defaultColDef={{ flex: 1, minWidth: 110 }} sideBar={{ toolPanels: ['columns', 'filters'], hiddenByDefault: false, defaultToolPanel: '' }} cellSelection enableCharts
      statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }, { statusPanel: 'agAggregationComponent', align: 'right' }] }} overlayNoRowsTemplate="No captured orders yet" />
  </div>;
}
