import { useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';
import type { AgGridReact, CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { cash, type AdminOverview, type IntegrationStatus, type Merchant, type Order, type ReconciliationQueue, type Review } from '../../lib/api';
import { Chip, Empty, PageHeader, Panel, Stat } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';
import { dateTimeFormatter, moneyFormatter, orderIdColumn, orderStatusCell, paymentCell, shortId } from '../../components/grid-cells';

type Audit = AdminOverview['audit'][number];
const H = 'calc(100dvh - 300px)';

function SearchBar({ grid, placeholder }: { grid: React.RefObject<AgGridReact<any> | null>; placeholder: string }) {
  const [v, setV] = useState('');
  return <div className="px-5 py-3.5 border-b border-line"><div className="relative max-w-md"><Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" /><input className="pf-input sm !pl-10 !rounded-full" type="search" placeholder={placeholder} aria-label={placeholder} value={v} onChange={e => { setV(e.target.value); grid.current?.api.setGridOption('quickFilterText', e.target.value); }} /></div></div>;
}
const statusBar = { statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' as const }] };

export function AdminOverviewPage({ data, queue, integrations }: { data: AdminOverview; queue: ReconciliationQueue | null; integrations: IntegrationStatus | null }) {
  const captured = data.orders.filter(o => o.payment_status === 'CAPTURED').reduce((n, o) => n + o.amount_cents, 0);
  const hidden = data.reviews.filter(r => r.visible === false).length;
  const attention = (queue?.orders.length || 0) + (queue?.failed_jobs.length || 0);
  return <div className="space-y-5 pf-enter">
    <PageHeader title="Platform overview" description="Moderate the pilot, inspect operational health and recover known payment or job failures." />
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
      <Stat label="Merchants" value={data.merchants.length} /><Stat label="Orders" value={data.orders.length} /><Stat label="Captured value" value={cash(captured)} hint="Mixed currencies shown as USD" />
      <Stat label="Hidden reviews" value={hidden} /><Stat label="Needs recovery" value={attention} tone={attention ? 'red' : undefined} />
    </div>
    <div className="grid xl:grid-cols-3 gap-5">
      <Panel title="Integration health" description="Safe operational flags only. No credentials or secrets are shown." className="xl:col-span-1"><IntegrationList integrations={integrations} /></Panel>
      <Panel title="Recent activity" className="xl:col-span-2" actions={<Link className="pf-link text-sm" to="/admin/audit">Audit log</Link>}>
        {data.audit.length === 0 ? <p className="text-sm text-muted">No activity yet.</p> : <ul className="divide-y divide-line -my-2">{data.audit.slice(0, 8).map(a => <li key={a.id} className="flex items-center gap-3 py-2.5 text-sm"><span className="font-medium">{a.action}</span><span className="text-muted truncate flex-1">{a.actor} · {shortId(a.entity_id)}</span><time className="text-xs text-muted tabular shrink-0">{new Date(a.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</time></li>)}</ul>}
      </Panel>
    </div>
  </div>;
}

function IntegrationList({ integrations }: { integrations: IntegrationStatus | null }) {
  const items = integrations?.integrations || [];
  if (!items.length) return <p className="text-sm text-muted">No status details available.</p>;
  const good = (s: string) => !/false|error|fail|down|missing|disabled/i.test(s);
  return <ul className="divide-y divide-line -my-2">{items.map(i => <li key={i.id || i.name} className="flex items-center gap-3 py-3"><span className={`w-2 h-2 rounded-full shrink-0 ${good(i.status) ? 'bg-ok' : 'bg-warn'}`} aria-hidden /><div className="min-w-0 flex-1"><p className="text-sm font-medium truncate">{i.name}</p>{i.detail && <p className="text-xs text-muted truncate">{i.detail}</p>}</div><Chip kind={good(i.status) ? 'green' : 'amber'}>{i.status}</Chip></li>)}</ul>;
}

export function MerchantsPage({ data }: { data: AdminOverview }) {
  const grid = useRef<AgGridReact<Merchant>>(null);
  const cols = useMemo<ColDef<Merchant>[]>(() => [
    { field: 'name', headerName: 'Store', flex: 2, minWidth: 210, floatingFilter: true },
    { field: 'category', headerName: 'Category', filter: 'agSetColumnFilter', minWidth: 140, enableRowGroup: true },
    { field: 'address', headerName: 'Location', flex: 2, minWidth: 220 },
    { headerName: 'Public status', colId: 'open', valueGetter: p => p.data?.is_open ? 'Open' : 'Not confirmed', filter: 'agSetColumnFilter', cellRenderer: ({ value }: CustomCellRendererProps) => <Chip kind={value === 'Open' ? 'green' : 'default'} dot>{value}</Chip> },
    { field: 'rating', headerName: 'Rating', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', valueFormatter: p => p.value ? Number(p.value).toFixed(1) : '—', width: 110 },
    { field: 'verified', headerName: 'Verified', filter: 'agSetColumnFilter', width: 130, cellRenderer: ({ value }: CustomCellRendererProps) => <Chip kind={value ? 'blue' : 'default'}>{value ? 'Verified' : 'Pending'}</Chip> },
  ], []);
  return <div className="space-y-5 pf-enter"><PageHeader title="Merchants" description="Directory of stores on the platform." />
    <Panel flush><SearchBar grid={grid} placeholder="Search merchants" /><PFGrid<Merchant> gridRef={grid} height={H} className="min-h-[420px]" rowData={data.merchants} columnDefs={cols} getRowId={p => p.data.id} sideBar={{ toolPanels: ['columns', 'filters'], hiddenByDefault: true }} statusBar={statusBar} pagination paginationPageSize={25} /></Panel></div>;
}

export function OrdersAdminPage({ data }: { data: AdminOverview }) {
  const grid = useRef<AgGridReact<Order>>(null);
  const cols = useMemo<ColDef<Order>[]>(() => [
    { ...orderIdColumn, cellRenderer: undefined, cellRendererParams: undefined, valueFormatter: p => p.value ? shortId(p.value) : '', minWidth: 150 },
    { field: 'merchant_name', headerName: 'Store', filter: 'agSetColumnFilter', enableRowGroup: true, minWidth: 160 },
    { field: 'product_name', headerName: 'Product', flex: 2, minWidth: 190 },
    { field: 'amount_cents', headerName: 'Total', valueFormatter: moneyFormatter, type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', minWidth: 120, aggFunc: 'sum' },
    { field: 'payment_status', headerName: 'Payment', cellRenderer: paymentCell, filter: 'agSetColumnFilter', minWidth: 150 },
    { field: 'status', headerName: 'Fulfilment', cellRenderer: orderStatusCell, filter: 'agSetColumnFilter', enableRowGroup: true, minWidth: 150 },
    { field: 'created_at', headerName: 'Placed', valueFormatter: dateTimeFormatter, sort: 'desc', minWidth: 160 },
  ], []);
  return <div className="space-y-5 pf-enter"><PageHeader title="Orders" description="All orders across stores. Drag columns to the group panel to group by store or status." />
    <Panel flush><SearchBar grid={grid} placeholder="Search orders" /><PFGrid<Order> gridRef={grid} height={H} className="min-h-[420px]" rowData={data.orders} columnDefs={cols} getRowId={p => p.data.id} rowGroupPanelShow="always" sideBar={{ toolPanels: ['columns', 'filters'], hiddenByDefault: true }} cellSelection enableCharts statusBar={{ statusPanels: [...statusBar.statusPanels, { statusPanel: 'agAggregationComponent', align: 'right' as const }] }} pagination paginationPageSize={25} /></Panel></div>;
}

export function ReviewsPage({ data, busy, onToggle }: { data: AdminOverview; busy: string; onToggle: (r: Review) => void }) {
  const grid = useRef<AgGridReact<Review>>(null);
  const cols = useMemo<ColDef<Review>[]>(() => [
    { field: 'rating', headerName: 'Rating', width: 110, filter: 'agSetColumnFilter', valueFormatter: p => `${p.value} / 5` },
    { field: 'body', headerName: 'Comment', flex: 3, minWidth: 260, wrapText: false, tooltipField: 'body' },
    { field: 'created_at', headerName: 'Posted', valueFormatter: dateTimeFormatter, minWidth: 160 },
    { field: 'visible', headerName: 'Visibility', width: 140, filter: 'agSetColumnFilter', cellRenderer: ({ value }: CustomCellRendererProps) => <Chip kind={value === false ? 'red' : 'green'} dot>{value === false ? 'Hidden' : 'Visible'}</Chip> },
    { headerName: 'Moderation', colId: 'mod', width: 170, sortable: false, filter: false, pinned: 'right', cellRenderer: ({ data: review }: CustomCellRendererProps<Review>) => review && <button className="pf-btn sm outline" disabled={busy === `review-${review.id}`} onClick={() => onToggle(review)}>{review.visible === false ? 'Restore review' : 'Hide review'}</button> },
  ], [busy, onToggle]);
  return <div className="space-y-5 pf-enter"><PageHeader title="Review moderation" description="Hide abusive or off-topic reviews. Hidden reviews no longer count towards ratings or appear to shoppers." />
    <Panel flush><SearchBar grid={grid} placeholder="Search reviews" /><PFGrid<Review> gridRef={grid} height={H} className="min-h-[420px]" rowData={data.reviews} columnDefs={cols} getRowId={p => p.data.id} statusBar={statusBar} pagination paginationPageSize={25} /></Panel></div>;
}

export function AuditPage({ data }: { data: AdminOverview }) {
  const grid = useRef<AgGridReact<Audit>>(null);
  const cols = useMemo<ColDef<Audit>[]>(() => [
    { field: 'created_at', headerName: 'When', valueFormatter: dateTimeFormatter, sort: 'desc', minWidth: 170, filter: 'agDateColumnFilter' },
    { field: 'actor', headerName: 'Actor', rowGroup: false, enableRowGroup: true, filter: 'agSetColumnFilter', minWidth: 170 },
    { field: 'action', headerName: 'Action', flex: 2, minWidth: 200, enableRowGroup: true, filter: 'agSetColumnFilter' },
    { field: 'entity_id', headerName: 'Entity', flex: 2, minWidth: 200 },
  ], []);
  return <div className="space-y-5 pf-enter"><PageHeader title="Audit log" description="Administrative actions, newest first. Drag Actor or Action into the group panel to group." />
    <Panel flush><SearchBar grid={grid} placeholder="Search audit log" /><PFGrid<Audit> gridRef={grid} height={H} className="min-h-[420px]" rowData={data.audit} columnDefs={cols} getRowId={p => String(p.data.id)} rowGroupPanelShow="always" groupDisplayType="multipleColumns" statusBar={statusBar} pagination paginationPageSize={50} /></Panel></div>;
}

type CaseRow = { key: string; kind: 'Payment' | 'Background job'; status: string; ref: string; owner: string; detail: string; attempts: number; items: number; rawId: string };

export function ReconciliationPage({ queue, integrations, busy, onReconcile, onRetry }: { queue: ReconciliationQueue | null; integrations: IntegrationStatus | null; busy: string; onReconcile: (id: string) => void; onRetry: (id: string) => void }) {
  const rows = useMemo<CaseRow[]>(() => [
    ...(queue?.orders || []).map<CaseRow>(o => ({ key: `order-${o.id}`, kind: 'Payment', status: o.payment_status || 'UNKNOWN', ref: shortId(o.id), owner: o.merchant_name || '', detail: `Confirmation: ${o.confirmation_status || '—'}`, attempts: 0, items: 1, rawId: o.id })),
    ...(queue?.failed_jobs || []).map<CaseRow>(j => ({ key: `job-${j.id}`, kind: 'Background job', status: String(j.status || 'FAILED'), ref: shortId(j.id), owner: j.order_id ? `Order ${shortId(j.order_id)}` : '', detail: String(j.last_error || j.error || '—'), attempts: j.attempts ?? 0, items: 1, rawId: j.id })),
  ], [queue]);
  const cols = useMemo<ColDef<CaseRow>[]>(() => [
    { field: 'status', headerName: 'Status', rowGroup: true, hide: true, enableRowGroup: true },
    { field: 'kind', headerName: 'Type', minWidth: 140, filter: 'agSetColumnFilter', enableRowGroup: true },
    { field: 'ref', headerName: 'Reference', minWidth: 150 },
    { field: 'owner', headerName: 'Merchant / order', minWidth: 170, flex: 1.2 },
    { field: 'detail', headerName: 'Detail', flex: 2, minWidth: 220, tooltipField: 'detail' },
    { field: 'attempts', headerName: 'Attempts', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', aggFunc: 'sum', width: 120 },
    { field: 'items', headerName: 'Cases', type: 'rightAligned', cellClass: 'pf-num', headerClass: 'pf-num', aggFunc: 'sum', width: 100 },
    { headerName: 'Action', colId: 'a', pinned: 'right', width: 150, sortable: false, filter: false, cellRenderer: ({ data: row }: CustomCellRendererProps<CaseRow>) => row && <button className="pf-btn sm" disabled={busy === row.key} aria-label={`Retry ${row.kind} ${row.ref}`} onClick={() => row.kind === 'Payment' ? onReconcile(row.rawId) : onRetry(row.rawId)}>{busy === row.key ? 'Retrying…' : 'Retry'}</button> },
  ], [busy, onReconcile, onRetry]);
  return <div className="space-y-5 pf-enter"><PageHeader title="Reconciliation" description="Retry checks the server-side PayPal record or re-queues a failed job. It does not create a payment or capture funds." />
    <div className="grid xl:grid-cols-3 gap-5 items-start">
      <div className="xl:col-span-2">
        <Panel title="Open cases" description="Grouped by status. Expand a group, then retry a single case." flush>{rows.length ? <PFGrid<CaseRow> height={Math.min(620, 300 + rows.length * 56)} rowData={rows} columnDefs={cols} getRowId={p => p.data.key} groupDefaultExpanded={1} autoGroupColumnDef={{ headerName: 'Status', minWidth: 190, cellRendererParams: { suppressCount: false } }} groupTotalRow="bottom" grandTotalRow="bottom" rowGroupPanelShow="always" cellSelection
          statusBar={{ statusPanels: [{ statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' }, { statusPanel: 'agAggregationComponent', align: 'right' }] }} /> : <Empty title="All clear" description="No payments or background jobs need recovery." />}</Panel>
      </div>
      <Panel title="Integration status" description="Credentials and secrets are never shown."><IntegrationList integrations={integrations} /></Panel>
    </div>
  </div>;
}
