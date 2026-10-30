import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Clock, Plug, ShoppingBag, Store } from 'lucide-react';
import { cash } from '../lib/api';
import type { PosLive } from '../lib/pos';

const time = (value?: string | null) => value ? new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Not yet';
const when = (value?: string | null) => value ? new Date(value).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '';
const label = (value: string) => value.replaceAll('_', ' ').toLowerCase().replace(/^\w/, c => c.toUpperCase());

export function LiveBadge({ updatedAt, error }: { updatedAt: number | null; error: boolean }) {
  const [, tick] = useState(0);
  useEffect(() => { const timer = window.setInterval(() => tick(n => n + 1), 1000); return () => window.clearInterval(timer); }, []);
  const age = updatedAt ? Math.round((Date.now() - updatedAt) / 1000) : null;
  const stale = error || age === null || age > 20;
  return <span className={`pos-live ${stale ? 'stale' : ''}`} role="status" data-testid="pos-live-indicator"><i />{error || (age !== null && age > 20) ? 'Reconnecting' : age === null ? 'Connecting' : 'Live'}<small>{updatedAt ? `updated ${time(new Date(updatedAt).toISOString())}` : 'waiting for data'}</small></span>;
}

export type FeedItem = { id: number; at: number; text: string };

/** Diffs consecutive polls of the store snapshot into a short, human activity feed. */
export function useLiveFeed(live: PosLive | undefined): FeedItem[] {
  const previous = useRef<PosLive | null>(null);
  const counter = useRef(0);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  useEffect(() => {
    if (!live) return;
    const before = previous.current; previous.current = live;
    if (!before) return;
    const found: string[] = [];
    const stock = new Map(before.products.map(p => [p.id, p]));
    live.products.forEach(p => { const old = stock.get(p.id); if (old && old.quantity !== p.quantity) found.push(`Stock changed: ${p.name} ${old.quantity} to ${p.quantity}`); else if (old && old.held !== p.held) found.push(`Online hold changed: ${p.name} now ${p.held} held`); });
    const seen = new Map(before.orders.map(o => [o.id, o]));
    live.orders.forEach(o => { const old = seen.get(o.id); if (!old) found.push(o.kind === 'reservation' ? `New online reservation: ${o.quantity} x ${o.product_name} for ${o.buyer_name}` : `New online order: ${o.product_name} (${label(o.status)})`); else if (old.kind !== o.kind) found.push(`Online order ${o.product_name} is now ${o.kind === 'paid' ? 'paid' : 'closed'}`); });
    if (found.length) setFeed(current => [...found.map(text => ({ id: ++counter.current, at: Date.now(), text })), ...current].slice(0, 30));
  }, [live]);
  return feed;
}

export function LiveStrip({ live, pending, conflicts }: { live: PosLive; pending: number; conflicts: number }) {
  return <div className="pos-live-grid" data-testid="pos-live-strip">
    <section><span>Online reservations</span><strong>{live.reservation_count}</strong><small>Held for shoppers right now</small></section>
    <section><span>Captured online</span><strong>{cash(live.captured_cents)}</strong><small>{live.captured_count} paid order{live.captured_count === 1 ? '' : 's'} · read-only</small></section>
    <section><span>Pending sync events</span><strong>{pending}</strong><small>{conflicts ? `${conflicts} conflict${conflicts > 1 ? 's' : ''} need review` : 'No conflicts'}</small></section>
    <section><span>Store catalogue</span><strong>{live.products.length}</strong><small>{live.products.filter(p => p.available <= 3).length} low on stock</small></section>
  </div>;
}

export function FeedPanel({ feed }: { feed: FeedItem[] }) {
  return <section className="pos-panel"><div className="pos-panel-heading"><h2>Live activity</h2><span>since you opened this page</span></div>
    {feed.length ? <div className="pos-feed" data-testid="pos-live-feed">{feed.map(item => <article key={item.id}><span>{item.text}</span><small>{time(new Date(item.at).toISOString())}</small></article>)}</div>
      : <p className="pos-muted-note">Waiting for changes. Stock updates, counter sales and new shopper reservations appear here as they happen.</p>}</section>;
}

export function OnlineOrders({ live }: { live: PosLive }) {
  const [filter, setFilter] = useState<'all' | 'reservation' | 'paid'>('all');
  const rows = live.orders.filter(o => filter === 'all' || o.kind === filter).slice(0, 24);
  return <>
    <div className="pos-overview-controls"><h2>{live.reservation_count} open reservation{live.reservation_count === 1 ? '' : 's'}</h2>
      <div className="pos-segmented">{([['all', 'All'], ['reservation', 'Reservations'], ['paid', 'Paid']] as const).map(([key, text]) => <button key={key} className={filter === key ? 'active' : ''} onClick={() => setFilter(key)}>{text}</button>)}</div></div>
    {rows.length ? <div className="pos-online-orders" data-testid="pos-online-orders">{rows.map(order => <article className="pos-panel" key={order.id} data-testid="pos-online-order">
      <span className="pos-eyebrow">{order.kind === 'reservation' ? 'RESERVED ONLINE' : order.kind === 'paid' ? 'PAID ONLINE' : 'CLOSED'}</span>
      <h3>{order.product_name}</h3><p>{order.buyer_name} · {order.quantity} item{order.quantity > 1 ? 's' : ''}{order.branch ? ` · ${order.branch}` : ''}</p>
      <div><span className={`pos-status ${order.kind === 'reservation' ? 'amber' : order.kind === 'closed' ? 'red' : ''}`}>{order.kind === 'reservation' && order.hold_expires_at ? `Held until ${when(order.hold_expires_at)}` : label(order.status)}</span><strong>{cash(order.amount_cents, order.currency)}</strong></div>
      <small>{order.id} · {when(order.created_at)}</small><Link to={`/checkout/${order.id}`}>View order <ArrowUpRight size={14} /></Link></article>)}</div>
      : <div className="pos-empty"><ShoppingBag size={32} /><h3>No online orders here yet</h3><p>When a shopper reserves an item from {live.products.length ? 'this store' : 'the storefront'} on the Browse page, it appears here within a few seconds.</p><Link className="pos-button" to="/browse">Open Browse <ArrowUpRight size={15} /></Link></div>}
  </>;
}

export function StoreCatalogue({ live }: { live: PosLive }) {
  if (!live.products.length) return <div className="pos-empty"><Store size={32} /><h3>No products in this store yet</h3><p>Add products or connect a POS in the merchant workspace, then they appear here.</p><Link className="pos-button" to="/merchant">Open workspace <ArrowUpRight size={15} /></Link></div>;
  return <div className="pos-table-wrap"><table className="pos-plain-table" data-testid="pos-store-catalogue"><thead><tr><th>Product</th><th>Branch</th><th>Price</th><th>On hand</th><th>Held online</th><th>Available</th></tr></thead>
    <tbody>{live.products.map(p => <tr key={p.id}><td><strong>{p.name}</strong><br /><small>{p.sku}</small></td><td>{p.branch || 'Main'}</td><td>{cash(p.price_cents, p.currency)}</td><td>{p.quantity}</td><td>{p.held}</td><td><span className={`pos-status ${p.available <= 3 ? 'amber' : ''}`}>{p.available}</span></td></tr>)}</tbody></table></div>;
}

export function ConnectionLive({ live }: { live: PosLive }) {
  const plugin = live.plugin;
  return <div className="pos-two">
    <section className="pos-panel"><div className="pos-panel-heading"><h2>POS plugin connection</h2><Plug size={18} /></div>
      {plugin ? <dl className="pos-kv"><div><dt>Connector</dt><dd>{plugin.name} · {plugin.mode === 'push' ? 'push events' : 'pull API'}</dd></div><div><dt>Status</dt><dd><span className={`pos-status ${plugin.status === 'connected' || plugin.status === 'syncing' ? '' : 'amber'}`}>{label(plugin.status)}</span></dd></div><div><dt>Last sync</dt><dd>{plugin.last_synced_at ? when(plugin.last_synced_at) : 'Not yet'}</dd></div>{plugin.last_error && <div><dt>Last error</dt><dd>{plugin.last_error}</dd></div>}</dl>
        : <p className="pos-muted-note">No external POS plugin is connected to this store. This simulator is the bridge stand-in. To link a real till, add it in Connections.</p>}
      {!plugin && <Link className="pos-button" to="/merchant/connections">Open Connections <ArrowUpRight size={15} /></Link>}</section>
    <section className="pos-panel"><div className="pos-panel-heading"><h2>Pickup windows</h2><Clock size={18} /></div>
      {live.pickup_slots.length ? <div className="pos-feed" data-testid="pos-pickup-slots">{live.pickup_slots.map(s => <article key={s.id}><span>{when(s.start_at)} to {time(s.end_at).slice(0, 5)}{s.branch ? ` · ${s.branch}` : ''}</span><small>{s.booked}/{s.capacity} booked</small></article>)}</div>
        : <p className="pos-muted-note">No upcoming pickup windows. Shoppers reserve for pickup once the store publishes windows in the merchant workspace.</p>}</section>
  </div>;
}
