import { useState } from 'react';
import { Link } from 'react-router-dom';
import { cash, messageOf, post, scoped, type Dashboard, type Order } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { statusLabel, Chip, ErrorLine, OrderStatus as StatusChip, Skeleton } from '../Shared';

const LOW_STOCK_AT = 3;
const NEXT: Record<string, string> = { PAID: 'ACCEPTED', ACCEPTED: 'PREPARING', PREPARING: 'READY', READY: 'COLLECTED' };
const idOk = (s?: string) => Boolean(s && /^[a-zA-Z0-9_-]{1,64}$/.test(s));
const ago = (iso: string) => { const h = Math.round((Date.now() - Date.parse(iso)) / 3.6e6); return h < 1 ? 'under an hour ago' : h < 48 ? `${h} h ago` : `${Math.round(h / 24)} days ago`; };

export function KpiRowView({ props }: { props: { metrics?: { label?: string; value?: string; hint?: string | null; tone?: string | null }[] } }) {
  const metrics = (props.metrics || []).filter(m => m && m.label && m.value);
  if (!metrics.length) return null;
  return <div className="pf-ag-kpis">{metrics.map(m => <div key={m.label} className="pf-ag-kpi"><span className="text-[12px] font-semibold text-muted">{m.label}</span><strong className={`font-display text-[28px] leading-[1.1] tracking-tight tabular ${m.tone === 'warn' ? 'text-warn' : m.tone === 'bad' ? 'text-bad' : m.tone === 'ok' ? 'text-ok' : ''}`}>{m.value}</strong>{m.hint && <span className="text-[12px] text-subtle">{m.hint}</span>}</div>)}</div>;
}

export function StockAlertsView({ props }: { props: { merchantId?: string } }) {
  const id = idOk(props.merchantId) ? props.merchantId! : null;
  const dash = useResource<Dashboard>(id ? scoped('/merchant/dashboard', id) : null, 30000);
  if (!id) return null;
  const rows = (dash.data?.products || []).filter(p => p.active && (p.available_quantity <= LOW_STOCK_AT || p.freshness === 'stale')).sort((a, b) => a.available_quantity - b.available_quantity).slice(0, 8);
  return <section className="pf-ag-card" aria-label="Stock alerts"><h4 className="pf-ag-card-title">Stock that needs a count</h4>
    {dash.error && <ErrorLine message={dash.error} retry={dash.refresh} />}
    {dash.loading ? <Skeleton className="h-24 !rounded-[var(--pf-r-lg)]" /> : !rows.length ? <p className="text-sm text-muted">Nothing is low or out of date right now.</p>
      : <ul>{rows.map(p => <li key={p.id} className="pf-ag-order"><div className="min-w-0 flex-1"><p className="font-semibold text-[14px] truncate">{p.name}</p><p className="pf-ag-meta">{p.sku} · counted {ago(p.stock_updated_at)}</p></div>
        {p.available_quantity <= LOW_STOCK_AT ? <Chip kind="amber" dot>{p.available_quantity} left</Chip> : <Chip dot>Stale</Chip>}
        <Link className="pf-btn sm outline" to="/merchant/inventory">Record count</Link></li>)}</ul>}
  </section>;
}

export function MerchantOrderQueueView({ props }: { props: { merchantId?: string; status?: string | null } }) {
  const id = idOk(props.merchantId) ? props.merchantId! : null;
  const dash = useResource<Dashboard>(id ? scoped('/merchant/dashboard', id) : null, 15000);
  const [busy, setBusy] = useState('');
  const [issue, setIssue] = useState('');
  if (!id) return null;
  const open = (dash.data?.orders || []).filter(o => !['COLLECTED', 'CANCELLED', 'EXPIRED', 'REFUNDED'].includes(o.status) && (!props.status || o.status === props.status.toUpperCase())).slice(0, 8);
  const run = async (o: Order, path: string, body?: object) => {
    if (busy) return;
    setBusy(o.id); setIssue('');
    try { await post(`/orders/${o.id}/${path}`, body || {}); await dash.refresh(); } catch (e) { setIssue(messageOf(e)); } finally { setBusy(''); }
  };
  return <section className="pf-ag-card" aria-label="Order queue"><h4 className="pf-ag-card-title">Orders waiting on you</h4>
    {dash.error && <ErrorLine message={dash.error} retry={dash.refresh} />}{issue && <ErrorLine message={issue} />}
    {dash.loading ? <Skeleton className="h-24 !rounded-[var(--pf-r-lg)]" /> : !open.length ? <p className="text-sm text-muted">No open orders.</p>
      : <ul>{open.map(o => { const next = NEXT[o.status]; return <li key={o.id} className="pf-ag-order">
        <div className="min-w-0 flex-1"><p className="font-semibold text-[14px] truncate">{o.buyer_name || 'Customer'} · {cash(o.amount_cents, o.currency)}</p><p className="pf-ag-meta truncate">{(o.items?.length ? o.items.map(i => `${i.quantity} × ${i.product_name || i.name}`) : [`${o.quantity} × ${o.product_name}`]).join(', ')}</p></div>
        <StatusChip order={o} />
        {o.confirmation_status === 'PENDING' && o.status === 'RESERVED' ? <button className="pf-btn sm accent" disabled={Boolean(busy)} onClick={() => void run(o, 'confirm')}>Confirm stock</button>
          : next && o.payment_status === 'CAPTURED' ? <button className="pf-btn sm" disabled={Boolean(busy)} onClick={() => void run(o, 'fulfilment', { status: next })}>Mark {statusLabel(next).toLowerCase()}</button> : <Link className="pf-btn sm outline" to="/merchant/orders">Open</Link>}
      </li>; })}</ul>}
    <Link to="/merchant/orders" className="pf-link text-sm mt-3 inline-block">All orders →</Link>
  </section>;
}
