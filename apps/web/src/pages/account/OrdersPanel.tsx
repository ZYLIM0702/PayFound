import { useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronLeft, ChevronRight, Download, MessageCircle, Printer, RotateCcw, Star, Truck } from 'lucide-react';
import { api, cash, messageOf, orderItems, post, type Order, type Product } from '../../lib/api';
import { downloadInvoice, printInvoice } from './invoice';
import { InvoiceStatus } from '../../components/InvoiceActions';
import { OrderTracker } from '../../components/OrderTracker';
import { useCart } from '../../lib/cart';
import { Empty, OrderStatus, TextAreaField } from '../../components/Shared';
import { ProductPhoto } from '../../components/ProductPhoto';
import { FILTERS, PaneHeader, Scroll, fmtDate, fmtTime, isOpenOrder, matchesFilter, paymentLabel, type OrderFilter } from './shared';

const PAGE = 10;

function StarRating({ value, onChange }: { value: number; onChange: (n: number) => void }) {
  return <div role="radiogroup" aria-label="Rating" className="flex gap-1">{[1, 2, 3, 4, 5].map(n => <button key={n} type="button" role="radio" aria-checked={value === n} aria-label={`${n} ${n === 1 ? 'star' : 'stars'}`} tabIndex={value === n ? 0 : -1} className="p-1 rounded-full hover:bg-sunk" onClick={() => onChange(n)} onKeyDown={e => { if (e.key === 'ArrowRight' || e.key === 'ArrowUp') { e.preventDefault(); onChange(Math.min(5, value + 1)); } if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') { e.preventDefault(); onChange(Math.max(1, value - 1)); } }}><Star size={24} className={n <= value ? 'fill-ink text-ink' : 'text-line-strong'} /></button>)}</div>;
}

export function orderMatches(o: Order, q: string) {
  if (!q) return true;
  const hay = [o.id, o.merchant_name, o.product_name, ...orderItems(o).map(i => i.product_name || i.name || '')].join(' ').toLowerCase();
  return q.toLowerCase().split(/\s+/).every(t => hay.includes(t));
}

export function OrdersPanel({ orders, query, onChanged, onError, onInfo, onDeliver }: {
  orders: Order[]; query: string; onChanged: () => Promise<void> | void; onError: (m: string) => void; onInfo: (m: string) => void; onDeliver: (orderId: string) => void;
}) {
  const [filter, setFilter] = useState<OrderFilter>('all');
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [page, setPage] = useState(0);
  const [open, setOpen] = useState('');
  const [reviewing, setReviewing] = useState('');
  const [rating, setRating] = useState(5);
  const [body, setBody] = useState('');
  const [busy, setBusy] = useState('');
  const cart = useCart();
  const cartRef = useRef(cart);
  cartRef.current = cart;
  const navigate = useNavigate();

  const counts = useMemo(() => Object.fromEntries(FILTERS.map(f => [f.id, orders.filter(o => orderMatches(o, query) && matchesFilter(o, f.id)).length])) as Record<OrderFilter, number>, [orders, query]);
  const rows = useMemo(() => orders.filter(o => orderMatches(o, query) && matchesFilter(o, filter)
    && (!from || o.created_at.slice(0, 10) >= from) && (!to || o.created_at.slice(0, 10) <= to)), [orders, query, filter, from, to]);
  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const current = Math.min(page, pages - 1);
  const shown = rows.slice(current * PAGE, current * PAGE + PAGE);

  async function reorder(order: Order) {
    setBusy(order.id); onError('');
    try {
      const lines = orderItems(order);
      const details = await Promise.all(lines.map(l => api<Product>(`/products/${encodeURIComponent(l.product_id)}`)));
      const catalog = [...details];
      for (const item of cartRef.current.items) if (!catalog.some(p => p.id === item.product_id)) catalog.push(await api<Product>(`/products/${encodeURIComponent(item.product_id)}`));
      for (let i = 0; i < lines.length; i++) {
        if (!details[i].in_stock) { onError(`${details[i].name} is out of stock right now. Added what is available.`); continue; }
        for (let n = 0; n < lines[i].quantity; n++) {
          await new Promise(r => setTimeout(r, 40));
          const message = cartRef.current.add(details[i], catalog);
          if (message) { onError(message); break; }
        }
      }
      navigate('/basket');
    } catch (issue) { onError(messageOf(issue)); } finally { setBusy(''); }
  }

  const clear = <button className="pf-link text-[13px]" onClick={() => { setFilter('all'); setFrom(''); setTo(''); setPage(0); }}>Clear filters</button>;
  return <div className="flex flex-col h-full min-h-0">
    <PaneHeader title="Orders" hint={`${rows.length} of ${orders.length} orders`} right={<div className="grid grid-cols-2 sm:flex items-center gap-2 text-[13px] text-muted w-full sm:w-auto">
      <label className="flex items-center gap-1.5 min-w-0">From<input className="pf-input sm min-w-0 w-full" type="date" aria-label="From date" value={from} max={to || undefined} onChange={e => { setFrom(e.target.value); setPage(0); }} /></label>
      <label className="flex items-center gap-1.5 min-w-0">To<input className="pf-input sm min-w-0 w-full" type="date" aria-label="To date" value={to} min={from || undefined} onChange={e => { setTo(e.target.value); setPage(0); }} /></label>
    </div>} />
    <div className="flex gap-2 overflow-x-auto px-4 sm:px-5 py-3 border-b border-line" role="group" aria-label="Filter orders by status">
      {FILTERS.map(f => <button key={f.id} type="button" aria-pressed={filter === f.id} onClick={() => { setFilter(f.id); setPage(0); }}
        className={`shrink-0 h-11 md:h-8 px-3 rounded-full text-[13px] font-semibold border transition-colors ${filter === f.id ? 'bg-ink text-white border-ink' : 'border-line-strong text-ink-2 hover:bg-sunk'}`}>{f.label} <span className={filter === f.id ? 'opacity-70' : 'text-muted'}>{counts[f.id]}</span></button>)}
    </div>
    <Scroll>
      {!shown.length ? (orders.length ? <Empty search title="No matching orders" description="Try another search, status or date range.">{clear}</Empty>
        : <Empty description="Reserve products from a nearby store to start."><Link className="pf-btn" to="/explore">Find products</Link></Empty>)
        : <ul className="divide-y divide-line" data-testid="order-list">{shown.map(order => {
          const expanded = open === order.id;
          const items = orderItems(order);
          const slot = order.pickup_window || order.pickup || order.pickup_slot;
          return <li key={order.id} data-testid={`order-row-${order.id}`}>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 sm:px-5 py-3">
              <div className="w-10 h-10 shrink-0 rounded-md overflow-hidden bg-canvas"><ProductPhoto name={order.product_name} imageUrl={order.items?.[0]?.image_url} merchantId={order.merchant_id} /></div>
              <button type="button" className="flex-1 min-w-[170px] text-left rounded-md hover:bg-sunk/60 transition-colors" aria-expanded={expanded} onClick={() => setOpen(expanded ? '' : order.id)} data-testid={`order-toggle-${order.id}`}>
                <span className="block text-sm font-semibold leading-snug truncate">{order.product_name}{items.length > 1 ? ` + ${items.length - 1} more` : ''}</span>
                <span className="block text-[12.5px] text-muted truncate">{order.merchant_name} · {fmtDate(order.created_at)} · <span className="font-mono text-[11.5px]">{order.id.slice(-8)}</span></span>
              </button>
              <OrderStatus order={order} />
              <strong className="font-display text-base tabular w-20 text-right">{cash(order.amount_cents, order.currency)}</strong>
              <div className="flex items-center gap-1.5">
                <Link className="pf-btn sm outline" to={`/checkout/${order.id}`}>View order</Link>
                {order.can_review && <button className="pf-btn sm" onClick={() => { setReviewing(order.id); setOpen(order.id); }}>Leave review</button>}
                <button className="pf-btn sm ghost icon" aria-expanded={expanded} aria-label={expanded ? 'Hide details' : 'Show details'} onClick={() => setOpen(expanded ? '' : order.id)}><ChevronDown size={16} className={`transition-transform ${expanded ? 'rotate-180' : ''}`} /></button>
              </div>
            </div>
            {expanded && <div className="px-4 sm:px-5 pb-4 bg-canvas pf-enter">
              <div className="grid md:grid-cols-2 gap-x-8 gap-y-3 pt-3">
                <ul className="divide-y divide-line">{items.map(item => <li className="flex items-center justify-between gap-4 py-2 text-sm" key={item.product_id}><span>{item.product_name || item.name} <span className="text-muted">× {item.quantity}</span></span>{item.amount_cents != null && <span className="tabular">{cash(item.amount_cents, order.currency)}</span>}</li>)}
                  <li className="flex justify-between py-2 text-sm font-semibold"><span>Total</span><span className="tabular">{cash(order.amount_cents, order.currency)}</span></li></ul>
                <dl className="text-[13px] grid grid-cols-[110px_1fr] gap-y-1.5 content-start">
                  <dt className="text-muted">Payment</dt><dd>{paymentLabel(order)}</dd>
                  <dt className="text-muted">Pickup window</dt><dd>{slot ? `${fmtDate(slot.start_at, false)}, ${fmtTime(slot.start_at)} to ${fmtTime(slot.end_at)}` : order.status === 'READY' ? 'Ready now at the counter' : 'Not booked'}</dd>
                  <dt className="text-muted">Store</dt><dd>{order.merchant_name}{(order as Order & { location_name?: string }).location_name ? `, ${(order as Order & { location_name?: string }).location_name}` : ''}</dd>
                  <dt className="text-muted">Order id</dt><dd className="font-mono text-[12px] break-all">{order.id}</dd>
                </dl>
              </div>
              <div className="flex flex-wrap gap-2 mt-3">
                <div className="w-full"><OrderTracker order={order} /></div>
                {order.payment_status === 'CAPTURED' && <div className="w-full"><InvoiceStatus orderId={order.id} /></div>}
                <button className="pf-btn sm outline" disabled={busy === order.id} onClick={() => void reorder(order)}><RotateCcw size={14} />{busy === order.id ? 'Adding…' : 'Reorder'}</button>
                <button className="pf-btn sm outline" onClick={() => printInvoice(order)}><Printer size={14} />Print invoice</button>
                <button className="pf-btn sm outline" onClick={() => downloadInvoice(order)}><Download size={14} />Download invoice</button>
                {isOpenOrder(order) && <button className="pf-btn sm outline" onClick={() => onDeliver(order.id)}><Truck size={14} />Get it delivered</button>}
                <Link className="pf-btn sm outline" to={`/account/messages?merchant=${encodeURIComponent(order.merchant_id)}&order=${encodeURIComponent(order.id)}`}><MessageCircle size={14} />Message store</Link>
              </div>
              {reviewing === order.id && <form className="border-t border-line mt-3 pt-4 space-y-3 max-w-xl" onSubmit={async e => { e.preventDefault(); setBusy(order.id); onError(''); try { await post('/reviews', { order_id: order.id, rating, body }); setReviewing(''); setBody(''); onInfo('Review submitted. Thank you.'); await onChanged(); } catch (issue) { onError(messageOf(issue)); } finally { setBusy(''); } }}>
                <div className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Rating</span><StarRating value={rating} onChange={setRating} /></div>
                <TextAreaField label="Your pickup experience" value={body} maxLength={1500} onChange={e => setBody(e.target.value)} />
                <div className="flex gap-2"><button className="pf-btn sm" disabled={busy === order.id}>{busy === order.id ? 'Submitting…' : 'Submit review'}</button><button type="button" className="pf-btn sm ghost" onClick={() => setReviewing('')}>Cancel</button></div>
              </form>}
            </div>}
          </li>;
        })}</ul>}
    </Scroll>
    {rows.length > PAGE && <nav className="flex items-center justify-between gap-3 px-4 sm:px-5 py-2.5 border-t border-line text-[13px]" aria-label="Order pages">
      <span className="text-muted">{current * PAGE + 1} to {Math.min(rows.length, current * PAGE + PAGE)} of {rows.length}</span>
      <div className="flex items-center gap-1"><button className="pf-btn sm ghost icon" aria-label="Previous page" disabled={current === 0} onClick={() => setPage(current - 1)}><ChevronLeft size={16} /></button><span className="tabular px-2">Page {current + 1} of {pages}</span><button className="pf-btn sm ghost icon" aria-label="Next page" disabled={current >= pages - 1} onClick={() => setPage(current + 1)}><ChevronRight size={16} /></button></div>
    </nav>}
  </div>;
}
