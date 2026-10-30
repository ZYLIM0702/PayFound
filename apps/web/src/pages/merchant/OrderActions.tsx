import { Link } from 'react-router-dom';
import { statusLabel } from '../../components/Shared';
import type { Order } from '../../lib/api';
import { FULFILMENT_NEXT } from './context';

/** Existing order actions: confirm stock, advance fulfilment, refund (via ConfirmDialog), receipt. */
export function OrderActions({ order, busy, run, requestRefund, showView = false }: { order: Order; busy: boolean; run: (path: string, body?: object) => Promise<void>; requestRefund: (order: Order) => void; showView?: boolean }) {
  const next = FULFILMENT_NEXT[order.status];
  return <div className="flex items-center gap-1.5 h-full">
    {order.confirmation_status === 'PENDING' && order.status === 'RESERVED' && <button className="pf-btn sm accent" disabled={busy} onClick={() => run(`/orders/${order.id}/confirm`)}>Confirm</button>}
    {next && order.payment_status === 'CAPTURED' && <button className="pf-btn sm" disabled={busy} onClick={() => run(`/orders/${order.id}/fulfilment`, { status: next })}>{statusLabel(next)}</button>}
    {order.payment_status === 'CAPTURED' && order.status !== 'COLLECTED' && <button className="pf-btn sm danger" disabled={busy} onClick={() => requestRefund(order)}>Refund</button>}
    {showView && <Link className="pf-btn sm outline" to={`/checkout/${order.id}`}>Receipt</Link>}
  </div>;
}
