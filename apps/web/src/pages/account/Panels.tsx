import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Copy, Star, Trash2 } from 'lucide-react';
import { api, cash, messageOf, post, remove, type Order, type Product } from '../../lib/api';
import { useCart } from '../../lib/cart';
import { useResource } from '../../lib/use-resource';
import { Chip, Empty, Notice, Spinner } from '../../components/Shared';
import { PriceAlerts } from '../../components/PriceWatch';
import { ProductPhoto } from '../../components/ProductPhoto';
import { PaneHeader, Quiet, Scroll, fmtDate, isOpenOrder, type Coupon, type DeliveryReq, type MyReview, type Profile, type Provider, type WishItem } from './shared';

type Notify = { onError: (m: string) => void; onInfo: (m: string) => void };

export function WishlistPanel({ items, query, refresh, loading, onError, onInfo }: Notify & { items: WishItem[]; query: string; refresh: () => Promise<void>; loading: boolean }) {
  const cart = useCart();
  const cartRef = useRef(cart);
  cartRef.current = cart;
  const navigate = useNavigate();
  const [busy, setBusy] = useState('');
  const q = query.toLowerCase();
  const rows = items.filter(i => !q || `${i.name} ${i.merchant_name} ${i.category}`.toLowerCase().includes(q));
  async function toBasket(item: WishItem) {
    setBusy(item.product_id); onError('');
    try {
      const product = await api<Product>(`/products/${encodeURIComponent(item.product_id)}`);
      const catalog = [product];
      for (const x of cartRef.current.items) if (x.product_id !== product.id) catalog.push(await api<Product>(`/products/${encodeURIComponent(x.product_id)}`));
      const message = cartRef.current.add(product, catalog);
      if (message) onError(message); else navigate('/basket');
    } catch (issue) { onError(messageOf(issue)); } finally { setBusy(''); }
  }
  async function drop(item: WishItem) {
    try { await remove(`/me/wishlist/${encodeURIComponent(item.product_id)}`); onInfo(`${item.name} removed from your wishlist.`); await refresh(); } catch (issue) { onError(messageOf(issue)); }
  }
  return <div className="flex flex-col h-full min-h-0">
    <PaneHeader title="Wishlist" hint="Prices and stock are checked live each time you open this page." />
    <Scroll>{loading ? <Spinner /> : !rows.length ? <Empty search={Boolean(q)} title={q ? 'No saved items match' : 'Nothing saved yet'} description="Save products from a product page and we will flag price drops and restocks here."><Link className="pf-btn" to="/explore">Browse products</Link></Empty>
      : <ul className="grid sm:grid-cols-2 2xl:grid-cols-3 gap-3 p-4 sm:p-5">{rows.map(item => <li key={item.id} className="pf-card p-3 flex gap-3" data-testid={`wish-${item.product_id}`}>
        <div className="w-16 h-16 shrink-0 rounded-md overflow-hidden bg-canvas"><ProductPhoto name={item.name} imageUrl={item.image_url} merchantId={item.merchant_id} /></div>
        <div className="min-w-0 flex-1">
          <Link to={`/products/${item.product_id}`} className="text-sm font-semibold leading-snug hover:underline line-clamp-2 pf-wish-title">{item.name}</Link>
          <p className="text-[12.5px] text-muted truncate">{item.merchant_name}</p>
          <div className="flex flex-wrap items-center gap-1.5 mt-1.5"><strong className="font-display tabular">{cash(item.price_cents, item.currency)}</strong>
            {item.price_dropped && <><span className="text-[12px] text-muted line-through tabular">{cash(item.saved_price_cents, item.currency)}</span><Chip kind="green">Price dropped</Chip></>}
            {item.back_in_stock && <Chip kind="blue">Back in stock</Chip>}
            {!item.in_stock && <Chip kind="amber">Out of stock</Chip>}
            {item.in_stock && !item.back_in_stock && !item.price_dropped && <span className="text-[12px] text-muted">{item.available_quantity} available</span>}</div>
          <div className="flex gap-1.5 mt-2"><button className="pf-btn sm" disabled={!item.in_stock || busy === item.product_id} onClick={() => void toBasket(item)}>{busy === item.product_id ? 'Adding…' : 'Add to basket'}</button>
            <button className="pf-btn sm ghost icon" aria-label={`Remove ${item.name} from wishlist`} onClick={() => void drop(item)}><Trash2 size={15} /></button></div>
        </div></li>)}</ul>}<PriceAlerts /></Scroll>
  </div>;
}

export function CouponsPanel({ query }: { query: string }) {
  const res = useResource<{ coupons: Coupon[]; note: string }>('/me/coupons');
  const [copied, setCopied] = useState('');
  const q = query.toLowerCase();
  const rows = (res.data?.coupons || []).filter(c => !q || `${c.code} ${c.title} ${c.category}`.toLowerCase().includes(q));
  const days = (c: Coupon) => Math.max(0, Math.ceil((new Date(c.expires_at).getTime() - Date.now()) / 86400000));
  return <div className="flex flex-col h-full min-h-0">
    <PaneHeader title="Coupons" hint="Demo codes. Informational only: checkout does not apply discounts in this demo, so no price changes." />
    <Scroll className="p-4 sm:p-5">{res.loading ? <Spinner /> : !rows.length ? <Empty search title="No coupons match" description="Try another search." />
      : <ul className="grid md:grid-cols-2 xl:grid-cols-3 gap-3">{rows.map(c => <li key={c.code} className="pf-card p-4 flex flex-col gap-2" data-testid={`coupon-${c.code}`}>
        <div className="flex items-start justify-between gap-2"><span className="font-display text-2xl leading-none">{c.kind === 'percent' ? `${c.value}%` : cash(c.value)} off</span><Chip kind={days(c) <= 7 ? 'amber' : 'default'}>{days(c) <= 7 ? `Ends in ${days(c)} days` : `Valid until ${fmtDate(c.expires_at)}`}</Chip></div>
        <div><h3 className="text-sm font-semibold">{c.title}</h3><p className="text-[13px] text-muted">{c.detail}</p><p className="text-[12.5px] text-muted mt-1">{c.category} · min spend {cash(c.min_spend_cents)}</p></div>
        <div className="flex items-center justify-between gap-2 mt-auto pt-2 border-t border-line"><code className="font-mono text-sm font-semibold tracking-wide">{c.code}</code>
          <button className="pf-btn sm outline" onClick={() => { void navigator.clipboard?.writeText(c.code).catch(() => undefined); setCopied(c.code); window.setTimeout(() => setCopied(''), 1800); }}><Copy size={14} />{copied === c.code ? 'Copied' : 'Copy code'}</button></div>
      </li>)}</ul>}
      {res.error && <p className="text-sm text-bad mt-3">{res.error}</p>}</Scroll>
  </div>;
}

export function ReviewsPanel({ reviews, orders, query, loading, onReview }: { reviews: MyReview[]; orders: Order[]; query: string; loading: boolean; onReview: (orderId: string) => void }) {
  const q = query.toLowerCase();
  const done = reviews.filter(r => !q || `${r.merchant_name} ${r.product_name} ${r.body}`.toLowerCase().includes(q));
  const todo = orders.filter(o => o.can_review && (!q || `${o.merchant_name} ${o.product_name}`.toLowerCase().includes(q)));
  return <div className="flex flex-col h-full min-h-0">
    <PaneHeader title="Reviews" hint={`${reviews.length} written · ${orders.filter(o => o.can_review).length} waiting for your review`} />
    <Scroll className="p-4 sm:p-5 grid grid-cols-[minmax(0,1fr)] gap-6 content-start lg:grid-cols-2 lg:items-start">
      <section aria-label="To review"><h3 className="text-sm font-semibold mb-2">To review</h3>
        {!todo.length ? <Quiet>Nothing waiting. Collected orders appear here until you review them.</Quiet> : <ul className="pf-card divide-y divide-line">{todo.map(o => <li key={o.id} className="flex items-center justify-between gap-3 p-3"><div className="min-w-0"><p className="text-sm font-medium truncate">{o.product_name}</p><p className="text-[12.5px] text-muted truncate">{o.merchant_name} · {fmtDate(o.created_at)}</p></div><button className="pf-btn sm" onClick={() => onReview(o.id)}>Leave review</button></li>)}</ul>}</section>
      <section aria-label="Your reviews"><h3 className="text-sm font-semibold mb-2">Your reviews</h3>
        {loading ? <Spinner inline /> : !done.length ? <Quiet>{q ? 'No reviews match your search.' : 'You have not written a review yet.'}</Quiet> : <ul className="space-y-3">{done.map(r => <li key={r.id} className="pf-card p-3.5" data-testid={`review-${r.id}`}>
          <div className="flex items-center justify-between gap-2"><span className="flex" aria-label={`${r.rating} out of 5`}>{[1, 2, 3, 4, 5].map(n => <Star key={n} size={14} className={n <= r.rating ? 'fill-ink text-ink' : 'text-line-strong'} />)}</span><span className="text-[12px] text-muted">{fmtDate(r.created_at)}</span></div>
          <p className="text-sm font-medium mt-1.5">{r.merchant_name}{r.product_name ? <span className="text-muted font-normal"> · {r.product_name}</span> : null}</p>
          {r.body && <p className="text-[13.5px] text-ink-2 mt-1">{r.body}</p>}</li>)}</ul>}</section>
    </Scroll>
  </div>;
}

export function DeliveryPanel({ orders, preselect, onError, onInfo }: Notify & { orders: Order[]; preselect: string }) {
  const providers = useResource<{ providers: Provider[]; note: string }>('/delivery/providers');
  const requests = useResource<{ requests: DeliveryReq[] }>('/me/delivery-requests');
  const profile = useResource<Profile>('/me/profile');
  const eligible = orders.filter(isOpenOrder);
  const [mode, setMode] = useState<'pickup' | 'courier'>(preselect ? 'courier' : 'pickup');
  const [orderId, setOrderId] = useState(preselect || '');
  const [provider, setProvider] = useState('');
  const [address, setAddress] = useState('');
  const [notes, setNotes] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (preselect) { setOrderId(preselect); setMode('courier'); } }, [preselect]);
  const chosen = eligible.find(o => o.id === orderId) || eligible[0];
  const open = requests.data?.requests.filter(r => r.status === 'requested') || [];
  const saved = profile.data?.addresses || [];
  async function submit(e: React.FormEvent) {
    e.preventDefault(); if (!chosen) return;
    setBusy(true); onError('');
    try { await post(`/orders/${chosen.id}/delivery-request`, { provider_id: provider, address, notes }); onInfo('Quote requested. This is a local demo record: no courier was contacted and no money moved.'); await requests.refresh(); setNotes(''); }
    catch (issue) { onError(messageOf(issue)); } finally { setBusy(false); }
  }
  async function cancel(id: string) {
    try { await api(`/orders/${id}/delivery-request`, { method: 'DELETE' }); await requests.refresh(); } catch (issue) { onError(messageOf(issue)); }
  }
  return <div className="flex flex-col h-full min-h-0">
    <PaneHeader title="Get it delivered" hint="Pickup stays the default. If you cannot collect, ask a delivery service to bring it." right={<div className="pf-segmented" role="group" aria-label="Delivery method"><button aria-pressed={mode === 'pickup'} onClick={() => setMode('pickup')}>Pickup yourself</button><button aria-pressed={mode === 'courier'} onClick={() => setMode('courier')}>Hire a courier</button></div>} />
    <Scroll className="p-4 sm:p-5 grid grid-cols-[minmax(0,1fr)] gap-6 content-start lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)] lg:items-start">
      {mode === 'pickup' ? <div className="pf-card p-4 lg:col-span-2"><h3 className="text-sm font-semibold">Pickup yourself</h3><Quiet>You collect the order from the store in your pickup window. Nothing else to set up. Switch to "Hire a courier" to request a quote for an active order.</Quiet></div> : <>
        <form onSubmit={e => void submit(e)} className="space-y-4" aria-label="Delivery quote request">
          <Notice tone="amber">{providers.data?.note || 'Demo provider list. Connect a real provider (e.g. Lalamove, Grab Express, Uber Direct) via their API to activate.'}</Notice>
          {!eligible.length ? <Quiet>No active orders to deliver. Place an order first.</Quiet> : <>
            <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Order</span><select className="pf-select" value={chosen?.id || ''} onChange={e => setOrderId(e.target.value)}>{eligible.map(o => <option key={o.id} value={o.id}>{o.merchant_name}: {o.product_name} ({cash(o.amount_cents, o.currency)})</option>)}</select></label>
            <fieldset className="space-y-2"><legend className="text-[13px] font-semibold text-ink-2 mb-1">Delivery provider (demo list)</legend>
              {(providers.data?.providers || []).map(p => <label key={p.id} className={`pf-card flex items-center gap-3 p-3 cursor-pointer ${provider === p.id ? 'border-ink' : ''}`}><input type="radio" name="provider" value={p.id} checked={provider === p.id} onChange={() => setProvider(p.id)} required /><span className="flex-1"><span className="text-sm font-semibold block">{p.name}</span><span className="text-[12.5px] text-muted">{p.vehicle} · {p.eta}</span></span><span className="text-[12.5px] text-muted">{p.indicative_fee}</span></label>)}</fieldset>
            <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Delivery address</span>
              {saved.length > 0 && <select className="pf-select mb-1.5" value="" aria-label="Use a saved address" onChange={e => { const a = saved.find(x => x.id === e.target.value); if (a) setAddress([a.line1, a.city, a.postal].filter(Boolean).join(', ')); }}><option value="">Use a saved address…</option>{saved.map(a => <option key={a.id} value={a.id}>{a.label}: {a.line1}</option>)}</select>}
              <input className="pf-input" required minLength={5} maxLength={300} value={address} onChange={e => setAddress(e.target.value)} placeholder="Street, city, postcode" /></label>
            <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Notes for the courier (optional)</span><input className="pf-input" maxLength={300} value={notes} onChange={e => setNotes(e.target.value)} /></label>
            <button className="pf-btn" disabled={busy || !provider}>{busy ? 'Requesting…' : 'Request a quote'}</button></>}
        </form>
        <section aria-label="Delivery requests"><h3 className="text-sm font-semibold mb-2">Your requests</h3>
          {requests.loading ? <Spinner inline /> : !requests.data?.requests.length ? <Quiet>No delivery requests yet.</Quiet> : <ul className="space-y-2">{requests.data.requests.map(r => <li key={r.id} className="pf-card p-3 text-sm" data-testid={`delivery-${r.id}`}>
            <div className="flex items-center justify-between gap-2"><strong>{r.provider_name}</strong><Chip kind={r.status === 'requested' ? 'blue' : 'default'}>{r.status === 'requested' ? 'Quote requested' : 'Cancelled'}</Chip></div>
            <p className="text-[12.5px] text-muted mt-1">Order {r.order_id.slice(-8)} · {r.address}</p>
            {r.status === 'requested' && <button className="pf-link text-[13px] mt-1" onClick={() => void cancel(r.order_id)}>Cancel request</button>}</li>)}</ul>}
          {open.length > 0 && <Quiet>Demo only: requests are stored locally; no courier is contacted.</Quiet>}</section></>}
    </Scroll>
  </div>;
}
