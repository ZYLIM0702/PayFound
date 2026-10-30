import { useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, ShieldCheck, ShoppingBag } from 'lucide-react';
import { cash, messageOf, post, type Order } from '../../lib/api';
import { useApp } from '../../lib/app-context';
import { useResource } from '../../lib/use-resource';
import { ProductPhoto } from '../ProductPhoto';
import { PayPalCheckout } from '../PayPalCheckout';
import { Chip, ErrorLine, Field, OrderStatus as StatusChip, Skeleton } from '../Shared';
import { useProductsByIds, useSettledIds } from './data';

/**
 * Human-in-the-loop checkout. The model can only propose this card; reserving and paying are
 * explicit clicks that use the same endpoints, idempotency and payable rules as Basket/Checkout.
 */
export function ReserveAndPayView({ props }: { props: { productIds?: unknown; quantities?: unknown } }) {
  const { session, demo, config } = useApp();
  const ids = useSettledIds(props.productIds, 10);
  const { products, loading, error, refresh } = useProductsByIds(ids);
  const quantities = Array.isArray(props.quantities) ? props.quantities : [];
  const lines = useMemo(() => products.map(product => ({ product, quantity: Math.min(10, Math.max(1, Math.floor(Number(quantities[ids.indexOf(product.id)]) || 1))) })),
    [products, ids, JSON.stringify(quantities)]);
  const [buyerName, setBuyerName] = useState('');
  const [busy, setBusy] = useState(false);
  const [issue, setIssue] = useState('');
  const [orderId, setOrderId] = useState('');
  const lock = useRef(false);
  const intent = useRef({ fingerprint: '', key: '' });
  const order = useResource<Order>(orderId ? `/orders/${orderId}` : null, 5000);
  if (!ids.length) return null;
  if (loading) return <section className="pf-ag-card"><Skeleton className="h-40 !rounded-[var(--pf-r-lg)]" /></section>;
  const merchants = new Set(lines.map(l => l.product.merchant_id)), currencies = new Set(lines.map(l => l.product.currency)), branches = new Set(lines.map(l => l.product.location_id));
  const invalid = !lines.length || lines.length !== ids.length || merchants.size > 1 || currencies.size > 1 || branches.size > 1
    || lines.some(l => !l.product.in_stock || l.quantity > l.product.available_quantity || l.product.is_open === false || l.product.checkout_mode === 'merchant_native');
  const currency = lines[0]?.product.currency;
  const total = lines.reduce((sum, l) => sum + l.product.price_cents * l.quantity, 0);
  const items = lines.map(l => ({ product_id: l.product.id, quantity: l.quantity }));
  const reserve = async () => {
    if (lock.current || invalid || !buyerName.trim()) return;
    lock.current = true; setBusy(true); setIssue('');
    const fingerprint = JSON.stringify({ items, buyer_name: buyerName.trim() });
    if (intent.current.fingerprint !== fingerprint) intent.current = { fingerprint, key: crypto.randomUUID() };
    try { const created = await post<Order>('/orders/reserve', { items, buyer_name: buyerName.trim(), idempotency_key: intent.current.key }); setOrderId(created.id); order.setData(created); }
    catch (e) { setIssue(messageOf(e)); void refresh(); }
    finally { lock.current = false; setBusy(false); }
  };
  const o = order.data;
  return <section className="pf-ag-card" aria-label="Reserve and pay" data-testid="agent-reserve">
    <h4 className="pf-ag-card-title">{o ? 'Your reservation' : 'Reserve for pickup'}</h4>
    <ul className="grid gap-3">{(o ? [] : lines).map(({ product: p, quantity }) => <li key={p.id} className="flex items-center gap-3">
      <span className="w-14 h-14 rounded-[var(--pf-r-md)] overflow-hidden shrink-0 block"><ProductPhoto name={p.name} imageUrl={p.image_url} merchantId={p.merchant_id} /></span>
      <div className="min-w-0 flex-1"><p className="font-semibold text-[14px] truncate">{p.name}</p><p className="pf-ag-meta">{p.merchant_name} · Qty {quantity}</p></div>
      <strong className="tabular">{cash(p.price_cents * quantity, p.currency)}</strong></li>)}</ul>
    {error && <ErrorLine message={error} retry={refresh} />}
    {!o && <>
      <div className="flex justify-between items-baseline pt-4 mt-4 border-t border-line"><span className="font-semibold text-[14px]">Estimated total</span><strong className="font-display text-2xl tracking-tight tabular">{currency ? cash(total, currency) : '—'}</strong></div>
      {invalid && lines.length > 0 && <p className="text-[13px] text-warn mt-3" role="alert">These items cannot be reserved together right now (different stores, out of stock, or the store is closed).</p>}
      {!invalid && (session || demo) && <div className="mt-4 grid gap-3">
        <Field label="Pickup name" autoComplete="name" maxLength={100} value={buyerName} onChange={e => setBuyerName(e.target.value)} hint="The name the store will look for at pickup." />
        <button className="pf-btn accent w-full" disabled={busy || !buyerName.trim()} onClick={() => void reserve()} data-testid="agent-reserve-button"><ShoppingBag size={16} />{busy ? 'Reserving…' : 'Reserve — you pay next'}</button>
      </div>}
      {!invalid && !session && !demo && <Link className="pf-btn accent w-full mt-4" to="/login">Sign in to reserve</Link>}
      <p className="text-[12px] text-subtle mt-3 leading-relaxed">Reserving holds the items and does not charge you. The server confirms the final total, and you choose whether to pay.</p>
    </>}
    {issue && <div className="mt-3"><ErrorLine message={issue} /></div>}
    {orderId && !o && <Skeleton className="h-24 mt-3 !rounded-[var(--pf-r-lg)]" />}
    {o && <ReservedOrder order={o} onChange={order.setData} refresh={order.refresh} config={config} />}
  </section>;
}

function ReservedOrder({ order, onChange, refresh, config }: { order: Order; onChange: (o: Order) => void; refresh: () => Promise<void>; config: ReturnType<typeof useApp>['config'] }) {
  const paid = order.payment_status === 'CAPTURED';
  const expired = Date.parse(order.hold_expires_at) <= Date.now();
  const payable = order.status === 'RESERVED' && !expired && order.confirmation_status === 'CONFIRMED' && ['NOT_STARTED', 'CREATED'].includes(order.payment_status);
  return <div className="grid gap-3">
    <div className="flex items-center justify-between gap-3"><div><p className="font-semibold text-[15px]">{order.merchant_name}</p><p className="pf-ag-meta">Order {order.id.slice(0, 8)}</p></div><div className="text-right"><strong className="font-display text-2xl tabular block">{cash(order.amount_cents, order.currency)}</strong><StatusChip order={order} /></div></div>
    {!paid && !expired && <p className="flex items-center gap-2 text-[13px] text-muted rounded-[var(--pf-r-md)] bg-canvas px-3 py-2.5"><Clock size={15} />Held for you until {new Date(order.hold_expires_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</p>}
    {payable && config?.paypal_sandbox_enabled && config.paypal_client_id && <PayPalCheckout order={order} clientId={config.paypal_client_id} onSuccess={onChange} />}
    {!paid && !payable && <p className="text-sm text-muted">{expired ? 'This hold has ended.' : order.confirmation_status === 'PENDING' ? 'Payment opens once the store confirms stock.' : 'Payment is unavailable in the current order state.'}</p>}
    {paid && <p className="flex items-center gap-2 text-sm text-ok font-semibold"><ShieldCheck size={16} />Paid{order.payment_mode === 'demo' ? ' (simulated, no funds moved)' : ' (PayPal sandbox)'}<Chip kind="green">Pickup next</Chip></p>}
    <Link className="pf-link text-sm" to={`/checkout/${order.id}`}>Open full checkout →</Link>
  </div>;
}
