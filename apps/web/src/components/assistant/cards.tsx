import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowUpRight, Clock, CloudRain, LocateFixed, MapPin, Navigation, ShoppingBag, Star, Wind } from 'lucide-react';
import { cash, type Merchant, type Product, type Review } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { useUserLocation } from '../../lib/location';
import { formatDistance, formatDuration, googleDirections } from '../../lib/directions';
import { useDrivingRoute } from '../../lib/use-driving-route';
import { useBasketAdd } from '../BasketFeedback';
import { ProductPhoto } from '../ProductPhoto';
import { ReserveCompact } from '../ReserveProduct';
import { StoreMap as MapView } from '../StoreMap';
import { DirectionsPanel } from '../DirectionsPanel';
import { Chip, ErrorLine, OrderStatus as StatusChip, Skeleton, availabilityTone, type Tone } from '../Shared';
import type { Order } from '../../lib/api';
import { FOCUS_EVENT, requestMapFocus, useProductsByIds, useSettledIds, useStores } from './data';

const availability = (p: Product) => p.in_stock ? p.freshness === 'stale' ? 'Check stock' : `${p.available_quantity} in stock` : 'Out of stock';
const stamp = (iso: string) => new Date(iso).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });

function CardShell({ title, children, label }: { title?: string; children: React.ReactNode; label: string }) {
  return <section className="pf-ag-card" aria-label={label}>{title && <h4 className="pf-ag-card-title">{title}</h4>}{children}</section>;
}
const Loading = ({ rows = 1 }: { rows?: number }) => <div className="grid gap-3">{Array.from({ length: rows }, (_, i) => <Skeleton key={i} className="h-[112px] !rounded-[var(--pf-r-lg)]" />)}</div>;

/* ---------------------------------------------------------------- Offers */

function OfferCard({ p, onAdd, featured = false }: { p: Product; onAdd: (p: Product) => void; featured?: boolean }) {
  const navigate = useNavigate();
  const { position } = useUserLocation();
  const disabled = !p.in_stock || p.available_quantity <= 0 || p.is_open === false;
  const distance = p.distance_km != null && position ? formatDistance(p.distance_km) : null;
  return <article className={`pf-ag-offer ${featured ? 'featured' : ''}`} data-testid={`agent-offer-${p.id}`}>
    <Link to={`/products/${p.id}`} className="pf-ag-offer-photo" aria-label={`View ${p.name}`}><ProductPhoto name={p.name} imageUrl={p.image_url} merchantId={p.merchant_id} /></Link>
    <div className="pf-ag-offer-body">
      <div className="flex items-start justify-between gap-3"><h4 className="pf-ag-offer-name">{p.name}</h4><strong className="tabular shrink-0 font-display text-[17px]">{cash(p.price_cents, p.currency)}</strong></div>
      <p className="pf-ag-meta"><Link to={`/stores/${p.merchant_slug || p.merchant_id}`} className="hover:text-ink">{p.merchant_name || 'Store'}</Link>{distance && <><span aria-hidden> · </span><span className="tabular">{distance}</span></>}{p.is_open === false && <> · Closed now</>}</p>
      <p className="flex flex-wrap items-center gap-x-2 gap-y-1"><Chip kind={availabilityTone(p)} dot>{availability(p)}</Chip><span className="text-[12px] text-subtle">{p.freshness === 'stale' ? 'Stock may be outdated · ' : 'Updated '}{stamp(p.stock_updated_at)}</span></p>
      <div className="pf-ag-actions">
        {p.checkout_mode === 'merchant_native'
          ? <Link className="pf-btn sm outline" to={`/products/${p.id}`}>View product<ArrowUpRight size={14} /></Link>
          : <><ReserveCompact product={p} className="pf-btn sm" /><button className="pf-btn sm outline" disabled={disabled} onClick={() => onAdd(p)} data-testid={`agent-add-${p.id}`}><ShoppingBag size={14} />Add to basket</button></>}
        <Link className="pf-btn sm outline" to={`/products/${p.id}`}>View</Link>
        <button className="pf-btn sm outline icon" aria-label={`Show ${p.name} on map`} title="Show on map" onClick={() => { if (!requestMapFocus(p.id)) navigate(`/explore?focus=${encodeURIComponent(p.id)}`); }}><MapPin size={14} /></button>
      </div>
    </div>
  </article>;
}

export function OfferGridView({ props }: { props: { productIds?: unknown; title?: string | null } }) {
  const ids = useSettledIds(props.productIds, 8);
  const { products, loading, error, refresh, data } = useProductsByIds(ids);
  const basket = useBasketAdd(data || []);
  if (!ids.length) return null;
  return <CardShell label="Nearby offers" title={props.title || undefined}>
    {basket.feedback}
    {error && <ErrorLine message={error} retry={refresh} />}
    {loading ? <Loading rows={Math.min(ids.length, 3)} /> : !products.length ? <p className="text-sm text-muted">Those listings are no longer available.</p>
      : <div className="pf-ag-offer-grid">{products.map(p => <OfferCard key={p.id} p={p} onAdd={basket.add} featured={false} />)}</div>}
  </CardShell>;
}

export function OfferView({ props }: { props: { productId?: string } }) {
  const ids = useSettledIds(props.productId ? [props.productId] : [], 1);
  const { products, loading, error, refresh, data } = useProductsByIds(ids);
  const basket = useBasketAdd(data || []);
  if (!ids.length) return null;
  return <CardShell label="Offer">{basket.feedback}{error && <ErrorLine message={error} retry={refresh} />}{loading ? <Loading /> : products[0] ? <OfferCard p={products[0]} onAdd={basket.add} featured /> : <p className="text-sm text-muted">This listing is no longer available.</p>}</CardShell>;
}

/* ------------------------------------------------------------------- Map */

function LocateButton() {
  const location = useUserLocation();
  if (location.position) return <span className="inline-flex items-center gap-1.5 text-[12px] text-muted"><LocateFixed size={13} />Using your location</span>;
  return <button className="pf-btn sm outline" onClick={() => void location.request()} disabled={location.locating}><LocateFixed size={14} />{location.locating ? 'Locating…' : 'Use my location'}</button>;
}

export function StoreMapView({ props }: { props: { storeIds?: unknown; focusProductId?: string | null; showRoute?: boolean | null } }) {
  const wanted = useSettledIds(props.storeIds, 8);
  const stores = useStores();
  const { position } = useUserLocation();
  const focusId = props.focusProductId && /^[a-zA-Z0-9_-]{1,48}$/.test(props.focusProductId) ? props.focusProductId : undefined;
  const focusProduct = useProductsByIds(useMemo(() => focusId ? [focusId] : [], [focusId])).products[0];
  const [pinned, setPinned] = useState<string>();
  const pinnedProduct = useProductsByIds(useMemo(() => pinned ? [pinned] : [], [pinned])).products[0];
  const [version, setVersion] = useState(0);
  const shown = pinnedProduct || focusProduct;
  const merchants = useMemo(() => {
    const all = stores.data || [];
    const picked = all.filter(m => wanted.includes(m.id) || wanted.includes(m.slug));
    const extra = shown && !picked.some(m => m.id === shown.merchant_id) ? all.filter(m => m.id === shown.merchant_id) : [];
    return [...picked, ...extra];
  }, [stores.data, wanted, shown]);
  const driving = useDrivingRoute(shown?.id);
  const wantRoute = Boolean(props.showRoute) && Boolean(shown);
  const loaded = useRef('');
  useEffect(() => { if (wantRoute && position && shown && loaded.current !== shown.id) { loaded.current = shown.id; void driving.load(); } }, [wantRoute, position, shown, driving]);
  useEffect(() => {
    const onFocus = (e: Event) => { const id = (e as CustomEvent<{ productId: string }>).detail?.productId; if (!id) return; e.preventDefault(); setPinned(id); setVersion(v => v + 1); };
    window.addEventListener(FOCUS_EVENT, onFocus);
    return () => window.removeEventListener(FOCUS_EVENT, onFocus);
  }, []);
  if (!wanted.length && !focusId) return null;
  const focus = shown?.latitude != null && shown.longitude != null ? { id: shown.id, name: shown.merchant_name || shown.name, latitude: shown.latitude, longitude: shown.longitude, merchant_id: shown.merchant_id } : null;
  return <CardShell label="Map of stores">
    <div className="pf-ag-map">{stores.loading ? <Skeleton className="w-full h-full" /> : <MapView merchants={merchants} focus={focus} focusVersion={version} userPosition={position} route={driving.route} />}</div>
    <div className="flex flex-wrap items-center justify-between gap-2 mt-3">
      <p className="text-[13px] text-muted min-w-0 truncate">{merchants.length ? merchants.map(m => m.name).join(' · ') : 'Loading stores…'}</p>
      <div className="flex gap-2 shrink-0">
        <LocateButton />
        {shown && <button className="pf-btn sm outline" disabled={driving.busy} onClick={() => void driving.load()}><Navigation size={14} />{driving.busy ? 'Routing…' : driving.route ? 'Refresh route' : 'Show route'}</button>}
      </div>
    </div>
    {driving.route && <p className="mt-2 text-[13px] tabular"><b>{formatDuration(driving.route.duration_seconds)}</b> · {formatDistance(driving.route.distance_m / 1000)} · {driving.route.traffic_aware ? 'with live traffic' : 'no live traffic'}</p>}
    <ErrorLine message={driving.error} />
  </CardShell>;
}

export function RouteCardView({ props }: { props: { productId?: string } }) {
  const ids = useSettledIds(props.productId ? [props.productId] : [], 1);
  const { products, loading } = useProductsByIds(ids);
  const p = products[0];
  const driving = useDrivingRoute(p?.id);
  const { position } = useUserLocation();
  const started = useRef('');
  useEffect(() => { if (p && position && started.current !== p.id) { started.current = p.id; void driving.load(); } }, [p, position, driving]);
  if (!ids.length) return null;
  if (loading || !p) return <CardShell label="Route"><Loading /></CardShell>;
  const destination = { latitude: p.latitude ?? driving.route?.destination.latitude ?? 0, longitude: p.longitude ?? driving.route?.destination.longitude ?? 0, name: p.merchant_name };
  return <CardShell label="Route" title={`Getting to ${p.merchant_name || 'the store'}`}><DirectionsPanel destination={destination} driving={driving} />{p.merchant_address && <p className="text-[12px] text-subtle mt-2">{p.merchant_address}</p>}</CardShell>;
}

/* --------------------------------------------------------------- Weather */

type Forecast = { current: { temperature_2m: number; weather_code: number; precipitation: number; wind_speed_10m: number; time: string }; hourly: { time: string[]; temperature_2m: number[]; precipitation_probability: number[] } };
const weatherText = (c: number) => c === 0 ? 'Clear' : c <= 2 ? 'Partly cloudy' : c === 3 ? 'Overcast' : c <= 48 ? 'Fog' : c <= 57 ? 'Drizzle' : c <= 67 ? 'Rain' : c <= 77 ? 'Snow' : c <= 82 ? 'Showers' : c <= 86 ? 'Snow showers' : 'Thunderstorms';

export function WeatherCardView({ props }: { props: { latitude?: number; longitude?: number; label?: string } }) {
  const { latitude, longitude } = props;
  const ok = typeof latitude === 'number' && typeof longitude === 'number' && Math.abs(latitude) <= 90 && Math.abs(longitude) <= 180;
  const [data, setData] = useState<Forecast | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    if (!ok) return;
    const abort = new AbortController();
    const timer = window.setTimeout(() => {
      fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,weather_code,precipitation,wind_speed_10m&hourly=temperature_2m,precipitation_probability&forecast_hours=6`, { signal: abort.signal })
        .then(r => r.ok ? r.json() : Promise.reject(new Error('Weather is unavailable right now.')))
        .then((value: Forecast) => { setData(value); setError(''); })
        .catch(e => { if (!abort.signal.aborted) setError(e instanceof Error ? e.message : 'Weather is unavailable right now.'); });
    }, 300);
    return () => { window.clearTimeout(timer); abort.abort(); };
  }, [ok, latitude, longitude]);
  if (!ok) return null;
  return <CardShell label="Weather" title={props.label ? `Weather · ${props.label}` : 'Weather'}>
    {error ? <ErrorLine message={error} /> : !data ? <Skeleton className="h-24 !rounded-[var(--pf-r-lg)]" /> : <div>
      <div className="flex items-end justify-between gap-4">
        <div><div className="font-display text-5xl font-semibold tracking-tight tabular leading-none">{Math.round(data.current.temperature_2m)}°</div><p className="text-sm text-muted mt-2">{weatherText(data.current.weather_code)}</p></div>
        <dl className="text-[13px] text-muted grid gap-1.5 text-right"><div className="flex items-center justify-end gap-1.5"><CloudRain size={14} /><dd className="tabular">{data.current.precipitation} mm now</dd></div><div className="flex items-center justify-end gap-1.5"><Wind size={14} /><dd className="tabular">{Math.round(data.current.wind_speed_10m)} km/h</dd></div></dl>
      </div>
      <ol className="grid grid-cols-6 gap-1 mt-4 pt-4 border-t border-line text-center">{data.hourly.time.slice(0, 6).map((t, i) => <li key={t} className="text-[12px]"><span className="text-subtle block">{new Date(t).toLocaleTimeString([], { hour: 'numeric' })}</span><b className="font-semibold tabular block mt-1">{Math.round(data.hourly.temperature_2m[i])}°</b><span className="text-muted tabular">{data.hourly.precipitation_probability[i]}%</span></li>)}</ol>
      <p className="text-[11px] text-subtle mt-3">Open-Meteo · rain chance per hour</p>
    </div>}
  </CardShell>;
}

/* --------------------------------------------------------------- Compare */

export function CompareOffersView({ props }: { props: { productId?: string } }) {
  const ids = useSettledIds(props.productId ? [props.productId] : [], 1);
  const { position } = useUserLocation();
  const id = ids[0];
  const detail = useResource<Product & { offers: Product[]; comparison_basis?: string }>(id ? `/products/${encodeURIComponent(id)}${position ? `?latitude=${position.latitude}&longitude=${position.longitude}` : ''}` : null);
  const basket = useBasketAdd(detail.data?.offers || []);
  if (!id) return null;
  const offers = detail.data?.offers || [];
  const lowest = Math.min(...offers.filter(o => o.in_stock).map(o => o.price_cents));
  return <CardShell label="Compare offers" title={detail.data ? `${detail.data.name} across stores` : 'Comparing stores'}>
    {basket.feedback}
    {detail.error && <ErrorLine message={detail.error} retry={detail.refresh} />}
    {detail.loading ? <Loading rows={2} /> : <ul className="pf-ag-compare">{offers.map(o => <li key={o.id} className={o.price_cents === lowest && o.in_stock ? 'best' : ''}>
      <div className="min-w-0 flex-1"><Link to={`/stores/${o.merchant_slug || o.merchant_id}`} className="font-semibold text-[14px] hover:underline">{o.merchant_name}</Link><p className="pf-ag-meta">{o.distance_km != null && position ? `${formatDistance(o.distance_km)} · ` : ''}{availability(o)}{o.is_open === false ? ' · Closed now' : ''}</p></div>
      <div className="text-right"><strong className="font-display text-lg tabular block">{cash(o.price_cents, o.currency)}</strong>{o.price_cents === lowest && o.in_stock && <span className="text-[11px] font-semibold text-accent">Lowest price</span>}</div>
      <button className="pf-btn sm" disabled={!o.in_stock || o.is_open === false} onClick={() => basket.add(o)}>Add</button>
    </li>)}</ul>}
    {detail.data?.comparison_basis && <p className="text-[11px] text-subtle mt-3">{detail.data.comparison_basis}. Local stock only; online offers do not prove local availability.</p>}
  </CardShell>;
}

/* ----------------------------------------------------------------- Store */

const slugOk = (s?: string) => Boolean(s && /^[a-zA-Z0-9_-]{1,80}$/.test(s));

export function StoreSummaryView({ props }: { props: { storeSlug?: string } }) {
  const [slug, setSlug] = useState('');
  useEffect(() => { const t = window.setTimeout(() => setSlug(slugOk(props.storeSlug) ? props.storeSlug! : ''), 220); return () => window.clearTimeout(t); }, [props.storeSlug]);
  const store = useResource<Merchant>(slug ? `/merchants/${encodeURIComponent(slug)}` : null);
  const m = store.data;
  if (!slug) return null;
  if (store.loading || !m) return <CardShell label="Store">{store.error ? <ErrorLine message={store.error} retry={store.refresh} /> : <Loading />}</CardShell>;
  return <CardShell label="Store"><div className="flex items-start gap-4">
    <div className="w-11 h-11 rounded-full bg-ink text-white grid place-items-center font-display text-lg font-semibold shrink-0" aria-hidden>{m.name.slice(0, 1)}</div>
    <div className="min-w-0 flex-1">
      <div className="flex flex-wrap items-center gap-2"><h4 className="font-semibold text-[16px]">{m.name}</h4><Chip kind={m.is_open ? 'green' : m.is_open === false ? 'default' : 'amber'} dot>{m.is_open ? 'Open now' : m.is_open === false ? 'Closed' : 'Hours unconfirmed'}</Chip></div>
      <p className="pf-ag-meta mt-1">{m.category} · {m.address}</p>
      <p className="pf-ag-meta flex items-center gap-3 mt-1"><span className="inline-flex items-center gap-1"><Star size={13} className="fill-ink text-ink" /><b className="text-ink">{m.rating?.toFixed(1) || 'New'}</b>{m.review_count > 0 && <>({m.review_count})</>}</span><span className="inline-flex items-center gap-1"><Clock size={13} />Ready in ~{m.fulfillment_minutes} min</span></p>
      {m.hours && <p className="pf-ag-meta mt-1">{m.hours}</p>}
      <div className="pf-ag-actions"><Link className="pf-btn sm" to={`/stores/${m.slug}`}>Open store</Link><a className="pf-btn sm outline" href={googleDirections(m)} target="_blank" rel="noreferrer">Directions<ArrowUpRight size={14} /></a></div>
    </div></div></CardShell>;
}

export function ReviewsView({ props }: { props: { storeSlug?: string; limit?: number | null } }) {
  const [slug, setSlug] = useState('');
  useEffect(() => { const t = window.setTimeout(() => setSlug(slugOk(props.storeSlug) ? props.storeSlug! : ''), 220); return () => window.clearTimeout(t); }, [props.storeSlug]);
  const store = useResource<Merchant>(slug ? `/merchants/${encodeURIComponent(slug)}` : null);
  const limit = Math.min(6, Math.max(1, Math.round(props.limit || 3)));
  if (!slug) return null;
  const reviews: Review[] = store.data?.reviews?.slice(0, limit) || [];
  return <CardShell label="Reviews" title={store.data ? `What shoppers say about ${store.data.name}` : 'Reviews'}>
    {store.error && <ErrorLine message={store.error} retry={store.refresh} />}
    {store.loading ? <Loading /> : !reviews.length ? <p className="text-sm text-muted">No reviews yet.</p> : <ul className="grid gap-3">{reviews.map(r => <li key={r.id} className="border-t border-line pt-3 first:border-0 first:pt-0"><p className="flex items-center gap-1 text-[13px]"><Star size={13} className="fill-ink text-ink" /><b className="tabular">{r.rating}.0</b><span className="text-subtle ml-1">{new Date(r.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}{r.demo_review ? ' · sample review' : ''}</span></p><p className="text-[14px] mt-1 leading-relaxed">{r.body}</p></li>)}</ul>}
  </CardShell>;
}

/* ---------------------------------------------------------------- Orders */

const orderTone = (o: Order): Tone => o.status === 'READY' ? 'blue' : 'default';
function OrderRow({ order }: { order: Order }) {
  return <li className="pf-ag-order">
    <div className="min-w-0 flex-1"><Link to={`/checkout/${order.id}`} className="font-semibold text-[14px] hover:underline">{order.merchant_name}</Link><p className="pf-ag-meta truncate">{(order.items?.length ? order.items.map(i => `${i.quantity} × ${i.product_name || i.name}`) : [`${order.quantity} × ${order.product_name}`]).join(', ')}</p><p className="pf-ag-meta">Order {order.id.slice(0, 8)} · payment {order.payment_status.toLowerCase().replaceAll('_', ' ')}</p></div>
    <div className="text-right shrink-0"><strong className="tabular block">{cash(order.amount_cents, order.currency)}</strong><StatusChip order={order} /></div>
    <Link className="pf-btn sm outline" to={`/checkout/${order.id}`}>{order.payment_status === 'CAPTURED' ? 'Details' : 'Open'}</Link>
  </li>;
}
void orderTone;

export function OrderStatusView({ props }: { props: { orderId?: string } }) {
  const [id, setId] = useState('');
  useEffect(() => { const t = window.setTimeout(() => setId(slugOk(props.orderId) ? props.orderId! : ''), 220); return () => window.clearTimeout(t); }, [props.orderId]);
  const order = useResource<Order>(id ? `/orders/${encodeURIComponent(id)}` : null, 15000);
  if (!id) return null;
  return <CardShell label="Order status">{order.error && <ErrorLine message={order.error} retry={order.refresh} />}{order.loading ? <Loading /> : order.data && <ul><OrderRow order={order.data} /></ul>}</CardShell>;
}

export function OrderListView() {
  const orders = useResource<Order[]>('/orders', 20000);
  return <CardShell label="Your orders" title="Your recent orders">{orders.error && <ErrorLine message={orders.error} retry={orders.refresh} />}{orders.loading ? <Loading rows={2} /> : !orders.data?.length ? <p className="text-sm text-muted">No orders yet.</p> : <ul>{orders.data.slice(0, 5).map(o => <OrderRow key={o.id} order={o} />)}</ul>}{(orders.data?.length || 0) > 5 && <Link to="/orders" className="pf-link text-sm mt-3 inline-block">All orders →</Link>}</CardShell>;
}
