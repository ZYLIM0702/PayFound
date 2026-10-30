import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Check, Clock, Copy, Download, Printer, ShieldCheck, X } from 'lucide-react';
import { cash, messageOf, orderItems, post, type Order, type PickupSlot } from '../lib/api';
import { useApp } from '../lib/app-context';
import { useResource } from '../lib/use-resource';
import { ErrorLine, Notice, OrderStatus, Spinner } from '../components/Shared';
import { loadPending } from '../lib/basket';
import { PayPalPayment } from '../components/PayPalCheckout';
import { downloadInvoice, printInvoice } from './account/invoice';
import { InvoiceStatus } from '../components/InvoiceActions';
import { OrderTracker } from '../components/OrderTracker';
import { PickupSuggestions } from '../components/PickupSuggestions';
import { ProductPhoto } from '../components/ProductPhoto';

const time = (value: string) => new Date(value).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
const dayKey = (base: string, offset: number) => { const d = new Date(`${base}T12:00:00`); d.setDate(d.getDate() + offset); return d.toLocaleDateString('en-CA'); };

function Stepper({ steps, current, failed = false }: { steps: string[]; current: number; failed?: boolean }) {
  return <ol className="flex items-start" aria-label="Order progress">{steps.map((label, i) => {
    const done = i < current, active = i === current, bad = active && failed;
    const circle = done ? 'bg-ink border-ink text-white' : bad ? 'bg-bad border-bad text-white' : active ? 'bg-surface border-accent text-accent' : 'bg-surface border-line-strong text-subtle';
    return <li key={label} className="flex-1 min-w-0 relative" aria-current={active ? 'step' : undefined}>
      {i > 0 && <span className={`absolute top-[13px] right-1/2 w-full h-[2px] ${i <= current ? 'bg-ink' : 'bg-line'}`} aria-hidden />}
      <div className="relative flex flex-col items-center text-center gap-2 px-1">
        <span className={`w-7 h-7 rounded-full grid place-items-center text-xs font-semibold border-2 ${circle}`}>{done ? <Check size={14} strokeWidth={3} aria-label="Done" /> : bad ? <X size={14} strokeWidth={3} aria-label="Stopped" /> : i + 1}</span>
        <span className={`text-[12px] sm:text-[13px] leading-tight ${bad ? 'font-semibold text-bad' : active ? 'font-semibold text-ink' : done ? 'text-ink-2' : 'text-muted'}`}>{label}</span>
      </div>
    </li>;
  })}</ol>;
}

function CopyId({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  return <span className="inline-flex items-center gap-1.5 min-w-0"><code className="font-mono text-xs truncate">{value}</code><button type="button" className="pf-btn ghost sm icon shrink-0" aria-label={copied ? 'Order ID copied' : 'Copy order ID'} onClick={() => { void navigator.clipboard?.writeText(value).then(() => { setCopied(true); window.setTimeout(() => setCopied(false), 1500); }).catch(() => undefined); }}>{copied ? <Check size={14} /> : <Copy size={14} />}</button></span>;
}

function HoldClock({ until, active }: { until: string; active: boolean }) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => { if (!active) return; const id = window.setInterval(() => setNow(Date.now()), 1000); return () => window.clearInterval(id); }, [active]);
  const left = Math.max(0, Math.floor((Date.parse(until) - now) / 1000));
  const text = `${Math.floor(left / 60)}:${String(left % 60).padStart(2, '0')}`;
  return <div className={`flex items-center gap-3 rounded-[var(--pf-r-md)] px-4 py-3 ${left > 0 ? 'bg-canvas' : 'bg-warn-soft text-warn'}`}><Clock size={18} aria-hidden /><div className="flex-1 text-sm">{left > 0 ? 'Items held for you until' : 'Hold ended'} <span className="tabular">{new Date(until).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</span></div>{left > 0 && <strong className="font-display text-xl tabular" aria-label={`${Math.floor(left / 60)} minutes ${left % 60} seconds left`}>{text}</strong>}</div>;
}

export function Checkout() {
  const { orderId } = useParams();
  const [search] = useSearchParams();
  const payFirst = search.get('pay') === '1';
  const paymentRef = useRef<HTMLElement>(null);
  const scrolled = useRef(false);
  useEffect(() => { if (payFirst && !scrolled.current && paymentRef.current) { scrolled.current = true; paymentRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' }); } });
  const others = loadPending().filter(x => x.id !== orderId);
  const { config } = useApp();
  const navigate = useNavigate();
  const resource = useResource<Order>(`/orders/${orderId}`, 5000);
  const onPaid = (next: Order) => { resource.setData(next); if (next.payment_status === 'CAPTURED') navigate('/account/orders'); };
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [today] = useState(() => new Date().toLocaleDateString('en-CA'));
  const [date, setDate] = useState(today);
  const order = resource.data;
  const methods = useResource<{ methods: { provider: string; label: string }[] }>('/me/payment-methods');
  const payer = methods.data?.methods.find(m => m.provider === 'paypal');
  const slots = useResource<PickupSlot[]>(order ? `/merchants/${order.merchant_id}/pickup-slots?date=${date}&view_timezone=${encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone)}${order.location_id ? `&location_id=${order.location_id}` : ''}` : null);
  const act = async (path: string, body = {}) => {
    if (busy) return;
    setBusy(true); setError('');
    try { resource.setData(await post<Order>(`/orders/${orderId}/${path}`, body)); }
    catch (issue) { setError(messageOf(issue)); }
    finally { setBusy(false); await resource.refresh(); }
  };
  if (resource.loading) return <main className="pf-container py-10"><Spinner /></main>;
  if (!order) return <main className="pf-container py-10"><ErrorLine message={resource.error || 'Order unavailable'} retry={resource.refresh} /></main>;
  const paid = order.payment_status === 'CAPTURED';
  const expired = Date.parse(order.hold_expires_at) <= Date.now();
  const payable = order.status === 'RESERVED' && !expired && order.confirmation_status === 'CONFIRMED' && ['NOT_STARTED', 'CREATED'].includes(order.payment_status);
  const closed = ['CANCELLED', 'EXPIRED'].includes(order.status);
  const confirmed = order.confirmation_status === 'CONFIRMED';
  const step = order.status === 'COLLECTED' ? 4 : paid ? 3 : confirmed ? 2 : 1;
  const days = Array.from({ length: 7 }, (_, i) => dayKey(today, i));
  const booked = order.pickup_window;
  return <main className="pf-container py-8 sm:py-12">
    {others.length > 0 && <p className="mb-6 text-sm text-ink-2" data-testid="other-reservations">Your other reservations: {others.map((o, i) => <span key={o.id}>{i > 0 && ', '}<Link className="pf-link" to={`/checkout/${o.id}`}>{o.store}</Link></span>)}</p>}
    <div className="mb-8"><h1 className="pf-heading">{paid ? 'Payment confirmed' : closed ? 'Order closed' : 'Checkout'}</h1><p className="text-muted text-[15px] mt-2">{order.merchant_name} · Order <span className="tabular">{order.id.slice(0, 8)}</span></p></div>
    <div className="pf-card p-5 sm:p-6 mb-8"><Stepper steps={['Reserved', 'Store confirms stock', 'Pay', 'Pick up']} current={closed ? (confirmed ? 2 : 1) : step} failed={closed} /></div>
    <div className="space-y-3 mb-6 empty:hidden"><ErrorLine message={resource.error || error} />
      {order.confirmation_status === 'PENDING' && <Notice>The store is physically checking this stock before payment opens. This page updates automatically.</Notice>}
      {expired && !paid && <Notice tone="amber">Reservation time elapsed. Check payment status before starting a new order.</Notice>}
      {paid && <Notice tone="green">{order.payment_mode === 'demo' ? 'Simulated payment complete. No funds moved.' : 'PayPal sandbox capture confirmed by the server.'} Track preparation in your orders.</Notice>}</div>
    <div className="grid grid-cols-[minmax(0,1fr)] lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] xl:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] gap-8 xl:gap-12 items-start">
      <section className="pf-card p-6 sm:p-7 space-y-5" aria-label="Order summary">
        <div className="flex items-center justify-between gap-3"><h2 className="pf-title">Order summary</h2><OrderStatus order={order} /></div>
        <ul className="divide-y divide-line">{orderItems(order).map(item => <li className="flex items-center gap-4 py-4" key={item.product_id}><div className="pf-line-photo"><ProductPhoto name={item.product_name || item.name || 'Product'} imageUrl={item.image_url} /></div><span className="flex-1 min-w-0 text-sm font-medium">{item.product_name || item.name}<span className="block text-muted font-normal">Qty {item.quantity}</span></span><b className="tabular text-sm">{cash(item.amount_cents ?? (item.unit_price_cents || 0) * item.quantity, order.currency)}</b></li>)}</ul>
        <div className="flex justify-between items-baseline pt-1"><span className="font-semibold">Total</span><strong className="font-display text-3xl tracking-tight tabular">{cash(order.amount_cents, order.currency)}</strong></div>
        {order.status === 'RESERVED' && !paid && <HoldClock until={order.hold_expires_at} active={!expired} />}
        <div className="pt-1"><OrderTracker order={order} /></div>
        <dl className="text-sm divide-y divide-line border-y border-line"><div className="flex items-center justify-between gap-4 py-2"><dt className="text-muted">Order ID</dt><dd className="min-w-0"><CopyId value={order.id} /></dd></div><div className="flex items-center justify-between gap-4 py-2"><dt className="text-muted">Payment</dt><dd className="capitalize">{order.payment_status.replaceAll('_', ' ').toLowerCase()}</dd></div><div className="flex items-center justify-between gap-4 py-2"><dt className="text-muted">Hold ends</dt><dd className="tabular">{new Date(order.hold_expires_at).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</dd></div></dl>
        <Link className="pf-btn outline" to="/account/orders">View my orders</Link>
      </section>
      <div className="space-y-6">
        <section className="pf-card p-6 sm:p-7 space-y-4 scroll-mt-24" aria-label="Payment" ref={paymentRef}><h2 className="pf-title">Payment</h2>
          {payable && config?.paypal_sandbox_enabled && config.paypal_client_id && <PayPalPayment order={order} clientId={config.paypal_client_id} onSuccess={onPaid} />}
          {!paid && !payable && <p className="text-sm text-muted" data-testid="payment-state-note">{order.confirmation_status === 'PENDING' ? 'Payment opens once the store confirms stock.' : closed ? 'This order is closed, so payment is no longer possible.' : expired ? 'The reservation time has elapsed. Check the PayPal status below before starting a new order.' : ['CREATING', 'CAPTURING'].includes(order.payment_status) ? 'PayPal is confirming this payment. This page updates automatically.' : order.payment_status === 'RECONCILIATION_REQUIRED' ? 'PayPal has not given a final answer yet. Use Check PayPal status below.' : 'Payment is not available for this order right now.'}</p>}
          {payable && payer && <p className="text-[13px] text-muted" data-testid="preferred-payer">Preferred payer: <b className="text-ink-2">{payer.label}</b> (sandbox). PayPal still asks you to sign in in its own window.</p>}
          {paid && <p className="flex items-center gap-2 text-sm text-ok font-semibold"><ShieldCheck size={16} />Paid{order.payment_mode === 'demo' ? ' (simulated)' : ' (PayPal sandbox)'}</p>}
          {paid && <InvoiceStatus orderId={order.id} />}
          {paid && <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button className="pf-btn outline" onClick={() => printInvoice(order)} data-testid="print-invoice"><Printer size={15} />Print invoice</button>
            <button className="pf-btn outline" onClick={() => downloadInvoice(order)} data-testid="download-invoice"><Download size={15} />Download invoice</button>
          </div>}
          {paid && order.status === 'READY' && <button className="pf-btn accent w-full" disabled={busy} onClick={() => act('confirm-pickup')} data-testid="confirm-pickup"><Check size={16} />{busy ? 'Confirming…' : 'Confirm pickup'}</button>}
          {paid && order.status === 'COLLECTED' && <p className="flex items-center gap-2 text-sm text-ok font-semibold" data-testid="pickup-confirmed"><Check size={16} />Pickup confirmed</p>}
          {order.payment_mode === 'paypal_sandbox' && <button className="pf-btn outline w-full" disabled={busy} onClick={() => act('paypal/reconcile')}>Check PayPal status / reconcile</button>}
          {order.payment_status === 'NOT_STARTED' && order.status === 'RESERVED' && <button className="pf-tap text-sm font-semibold text-muted hover:text-bad underline underline-offset-4" disabled={busy} onClick={() => act('cancel')}>Cancel unpaid reservation</button>}
        </section>
        {!['CANCELLED', 'EXPIRED', 'COLLECTED'].includes(order.status) && <section className="pf-card p-6 sm:p-7 space-y-5" aria-label="Pickup window"><div><h2 className="pf-title">Choose pickup window</h2><p className="text-sm text-muted mt-1">Times are shown in your local time zone.</p></div>
          <div className="flex gap-2 overflow-x-auto pb-1" role="group" aria-label="Pickup date">{days.map(d => { const dt = new Date(`${d}T12:00:00`); return <button key={d} type="button" aria-pressed={d === date} onClick={() => setDate(d)} className={`shrink-0 w-[62px] py-2 rounded-[var(--pf-r-md)] border text-center transition-colors ${d === date ? 'bg-ink text-white border-ink' : 'border-line-strong hover:border-ink'}`}><span className={`block text-xs ${d === date ? 'text-white/80' : 'text-muted'}`}>{d === today ? 'Today' : dt.toLocaleDateString([], { weekday: 'short' })}</span><span className={`block font-display text-lg leading-tight ${d === date ? 'text-white' : 'text-ink'}`}>{dt.getDate()}</span></button>; })}
            <label className="shrink-0 flex flex-col justify-center text-xs text-muted px-2">More dates<input className="pf-input sm !w-[140px]" type="date" value={date} min={today} onChange={e => setDate(e.target.value)} aria-label="Pickup date" /></label></div>
          <PickupSuggestions merchantId={order.merchant_id} day={date} selectedId={booked?.id} disabled={busy} onSelect={id => void act('pickup', { slot_id: id })} />
          <ErrorLine message={slots.error} />
          {slots.loading ? <Spinner /> : slots.data?.length ? <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">{slots.data.map(slot => { const chosen = booked?.id === slot.id; return <button className={`rounded-[var(--pf-r-md)] border px-3 py-2.5 text-left transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${chosen ? 'border-accent bg-accent-soft' : 'border-line-strong hover:border-ink'}`} key={slot.id} aria-pressed={chosen} disabled={busy || slot.remaining < 1 || Date.parse(slot.start_at) < Date.now()} onClick={() => act('pickup', { slot_id: slot.id })}><span className="block text-sm font-semibold tabular">{time(slot.start_at)} – {time(slot.end_at)}</span><span className="block text-xs text-muted">{slot.remaining < 1 ? 'Full' : `${slot.remaining} ${slot.remaining === 1 ? 'spot' : 'spots'} left`}</span></button>; })}</div> : <p className="text-sm text-muted">No windows published for this day. The merchant can still prepare your order and confirm pickup.</p>}
          {booked && <p className="flex items-center gap-2 text-sm font-semibold"><Check size={16} className="text-ok" />Booked: {new Date(booked.start_at).toLocaleString([], { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</p>}
        </section>}
      </div>
    </div>
  </main>;
}
