import { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingBag, Trash2 } from 'lucide-react';
import { cash, messageOf, post, type Order, type Product } from '../lib/api';
import { useApp } from '../lib/app-context';
import { useCart } from '../lib/cart';
import { groupByStore, savePending, type Group, type PendingReservation } from '../lib/basket';
import { useResource } from '../lib/use-resource';
import { Empty, ErrorLine, Field, Notice, Spinner } from '../components/Shared';
import { ProductPhoto } from '../components/ProductPhoto';
import { useBuyerName } from '../lib/use-buyer-name';

type Line = { product_id: string; quantity: number; product?: Product };
const lineBad = (x: Line) => !x.product || !x.product.in_stock || x.quantity > x.product.available_quantity || x.product.is_open === false;

export function Basket() {
  const cart = useCart();
  const { session, demo } = useApp();
  const catalog = useResource<Product[]>(cart.items.length ? `/products?radius_km=20040&ids=${cart.items.map(x => encodeURIComponent(x.product_id)).join(',')}` : null);
  const [buyerName, setBuyerName] = useBuyerName();
  const [busy, setBusy] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [notice, setNotice] = useState('');
  const lock = useRef(false);
  // One idempotency key per group + exact contents + name, so a retry of the same attempt cannot reserve twice.
  const intents = useRef(new Map<string, { fingerprint: string; key: string }>());
  const navigate = useNavigate();
  const lines: Line[] = cart.items.map(item => ({ product_id: item.product_id, quantity: item.quantity, product: catalog.data?.find(p => p.id === item.product_id) }));
  const groups = groupByStore(lines);
  const count = cart.items.reduce((sum, x) => sum + x.quantity, 0);
  const canReserve = Boolean(catalog.data) && !catalog.error && !busy;
  const groupBad = (g: Group<Line>) => g.merchant_id === '' || g.lines.some(lineBad);
  const groupTotal = (g: Group<Line>) => g.lines.reduce((sum, x) => sum + (x.product?.price_cents || 0) * x.quantity, 0);
  const anyBad = groups.some(groupBad);
  const storeNames = new Set(groups.map(g => g.merchant_id).filter(Boolean)).size;

  const pickupName = buyerName.trim() || 'Local shopper';

  async function reserveGroup(g: Group<Line>): Promise<Order> {
    const items = g.lines.map(x => ({ product_id: x.product_id, quantity: x.quantity }));
    const fingerprint = JSON.stringify({ items, buyer_name: pickupName });
    const known = intents.current.get(g.key);
    const intent = known && known.fingerprint === fingerprint ? known : { fingerprint, key: crypto.randomUUID() };
    intents.current.set(g.key, intent);
    const order = await post<Order>('/orders/reserve', { items, buyer_name: pickupName, idempotency_key: intent.key });
    cart.remove(items.map(x => x.product_id));
    return order;
  }

  async function run(targets: Group<Line>[], form: HTMLFormElement | null, payNow = false) {
    if (lock.current || !canReserve || !targets.length) return;
    if (form && !form.reportValidity()) return;
    lock.current = true; setBusy(targets.length === 1 ? targets[0].key : 'all'); setErrors({}); setNotice('');
    const created: { order: Order; store: string }[] = [];
    const failed: Record<string, string> = {};
    for (const g of targets) {
      if (groupBad(g)) { failed[g.key] = 'Fix unavailable items in this group first.'; continue; }
      try { created.push({ order: await reserveGroup(g), store: g.lines[0].product?.merchant_name || 'Store' }); }
      catch (issue) { failed[g.key] = messageOf(issue); }
    }
    lock.current = false; setBusy('');
    if (Object.keys(failed).length) { setErrors(failed); void catalog.refresh(); }
    if (created.length) {
      savePending(created.slice(1).map<PendingReservation>(c => ({ id: c.order.id, store: c.store })));
      if (Object.keys(failed).length) setNotice(`${created.length} reserved, ${Object.keys(failed).length} failed. Review and pay for the reserved ones below.`);
      else navigate(`/checkout/${created[0].order.id}${payNow ? '?pay=1' : ''}`);
      if (Object.keys(failed).length) setReserved(created.map(c => ({ id: c.order.id, store: c.store })));
    }
  }
  const [reserved, setReserved] = useState<PendingReservation[]>([]);
  const header = (g: Group<Line>) => { const p = g.lines.find(x => x.product)?.product; return { store: p?.merchant_name || 'Unavailable items', branch: p?.location_name || '' }; };

  return <main className="pf-container py-8 sm:py-12">
    <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
      <div><h1 className="pf-heading">Your basket</h1>{cart.items.length > 0 && <p className="text-muted text-[15px] mt-2">{count} {count === 1 ? 'item' : 'items'} from {storeNames || 1} {storeNames === 1 ? 'store' : 'stores'}. Each store is reserved separately for its own pickup.</p>}</div>
      <div className="flex gap-3">{cart.items.length > 0 && <button className="pf-btn ghost" onClick={cart.clear} disabled={Boolean(busy)}>Clear basket</button>}<Link className="pf-btn outline" to="/explore">Keep exploring</Link></div>
    </div>
    {reserved.length > 0 && <div className="mb-6"><Notice tone="green"><p data-testid="basket-reserved">{notice}</p><ul className="mt-2 space-y-1">{reserved.map(r => <li key={r.id}><Link className="pf-link" to={`/checkout/${r.id}`}>{r.store}: review and pay</Link></li>)}</ul></Notice></div>}
    {!cart.items.length ? (reserved.length ? null : <Empty title="Your basket is empty" description="Find something nearby and add it to your basket."><Link className="pf-btn" to="/explore">Find nearby products</Link></Empty>) : catalog.loading ? <Spinner label="Checking basket availability…" /> : <>
      <div className="space-y-3 mb-6 empty:hidden">{catalog.error && <ErrorLine message={catalog.error} retry={catalog.refresh} />}{anyBad && catalog.data && <Notice tone="amber">Some items are unavailable. Remove them or adjust quantities before reserving that store.</Notice>}</div>
      <form className="grid grid-cols-[minmax(0,1fr)] lg:grid-cols-[minmax(0,1fr)_380px] xl:grid-cols-[minmax(0,1fr)_420px] gap-8 xl:gap-12 items-start" onSubmit={e => { e.preventDefault(); void run(groups, e.currentTarget); }}>
        <div className="space-y-6" aria-label="Basket items">
          {groups.map(g => { const { store, branch } = header(g); const err = errors[g.key]; const bad = groupBad(g);
            return <section key={g.key} className="pf-card overflow-hidden" data-testid={`basket-group-${g.merchant_id || 'unknown'}`} aria-label={`${store} items`}>
              <header className="flex flex-wrap items-baseline justify-between gap-2 px-5 sm:px-6 pt-5 pb-3 border-b border-line"><div><h2 className="pf-title">{store}</h2>{branch && <p className="text-[13px] text-muted mt-0.5">{branch}</p>}</div><span className="text-sm text-muted tabular">Subtotal <strong className="font-display text-lg text-ink">{cash(groupTotal(g), g.currency || undefined)}</strong></span></header>
              <ul className="px-5 sm:px-6">{g.lines.map(({ product_id, quantity, product }) => <li key={product_id} className="flex gap-4 sm:gap-5 py-5 border-b border-line last:border-b-0" data-testid={`cart-item-${product_id}`}>
                <div className="pf-line-photo !w-20 !h-20 sm:!w-24 sm:!h-24 !rounded-[var(--pf-r-lg)]"><ProductPhoto name={product?.name || 'Product'} imageUrl={product?.image_url} merchantId={product?.merchant_id} /></div>
                <div className="flex-1 min-w-0 flex flex-col">
                  <div className="flex items-start justify-between gap-4"><h3 className="text-base font-semibold leading-snug min-w-0">{product ? <Link className="hover:underline underline-offset-2" to={`/products/${product.id}`}>{product.name}</Link> : 'Product no longer listed'}</h3><strong className="font-display text-lg tabular shrink-0">{product ? cash(product.price_cents * quantity, product.currency) : 'Unavailable'}</strong></div>
                  {product && quantity > product.available_quantity && <p className="text-[13px] text-bad mt-1" role="alert">Only {product.available_quantity} units currently available.</p>}
                  <div className="mt-auto pt-3 flex items-center gap-3">
                    <select className="pf-select sm !w-[88px]" aria-label={`Quantity for ${product?.name || product_id}`} value={quantity} disabled={Boolean(busy)} onChange={e => cart.update(product_id, Number(e.target.value))}>{Array.from({ length: Math.min(10, Math.max(quantity, product?.available_quantity || 1)) }, (_, i) => <option key={i + 1}>{i + 1}</option>)}</select>
                    {product && quantity > 1 && <span className="text-[13px] text-muted tabular">{cash(product.price_cents, product.currency)} each</span>}
                    <button type="button" className="pf-btn ghost sm ml-auto" aria-label={`Remove ${product?.name || product_id}`} onClick={() => cart.update(product_id, 0)} disabled={Boolean(busy)}><Trash2 size={15} />Remove</button>
                  </div>
                </div>
              </li>)}</ul>
              <footer className="px-5 sm:px-6 py-4 bg-canvas border-t border-line flex flex-wrap items-center gap-3">
                {err && <p className="w-full text-sm text-bad" role="alert" data-testid={`reserve-error-${g.merchant_id || 'unknown'}`}>{g.lines[0].product?.merchant_name || 'This store'}: {err}</p>}
                {session || demo ? <button type="button" className="pf-btn lg" data-testid={`reserve-group-${g.merchant_id || 'unknown'}`} disabled={!canReserve || bad} onClick={e => void run([g], e.currentTarget.form)}><ShoppingBag size={16} />{busy === g.key ? 'Reserving…' : 'Reserve this store’s items'}</button> : <Link className="pf-btn lg" to="/login?next=%2Fbasket">Sign in to reserve</Link>}
                                {session || demo ? <button type="button" className="pf-btn accent lg" data-testid={`pay-group-${g.merchant_id || 'unknown'}`} disabled={!canReserve || bad} onClick={e => void run([g], e.currentTarget.form, true)}>Pay online & pick up</button> : null}

              </footer>
            </section>; })}
        </div>
        <aside className="pf-card p-6 sm:p-7 space-y-5 lg:sticky lg:top-24">
          <h2 className="pf-title">Order summary</h2>
          <dl className="space-y-2 text-sm">{groups.map(g => <div key={g.key} className="flex justify-between gap-3"><dt className="text-muted truncate">{header(g).store}</dt><dd className="tabular">{cash(groupTotal(g), g.currency || undefined)}</dd></div>)}<div className="flex justify-between"><dt className="text-muted">Pickup</dt><dd>Free, in store</dd></div></dl>
          {new Set(groups.map(g => g.currency).filter(Boolean)).size <= 1 && <div className="flex justify-between items-baseline pt-4 border-t border-line"><span className="font-semibold">Estimated total</span><strong className="font-display text-3xl tracking-tight tabular">{cash(groups.reduce((s, g) => s + groupTotal(g), 0), groups[0]?.currency || undefined)}</strong></div>}
          <Field label="Pickup name" autoComplete="name" maxLength={100} value={buyerName} onChange={e => setBuyerName(e.target.value)} data-testid="buyer-name" hint="Optional. Stores look for this name at pickup." />
          {session || demo ? groups.length === 1 && <button type="button" className="pf-btn accent lg w-full" data-testid="pay-basket" disabled={!canReserve || anyBad} onClick={e => void run(groups, e.currentTarget.form, true)}>Pay online & pick up</button> : null}
          {session || demo ? <button className="pf-btn lg w-full" data-testid="reserve-basket" disabled={!canReserve || anyBad}><ShoppingBag size={16} />{busy === 'all' ? 'Reserving…' : groups.length > 1 ? 'Reserve all stores' : 'Reserve basket & review total'}</button> : <Link className="pf-btn accent lg w-full" to="/login?next=%2Fbasket">Sign in to reserve</Link>}
          <p className="text-xs text-muted leading-relaxed">{groups.length > 1 ? 'Each store is a separate reservation with its own checkout. ' : ''}Estimate only: checkout shows the server-confirmed total. Reserving holds the items and does not charge you. {demo ? 'Holds apply to PayFound-owned sample stock only.' : 'Eligibility is checked against the store’s inventory by the server.'}</p>
        </aside>
      </form>
    </>}
  </main>;
}
