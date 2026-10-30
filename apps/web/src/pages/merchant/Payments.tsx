import { useMemo, useState } from 'react';
import type { ColDef, ICellRendererParams } from 'ag-grid-community';
import { cash, messageOf, post } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, Empty, ErrorLine, Notice, PageHeader, Panel, Spinner } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';

type PayRow = { id: string; order_id: string; event_type: string; stage: string; amount_cents: number; currency: string; provider_order_id: string | null; capture_id: string | null; payee: string | null; order_status: string; payment_status: string; created_at: string; demo?: boolean; label?: string | null; reference?: string | null };
type Totals = Record<string, { captured_cents: number; refunded_cents: number; pending_cents: number; orders: number }>;
type History = { items: PayRow[]; total: number; totals: Totals; demo_totals?: Totals; daily?: { day: string; currency: string; captured_cents: number }[]; payee_account: boolean; payee_email?: string | null; payee_source?: string };

const STAGES: [string, string][] = [['', 'All'], ['created', 'Awaiting payment'], ['approved', 'Approved'], ['captured', 'Captured'], ['refunded', 'Refunded'], ['failed', 'Failed']];
const STAGE_LABEL: Record<string, string> = { created: 'Awaiting payment', approved: 'Approved', captured: 'Captured', refunded: 'Refunded', refund_pending: 'Refund pending', failed: 'Needs reconciliation', abandoned: 'Not approved' };
const STAGE_KIND: Record<string, 'green' | 'amber' | 'red' | 'blue' | 'default'> = { captured: 'green', approved: 'blue', created: 'default', refunded: 'amber', refund_pending: 'amber', failed: 'red', abandoned: 'default' };

type Ctx = { reconcile: (row: PayRow) => void; busyId: string };

function StageCell({ value, data }: ICellRendererParams<PayRow, string>) {
  return <span className="inline-flex items-center gap-2"><Chip kind={STAGE_KIND[value || ''] || 'default'}>{STAGE_LABEL[value || ''] || value}</Chip>{data?.demo && <Chip kind="blue">Sandbox demo</Chip>}</span>;
}
function sumTotals(a: Totals, b: Totals | undefined, withDemo: boolean): Totals {
  const out: Totals = JSON.parse(JSON.stringify(a));
  if (withDemo) for (const [cur, t] of Object.entries(b || {})) {
    const o = out[cur] ||= { captured_cents: 0, refunded_cents: 0, pending_cents: 0, orders: 0 };
    o.captured_cents += t.captured_cents; o.refunded_cents += t.refunded_cents; o.pending_cents += t.pending_cents; o.orders += t.orders;
  }
  return out;
}
function DailyChart({ days, currency }: { days: { day: string; captured_cents: number }[]; currency: string }) {
  const max = Math.max(1, ...days.map(d => d.captured_cents));
  return <div role="img" aria-label={`Captured per day, ${currency}, last ${days.length} days`} className="flex items-end gap-[3px] h-28">
    {days.map(d => <div key={d.day} className="flex-1 min-w-[4px] bg-accent rounded-t-[3px]" style={{ height: `${Math.max(3, (d.captured_cents / max) * 100)}%` }} title={`${d.day}: ${cash(d.captured_cents, currency)}`} />)}</div>;
}
function ActionCell({ data, context }: ICellRendererParams<PayRow, unknown, Ctx>) {
  if (!data || data.demo) return null;
  return <button className="pf-btn sm outline" disabled={context.busyId === data.id} onClick={() => context.reconcile(data)} aria-label={`Reconcile order ${data.order_id.slice(0, 8)} with PayPal`}>{context.busyId === data.id ? 'Checking…' : 'Reconcile'}</button>;
}

export function PaymentsPage({ merchantId }: { merchantId: string }) {
  const [stage, setStage] = useState('');
  const res = useResource<History>(`/merchants/${encodeURIComponent(merchantId)}/payments?limit=200${stage ? `&stage=${stage}` : ''}`, 15000);
  const [busyId, setBusyId] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const reconcile = async (row: PayRow) => {
    setBusyId(row.id); setError(''); setInfo('');
    try { await post(`/merchants/${encodeURIComponent(merchantId)}/payments/${encodeURIComponent(row.order_id)}/reconcile`); setInfo(`Order ${row.order_id.slice(0, 8)} checked with PayPal.`); await res.refresh(); }
    catch (issue) { setError(messageOf(issue)); } finally { setBusyId(''); }
  };
  const columns = useMemo<ColDef<PayRow>[]>(() => [
    { field: 'created_at', headerName: 'Time', minWidth: 170, sort: 'desc', valueFormatter: p => p.value ? new Date(p.value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '' },
    { field: 'stage', headerName: 'Event', minWidth: 280, cellRenderer: StageCell },
    { field: 'amount_cents', headerName: 'Amount', minWidth: 120, type: 'rightAligned', valueFormatter: p => p.data ? cash(p.data.amount_cents, p.data.currency) : '' },
    { field: 'currency', headerName: 'Currency', minWidth: 100 },
    { field: 'provider_order_id', headerName: 'PayPal order', minWidth: 190, cellClass: 'font-mono text-xs', valueGetter: p => p.data?.provider_order_id || p.data?.reference || '' },
    { field: 'order_id', headerName: 'PayFound order', minWidth: 190, valueFormatter: p => p.value ? String(p.value).slice(0, 12) : '' },
    { field: 'payment_status', headerName: 'Status', minWidth: 170, valueFormatter: p => String(p.value || '').replaceAll('_', ' ').toLowerCase() },
    { headerName: '', colId: 'action', minWidth: 130, maxWidth: 140, sortable: false, filter: false, pinned: 'right', cellRenderer: ActionCell },
  ], []);
  const totals = Object.entries(sumTotals(res.data?.totals || {}, res.data?.demo_totals, true));
  const chartCur = totals[0]?.[0] || 'USD';
  const days = (res.data?.daily || []).filter(d => d.currency === chartCur);
  return <div className="space-y-6 pf-enter" data-testid="merchant-payments">
    <PageHeader title="Payments" description="PayPal sandbox events for this store's orders. Amounts are per currency and come from the server, never from the browser." />
    <ErrorLine message={error || res.error} />{info && <Notice tone="green">{info}</Notice>}
    {totals.length > 0 && <div data-testid="payment-totals" className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">{totals.map(([currency, t]) => <div key={currency} className="pf-card p-5" aria-label={`${currency} totals`}>
      <p className="text-sm text-muted">Captured · {currency}</p><p className="font-display text-3xl tracking-tight tabular mt-1">{cash(t.captured_cents, currency)}</p>
      <p className="text-[13px] text-muted mt-2 tabular">{cash(t.refunded_cents, currency)} refunded · {cash(t.pending_cents, currency)} awaiting payment · {t.orders} order{t.orders === 1 ? '' : 's'}</p></div>)}</div>}
    {days.length > 1 && <Panel title={`Captured per day · ${chartCur}`}><DailyChart days={days} currency={chartCur} /></Panel>}
    <Panel title="PayPal events" description={res.data?.payee_account ? `Payments are routed to your PayPal sandbox account${res.data.payee_email ? ` (${res.data.payee_email})` : ''}.` : 'Payments currently go to the platform sandbox seller. Add your PayPal account in Settings to receive them yourself.'}
      actions={<div className="pf-segmented" role="group" aria-label="Filter by event">{STAGES.map(([id, label]) => <button key={id || 'all'} aria-pressed={stage === id} onClick={() => setStage(id)}>{label}</button>)}</div>}>
      {res.loading ? <Spinner /> : !res.data?.items.length ? <Empty title="No PayPal payments yet" description="Events appear here when a shopper starts a PayPal sandbox payment for one of your orders. Simulated demo payments are not PayPal transactions." />
        : <PFGrid<PayRow> height={Math.min(560, 60 + res.data.items.length * 48)} rowData={res.data.items} columnDefs={columns} context={{ reconcile, busyId } as Ctx} rowHeight={48} getRowId={p => p.data.id} animateRows={false} />}
    </Panel>
    <p className="text-xs text-muted">Sandbox only. Reconcile reads the order back from PayPal and applies a capture if the shopper had approved it. It never moves money by itself.</p>
  </div>;
}
