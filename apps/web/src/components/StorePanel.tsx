import { Link } from 'react-router-dom';
import { Clock3, MapPin, Navigation, ShieldCheck, ShoppingBag, Star, X } from 'lucide-react';
import { cash, type Merchant, type Product } from '../lib/api';
import { formatDistance, googleDirections } from '../lib/directions';
import { ProductPhoto } from './ProductPhoto';
import { ReserveCompact } from './ReserveProduct';

/**
 * Store card shown over the map when a store pin is clicked: store facts, a "Top pick"
 * (lowest in-stock price) and a scrollable list of what this store has in the current results.
 */
export function StorePanel({ store, products, distanceKm, onAdd, onClose }: {
  store: Merchant; products: Product[]; distanceKm: number | null; onAdd: (p: Product) => void; onClose: () => void;
}) {
  const inStock = products.filter(p => p.in_stock && p.available_quantity > 0);
  const top = [...inStock].sort((a, b) => a.price_cents - b.price_cents)[0];
  const openLabel = store.is_open ? 'Open now' : store.is_open === false ? 'Closed' : 'Hours unconfirmed';
  return <section className="pf-enter absolute z-10 left-3 right-3 bottom-16 lg:bottom-8 sm:right-auto sm:w-[400px] max-h-[calc(100%-24px)] flex flex-col rounded-[var(--pf-r-lg)] bg-surface shadow-[var(--pf-shadow-float)] overflow-hidden" aria-label={`Store: ${store.name}`} data-testid="store-panel">
    <header className="p-4 pb-3 flex items-start gap-3 border-b border-line">
      <div className="w-11 h-11 rounded-full bg-ink text-white grid place-items-center font-display text-lg font-semibold shrink-0" aria-hidden>{store.name.slice(0, 1)}</div>
      <div className="min-w-0 flex-1">
        <h3 className="text-[15px] font-semibold flex items-center gap-1.5 truncate">{store.name}{store.verified && <ShieldCheck size={14} className="text-accent shrink-0" aria-label="Verified" />}</h3>
        <p className="text-[13px] text-muted flex flex-wrap items-center gap-x-2">
          <span className={store.is_open ? 'text-ok font-semibold' : 'text-muted'}>{openLabel}</span>
          <span className="inline-flex items-center gap-1"><Star size={12} className="fill-ink text-ink" />{store.rating?.toFixed(1) || 'New'}{store.review_count > 0 && <span>({store.review_count})</span>}</span>
          {distanceKm != null && <span className="tabular">{formatDistance(distanceKm)}</span>}
        </p>
        <p className="text-xs text-muted flex items-start gap-1 mt-1"><MapPin size={12} className="shrink-0 mt-0.5" />{store.address}</p>
        {store.hours && <p className="text-xs text-muted flex items-start gap-1 mt-0.5"><Clock3 size={12} className="shrink-0 mt-0.5" />{store.hours}</p>}
      </div>
      <button className="pf-btn ghost sm icon shrink-0" aria-label="Close store" onClick={onClose}><X size={16} /></button>
    </header>

    {top && <div className="px-4 py-3 border-b border-line bg-canvas flex items-center gap-3">
      <Link to={`/products/${top.id}`} className="w-14 h-14 shrink-0 rounded-[var(--pf-r-md)] overflow-hidden" aria-label={`View ${top.name}`}><ProductPhoto name={top.name} imageUrl={top.image_url} merchantId={top.merchant_id} /></Link>
      <div className="min-w-0 flex-1">
        <span className="pf-chip ink !h-5 !text-[11px]">Top pick</span>
        <p className="text-[14px] font-semibold leading-snug line-clamp-1 mt-1">{top.name}</p>
        <p className="text-[13px] tabular">{cash(top.price_cents, top.currency)} · {top.available_quantity} in stock</p>
      </div>
      <div className="flex flex-col gap-1.5 shrink-0"><ReserveCompact product={top} className="pf-btn sm" /><button className="pf-btn sm outline" onClick={() => onAdd(top)} aria-label={`Add ${top.name} to basket`}><ShoppingBag size={14} />Add</button></div>
    </div>}

    <div className="px-4 pt-3 pb-1 flex items-baseline justify-between">
      <h4 className="text-[13px] font-semibold">Available here <span className="text-muted font-normal">({products.length})</span></h4>
      <a className="text-xs font-semibold underline underline-offset-2" href={googleDirections({ latitude: store.latitude, longitude: store.longitude })} target="_blank" rel="noreferrer"><Navigation size={11} className="inline mr-1" />Directions</a>
    </div>
    <ul className="flex-1 min-h-0 overflow-y-auto px-2 pb-3" aria-label="Products at this store">
      {products.length === 0 && <li className="px-2 py-4 text-sm text-muted">Nothing from this store matches your current filters.</li>}
      {products.map(p => <li key={p.id} className="flex items-center gap-3 px-2 py-2 rounded-[var(--pf-r-md)] hover:bg-canvas">
        <Link to={`/products/${p.id}`} className="w-12 h-12 shrink-0 rounded-[var(--pf-r-sm)] overflow-hidden" aria-label={`View ${p.name}`}><ProductPhoto name={p.name} imageUrl={p.image_url} merchantId={p.merchant_id} /></Link>
        <div className="min-w-0 flex-1">
          <p className="text-[13px] font-semibold leading-snug line-clamp-1">{p.name}</p>
          <p className="text-[12px] text-muted tabular">{cash(p.price_cents, p.currency)} · {p.in_stock ? `${p.available_quantity} in stock` : 'Out of stock'}</p>
        </div>
        <ReserveCompact product={p} className="pf-btn sm" />
        <button className="pf-btn sm outline" disabled={!p.in_stock || p.available_quantity <= 0} onClick={() => onAdd(p)} aria-label={`Add ${p.name} to basket`}>Add</button>
      </li>)}
    </ul>
    <footer className="px-4 py-3 border-t border-line"><Link className="pf-btn outline sm w-full text-center" to={`/stores/${store.slug}`}>Visit store page</Link></footer>
  </section>;
}
