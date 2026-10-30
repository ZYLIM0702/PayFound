import { useEffect, useMemo } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { ArrowRight, ArrowUpRight, ChevronRight, Clock3, LocateFixed, MapPin, Package, ShoppingBag } from 'lucide-react';
import { cash, type Merchant, type Product } from '../lib/api';
import { useApp } from '../lib/app-context';
import { useResource } from '../lib/use-resource';
import { useUserLocation, straightLineKm } from '../lib/location';
import { formatDistance } from '../lib/directions';
import { useDrivingRoute } from '../lib/use-driving-route';
import { ProductPhoto } from '../components/ProductPhoto';
import { ReserveProduct } from '../components/ReserveProduct';
import { DirectionsPanel } from '../components/DirectionsPanel';
import { StoreMap } from '../components/StoreMap';
import { Chip, Empty, ErrorLine, ProductCard, Spinner } from '../components/Shared';
import { WatchPriceButton } from '../components/PriceWatch';
import { useBasketAdd } from '../components/BasketFeedback';

type Detail = Product & { merchant: Merchant; offers: Product[]; comparison_basis: string;
  attributes: Record<string, string>; photo_credits_url: string };

export function ProductPage() {
  const { productId } = useParams();
  const routeLocation = useLocation();
  const location = useUserLocation();
  const { demo } = useApp();
  const origin = location.position ? `?latitude=${location.position.latitude}&longitude=${location.position.longitude}` : '';
  const resource = useResource<Detail>(productId ? `/products/${encodeURIComponent(productId)}${origin}` : null, 30000);
  const product = resource.data;
  const driving = useDrivingRoute(productId);
  const basket = useBasketAdd(product?.offers || []);
  const related = useResource<Product[]>(product ? `/products?merchant_id=${product.merchant_id}&category=${encodeURIComponent(product.category)}&limit=8` : null);
  const merchants = useMemo(() => product ? [product.merchant] : [], [product?.merchant]);
  useEffect(() => {
    if (product && routeLocation.hash === '#compare') requestAnimationFrame(() => document.getElementById('compare')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }, [product?.id, routeLocation.hash]);
  if (resource.loading) return <main className="pf-container py-10"><Spinner label="Opening product details…" /></main>;
  if (!product) return <main className="pf-container py-10"><ErrorLine message={resource.error} retry={resource.refresh} /><Empty title="Product unavailable" description="This listing may have been removed or is no longer public."><Link className="pf-btn" to="/explore">Back to discovery</Link></Empty></main>;
  const destination = { id: product.id, merchant_id: product.merchant_id, name: product.merchant_name || product.merchant.name,
    latitude: product.latitude ?? product.merchant.latitude, longitude: product.longitude ?? product.merchant.longitude };
  const distance = location.position ? straightLineKm(location.position, destination) : null;
  const otherProducts = related.data?.filter(p => p.id !== product.id).slice(0, 6) || [];
  const cheapest = Math.min(...product.offers.map(offer => offer.price_cents));
  const canBuy = product.in_stock && product.is_open !== false;
  const specs: [string, string][] = [['Product', product.name], ['Merchant SKU', product.sku], ['Category', product.category], ...(product.brand ? [['Brand', product.brand]] as [string, string][] : []),
    ...Object.entries(product.attributes), ['Inventory source', demo ? 'Synthetic demo inventory' : product.source || 'Merchant catalogue']];
  return <main className="pf-container pt-6 pb-20">
    <nav className="flex flex-wrap items-center gap-1.5 text-[13px] text-muted" aria-label="Breadcrumb"><Link className="hover:text-ink" to="/explore">Explore products</Link><ChevronRight size={13} /><Link className="hover:text-ink" to={`/stores/${product.merchant_slug}`}>{product.merchant_name}</Link><ChevronRight size={13} /><span className="text-ink">Product details</span></nav>
    <ErrorLine message={resource.error} />{basket.feedback}
    <section className="grid grid-cols-[minmax(0,1fr)] md:grid-cols-[minmax(0,1fr)_minmax(320px,400px)] lg:grid-cols-[minmax(0,1fr)_minmax(380px,460px)] gap-6 lg:gap-8 xl:gap-20 mt-6 items-start">
      <div>
        <div className="aspect-square lg:aspect-[5/4] rounded-[var(--pf-r-lg)] overflow-hidden"><ProductPhoto name={product.name} imageUrl={product.image_url} merchantId={product.merchant_id} eager /></div>
        <a className="inline-flex items-center gap-1 text-xs text-muted hover:text-ink mt-3" href={product.photo_credits_url} target="_blank" rel="noreferrer">Catalogue photograph · source and license<ArrowUpRight size={12} /></a>
        {product.description && <div className="mt-8 max-w-prose"><h2 className="pf-title mb-2">About this item</h2><p className="text-[15px] text-ink-2 leading-relaxed">{product.description}</p></div>}
      </div>

      <div className="pf-product-summary md:sticky md:top-[calc(var(--pf-header-h)+24px)] flex flex-col">
        <p className="text-sm text-muted">{product.category}{product.brand && ` · ${product.brand}`}</p>
        <h1 className="font-display text-[clamp(30px,3.4vw,44px)] font-semibold tracking-[-0.03em] leading-[1.05] mt-2">{product.name}</h1>
        <div className="pf-product-price flex items-baseline gap-3 mt-5"><strong className="font-display text-5xl font-semibold tracking-tight tabular">{cash(product.price_cents, product.currency)}</strong><span className="text-sm text-muted">at {product.merchant_name}</span></div>
        <div className="flex flex-wrap gap-2 mt-4">
          <Chip kind={product.in_stock ? 'green' : 'red'} dot>{product.in_stock ? `${product.available_quantity} available` : 'Out of stock'}</Chip>
          <Chip kind={product.is_open ? 'green' : 'amber'}>{product.is_open ? 'Store open' : product.is_open === false ? 'Store closed' : 'Check store hours'}</Chip>
          {demo && <Chip>Demo listing</Chip>}
        </div>
        <div className="flex flex-col gap-2.5 mt-6">
          <ReserveProduct product={product} disabled={!canBuy} />
          <button className="pf-btn outline lg w-full" data-testid={`product-detail-add-${product.id}`} disabled={!canBuy} onClick={() => void basket.add(product)}><ShoppingBag size={18} />Add to basket</button>
          <WatchPriceButton productId={product.id} />
          <Link className="pf-btn outline lg w-full" to={`/explore?merchant_id=${product.merchant_id}&focus=${product.id}`}><MapPin size={17} />Show on map</Link>
        </div>
        <ul className="mt-6 pt-6 border-t border-line flex flex-col gap-3 text-sm text-ink-2">
          <li className="flex gap-3"><MapPin size={17} className="shrink-0 mt-0.5 text-muted" /><span><Link className="font-semibold text-ink hover:underline" to={`/stores/${product.merchant_slug}`}>{product.merchant_name}</Link><br />{product.merchant_address}</span></li>
          <li className="flex gap-3"><Clock3 size={17} className="shrink-0 mt-0.5 text-muted" />Pickup preparation about {product.merchant.fulfillment_minutes} min</li>
          <li className="flex gap-3"><Package size={17} className="shrink-0 mt-0.5 text-muted" />{product.location_name || 'Selected store branch'}</li>
          <li className="flex gap-3"><LocateFixed size={17} className="shrink-0 mt-0.5 text-muted" />{distance != null ? <span>{formatDistance(distance)} from you · straight-line estimate</span> : <button className="underline underline-offset-2 text-left pf-tap" disabled={location.locating} onClick={() => void location.request()}>{location.locating ? 'Locating…' : 'Allow location to see your distance'}</button>}</li>
        </ul>
        <p className="text-xs text-muted leading-relaxed mt-5">Stock last updated {new Date(product.stock_updated_at).toLocaleString()}. {product.freshness === 'stale' ? 'Availability may have changed; confirm before travelling.' : 'A basket is not a stock reservation.'}</p>
        {product.offers.length > 1 && <a href="#compare" className="pf-link text-sm mt-4 inline-flex items-center gap-1.5">Same item at {product.offers.length} stores · from {cash(cheapest, product.currency)}<ArrowRight size={15} /></a>}
      </div>
    </section>

    <section id="compare" className="mt-20 scroll-mt-24" aria-labelledby="compare-heading">
      <div className="flex flex-wrap items-end justify-between gap-3 mb-5"><div><h2 id="compare-heading" className="pf-heading">Compare stores</h2><p className="text-sm text-muted mt-2">{product.comparison_basis}. Compare the same currency and item identity.</p></div><span className="text-sm text-muted">{product.offers.length} store {product.offers.length === 1 ? 'offer' : 'offers'}</span></div>
      <div className="pf-store-offers border-y border-line">
        <div className="hidden md:grid grid-cols-[56px_minmax(0,2fr)_1fr_1fr_160px] gap-6 py-3 text-xs font-semibold text-muted border-b border-line" aria-hidden><span /><span>Store</span><span>Distance</span><span>Price</span><span /></div>
        {product.offers.map(offer => {
          const km = location.position && offer.latitude != null && offer.longitude != null ? straightLineKm(location.position, { latitude: offer.latitude, longitude: offer.longitude }) : null;
          const lowest = offer.price_cents === cheapest && product.offers.length > 1; const current = offer.id === product.id;
          return <article key={offer.id} data-testid={`product-offer-${offer.id}`} className={`grid grid-cols-[56px_minmax(0,1fr)_auto] md:grid-cols-[56px_minmax(0,2fr)_1fr_1fr_160px] items-center gap-x-4 md:gap-x-6 gap-y-2 py-5 border-b border-line last:border-b-0 ${current ? 'bg-canvas -mx-4 px-4 rounded-[var(--pf-r-md)] border-transparent' : ''}`}>
            <div className="pf-offer-thumb w-14 h-14 rounded-[var(--pf-r-md)] overflow-hidden"><ProductPhoto name={offer.name} imageUrl={offer.image_url} merchantId={offer.merchant_id} /></div>
            <div className="min-w-0"><Link className="font-semibold hover:underline pf-tap" to={`/stores/${offer.merchant_slug}`}>{offer.merchant_name}</Link><p className="text-[13px] text-muted truncate">{offer.merchant_address}</p></div>
            <div className="order-last col-span-3 md:order-none md:col-span-1 text-[13px] text-muted pl-[72px] md:pl-0">{km != null ? `${formatDistance(km)} from you` : 'Allow location for distance'} · {offer.available_quantity} available</div>
            <div className="text-right md:text-left"><strong className={`font-display text-2xl font-semibold tabular ${lowest ? 'text-accent' : ''}`}>{cash(offer.price_cents, offer.currency)}</strong>{lowest && <span className="block text-xs font-semibold text-accent">Lowest price</span>}</div>
            <Link className={`pf-btn sm col-span-3 md:col-span-1 ${current ? 'outline' : ''}`} to={`/products/${offer.id}`} aria-current={current ? 'true' : undefined}>{current ? 'Current store' : 'View this offer'}{!current && <ArrowUpRight size={14} />}</Link>
          </article>;
        })}
      </div>
    </section>

    <div className="pf-product-info-grid grid lg:grid-cols-2 gap-10 xl:gap-20 mt-20 items-start">
      <section aria-labelledby="specs-heading"><h2 id="specs-heading" className="pf-heading mb-5">Product information</h2>
        <dl className="border-t border-line">{specs.map(([key, value]) => <div key={key} className="grid grid-cols-[120px_minmax(0,1fr)] sm:grid-cols-[160px_minmax(0,1fr)] gap-4 py-3.5 border-b border-line text-sm"><dt className="text-muted capitalize">{key}</dt><dd className="break-words">{value}</dd></div>)}</dl>
      </section>
      <section aria-labelledby="pickup-heading"><h2 id="pickup-heading" className="pf-heading mb-1">Plan your pickup</h2><p className="text-sm text-muted mb-5">{product.merchant_name} · {product.merchant_address}</p>
        <div className="h-[340px] rounded-[var(--pf-r-lg)] overflow-hidden border border-line"><StoreMap merchants={merchants} focus={destination} userPosition={location.position} route={driving.route} /></div>
        <div className="mt-4"><DirectionsPanel destination={destination} driving={driving} /></div>
      </section>
    </div>

    {otherProducts.length > 0 && <section className="mt-20" aria-labelledby="more-heading"><div className="flex items-end justify-between gap-4 mb-6"><h2 id="more-heading" className="pf-heading">More from this store</h2><Link className="pf-link pf-tap text-sm" to={`/stores/${product.merchant_slug}`}>View store →</Link></div><div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-x-4 gap-y-8">{otherProducts.map(item => <ProductCard key={item.id} p={item} onPick={basket.add} />)}</div></section>}
  </main>;
}
