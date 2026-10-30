import { useMemo } from 'react';
import type { CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { cash, orderItems, type Order, type OrderItem } from '../../lib/api';
import { statusLabel } from '../../components/Shared';
import { PFGrid } from '../../components/Tables';

type Proof = { state: string; actor: string; proof: string; created_at: string };
type OrderWithProof = Order & { fulfilment_proof?: Proof[] };
const when = (iso: string) => new Date(iso).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });

export function timelineOf(order: OrderWithProof) {
  const out: { key: string; label: string; at?: string; note?: string; tone: 'ink' | 'ok' | 'bad' | 'muted' }[] = [{ key: 'placed', label: 'Order placed', at: order.created_at, note: order.buyer_name || undefined, tone: 'ink' }];
  if (order.payment_status === 'CAPTURED' || order.payment_status === 'REFUNDED') out.push({ key: 'paid', label: order.payment_mode === 'demo' ? 'Payment captured (demo)' : 'Payment captured', tone: 'ok' });
  for (const p of order.fulfilment_proof || []) out.push({ key: p.state, label: statusLabel(p.state), at: p.created_at, note: p.actor && p.actor !== 'demo-merchant' ? p.actor : undefined, tone: p.state === 'COLLECTED' ? 'ok' : 'ink' });
  if (!(order.fulfilment_proof || []).some(p => p.state === order.status)) out.push({ key: `now-${order.status}`, label: `${statusLabel(order.status)} (current)`, tone: ['CANCELLED', 'EXPIRED', 'REFUNDED'].includes(order.status) ? 'bad' : 'muted' });
  const win = order.pickup_window; if (win) out.push({ key: 'pickup', label: 'Pickup window', at: win.start_at, note: `until ${new Date(win.end_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`, tone: 'muted' });
  return out;
}

/** Expandable order row: line items on the left, status timeline on the right. */
export function OrderMasterDetail({ data }: CustomCellRendererProps<OrderWithProof>) {
  const order = data!;
  const items = useMemo(() => orderItems(order), [order]);
  const cols = useMemo<ColDef<OrderItem>[]>(() => [
    { headerName: 'Item', valueGetter: p => p.data?.product_name || p.data?.name || p.data?.product_id, flex: 3, minWidth: 160 },
    { field: 'quantity', headerName: 'Qty', maxWidth: 80 },
    { headerName: 'Unit', valueGetter: p => p.data?.unit_price_cents ?? p.data?.price_cents ?? null, valueFormatter: p => p.value == null ? '—' : cash(p.value, order.currency), maxWidth: 110 },
    { headerName: 'Line total', valueGetter: p => p.data?.amount_cents ?? ((p.data?.unit_price_cents ?? p.data?.price_cents ?? 0) * (p.data?.quantity ?? 0)), valueFormatter: p => cash(p.value, order.currency), maxWidth: 130, type: 'rightAligned', cellClass: 'pf-num' },
  ], [order.currency]);
  const steps = timelineOf(order);
  return <div className="pf-md" data-testid="order-detail-row">
    <div className="pf-md-items"><h4 className="pf-md-h">Items</h4>
      <PFGrid<OrderItem> height="auto" domLayout="autoHeight" rowData={items} columnDefs={cols} rowHeight={44} headerHeight={36} defaultColDef={{ sortable: false, resizable: false, flex: 1, minWidth: 70 }} animateRows={false} />
      <p className="pf-md-total"><span>Total</span><strong className="tabular">{cash(order.amount_cents, order.currency)}</strong></p></div>
    <div className="pf-md-time"><h4 className="pf-md-h">Status timeline</h4>
      <ol className="pf-timeline">{steps.map(s => <li key={s.key} className={`tone-${s.tone}`}><i /><div><b>{s.label}</b>{s.at && <time>{when(s.at)}</time>}{s.note && <span>{s.note}</span>}</div></li>)}</ol></div>
  </div>;
}
