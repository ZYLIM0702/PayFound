import { Link } from 'react-router-dom';
import { Heart, Trash2 } from 'lucide-react';
import { cash } from '../../lib/api';
import type { Product } from '../../lib/api';
import { useCart } from '../../lib/cart';
import { groupByStore } from '../../lib/basket';
import { useResource } from '../../lib/use-resource';
import { Empty, ErrorLine, Notice, Spinner } from '../../components/Shared';
import { ProductPhoto } from '../../components/ProductPhoto';
import { Pane, PaneHeader, Scroll } from './shared';

/** The live basket (CartProvider). Reservation and payment stay in the Basket and Checkout pages. */
export function CartPanel({ query, savedCount }: { query: string; savedCount: number }) {
  const cart = useCart();
  const catalog = useResource<Product[]>(cart.items.length ? `/products?radius_km=20040&ids=${cart.items.map(x => encodeURIComponent(x.product_id)).join(',')}` : null);
  const q = query.toLowerCase();
  const lines = cart.items.map(item => ({ ...item, product: catalog.data?.find(p => p.id === item.product_id) }));
  const shown = lines.filter(l => !q || `${l.product?.name || ''} ${l.product?.merchant_name || ''}`.toLowerCase().includes(q));
  const estimate = lines.reduce((sum, l) => sum + (l.product?.price_cents || 0) * l.quantity, 0);
  const currency = lines.find(l => l.product)?.product?.currency || 'USD';
  const count = cart.items.reduce((sum, x) => sum + x.quantity, 0);
  const groups = groupByStore(shown);
  const stores = new Set(lines.map(l => l.product?.merchant_id).filter(Boolean));
  const invalid = lines.some(l => catalog.data && (!l.product || !l.product.in_stock || l.quantity > l.product.available_quantity || l.product.is_open === false));
  return <Pane>
    <PaneHeader title="Cart" hint={cart.items.length ? `${count} ${count === 1 ? 'item' : 'items'}${stores.size ? ` from ${stores.size} ${stores.size === 1 ? 'store' : 'stores'}` : ''}` : 'Your basket is empty'}
      right={cart.items.length > 0 ? <button className="pf-link text-[13px]" onClick={cart.clear}>Clear cart</button> : undefined} />
    <Scroll>
      {!cart.items.length ? <Empty title="Your cart is empty" description="Find something nearby and add it to your basket."><Link className="pf-btn" to="/explore">Find nearby products</Link><Link className="pf-btn outline" to="/account/wishlist">Saved for later ({savedCount})</Link></Empty>
        : catalog.loading ? <Spinner label="Checking availability…" /> : <div className="p-4 sm:p-5 space-y-4">
          <div className="empty:hidden space-y-2"><ErrorLine message={catalog.error} retry={catalog.refresh} />{invalid && <Notice tone="amber">Some items are unavailable Adjust them before checking out.</Notice>}</div>
          {groups.map(g => { const p = g.lines.find(l => l.product)?.product; return <section key={g.key} data-testid={`account-cart-group-${g.merchant_id || 'unknown'}`}>
            <h3 className="text-sm font-semibold mb-1">{p?.merchant_name || 'Unavailable items'}{p?.location_name && <span className="font-normal text-muted"> · {p.location_name}</span>}</h3>
            <ul className="divide-y divide-line border-y border-line" aria-label={`${p?.merchant_name || 'Unavailable'} items`}>{g.lines.map(({ product_id, quantity, product }) => <li key={product_id} className="flex gap-3 py-3" data-testid={`account-cart-${product_id}`}>
            <div className="w-16 h-16 shrink-0 rounded-md overflow-hidden bg-canvas"><ProductPhoto name={product?.name || 'Product'} imageUrl={product?.image_url} merchantId={product?.merchant_id} /></div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-3"><div className="min-w-0">
                {product ? <Link to={`/products/${product.id}`} className="text-sm font-semibold leading-snug hover:underline line-clamp-2 pf-wish-title">{product.name}</Link> : <span className="text-sm font-semibold">Product no longer listed</span>}
                <p className="text-[12.5px] text-muted truncate">{[product?.merchant_name, product?.location_name].filter(Boolean).join(' · ')}</p></div>
                <strong className="font-display tabular shrink-0">{product ? cash(product.price_cents * quantity, product.currency) : 'Unavailable'}</strong></div>
              {product && quantity > product.available_quantity && <p className="text-[12.5px] text-bad mt-0.5" role="alert">Only {product.available_quantity} available.</p>}
              <div className="flex items-center gap-2 mt-2">
                <select className="pf-select sm !w-[80px]" aria-label={`Quantity for ${product?.name || product_id}`} value={quantity} onChange={e => cart.update(product_id, Number(e.target.value))}>{Array.from({ length: Math.min(10, Math.max(quantity, product?.available_quantity || 1)) }, (_, i) => <option key={i + 1}>{i + 1}</option>)}</select>
                <button className="pf-btn ghost sm ml-auto" aria-label={`Remove ${product?.name || product_id}`} onClick={() => cart.update(product_id, 0)}><Trash2 size={15} />Remove</button></div>
            </div></li>)}</ul></section>; })}
          {!shown.length && <p className="text-sm text-muted">No cart items match your search.</p>}
          <Link to="/account/wishlist" className="pf-card interactive flex items-center gap-3 px-4 py-3 text-sm"><Heart size={16} /><span className="flex-1"><strong className="font-semibold">Saved for later</strong><span className="text-muted"> · {savedCount} {savedCount === 1 ? 'item' : 'items'} on your wishlist</span></span><span className="pf-link">Open</span></Link>
        </div>}
    </Scroll>
    {cart.items.length > 0 && !catalog.loading && <footer className="border-t border-line px-4 sm:px-5 py-3 flex flex-wrap items-center justify-between gap-3">
      <div><p className="text-[12.5px] text-muted">Subtotal estimate</p><p className="font-display text-xl tabular leading-tight">{cash(estimate, currency)}</p></div>
      <div className="flex items-center gap-3"><p className="text-[12.5px] text-muted max-w-[220px] hidden sm:block">Stock is checked and held when you reserve at the basket.</p><Link className="pf-btn accent" to="/basket" data-testid="account-cart-reserve">{stores.size > 1 ? 'Reserve by store' : 'Reserve basket'}</Link>
</div>
    </footer>}
  </Pane>;
}
