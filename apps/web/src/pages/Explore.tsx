import { useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ChevronDown, ChevronLeft, ChevronRight, List, LocateFixed, Map as MapIcon, MapPin, PanelRightClose, PanelRightOpen, Search, X } from 'lucide-react';
import { useResource } from '../lib/use-resource';
import { useApp } from '../lib/app-context';
import { api, cash, messageOf, safeExternalUrl, type Merchant, type OnlineOffer, type OnlineSources, type Product } from '../lib/api';
import { Empty, ErrorLine, Notice, ProductCard, Spinner } from '../components/Shared';
import { ProductPhoto } from '../components/ProductPhoto';
import { StoreMap } from '../components/StoreMap';
import { DirectionsPanel } from '../components/DirectionsPanel';
import { StorePanel } from '../components/StorePanel';
import { useBasketAdd } from '../components/BasketFeedback';
import { useUserLocation, straightLineKm } from '../lib/location';
import { tabbarHeight } from '../components/MobileShell';
import { useDrivingRoute } from '../lib/use-driving-route';
import { formatDistance } from '../lib/directions';

// Original demo-store centre, used only when the API could not place the stores near the viewer.
const DEMO_CENTER: [number, number] = [37.7786, -122.414];
const PAGE_SIZE = 24;

function useIsLarge() {
  return useSyncExternalStore(
    notify => { const query = window.matchMedia('(min-width: 768px)'); query.addEventListener('change', notify); return () => query.removeEventListener('change', notify); },
    () => window.matchMedia('(min-width: 768px)').matches, () => true);
}

/** Makes Explore a viewport-height app below the sticky header and demo strip. */
function useViewportFill() {
  const ref = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState<number>();
  useLayoutEffect(() => {
    const fit = () => { const el = ref.current; if (el) setHeight(Math.max(480, window.innerHeight - tabbarHeight() - (el.getBoundingClientRect().top + window.scrollY))); };
    fit(); window.addEventListener('resize', fit); return () => window.removeEventListener('resize', fit);
  }, []);
  return [ref, height] as const;
}

export function Explore() {
  const { config } = useApp();
  const location = useUserLocation();
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get('q') || '');
  const [browseOriginal, setBrowseOriginal] = useState(false);
  const original = location.placement?.mode === 'original';
  // Stores for a new area take ~25 s to place; until then say so instead of reporting zero matches.
  const placing = Boolean(location.position) && (!location.placement || location.placement.reason === 'pending');
  const center = useMemo<[number, number]>(() => browseOriginal || (original && !location.position) ? DEMO_CENTER
    : location.position && location.anchor.source === 'precise' ? [location.position.latitude, location.position.longitude] : [location.anchor.latitude, location.anchor.longitude],
    [browseOriginal, original, location.position, location.anchor.latitude, location.anchor.longitude]);
  const isLarge = useIsLarge();
  const [mapVisible, setMapVisible] = useState(true);
  const [mobileMap, setMobileMap] = useState(false);
  const [selected, setSelected] = useState<Product | null>(null);
  const [storeId, setStoreId] = useState('');
  const [focusVersion, setFocusVersion] = useState(0);
  const [page, setPage] = useState(0);
  const [sort, setSort] = useState('distance');
  const [online, setOnline] = useState<OnlineOffer[] | null>(null);
  const [onlineBusy, setOnlineBusy] = useState(false);
  const [onlineError, setOnlineError] = useState('');
  const [onlineSources, setOnlineSources] = useState<OnlineSources | null>(null);
  const [mode, setMode] = useState<'local' | 'online' | 'both'>('local');
  const resolvedFocus = useRef('');
  const scroller = useRef<HTMLDivElement>(null);
  const [frame, frameHeight] = useViewportFill();
  const driving = useDrivingRoute(selected?.id);
  const query = new URLSearchParams(params); query.set('latitude', String(center[0])); query.set('longitude', String(center[1])); query.set('limit', '1000');
  if (!query.has('radius_km')) query.set('radius_km', '100');
  const products = useResource<Product[]>(`/products?${query}`, 30000);
  const busy = products.loading || placing;
  const stores = useResource<Merchant[]>('/merchants');
  const summary = useResource<{ offers: number; distinct_products: number; stores: number; categories: string[] }>('/catalogue/summary');
  const ordered = useMemo(() => {
    const result = [...(products.data || [])];
    const distance = (p: Product) => location.position && p.latitude != null && p.longitude != null
      ? straightLineKm(location.position, { latitude: p.latitude, longitude: p.longitude }) : p.distance_km || 0;
    return result.sort((a, b) => sort === 'price' ? a.price_cents - b.price_cents : sort === 'name' ? a.name.localeCompare(b.name) : distance(a) - distance(b) || a.price_cents - b.price_cents);
  }, [products.data, location.position, sort]);
  const basket = useBasketAdd(ordered);
  const matchedStores = useMemo(() => stores.data?.filter(m => products.data?.some(p => p.merchant_id === m.id)) || [], [stores.data, products.data]);
  const pinnedStore = storeId ? stores.data?.find(m => m.id === storeId) : undefined;
  const storeProducts = pinnedStore ? ordered.filter(p => p.merchant_id === pinnedStore.id) : [];
  const storeFocus = !selected && pinnedStore ? { id: pinnedStore.id, name: pinnedStore.name, merchant_id: pinnedStore.id, latitude: pinnedStore.latitude, longitude: pinnedStore.longitude } : null;
  const selectedStore = stores.data?.find(m => m.id === selected?.merchant_id);
  const focus = selected && selected.latitude != null && selected.longitude != null ? {
    id: selected.id, name: selected.merchant_name || '', merchant_id: selected.merchant_id,
    latitude: selected.latitude, longitude: selected.longitude } : storeFocus;
  const farFromDemo = original && !browseOriginal;
  const areaName = location.anchor.source === 'precise' ? 'you' : location.anchor.label;
  const distance = focus && location.position ? straightLineKm(location.position, focus) : null;
  const showMap = isLarge ? mapVisible : mobileMap;
  function selectProduct(product: Product) {
    driving.clear(); setStoreId(''); setSelected(product); setMapVisible(true); setMobileMap(true); setFocusVersion(value => value + 1);
  }
  // Clicking a store pin opens the store panel (facts, top pick, everything it has in these results).
  function selectStore(id: string) {
    driving.clear(); setSelected(null); setStoreId(id); setMapVisible(true); setMobileMap(true); setFocusVersion(value => value + 1);
  }
  useEffect(() => {
    const id = params.get('focus');
    if (!id || resolvedFocus.current === id || !products.data) return;
    const product = products.data.find(p => p.id === id);
    if (product) { resolvedFocus.current = id; setSelected(product); setMobileMap(true); setFocusVersion(value => value + 1); }
  }, [params, products.data]);
  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(params); if (value) next.set(key, value); else next.delete(key);
    next.delete('focus'); setParams(next); setOnline(null); setPage(0); setSelected(null); driving.clear();
  };
  async function locate() {
    const position = await location.request();
    if (position) { setBrowseOriginal(false); setPage(0); setSelected(null); driving.clear(); }
  }
  // Online search uses the search you submitted, else what is typed, else the chosen category.
  const onlineQuery = (params.get('q') || q || params.get('category') || '').trim();
  async function searchOnline() {
    setOnlineBusy(true); setOnlineError('');
    try {
      const value = await api<{ offers?: OnlineOffer[]; results?: OnlineOffer[]; sources?: OnlineSources } | OnlineOffer[]>(`/online/search?q=${encodeURIComponent(onlineQuery)}`);
      setOnline(Array.isArray(value) ? value : value.offers || value.results || []);
      setOnlineSources(Array.isArray(value) ? null : value.sources || null);
    } catch (e) { setOnlineError(messageOf(e)); } finally { setOnlineBusy(false); }
  }
  // Online and Both modes search automatically; Local keeps the explicit "Compare online offers" button.
  useEffect(() => { if (mode !== 'local' && onlineQuery) void searchOnline(); }, [mode, onlineQuery]);
  const showLocal = mode !== 'online';
  const notSetUp = !!onlineSources && Object.values(onlineSources).every(s => s.status === 'not_configured');
  const pages = Math.max(1, Math.ceil(ordered.length / PAGE_SIZE));
  const visiblePage = Math.min(page, pages - 1);
  const goToPage = (next: number) => { setPage(next); scroller.current?.scrollTo({ top: 0, behavior: 'smooth' }); };
  const clearAll = () => { setQ(''); setParams({}); setPage(0); setSelected(null); driving.clear(); };
  const filtered = [...params.keys()].some(key => key !== 'focus');

  return <div ref={frame} style={{ height: frameHeight }} className="flex flex-col overflow-hidden bg-surface">
    <div className="border-b border-line bg-surface">
      <div className="pf-container py-3 flex flex-wrap xl:flex-nowrap items-center gap-2">
        {/* Yelp-style search pill: distance scope on the left, query on the right. */}
        <form className="order-1 flex items-center h-11 w-full sm:w-auto sm:flex-1 xl:flex-[1_1_380px] xl:max-w-[540px] rounded-full border border-line-strong bg-surface transition-[border-color,box-shadow] focus-within:border-ink focus-within:shadow-[0_0_0_3px_rgb(10_10_11/0.08)]" role="search" onSubmit={e => { e.preventDefault(); setFilter('q', q.trim()); }}>
          <label className="relative flex items-center h-full pl-4 pr-1 shrink-0 border-r border-line cursor-pointer hover:bg-canvas rounded-l-full">
            <MapPin size={15} className="text-muted mr-1.5 shrink-0" aria-hidden />
            <select className="appearance-none bg-transparent pr-6 text-[13px] font-semibold cursor-pointer focus:outline-none" aria-label="Distance" value={params.get('radius_km') || '100'} onChange={e => setFilter('radius_km', e.target.value)}>{[2, 5, 15, 30, 60, 100, 20040].map(n => <option key={n} value={n}>{n === 20040 ? 'Anywhere' : `${n} km`}</option>)}</select>
            <ChevronDown size={14} className="absolute right-2 text-muted pointer-events-none" aria-hidden />
          </label>
          <Search size={16} className="ml-3 text-muted shrink-0" aria-hidden />
          <input className="flex-1 min-w-0 h-full bg-transparent px-2.5 text-sm placeholder:text-subtle focus:outline-none" aria-label="Search products" value={q} onChange={e => setQ(e.target.value)} placeholder="Search products" data-testid="explore-search" />
          <button className="pf-btn icon !w-9 !h-9 mr-1 shrink-0" aria-label="Search local" title="Search local"><Search size={16} /></button>
        </form>
        <div className="order-2 sm:order-3 xl:order-2 flex items-center gap-2 flex-1 sm:basis-full xl:basis-auto xl:flex-[0_1_auto] min-w-0 overflow-x-auto pf-no-scrollbar py-1 -my-1">
          <select className="pf-select sm !w-auto shrink-0 max-w-[160px]" aria-label="Category" value={params.get('category') || ''} onChange={e => setFilter('category', e.target.value)}><option value="">All categories</option>{summary.data?.categories.map(name => <option key={name}>{name}</option>)}</select>
          <select className="pf-select sm !w-auto shrink-0 max-w-[150px]" aria-label="Store" value={params.get('merchant_id') || ''} onChange={e => setFilter('merchant_id', e.target.value)}><option value="">All stores</option>{stores.data?.map(store => <option key={store.id} value={store.id}>{store.name}</option>)}</select>
          <select className="pf-select sm !w-auto shrink-0" aria-label="Sort" value={sort} onChange={e => { setSort(e.target.value); setPage(0); }}><option value="distance">Nearest</option><option value="price">Lowest price</option><option value="name">Name A–Z</option></select>
          <label className="pf-toggle shrink-0"><input type="checkbox" checked={params.get('in_stock') === 'true'} onChange={e => setFilter('in_stock', e.target.checked ? 'true' : '')} />In stock</label>
          <label className="pf-toggle shrink-0"><input type="checkbox" checked={params.get('open_now') === 'true'} onChange={e => setFilter('open_now', e.target.checked ? 'true' : '')} />Open now</label>
          {filtered && <button className="pf-btn ghost sm shrink-0" onClick={clearAll}>Clear</button>}
        </div>
        <div className="pf-segmented order-1 sm:order-2 xl:order-3 shrink-0" role="group" aria-label="Search mode" data-testid="explore-mode">
          {(['local', 'online', 'both'] as const).map(m => <button key={m} type="button" aria-pressed={mode === m} data-testid={`mode-${m}`} onClick={() => setMode(m)}>{m === 'local' ? 'Local' : m === 'online' ? 'Online' : 'Both'}</button>)}
        </div>
        <div className="order-3 sm:order-2 xl:order-3 flex items-center gap-2 shrink-0 ml-auto">
          <button className="pf-btn outline sm" type="button" onClick={() => void locate()} disabled={location.locating} title={location.position ? 'Update my location' : 'Use my location'}><LocateFixed size={15} /><span className="hidden sm:inline">{location.locating ? 'Locating…' : location.position ? 'Update my location' : 'Use my location'}</span></button>
          <button className="pf-btn soft sm hidden md:inline-flex" aria-pressed={mapVisible} onClick={() => setMapVisible(value => !value)}>{mapVisible ? <PanelRightClose size={15} /> : <PanelRightOpen size={15} />}{mapVisible ? 'Hide map' : 'Show map'}</button>
        </div>
      </div>
    </div>

    <div className="relative flex-1 min-h-0 flex">
      <div ref={scroller} className={`${showMap && !isLarge ? 'hidden' : 'block'} flex-1 min-w-0 overflow-y-auto`}>
        <div className="pf-container py-5 pb-24 md:pb-10">
          {showLocal && <>
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 mb-4">
            <p role="status" className="text-[15px]">{busy ? (placing ? 'Placing stores near your location…' : 'Finding local offers…') : <><strong className="font-display text-xl font-semibold tabular">{ordered.length}</strong> matching offers <span className="text-muted">from {matchedStores.length} {matchedStores.length === 1 ? 'store' : 'stores'}</span></>}</p>
            <p className="text-xs text-muted flex items-center gap-2">{location.position ? <><span className="w-1.5 h-1.5 rounded-full bg-accent" />Location shared for this app session · accuracy about {Math.round(location.position.accuracy)} m<button className="pf-tap underline underline-offset-2 hover:text-ink inline-flex items-center gap-1" onClick={() => { location.clear(); setBrowseOriginal(false); driving.clear(); }}>Stop using location<X size={11} /></button></> : <span data-testid="demo-area">{original ? 'Demo stores are in San Francisco' : `Showing demo stores near ${areaName}`} · <button className="pf-tap underline underline-offset-2 hover:text-ink" type="button" onClick={() => void locate()} disabled={location.locating}>Use precise location</button></span>}</p>
          </div>
          {location.error && <div className="mb-4"><ErrorLine message={location.error} /></div>}
          {farFromDemo && <div className="mb-4"><Notice tone="default">We could not place the demo stores on land near you, so they stay in San Francisco. <button className="font-semibold underline ml-1" onClick={() => { setBrowseOriginal(true); setPage(0); }}>Browse the San Francisco demo area</button></Notice></div>}
          <ErrorLine message={products.error} retry={products.refresh} />
          {busy ? <Spinner label={placing ? 'Placing stores near your location…' : 'Searching local stock…'} /> : ordered.length ? <>
            <div className={`pf-discovery-products grid grid-cols-2 gap-x-4 gap-y-8 ${mapVisible ? 'sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4' : 'sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6'}`}>
              {ordered.slice(visiblePage * PAGE_SIZE, (visiblePage + 1) * PAGE_SIZE).map(p => <ProductCard key={p.id} p={p} onPick={basket.add} onLocate={selectProduct} selected={selected?.id === p.id} />)}
            </div>
            <nav className="pf-pagination flex items-center justify-between gap-3 mt-10 text-sm text-muted" aria-label="Pagination">
              <button className="pf-btn sm outline" disabled={visiblePage === 0} onClick={() => goToPage(visiblePage - 1)}><ChevronLeft size={15} />Previous</button>
              <span className="tabular">Page {visiblePage + 1} of {pages} · {ordered.length} offers</span>
              <button className="pf-btn sm outline" disabled={visiblePage + 1 >= pages} onClick={() => goToPage(visiblePage + 1)}>Next<ChevronRight size={15} /></button>
            </nav></>
            : <Empty search title="No nearby matches yet" description="Increase the radius, choose all locations, or browse the demo area." />}
          </>}
          <section className={`${showLocal ? 'mt-14 pt-8 border-t border-line' : ''}`} aria-labelledby="online-offers" data-testid="online-section">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="max-w-xl"><h2 id="online-offers" className="pf-title">Looking further afield?</h2><p className="text-sm text-muted mt-1.5">Online offers come from Channel3. They are separate from local inventory and never confirm in-store stock. Merchant links open an external store.</p>{!config?.channel3_enabled && <p className="text-xs text-muted mt-2" data-testid="online-not-configured">Online offers are not set up yet.</p>}</div>
              {mode === 'local' && <button className="pf-btn outline" disabled={!config?.channel3_enabled || onlineBusy || !onlineQuery} onClick={() => void searchOnline()}>{onlineBusy ? 'Searching online…' : 'Compare online offers'}</button>}
            </div>
            <ErrorLine message={onlineError} />
            {mode !== 'local' && !onlineQuery && <p className="text-sm text-muted mt-4">Type a search to see online offers.</p>}
            {mode !== 'local' && onlineBusy && <Spinner label="Searching online…" />}
            {online && (!online.length ? <p className="text-sm text-muted mt-4" data-testid="online-empty">{notSetUp ? 'Online offers are not set up yet.' : onlineSources && Object.values(onlineSources).some(s => s.status === 'unavailable') ? 'Channel3 is unavailable right now. Try again shortly.' : 'No online offers found.'}</p> : <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4 mt-5">{online.map((offer, i) => <OnlineCard key={`${offer.product_id}-${i}`} offer={offer} />)}</div>)}
                      </section>
        </div>
      </div>

      {showMap && <aside className="relative flex flex-col w-full md:w-[42%] md:max-w-[920px] md:border-l border-line bg-surface" aria-label="Matching store locations">
        <div className="pf-map-panel-head h-12 shrink-0 px-4 flex items-center justify-between gap-3 border-b border-line"><h2 className="pf-subtitle truncate">{selectedStore?.name || 'Stores on the map'}</h2><span className="text-xs text-muted shrink-0">{config?.routing?.provider === 'google' ? 'Google Maps' : 'OpenStreetMap'}</span></div>
        <div className="relative flex-1 min-h-0">
          <div className="absolute inset-0"><StoreMap merchants={matchedStores} center={center} focus={focus} focusVersion={focusVersion} userPosition={location.position} route={driving.route} scrollZoom onSelectMerchant={selectStore} /></div>
          {pinnedStore && !selected && <StorePanel store={pinnedStore} products={storeProducts} distanceKm={location.position && pinnedStore.latitude != null ? straightLineKm(location.position, { latitude: pinnedStore.latitude, longitude: pinnedStore.longitude }) : null} onAdd={p => void basket.add(p)} onClose={() => setStoreId('')} />}
          {focus && selected
            ? <section className="pf-selected-store pf-enter absolute z-10 left-3 right-3 bottom-16 md:bottom-8 sm:right-auto sm:w-[400px] max-h-[calc(100%-24px)] overflow-y-auto rounded-[var(--pf-r-lg)] bg-surface shadow-[var(--pf-shadow-float)] p-4" aria-label="Selected product">
              <div className="flex items-start gap-3">
                <Link to={`/products/${selected.id}`} className="w-16 h-16 shrink-0 rounded-[var(--pf-r-md)] overflow-hidden" aria-label={`View ${selected.name}`}><ProductPhoto name={selected.name} imageUrl={selected.image_url} merchantId={selected.merchant_id} /></Link>
                <div className="min-w-0 flex-1"><strong className="block text-[15px] font-semibold leading-snug line-clamp-2">{selected.name}</strong><p className="font-display text-xl font-semibold tabular mt-0.5">{cash(selected.price_cents, selected.currency)}</p></div>
                <button className="pf-btn ghost sm icon shrink-0 -mr-1 -mt-1" aria-label="Clear selected store" onClick={() => { setSelected(null); driving.clear(); }}><X size={16} /></button>
              </div>
              <p className="flex gap-2 text-[13px] text-muted mt-3"><MapPin size={15} className="shrink-0 mt-0.5" /><span><span className="text-ink font-semibold">{selected.merchant_name}</span><br />{selected.merchant_address}</span></p>
              {distance != null && <p className="text-[13px] text-muted mt-2"><strong className="text-ink font-semibold">{formatDistance(distance)}</strong> from your location · straight-line estimate</p>}
              <div className="mt-3"><DirectionsPanel destination={focus} driving={driving} /></div>
              <Link className="pf-link text-sm inline-block mt-3" to={`/products/${selected.id}`}>View product and compare stores →</Link>
            </section>
            : pinnedStore ? null : <p className="absolute z-10 left-1/2 -translate-x-1/2 bottom-16 md:bottom-9 max-w-[calc(100%-32px)] rounded-full bg-surface shadow-[var(--pf-shadow-float)] px-4 h-9 inline-flex items-center gap-2 text-[13px] text-ink-2 whitespace-nowrap"><MapPin size={15} />Pick a product to see its store and route</p>}
        </div>
      </aside>}

      <div className="md:hidden absolute z-20 bottom-4 right-4"><button className="pf-btn shadow-[var(--pf-shadow-float)]" onClick={() => setMobileMap(value => !value)}>{mobileMap ? <><List size={16} />List</> : <><MapIcon size={16} />Map</>}</button></div>
    </div>
    {basket.feedback}
  </div>;
}

function OnlineCard({ offer }: { offer: OnlineOffer }) {
  const href = safeExternalUrl(offer.url); const image = safeExternalUrl(offer.image);
  return <article className="pf-card p-4 flex flex-col"><span className="pf-chip amber self-start" data-testid="online-badge">Online · Channel3</span>{image && <img className="h-28 object-contain w-full my-3" src={image} alt="" loading="lazy" />}<h3 className="font-semibold mt-2">{offer.title}</h3><p className="text-sm text-muted mt-1">{offer.merchant}</p>{offer.condition && <p className="text-xs text-muted mt-1">{offer.condition}</p>}<p className="font-display text-lg font-semibold mt-2">{offer.price == null ? 'See retailer for price' : `${offer.currency || ''} ${offer.price}`}</p>{offer.shipping_summary && <p className="text-xs text-muted mt-1">{offer.shipping_summary}</p>}{href && <a className="pf-btn sm outline mt-3 self-start" href={href} target="_blank" rel="noopener noreferrer">Visit retailer ↗</a>}</article>;
}
