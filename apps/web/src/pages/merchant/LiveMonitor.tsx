import { useEffect, useMemo, useState } from 'react';
import type { ColDef } from 'ag-grid-community';
import { cash, type Product } from '../../lib/api';
import { PFGrid } from '../../components/Tables';
import { LOW_STOCK_AT, useMerchant } from './context';

/** Live price and stock monitor. The workspace re-fetches every 15 s; cells flash when a value changes (sale, POS sync, count). */
export function LiveMonitor() {
  const { dashboard } = useMerchant();
  const [seen, setSeen] = useState(() => Date.now());
  const [now, setNow] = useState(() => Date.now());
  const [data, setData] = useState(dashboard.products);
  if (data !== dashboard.products) { setData(dashboard.products); setSeen(Date.now()); }
  useEffect(() => { const t = window.setInterval(() => setNow(Date.now()), 1000); return () => window.clearInterval(t); }, []);
  const cols = useMemo<ColDef<Product>[]>(() => [
    { field: 'name', headerName: 'Product', flex: 2, minWidth: 200, pinned: 'left', floatingFilter: true },
    { field: 'location_name', headerName: 'Branch', minWidth: 150, filter: 'agSetColumnFilter', valueFormatter: p => p.value || '—' },
    { field: 'price_cents', headerName: 'Price', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 110, enableCellChangeFlash: true, valueFormatter: p => p.data ? cash(p.value, p.data.currency) : '' },
    { field: 'quantity', headerName: 'On hand', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 110, enableCellChangeFlash: true },
    { field: 'available_quantity', headerName: 'Available', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 120, cellRenderer: 'agAnimateShowChangeCellRenderer', filter: 'agNumberColumnFilter' },
    { field: 'freshness', headerName: 'Freshness', minWidth: 120, enableCellChangeFlash: true, filter: 'agSetColumnFilter', valueFormatter: p => p.value === 'fresh' ? 'Fresh' : 'Stale' },
    { field: 'stock_updated_at', headerName: 'Stock updated', minWidth: 150, enableCellChangeFlash: true, valueFormatter: p => p.value ? new Date(p.value).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' }) : '' },
  ], []);
  const ago = Math.max(0, Math.round((now - seen) / 1000));
  return <div data-testid="live-monitor">
    <div className="flex flex-wrap items-center gap-3 px-5 py-3.5 border-b border-line text-[13px]">
      <span className="inline-flex items-center gap-2 font-semibold"><i className="pf-live-dot" aria-hidden />Live · refreshes every 15 s</span>
      <span className="text-muted tabular">Last refresh {ago}s ago</span>
      <span className="text-muted">Changed cells flash. Record a count or sell an item at the POS and watch the row update.</span>
    </div>
    <PFGrid<Product> height="calc(100dvh - 330px)" className="min-h-[460px]" rowData={data} columnDefs={cols} getRowId={p => p.data.id} animateRows={false}
      rowClassRules={{ 'pf-row-low': p => (p.data?.available_quantity ?? 99) <= LOW_STOCK_AT }} statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }] }} pagination paginationPageSize={50} />
  </div>;
}
