import type { ReactNode } from 'react';
import type { Order } from '../../lib/api';

export type WishItem = {
  id: string; product_id: string; name: string; merchant_id: string; merchant_name: string; category: string; currency: string;
  image_url: string | null; image_emoji: string; active: boolean; price_cents: number; in_stock: boolean; available_quantity: number;
  saved_price_cents: number; saved_in_stock: boolean; price_dropped: boolean; back_in_stock: boolean; created_at: string;
};
export type MyReview = { id: string; order_id: string; merchant_id: string; merchant_name: string; rating: number; body: string; product_name: string; created_at: string; visible: boolean };
export type Coupon = { code: string; title: string; detail: string; kind: 'percent' | 'amount'; value: number; category: string; min_spend_cents: number; expires_at: string };
export type Provider = { id: string; name: string; vehicle: string; eta: string; indicative_fee: string };
export type DeliveryReq = { id: string; order_id: string; provider_id: string; provider_name: string; address: string; notes: string; status: string; created_at: string; message: string };
export type Address = { id: string; label: string; line1: string; city: string; postal: string };
export type Profile = { display_name: string; addresses: Address[]; notifications: Record<string, boolean> };

export const ACTIVE = ['RESERVED', 'PAID', 'ACCEPTED', 'PREPARING'];
export const CLOSED = ['CANCELLED', 'EXPIRED', 'REFUNDED'];
export type OrderFilter = 'all' | 'active' | 'ready' | 'done' | 'closed';
export const FILTERS: { id: OrderFilter; label: string }[] = [
  { id: 'all', label: 'All' }, { id: 'active', label: 'Active' }, { id: 'ready', label: 'Ready for pickup' },
  { id: 'done', label: 'Delivered / collected' }, { id: 'closed', label: 'Cancelled / refunded' },
];
export const isClosed = (o: Order) => CLOSED.includes(o.status) || o.payment_status === 'REFUNDED';
export function matchesFilter(o: Order, f: OrderFilter) {
  if (f === 'all') return true;
  if (f === 'ready') return o.status === 'READY';
  if (f === 'done') return o.status === 'COLLECTED' && !isClosed(o);
  if (f === 'closed') return isClosed(o);
  return ACTIVE.includes(o.status) && !isClosed(o);
}
export const isOpenOrder = (o: Order) => !isClosed(o) && o.status !== 'COLLECTED';
export const fmtDate = (value: string, withYear = true) => new Date(value).toLocaleDateString([], { month: 'short', day: 'numeric', ...(withYear ? { year: 'numeric' } : {}) });
export const fmtTime = (value: string) => new Date(value).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
export const paymentLabel = (o: Pick<Order, 'payment_status' | 'payment_mode'>) => {
  const state = o.payment_status === 'CAPTURED' ? 'Paid' : o.payment_status === 'REFUNDED' ? 'Refunded' : o.payment_status === 'REFUND_PENDING' ? 'Refund pending'
    : o.payment_status === 'EXPIRED' ? 'Not paid, expired' : o.payment_status === 'NOT_STARTED' ? 'Not paid' : o.payment_status === 'CREATED' ? 'Awaiting PayPal approval' : o.payment_status.replaceAll('_', ' ').toLowerCase();
  return `${state}${o.payment_mode === 'demo' ? ' (demo, no funds moved)' : o.payment_mode === 'paypal_sandbox' ? ' (PayPal sandbox)' : ''}`;
};

export function PaneHeader({ title, hint, right }: { title: string; hint?: ReactNode; right?: ReactNode }) {
  return <div className="flex flex-wrap items-end justify-between gap-3 px-4 sm:px-5 pt-4 pb-3 border-b border-line">
    <div><h2 className="pf-subtitle">{title}</h2>{hint && <p className="text-[13px] text-muted mt-0.5">{hint}</p>}</div>{right}
  </div>;
}
export function Scroll({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`flex-1 min-h-0 overflow-y-auto overscroll-contain ${className}`}>{children}</div>;
}
export function Quiet({ children }: { children: ReactNode }) {
  return <p className="text-[13px] text-muted leading-relaxed">{children}</p>;
}

export type PaymentMethod = { id: string; provider: string; label: string; status: string; sandbox: boolean; created_at: string };
export type ThreadMsg = { id: string; sender: 'buyer' | 'merchant'; body: string; created_at: string };
export type Thread = { id: string; merchant_id: string; merchant_name: string; order_id: string | null; subject: string; updated_at: string; last_message: ThreadMsg | null };
export type ThreadDetail = Thread & { viewer: string; messages: ThreadMsg[] };
export type Ticket = { id: string; topic: string; subject: string; message: string; order_id: string | null; status: string; created_at: string };

/** Full-height pane with a header and an internally scrolling body. */
export function Pane({ children }: { children: ReactNode }) {
  return <div className="flex flex-col h-full min-h-0">{children}</div>;
}
