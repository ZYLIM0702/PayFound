import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { StoreMap } from '../components/StoreMap';
import { formatDistance } from '../lib/directions';
import { straightLineKm } from '../lib/location';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Apple, ArrowRight, ArrowUpRight, Bike, Laptop, LayoutGrid, MapPin, ShoppingBasket, Utensils, LocateFixed, PawPrint, Pencil, Sofa, Sparkles, Star, Wrench, type LucideIcon } from 'lucide-react';
import { cash, type Merchant, type Product } from '../lib/api';
import { useResource } from '../lib/use-resource';
import { useApp } from '../lib/app-context';
import { Chip, Empty, ErrorLine, ProductCard, Spinner } from '../components/Shared';
import { ProductPhoto } from '../components/ProductPhoto';
import { useUserLocation } from '../lib/location';
import { AssistantGate } from '../components/assistant/AssistantGate';
import { AssistantSurface } from '../components/assistant/AssistantSurface';
import { RealtimeVoice } from '../components/assistant/realtime/RealtimeVoice';
import { Camera } from 'lucide-react';
import { shopperStarters, shopperSuggestions } from './agent/starters';
import './agent/home.css';
import { useBasketAdd } from '../components/BasketFeedback';
import { TypedHeadline, heroPhrases, type TypedPhrase } from '../components/TypedHeadline';

export const categories: [string, LucideIcon][] = [['All products', LayoutGrid], ['Electronics', Laptop], ['Hardware', Wrench], ['Pet essentials', PawPrint], ['Sports & cycling', Bike], ['Home & living', Sofa], ['Office supplies', Pencil], ['Groceries', ShoppingBasket], ['Fresh produce', Apple], ['Ready meals', Utensils]];
export const pillars = [
  ['Merchants', 'Visibility', 'Local shops have stock, but no way to show it. PayFound puts their real shelf in front of nearby shoppers, with a timestamp that shows how fresh it is.'],
  ['AI', 'Data and realtime data', 'AI is only as good as the context behind it. Our assistant answers from live stock, prices, routes and opening hours, not from guesses, and tells you when a figure is old.'],
  ['People', 'Convenience', 'Ask in plain words, see what is nearby, reserve it, and pick it up. One basket from one store, with the route and a pickup time, without the store-by-store search.'],
] as const;

/** Reusable browse sections (also used below the assistant on the landing page). */
export function CategoryTiles() {
  return (
    <section className="pf-container pb-16" aria-labelledby="home-categories">
      <h2 id="home-categories" className="pf-heading mb-6">Shop by category</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 2xl:grid-cols-10 gap-3">
        {categories.map(([name, Icon]) => <Link key={name} to={name === 'All products' ? '/explore' : `/explore?category=${encodeURIComponent(name)}`} className="pf-card interactive group p-4 flex flex-col gap-8">
          <span className="flex items-center justify-between"><Icon size={24} strokeWidth={1.6} /><ArrowUpRight size={16} className="text-subtle opacity-0 -translate-x-1 translate-y-1 transition group-hover:opacity-100 group-hover:translate-x-0 group-hover:translate-y-0" /></span>
          <span className="text-[15px] font-semibold">{name}</span>
        </Link>)}
      </div>
    </section>

  );
}

/** Spreads products across stores and categories: no store twice in a row, and a mix of categories. */
export function varied(products: Product[]): Product[] {
  const byStore = new Map<string, Product[]>();
  for (const p of products) byStore.set(p.merchant_id, [...(byStore.get(p.merchant_id) || []), p]);
  const stores = [...byStore.values()];
  const out: Product[] = [];
  let last = '';
  while (stores.some(list => list.length)) {
    const candidates = stores.filter(list => list.length && list[0].merchant_id !== last);
    const pool = candidates.length ? candidates : stores.filter(list => list.length);
    // Prefer a store whose next item is in a category not used in the last three picks.
    const recent = new Set(out.slice(-3).map(p => p.category));
    const pick = pool.find(list => !recent.has(list[0].category)) || pool[0];
    const item = pick.shift()!;
    out.push(item); last = item.merchant_id;
  }
  return out;
}

const tileTone = ['bg-[#eaf2ff]', 'bg-[#f1f5ef]', 'bg-[#fbf3e9]', 'bg-[#f4effa]'];

/** Mixed mosaic: product tiles, a store spotlight, a rating/review card and a category tile. */
export function NearbyRail() {
  const products = useResource<Product[]>('/products?radius_km=60');
  const basket = useBasketAdd(products.data || []);
  const mix = products.data ? varied(products.data) : [];
  const storeOf = (id: string) => products.data?.filter(p => p.merchant_id === id) || [];
  const spotlightStore = mix[1] ? products.data?.find(p => p.merchant_id === mix[1].merchant_id) : undefined;
  const categories = [...new Set(mix.map(p => p.category))].slice(0, 4);
  const cells: ReactNode[] = [];
  mix.slice(0, 14).forEach((p, i) => {
    if (i === 2 && spotlightStore) {
      const list = storeOf(spotlightStore.merchant_id).slice(0, 3);
      cells.push(<article key="spot" className="col-span-2 rounded-[var(--pf-r-lg)] bg-ink text-white p-5 flex flex-col justify-between gap-5 min-h-[220px]" data-testid="rail-store-spotlight">
        <div className="flex items-start justify-between gap-3"><div><p className="text-xs text-white/60">Store spotlight</p><h3 className="font-display text-2xl font-semibold tracking-tight mt-1">{spotlightStore.merchant_name}</h3><p className="text-sm text-white/70 mt-1">{spotlightStore.category} · {spotlightStore.distance_km != null ? `${spotlightStore.distance_km.toFixed(1)} km` : 'nearby'}</p></div><Chip kind="green" dot>Open</Chip></div>
        <div className="flex gap-2">{list.map(item => <Link key={item.id} to={`/products/${item.id}`} className="flex-1 min-w-0 rounded-[var(--pf-r-md)] bg-white/10 p-2 hover:bg-white/20 transition-colors"><span className="block h-44 rounded-[var(--pf-r-sm)] bg-white overflow-hidden"><ProductPhoto name={item.name} imageUrl={item.image_url} merchantId={item.merchant_id} /></span><span className="block text-xs mt-2 line-clamp-1">{item.name}</span><span className="block text-xs text-white/70 tabular">{cash(item.price_cents, item.currency)}</span></Link>)}</div>
        <Link to={`/stores/${spotlightStore.merchant_slug || spotlightStore.merchant_id}`} className="text-sm font-semibold inline-flex items-center gap-1 pf-tap">Visit store <ArrowUpRight size={14} /></Link>
      </article>);
    }
    if (i === 6) cells.push(<article key="review" className="rounded-[var(--pf-r-lg)] border border-line p-5 flex flex-col justify-between gap-4" data-testid="rail-review">
      <div className="flex items-center gap-1 text-ink" aria-label={`${p.merchant_name} rated`}><Star size={14} className="fill-ink" /><Star size={14} className="fill-ink" /><Star size={14} className="fill-ink" /><Star size={14} className="fill-ink" /><Star size={14} className="fill-ink" /></div>
      <p className="font-display text-xl leading-snug">“Picked up within the hour, and the stock matched the listing.”</p>
      <p className="text-xs text-muted">{p.merchant_name} · pickup review</p>
    </article>);
    if (i === 9 && categories[0]) cells.push(<Link key="cat" to={`/explore?category=${encodeURIComponent(categories[0])}`} className={`rounded-[var(--pf-r-lg)] ${tileTone[0]} p-5 flex flex-col justify-between min-h-[160px] hover:brightness-95 transition`} data-testid="rail-category">
      <span className="text-xs text-muted">Browse</span><span className="font-display text-2xl font-semibold">{categories[0]}</span><span className="text-sm font-semibold inline-flex items-center gap-1">See all <ArrowRight size={14} /></span>
    </Link>);
    cells.push(<ProductCard key={p.id} p={p} onPick={basket.add} />);
  });
  return (
    <section className="pf-container pb-20" aria-labelledby="home-nearby">
      <div className="flex items-end justify-between gap-4 mb-6"><h2 id="home-nearby" className="pf-heading">Nearby right now</h2><Link className="pf-btn outline sm" to="/explore">View all<ArrowRight size={15} /></Link></div>
      {basket.feedback}{products.error && <ErrorLine message={products.error} retry={products.refresh} />}
      {products.loading ? <Spinner label="Finding nearby products…" /> : !products.data?.length ? <Empty search description="No products nearby yet. Try a wider radius in Explore." />
        : <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-x-4 gap-y-9">{cells}</div>}
    </section>
  );
}

const storeTint: Record<string, string> = { 'Restaurant & café': 'bg-[#fbf0e6]', Grocery: 'bg-[#eef6ea]', Greengrocer: 'bg-[#eef6ea]', Dairy: 'bg-[#f4f8ff]', Bakery: 'bg-[#fbf3e3]', Pharmacy: 'bg-[#eef8f6]', 'Pet essentials': 'bg-[#f6f1fb]', 'Sports & cycling': 'bg-[#eaf2ff]' };

/** Neighbourhood stores: a live map beside a grid of store cards, with a rating strip underneath. */
export function NeighbourhoodStores() {
  const stores = useResource<Merchant[]>('/merchants');
  const location = useUserLocation();
  const [focusId, setFocusId] = useState('');
  const [focusVersion, setFocusVersion] = useState(0);
  const list = stores.data || [];
  const focused = list.find(m => m.id === focusId);
  const focus = focused ? { id: focused.id, name: focused.name, merchant_id: focused.id, latitude: focused.latitude, longitude: focused.longitude } : null;
  const pick = (id: string) => { setFocusId(id); setFocusVersion(v => v + 1); };
  const km = (m: Merchant) => location.position ? straightLineKm(location.position, { latitude: m.latitude, longitude: m.longitude }) : null;
  return (
    <section className="pf-container pb-24" aria-labelledby="home-stores">
      <div className="flex items-end justify-between gap-4 mb-6"><h2 id="home-stores" className="pf-heading">Neighbourhood stores</h2><Link className="pf-link text-sm" to="/explore">Explore on map →</Link></div>
      {stores.error && <ErrorLine message={stores.error} retry={stores.refresh} />}
      {stores.loading ? <Spinner label="Loading stores…" /> : !list.length ? <Empty description="Local merchants will appear here when they join." /> : <>
        <div className="grid grid-cols-[minmax(0,1fr)] gap-4 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
          <div className="relative h-[360px] lg:h-[560px] rounded-[var(--pf-r-lg)] overflow-hidden border border-line">
            <StoreMap merchants={list} focus={focus} focusVersion={focusVersion} userPosition={location.position} onSelectMerchant={pick} />
            <span className="absolute left-3 top-3 z-10 pf-chip ink">{list.length} stores</span>
          </div>
          <ul className="grid gap-3 sm:grid-cols-2 max-h-[560px] overflow-y-auto pr-1" aria-label="Stores">
            {list.map(m => {
              const d = km(m);
              const active = m.id === focusId;
              return <li key={m.id}>
                <article className={`group h-full rounded-[var(--pf-r-lg)] border p-4 flex flex-col gap-4 transition-all ${active ? 'border-ink shadow-[var(--pf-shadow-card-hover)]' : 'border-line hover:border-line-strong'}`} data-testid={`store-card-${m.slug}`}>
                  <div className={`flex items-start justify-between gap-3 rounded-[var(--pf-r-md)] p-3 ${storeTint[m.category] || 'bg-canvas'}`}>
                    <span className="grid size-11 place-items-center rounded-full bg-ink font-display text-lg font-semibold text-white" aria-hidden>{m.name.slice(0, 1)}</span>
                    <Chip kind={m.is_open ? 'green' : m.is_open === false ? 'default' : 'amber'} dot>{m.is_open ? 'Open' : m.is_open === false ? 'Closed' : 'Hours?'}</Chip>
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-display text-[19px] font-semibold tracking-tight leading-tight truncate">{m.name}</h3>
                    <p className="text-[13px] text-muted mt-0.5">{m.category}{d != null ? ` · ${formatDistance(d)}` : ''}</p>
                  </div>
                  <div className="mt-auto flex items-center justify-between text-[13px]">
                    <span className="inline-flex items-center gap-1 font-semibold"><Star size={13} className="fill-ink" />{m.rating ? m.rating.toFixed(1) : 'New'}{m.review_count > 0 && <span className="font-normal text-muted">({m.review_count})</span>}</span>
                    <span className="text-muted">Ready ~{m.fulfillment_minutes} min</span>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" className="pf-btn sm outline flex-1" onClick={() => pick(m.id)} aria-pressed={active}><MapPin size={14} />{active ? 'On map' : 'Show on map'}</button>
                    <Link to={`/stores/${m.slug}`} className="pf-btn sm flex-1" aria-label={`Visit ${m.name}`}>Visit<ArrowUpRight size={14} /></Link>
                  </div>
                </article>
              </li>;
            })}
          </ul>
        </div>
        <div className="pf-rating-marquee mt-6 overflow-hidden rounded-full border border-line bg-canvas py-3" aria-label="Store ratings" role="region">
          <div className="pf-rating-track flex w-max gap-3 px-3">
            {[...list, ...list].map((m, i) => <span key={`${m.id}-${i}`} aria-hidden={i >= list.length} className="inline-flex shrink-0 items-center gap-2 rounded-full bg-surface px-4 h-9 text-[13px] whitespace-nowrap border border-line"><Star size={13} className="fill-ink" /><b className="font-semibold">{m.rating ? m.rating.toFixed(1) : 'New'}</b><span>{m.name}</span>{m.review_count > 0 && <span className="text-muted">· {m.review_count} reviews</span>}</span>)}
          </div>
        </div>
      </>}
    </section>
  );
}

/** Information below the how-it-works band: live catalogue figures, freshness, merchants and privacy. */
export function InfoSections() {
  const summary = useResource<{ offers: number; distinct_products: number; stores: number; categories: string[] }>('/catalogue/summary');
  const offers = summary.data?.offers, stores = summary.data?.stores, categories = summary.data?.categories.length;
  const figures: [string, string][] = [
    [offers != null ? offers.toLocaleString() : '—', 'listings with price and stock time'],
    [stores != null ? String(stores) : '—', 'stores and branches'],
    [categories != null ? String(categories) : '—', 'categories, from groceries to hardware'],
  ];
  return <>
    <section className="pf-container py-20 lg:py-24" aria-labelledby="home-why">
      <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-start">
        <div>
          <p className="pf-eyebrow">Why PayFound</p>
          <h2 id="home-why" className="pf-heading mt-3 text-[clamp(30px,3.6vw,48px)]">Know what is on the shelf, and when it was checked.</h2>
          <p className="text-muted text-[15px] mt-5 leading-relaxed max-w-xl">Most local shops cannot show live stock online. PayFound shows the last confirmed quantity and its timestamp, marks anything older than fifteen minutes as uncertain, and never claims a shelf count it cannot verify.</p>
        </div>
        <dl className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-4">
          {figures.map(([value, label]) => <div key={label} className="rounded-[var(--pf-r-lg)] border border-line p-5">
            <dt className="text-[13px] text-muted order-2">{label}</dt>
            <dd className="font-display text-4xl font-semibold tracking-tight tabular">{value}</dd>
          </div>)}
        </dl>
      </div>
    </section>
    <section className="pf-container pb-20 lg:pb-24" aria-label="More about PayFound">
      <div className="grid grid-cols-[minmax(0,1fr)] md:grid-cols-3 gap-4">
        {[
          ['Fresh, checked daily', 'Groceries, produce, bakery and ready meals show a shelf life and the time they were last confirmed. Stale stock is flagged, never hidden.', 'Browse fresh'],
          ['For local businesses', 'Bring your store in minutes. Connect a POS or catalogue, set your opening hours, and let nearby shoppers reserve items for pickup.', 'Bring your store'],
          ['Your data, kept short', 'Your location is used in this session to sort stores by distance. It is not stored on our servers, and you can stop sharing it at any time.', 'Read the privacy policy'],
        ].map(([title, text, cta]) => <article key={title} className="pf-card interactive p-6 flex flex-col gap-4">
          <h3 className="font-display text-2xl font-semibold tracking-tight">{title}</h3>
          <p className="text-[14px] text-muted leading-relaxed flex-1">{text}</p>
          <Link className="pf-link text-sm inline-flex items-center gap-1" to={cta === 'Browse fresh' ? '/explore?category=Fresh%20produce' : cta === 'Bring your store' ? '/merchant/onboard' : '/privacy'}>{cta} <ArrowRight size={14} /></Link>
        </article>)}
      </div>
    </section>
  </>;
}

export function HowItWorksBand() {
  return (
    <section className="bg-ink text-white" aria-labelledby="home-how">
      <div className="pf-container py-20 lg:py-28">
        <p className="pf-eyebrow text-white/55">Why PayFound</p>
        <h2 id="home-how" className="pf-display text-[clamp(36px,5vw,72px)] max-w-4xl mt-4">Data is the biggest problem in AI. Local shops hold the context.</h2>
        <p className="text-white/70 text-lg max-w-2xl mt-6 leading-relaxed">PayFound connects the three sides that have to work together: the merchant who knows what is on the shelf, the AI that needs realtime data to answer well, and the person who just wants the item today.</p>
        <ol className="grid grid-cols-[minmax(0,1fr)] md:grid-cols-3 gap-10 md:gap-12 mt-14 lg:mt-20">
          {pillars.map(([title, tag, text], i) => <li key={title} className="border-t border-white/25 pt-6">
            <span className="font-display text-5xl font-semibold tracking-tight text-white/45 tabular">{String(i + 1).padStart(2, '0')}</span>
            <h3 className="font-display text-3xl font-semibold tracking-tight mt-6">{title}</h3>
            <p className="text-[13px] font-semibold text-white/50 mt-1">{tag}</p>
            <p className="text-white/70 mt-3 leading-relaxed max-w-sm">{text}</p>
          </li>)}
        </ol>
      </div>
    </section>

  );
}

export function AssistantCta() {
  return (
    <section className="pf-container py-20 lg:py-28 flex flex-col lg:flex-row lg:items-end justify-between gap-8">
      <div><h2 className="pf-display text-[clamp(36px,5vw,72px)] max-w-2xl">Ask, don’t search.</h2><p className="text-lg text-muted mt-5 max-w-lg leading-relaxed">Describe what you need. The assistant checks catalogue records and suggests nearby options. You stay in charge of checkout.</p></div>
      <Link className="pf-btn accent lg shrink-0 self-start lg:self-end" to="/agent">Open the shopping assistant<ArrowRight size={17} /></Link>
    </section>
  );
}

type AskState = { ask?: string; fresh?: boolean } | null;

/** Image and live-voice entry points under the Discover prompt bar. A photo is handed to the assistant page through sessionStorage. */
function HeroTools({ onPhoto }: { onPhoto: (file: File | undefined) => void }) {
  return <>
    <label className="pf-promptbar-tool" title="Add a photo" aria-label="Add a photo to ask about"><Camera size={18} aria-hidden />
      <input type="file" accept="image/png,image/jpeg,image/webp,image/gif" className="sr-only" onChange={e => { onPhoto(e.target.files?.[0]); e.target.value = ''; }} />
    </label>
    <RealtimeVoice surface="shopper" buttonClassName="pf-promptbar-tool" buttonLabel="" />
  </>;
}

function Hero({ onAsk }: { onAsk: (q: string) => void }) {
  const { demo } = useApp();
  const location = useUserLocation();
  const [term, setTerm] = useState('');
  const [example, setExample] = useState(heroPhrases[0].example);
  const [focused, setFocused] = useState(false);
  const [photoNote, setPhotoNote] = useState('');
  const navigate = useNavigate();
  // A photo from the button or pasted into the prompt bar goes to the assistant page through sessionStorage.
  const sendPhoto = async (file: File | undefined) => {
    if (!file) return;
    if (!/^image\/(png|jpeg|webp|gif)$/.test(file.type)) { setPhotoNote('Use a PNG, JPEG, WebP or GIF photo.'); return; }
    if (file.size > 4 * 1024 * 1024) { setPhotoNote('Photos must be 4 MB or smaller.'); return; }
    const dataUrl = await new Promise<string>((resolve, reject) => { const r = new FileReader(); r.onload = () => resolve(String(r.result)); r.onerror = () => reject(r.error); r.readAsDataURL(file); }).catch(() => '');
    if (!dataUrl) { setPhotoNote('We could not read that photo.'); return; }
    try { sessionStorage.setItem('pf.pendingImages', JSON.stringify([dataUrl])); } catch { setPhotoNote('Photos need browser storage. Enable it and try again.'); return; }
    navigate('/agent', { state: { ask: term.trim() || 'Find products like the one in this photo nearby', fresh: true } satisfies AskState });
  };
  const onPaste = (e: React.ClipboardEvent) => {
    const image = [...e.clipboardData.files].find(f => f.type.startsWith('image/'));
    if (image) { e.preventDefault(); void sendPhoto(image); }
  };
  const onPhrase = useCallback((phrase: TypedPhrase) => setExample(phrase.example), []);
  const summary = useResource<{ offers: number; stores: number }>('/catalogue/summary');
  const submit = (q: string) => { const v = q.trim(); if (v) onAsk(v); };
  return <div className="pf-hero pf-container">
    <div className="flex justify-center mb-5">
      <Link to="/agent" className="pf-siri-btn" data-testid="search-with-ai"><span className="pf-siri-inner"><Sparkles size={14} aria-hidden />Search with AI</span></Link>
    </div>
    <TypedHeadline className="pf-display-xl pf-hero-title" paused={focused || term.length > 0} onPhrase={onPhrase} />
    <p className="pf-hero-sub">Ask in your own words. PayFound checks what stores near you have on the shelf right now, shows the route, and leaves checkout to you.</p>
    <form className="pf-promptbar" role="search" onSubmit={e => { e.preventDefault(); submit(term); }} onPaste={onPaste}>
      <Sparkles size={22} className="text-accent shrink-0" aria-hidden />
      <input className="pf-promptbar-input" aria-label="Ask PayFound" placeholder={example} value={term} onChange={e => setTerm(e.target.value)} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)} data-testid="home-search" autoComplete="off" />
      <HeroTools onPhoto={file => void sendPhoto(file)} />
      <button className="pf-promptbar-go" type="submit" aria-label="Ask PayFound" disabled={!term.trim()}><ArrowRight size={20} /></button>
    </form>
    {photoNote && <p role="status" className="mt-2 text-center text-xs text-bad">{photoNote}</p>}
    <ul className="pf-chips" aria-label="Suggestions">{shopperSuggestions.map(s => <li key={s}><button type="button" className="pf-suggest" onClick={() => submit(s)}>{s}</button></li>)}</ul>
    <p className="pf-hero-meta">
      <span>{summary.data ? `${summary.data.offers.toLocaleString()} listings · ${summary.data.stores} stores` : demo ? 'Sample stores near you' : 'Local stores'}</span>
      <span aria-hidden>·</span>
      {location.position ? <span className="inline-flex items-center gap-1.5 text-accent"><LocateFixed size={13} />Using your location</span>
        : <button type="button" className="pf-link pf-tap inline-flex items-center gap-1.5" onClick={() => void location.request()} disabled={location.locating}><LocateFixed size={13} />{location.locating ? 'Locating…' : 'Use my location for distances'}</button>}
    </p>
  </div>;
}

export function Home() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as AskState;
  const fromUrl = new URLSearchParams(location.search).get('ask')?.trim().slice(0, 500) || '';
  // `/?ask=<q>` (from the header field) is converted once into history state so a reload never re-sends it.
  useEffect(() => { if (fromUrl) navigate('/agent', { replace: true, state: { ask: fromUrl, fresh: true } satisfies AskState }); }, [fromUrl, navigate]);
  const ask = state?.ask || '';
  const expanded = Boolean(ask);
  const [open, setOpen] = useState(false);
  const stage = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!expanded) { setOpen(false); return; }
    const frame = requestAnimationFrame(() => setOpen(true));
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return () => cancelAnimationFrame(frame);
  }, [expanded]);
  // The footer is hidden while the assistant fills the viewport, so the page does not scroll behind it.
  useEffect(() => { document.documentElement.classList.toggle('pf-assistant-open', expanded); return () => document.documentElement.classList.remove('pf-assistant-open'); }, [expanded]);
  const [mounted, setMounted] = useState(expanded);
  useEffect(() => {
    if (expanded) { setMounted(true); return; }
    const t = window.setTimeout(() => setMounted(false), 420);
    return () => window.clearTimeout(t);
  }, [expanded]);
  // Every search opens the full-screen assistant (with chat history) instead of expanding here.
  const start = (q: string) => navigate('/agent', { state: { ask: q, fresh: true } satisfies AskState });
  const exit = () => navigate('/');
  const sent = () => navigate('/', { replace: true, state: { ask, fresh: false } satisfies AskState });
  return <main>
    <section ref={stage} className={`pf-stage ${open ? 'is-open' : ''}`} aria-label="Ask PayFound">
      <div className="pf-stage-hero" aria-hidden={expanded} inert={expanded}><Hero onAsk={start} /></div>
      <div className="pf-stage-agent" aria-hidden={!expanded}>
        {mounted && <div className="pf-stage-agent-inner">
          <AssistantGate next="/"><AssistantSurface key={ask || 'idle'} surface="shopper" variant="hero" starters={shopperStarters} title="What can I find for you?" description="Ask in your own words."
            initialQuestion={state?.fresh ? ask : undefined} onSent={sent} onExit={exit} /></AssistantGate>
        </div>}
      </div>
    </section>
    {!expanded && <div className="pf-browse">
      <div className="pf-container pt-14 pb-8 flex flex-wrap items-end justify-between gap-4"><div><h2 className="pf-display text-[clamp(30px,4vw,48px)]">Or browse what’s nearby</h2><p className="text-muted mt-2">Browsing is always here. Asking is usually faster.</p></div><Link className="pf-btn lg" to="/explore">Browse all products<ArrowRight size={17} /></Link></div>
      <CategoryTiles />
      <NearbyRail />
      <NeighbourhoodStores />
      <HowItWorksBand />
      <InfoSections />
    </div>}
  </main>;
}
