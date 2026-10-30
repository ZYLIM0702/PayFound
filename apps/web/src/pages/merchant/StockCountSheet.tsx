import { useMemo, useRef, useState } from 'react';
import { ClipboardCheck, ListRestart } from 'lucide-react';
import type { AgGridReact, CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef, ValueSetterParams } from 'ag-grid-community';
import { messageOf, patch, type Product } from '../../lib/api';
import { Chip, ConfirmDialog } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';
import { useMerchant } from './context';

type Row = Product & { counted: number | null };
const GAP_MS = 350; // rate limit: one stock write at a time, spaced, so a big count never floods the API

const varianceCell = (p: CustomCellRendererProps<Row>) => {
  if (!p.data || p.data.counted === null) return <span className="text-subtle">Not counted</span>;
  const v = p.data.counted - p.data.quantity;
  return <Chip kind={v === 0 ? 'green' : v < 0 ? 'red' : 'amber'} dot>{v === 0 ? 'Match' : v > 0 ? `+${v} over` : `${v} short`}</Chip>;
};

/** Cycle-count sheet: type what is physically on the shelf, see the variance, then apply the counts through the existing stock endpoint. */
export function StockCountSheet() {
  const { dashboard, flash, fail, refresh } = useMerchant();
  const grid = useRef<AgGridReact<Row>>(null);
  const branches = useMemo(() => [...new Set(dashboard.products.map(p => p.location_name || 'Unassigned'))].sort(), [dashboard.products]);
  const [branch, setBranch] = useState('');
  const active = branch || branches[0] || '';
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [confirm, setConfirm] = useState(false);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);
  const rows = useMemo<Row[]>(() => dashboard.products.filter(p => p.active !== false && (p.location_name || 'Unassigned') === active).map(p => ({ ...p, counted: counts[p.id] ?? null })), [dashboard.products, active, counts]);
  const pending = rows.filter(r => r.counted !== null && r.counted !== r.quantity);
  const short = pending.filter(r => r.counted! < r.quantity).reduce((n, r) => n + (r.quantity - r.counted!), 0);
  const over = pending.filter(r => r.counted! > r.quantity).reduce((n, r) => n + (r.counted! - r.quantity), 0);

  const cols = useMemo<ColDef<Row>[]>(() => [
    { field: 'name', headerName: 'Product', flex: 2, minWidth: 200, pinned: 'left', floatingFilter: true },
    { field: 'sku', headerName: 'SKU', minWidth: 110 },
    { field: 'quantity', headerName: 'Expected', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 110, aggFunc: 'sum' },
    { field: 'counted', headerName: 'Counted', type: 'rightAligned', headerClass: 'pf-num', minWidth: 130, editable: true, cellEditor: 'agNumberCellEditor', cellEditorParams: { min: 0, max: 100000, precision: 0, showStepperButtons: true },
      cellClass: 'pf-num !bg-accent-soft/40 cursor-text', headerTooltip: 'Double-click, type the physical count and press Enter', valueFormatter: p => p.value === null || p.value === undefined ? 'Enter count' : String(p.value),
      valueSetter: (p: ValueSetterParams<Row>) => { const text = String(p.newValue ?? '').trim(); if (!text) { setCounts(c => { const n = { ...c }; delete n[p.data.id]; return n; }); return true; } const n = Number(text); if (!Number.isInteger(n) || n < 0 || n > 100000) return false; setCounts(c => ({ ...c, [p.data.id]: n })); return true; } },
    { colId: 'variance', headerName: 'Variance', minWidth: 150, valueGetter: p => p.data && p.data.counted !== null ? p.data.counted - p.data.quantity : null, cellRenderer: varianceCell, filter: 'agNumberColumnFilter', type: 'rightAligned', headerClass: 'pf-num', cellClass: 'justify-end' },
  ], []);

  async function apply() {
    setConfirm(false);
    const todo = pending.map(r => ({ id: r.id, name: r.name, qty: r.counted! }));
    setProgress({ done: 0, total: todo.length });
    let done = 0;
    for (const item of todo) {
      try { await patch(`/merchant/products/${item.id}/stock`, { quantity: item.qty }); } catch (issue) { fail(`${item.name}: ${messageOf(issue)} Remaining counts were not applied.`); break; }
      done++; setProgress({ done, total: todo.length });
      setCounts(c => { const n = { ...c }; delete n[item.id]; return n; });
      await new Promise(resolve => setTimeout(resolve, GAP_MS));
    }
    setProgress(null);
    if (done) flash(`${done} stock count${done === 1 ? '' : 's'} applied.`);
    await refresh();
  }

  return <div data-testid="count-sheet">
    <div className="flex flex-wrap items-center gap-3 px-5 py-3.5 border-b border-line">
      <select className="pf-select sm !w-auto min-w-[200px]" aria-label="Branch to count" value={active} onChange={e => { setBranch(e.target.value); setCounts({}); }}>{branches.map(b => <option key={b} value={b}>{b}</option>)}</select>
      <button className="pf-btn sm outline" onClick={() => setCounts(Object.fromEntries(rows.map(r => [r.id, r.quantity])))} title="Pre-fill every counted cell with the expected figure, then correct the exceptions"><ListRestart size={14} />Start from expected</button>
      <button className="pf-btn sm outline" onClick={() => setCounts({})} disabled={!Object.keys(counts).length}>Clear</button>
      <span className="text-[13px] text-muted tabular">{pending.length} to apply · {short} short · {over} over</span>
      <button className="pf-btn sm accent ml-auto" disabled={!pending.length || progress !== null} onClick={() => setConfirm(true)} data-testid="apply-counts"><ClipboardCheck size={15} />{progress ? `Applying ${progress.done}/${progress.total}…` : `Apply ${pending.length} count${pending.length === 1 ? '' : 's'}`}</button>
    </div>
    <PFGrid<Row> gridRef={grid} height="calc(100dvh - 330px)" className="min-h-[460px]" rowData={rows} columnDefs={cols} getRowId={p => p.data.id} singleClickEdit={false} stopEditingWhenCellsLoseFocus
      rowClassRules={{ 'pf-row-low': p => p.data?.counted != null && p.data.counted < p.data.quantity, 'pf-row-attention': p => p.data?.counted != null && p.data.counted > p.data.quantity }}
      statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }, { statusPanel: 'agAggregationComponent', align: 'right' }] }} cellSelection pagination paginationPageSize={50} overlayNoRowsTemplate="No products at this branch" />
    <ConfirmDialog open={confirm} title="Apply physical counts?" description={`${pending.length} product${pending.length === 1 ? '' : 's'} will be updated to the counted quantity (${short} short, ${over} over). Each update uses the normal stock endpoint, one at a time. Online and Channel3 offers never prove local stock.`} confirmLabel="Apply counts" onClose={() => setConfirm(false)} onConfirm={() => void apply()} />
  </div>;
}
