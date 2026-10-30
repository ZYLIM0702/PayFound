import { useMemo, useRef, useState } from 'react';
import { Download, Plus, Search } from 'lucide-react';
import type { AgGridReact, CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef, ValueSetterParams } from 'ag-grid-community';
import { cash, messageOf, patch, post, scoped, type MerchantLocation, type Product } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, ErrorLine, Field, PageHeader, Panel, Sheet } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';
import { LOW_STOCK_AT, useMerchant } from './context';
import { StockCountSheet } from './StockCountSheet';
import { LiveMonitor } from './LiveMonitor';
import { OnlinePriceCheck } from './OnlinePriceCheck';

const stockBar = (p: CustomCellRendererProps<Product>) => {
  const q = p.data?.available_quantity ?? 0;
  const max = Math.max(20, ...(p.api.getRenderedNodes().map(n => n.data?.quantity ?? 0)));
  const tone = q <= 0 ? 'var(--pf-red)' : q <= LOW_STOCK_AT ? 'var(--pf-amber)' : 'var(--pf-ink)';
  return <div className="flex items-center gap-3 w-full"><div className="flex-1 h-1.5 rounded-full bg-sunk overflow-hidden"><div className="h-full rounded-full" style={{ width: `${Math.min(100, (q / max) * 100)}%`, background: tone }} /></div><span className="tabular text-[13px] w-8 text-right font-semibold">{q}</span></div>;
};

export function InventoryPage() {
  const { dashboard, merchantId, refresh, flash, fail } = useMerchant();
  const grid = useRef<AgGridReact<Product>>(null);
  const [rows, setRows] = useState<Product[] | null>(null);
  const [adding, setAdding] = useState(false);
  const [tab, setTab] = useState<'stock' | 'count' | 'live'>('stock');
  const [search, setSearch] = useState('');
  const source = dashboard.products;
  const data = rows && rows.length === source.length ? rows : source;
  // keep local optimistic copy in sync when the server copy changes
  const [seen, setSeen] = useState(source);
  if (seen !== source) { setSeen(source); setRows(null); }

  const columns = useMemo<ColDef<Product>[]>(() => [
    { field: 'name', headerName: 'Product', flex: 2, minWidth: 220, pinned: 'left', checkboxSelection: false, floatingFilter: true },
    { field: 'location_name', headerName: 'Branch', minWidth: 150, filter: 'agSetColumnFilter', floatingFilter: true, valueFormatter: p => p.value || '—' },
    { field: 'category', headerName: 'Category', minWidth: 130, filter: 'agSetColumnFilter', enableRowGroup: true, hide: true },
    { field: 'sku', headerName: 'SKU', minWidth: 120 },
    { field: 'price_cents', headerName: 'Price', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 110, valueFormatter: p => p.data?.currency && p.value != null ? cash(p.value, p.data.currency) : '', filter: 'agNumberColumnFilter' },
    { field: 'quantity', headerName: 'Counted', type: 'rightAligned', headerClass: 'pf-num', minWidth: 130, editable: true, filter: 'agNumberColumnFilter', aggFunc: 'sum', cellEditor: 'agNumberCellEditor', cellEditorParams: { min: 0, max: 100000, precision: 0, showStepperButtons: true },
      cellClass: 'pf-num !bg-accent-soft/40 cursor-text', headerTooltip: 'Double-click to record a physically verified count', tooltipValueGetter: () => 'Double-click to record a count',
      valueSetter: (p: ValueSetterParams<Product>) => { const n = Number(p.newValue); if (!Number.isInteger(n) || n < 0 || n > 100000) return false; p.data.quantity = n; return true; } },
    { field: 'available_quantity', headerName: 'Available', minWidth: 190, cellRenderer: stockBar, filter: 'agNumberColumnFilter' },
    { field: 'freshness', headerName: 'Freshness', minWidth: 130, filter: 'agSetColumnFilter', floatingFilter: true, cellRenderer: (p: CustomCellRendererProps<Product>) => p.value ? <Chip kind={p.value === 'fresh' ? 'green' : 'amber'} dot>{p.value === 'fresh' ? 'Fresh' : 'Stale'}</Chip> : null },
    { field: 'stock_updated_at', headerName: 'Counted at', minWidth: 150, valueFormatter: p => p.value ? new Date(p.value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '' },
  ], []);

  const totals = useMemo(() => [{ name: `${data.length} products`, quantity: data.reduce((n, p) => n + p.quantity, 0), available_quantity: data.reduce((n, p) => n + p.available_quantity, 0) } as Partial<Product>] as Product[], [data]);

  async function onCellEditRequest(e: { data: Product; newValue: unknown; oldValue: unknown; node: { setDataValue: (k: string, v: unknown) => void } }) {
    const next = Number(e.newValue);
    if (!Number.isInteger(next) || next < 0 || next > 100000) { fail('Enter a whole number between 0 and 100,000.'); return; }
    const previous = e.data.quantity;
    if (next === previous) return;
    const before = data;
    setRows(data.map(p => p.id === e.data.id ? { ...p, quantity: next, available_quantity: p.available_quantity + (next - previous) } : p)); // optimistic
    try { await patch(`/merchant/products/${e.data.id}/stock`, { quantity: next }); flash(`${e.data.name}: count recorded (${next}).`); await refresh(); }
    catch (issue) { setRows(before); fail(messageOf(issue)); }
  }

  return <div className="space-y-5 pf-enter">
    <PageHeader title="Inventory" description="Double-click a Counted cell to record a physically verified count. Stock freshness is shown per product." right={<>
      <button className="pf-btn sm outline" onClick={() => grid.current?.api.exportDataAsCsv({ fileName: 'payfound-inventory.csv' })}><Download size={14} />CSV</button>
      <button className="pf-btn sm outline" onClick={() => grid.current?.api.exportDataAsExcel({ fileName: 'payfound-inventory.xlsx' })}><Download size={14} />Excel</button>
      <button className="pf-btn sm" onClick={() => setAdding(true)}><Plus size={15} />Add product</button></>} />
    <div className="pf-tabs" role="tablist" aria-label="Inventory views">{([['stock', 'Stock levels'], ['count', 'Count sheet'], ['live', 'Live monitor']] as const).map(([id, label]) => <button key={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)} data-testid={`inventory-tab-${id}`}>{label}</button>)}</div>
    {tab === 'count' && <Panel flush><StockCountSheet /></Panel>}
    {tab === 'live' && <Panel flush><LiveMonitor /></Panel>}
    {tab === 'stock' && <Panel flush>
      <div className="flex flex-wrap items-center gap-3 px-5 py-3.5 border-b border-line"><div className="relative flex-1 min-w-[220px] max-w-md"><Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" /><input className="pf-input sm !pl-10 !rounded-full" type="search" placeholder="Search products, SKU, branch" aria-label="Search inventory" value={search} onChange={e => { setSearch(e.target.value); grid.current?.api.setGridOption('quickFilterText', e.target.value); }} /></div><span className="text-xs text-muted">Online and Channel3 offers never prove local stock.</span></div>
      <PFGrid<Product> gridRef={grid} height="calc(100dvh - 330px)" className="min-h-[460px]" rowData={data} columnDefs={columns} getRowId={p => p.data.id} readOnlyEdit onCellEditRequest={onCellEditRequest} singleClickEdit={false}
        rowClassRules={{ 'pf-row-low': p => (p.data?.available_quantity ?? 99) <= LOW_STOCK_AT }} pinnedBottomRowData={totals} suppressAggFuncInHeader
        sideBar={{ toolPanels: ['columns', 'filters'], hiddenByDefault: true }} cellSelection
        statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }, { statusPanel: 'agAggregationComponent', align: 'right', statusPanelParams: { aggFuncs: ['sum', 'avg'] } }] }}
        pagination paginationPageSize={25} paginationPageSizeSelector={[25, 50, 100]} overlayNoRowsTemplate="No products yet" />
    </Panel>}
    <OnlinePriceCheck merchantId={merchantId} currency={source[0]?.currency} />
    <AddProduct open={adding} onClose={() => setAdding(false)} merchantId={merchantId} onSaved={async () => { setAdding(false); flash('Product added.'); await refresh(); }} />
  </div>;
}

function AddProduct({ open, onClose, merchantId, onSaved }: { open: boolean; onClose: () => void; merchantId: string; onSaved: () => Promise<void> }) {
  const locations = useResource<MerchantLocation[]>(scoped('/merchant/locations', merchantId));
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  return <Sheet open={open} onClose={onClose} title="Add a product" description="Merchant-managed catalog entry with a verified count." footer={<><button type="button" className="pf-btn outline" onClick={onClose}>Cancel</button><button form="add-product" className="pf-btn" disabled={busy}>{busy ? 'Adding…' : 'Add product'}</button></>}>
    <form id="add-product" className="grid gap-4" onSubmit={async e => { e.preventDefault(); const values = new FormData(e.currentTarget); setBusy(true); setError(''); try { await post(scoped('/merchant/products', merchantId), { name: values.get('name'), sku: values.get('sku'), description: values.get('description'), category: values.get('category'), location_id: values.get('location_id'), price_cents: Math.round(Number(values.get('price')) * 100), currency: values.get('currency'), quantity: Number(values.get('quantity')) }); await onSaved(); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); } }}>
      <ErrorLine message={error} />
      <Field label="Product name" name="name" required /><div className="grid grid-cols-2 gap-4"><Field label="SKU" name="sku" required /><Field label="Category" name="category" defaultValue="Retail" /></div>
      <Field label="Description" name="description" />
      <div className="grid grid-cols-2 gap-4"><Field label="Price" name="price" type="number" min="0.01" step="0.01" required /><Field label="Currency" name="currency" defaultValue="USD" pattern="[A-Z]{3}" required /></div>
      <div className="grid grid-cols-2 gap-4"><Field label="On-hand count" name="quantity" type="number" min={0} defaultValue={0} required /><div className="pf-field"><label htmlFor="loc">Branch</label><select id="loc" name="location_id" className="pf-select" required>{locations.data?.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}</select></div></div>
    </form>
  </Sheet>;
}
