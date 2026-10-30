import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom';
import { CircleHelp, Gift, Heart, MessageCircle, Search, Settings, ShoppingBag, ShoppingCart, Star, Truck, Wallet, X } from 'lucide-react';
import { messageOf, post, type Order } from '../lib/api';
import { useCart } from '../lib/cart';
import { useResource } from '../lib/use-resource';
import { tabbarHeight } from '../components/MobileShell';
import { ErrorLine, Notice, Spinner } from '../components/Shared';
import { StaffInvitations } from './MerchantSettings';
import { OrdersPanel } from './account/OrdersPanel';
import { CouponsPanel, DeliveryPanel, ReviewsPanel, WishlistPanel } from './account/Panels';
import { CartPanel } from './account/CartPanel';
import { PaymentsHub } from './account/PaymentsHub';
import { MessagesPanel } from './account/MessagesPanel';
import { HelpPanel } from './account/HelpPanel';
import { SettingsPanel } from './account/SettingsPanel';
import { isOpenOrder, matchesFilter, type MyReview, type Thread, type WishItem } from './account/shared';

type Section = 'orders' | 'cart' | 'wishlist' | 'payments' | 'messages' | 'help' | 'settings' | 'coupons' | 'reviews' | 'delivery';
type NavItem = { id: Section; label: string; icon: ReactNode; hint: string };
const MAIN: NavItem[] = [
  { id: 'orders', label: 'Orders', icon: <ShoppingBag size={17} />, hint: 'Search orders by store, product or order id' },
  { id: 'cart', label: 'Cart', icon: <ShoppingCart size={17} />, hint: 'Search your cart' },
  { id: 'wishlist', label: 'Wishlist', icon: <Heart size={17} />, hint: 'Search saved items' },
  { id: 'payments', label: 'Payments', icon: <Wallet size={17} />, hint: 'Search payments by store or order' },
  { id: 'messages', label: 'Messages', icon: <MessageCircle size={17} />, hint: 'Search conversations' },
  { id: 'help', label: 'Help center', icon: <CircleHelp size={17} />, hint: 'Search help articles' },
  { id: 'settings', label: 'Settings', icon: <Settings size={17} />, hint: 'Settings' },
];
const MORE: NavItem[] = [
  { id: 'coupons', label: 'Coupons', icon: <Gift size={17} />, hint: 'Search coupons' },
  { id: 'reviews', label: 'Reviews', icon: <Star size={17} />, hint: 'Search your reviews' },
  { id: 'delivery', label: 'Delivery', icon: <Truck size={17} />, hint: 'Delivery' },
];
const ALL = [...MAIN, ...MORE];

export function Orders() {
  const { section: slug } = useParams();
  const navigate = useNavigate();
  const current = ALL.find(s => s.id === slug);
  if (!current) return <Navigate to="/account/orders" replace />;
  return <Account section={current.id} nav={current} go={(s: Section) => navigate(`/account/${s}`)} />;
}

/** Height from the top of <main> to the bottom of the viewport, so every section fits one screen and scrolls inside. */
function useFitHeight() {
  const ref = useRef<HTMLElement>(null);
  const [h, setH] = useState(0);
  useEffect(() => {
    const measure = () => { const top = ref.current ? ref.current.getBoundingClientRect().top + window.scrollY : 0; setH(Math.max(520, window.innerHeight - tabbarHeight() - top - 8)); };
    measure(); window.addEventListener('resize', measure);
    const t = window.setTimeout(measure, 600);
    return () => { window.removeEventListener('resize', measure); window.clearTimeout(t); };
  }, []);
  return { ref, style: h ? { height: h } : undefined };
}

function Account({ section, nav, go: navTo }: { section: Section; nav: NavItem; go: (s: Section) => void }) {
  const resource = useResource<Order[]>('/orders', 10000);
  const notifications = useResource<{ notifications: { id: string; order_id: string; message: string; seen_at: string | null }[] }>('/notifications', 15000);
  const wishlist = useResource<{ items: WishItem[] }>('/me/wishlist');
  const reviews = useResource<{ reviews: MyReview[] }>('/me/reviews');
  const threads = useResource<{ threads: Thread[] }>('/me/messages');
  const cart = useCart();
  const fit = useFitHeight();
  const [query, setQuery] = useState('');
  const [deliverFor, setDeliverFor] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [showAllUpdates, setShowAllUpdates] = useState(false);
  useEffect(() => { if (!info) return; const t = window.setTimeout(() => setInfo(''), 6000); return () => window.clearTimeout(t); }, [info]);
  const orders = useMemo(() => resource.data?.filter(o => !o.id.startsWith('seed-')) || [], [resource.data]);
  const unseen = notifications.data?.notifications.filter(n => !n.seen_at) || [];
  const q = query.trim().toLowerCase();
  const wishItems = wishlist.data?.items || [];
  const myReviews = reviews.data?.reviews || [];
  const cartCount = cart.items.reduce((sum, x) => sum + x.quantity, 0);
  const badges: Partial<Record<Section, number>> = {
    orders: orders.filter(o => matchesFilter(o, 'active') || matchesFilter(o, 'ready')).length,
    cart: cartCount, wishlist: wishItems.length, messages: threads.data?.threads.length ?? 0,
  };
  const go = (s: Section, nextQuery = '') => { setQuery(nextQuery); setError(''); navTo(s); };
  const refreshAll = async () => { await Promise.all([resource.refresh(), reviews.refresh()]); };
  const common = { onError: setError, onInfo: setInfo };
  const searchable = section !== 'settings' && section !== 'delivery';

  const tab = (s: NavItem) => <Link key={s.id} to={`/account/${s.id}`} role="tab" id={`tab-${s.id}`} aria-selected={section === s.id} aria-controls="account-pane" aria-current={section === s.id ? 'page' : undefined}
    onClick={() => { setQuery(''); setError(''); }}
    title={s.label} aria-label={s.label} className={`relative shrink-0 flex items-center gap-2.5 h-11 md:h-10 px-3.5 md:px-0 md:justify-center lg:justify-start lg:px-3.5 rounded-full md:rounded-lg text-sm font-semibold whitespace-nowrap transition-colors ${section === s.id ? 'bg-ink text-white' : 'text-ink-2 hover:bg-sunk'}`}>
    {s.icon}<span className="md:hidden lg:inline lg:flex-1 lg:text-left">{s.label}</span>
    {!!badges[s.id] && <span className={`text-[11.5px] tabular px-1.5 rounded-full md:absolute md:top-0 md:right-0 md:scale-75 lg:static lg:scale-100 ${section === s.id ? 'bg-white/20' : 'bg-sunk text-muted'}`} aria-label={`${badges[s.id]} items`}>{badges[s.id]}</span>}
  </Link>;

  return <main ref={fit.ref} style={fit.style} className="pf-container pt-3 pb-2 sm:pt-4 flex flex-col gap-3 min-h-[520px]">
    <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
      <h1 className="pf-heading !text-[28px] shrink-0">My account</h1>
      <form role="search" className="relative flex-1 min-w-[220px] max-w-2xl" onSubmit={e => e.preventDefault()}>
        <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" aria-hidden="true" />
        <input className="pf-input w-full !pl-10 !pr-9" type="search" disabled={!searchable} aria-label={`Search ${nav.label.toLowerCase()}`} placeholder={searchable ? nav.hint : 'Search is not used on this page'} value={query} onChange={e => setQuery(e.target.value)} />
        {query && <button type="button" aria-label="Clear search" className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full hover:bg-sunk" onClick={() => setQuery('')}><X size={14} /></button>}
      </form>
    </div>
    <div className="empty:hidden space-y-2"><ErrorLine message={error || resource.error} />{info && <Notice tone="green">{info}</Notice>}<StaffInvitations />
      {unseen.length > 0 && <aside className="pf-card px-4 py-1.5" aria-label="Order updates"><ul className="divide-y divide-line">{unseen.slice(0, showAllUpdates ? 10 : 1).map(n => <li className="flex items-center justify-between gap-3 py-1.5 text-sm" key={n.id}><Link className="hover:underline underline-offset-2 truncate pf-tap" to={`/checkout/${n.order_id}`}>{n.message}</Link><span className="flex items-center gap-3 shrink-0">{!showAllUpdates && unseen.length > 1 && <button className="pf-link text-[13px]" onClick={() => setShowAllUpdates(true)}>{unseen.length - 1} more</button>}<button className="pf-link text-[13px]" onClick={async () => { try { await post(`/notifications/${n.id}/read`); await notifications.refresh(); } catch (issue) { setError(messageOf(issue)); } }}>Mark read</button></span></li>)}</ul></aside>}</div>
    <div className="grid grid-cols-[minmax(0,1fr)] grid-rows-[auto_minmax(0,1fr)] md:grid-rows-none md:grid-cols-[64px_minmax(0,1fr)] lg:grid-cols-[230px_minmax(0,1fr)] gap-3 lg:gap-4 flex-1 min-h-0">
      <nav aria-label="Account sections" className="min-w-0 md:pf-card md:p-2 md:self-start">
        <div role="tablist" aria-orientation="vertical" className="flex md:flex-col gap-1 overflow-x-auto md:overflow-visible pb-1 md:pb-0 [scrollbar-width:none]">
          {MAIN.map(tab)}
          <span className="hidden md:block h-px bg-line my-1" aria-hidden="true" />
          {MORE.map(tab)}
        </div>
      </nav>
      <section id="account-pane" role="tabpanel" aria-labelledby={`tab-${section}`} className="pf-card overflow-hidden flex flex-col min-h-0">
        {resource.loading && section === 'orders' ? <Spinner /> : <>
          {section === 'orders' && <OrdersPanel orders={orders} query={q} onChanged={refreshAll} onDeliver={id => { setDeliverFor(id); go('delivery'); }} {...common} />}
          {section === 'cart' && <CartPanel query={q} savedCount={wishItems.length} />}
          {section === 'wishlist' && <WishlistPanel items={wishItems} query={q} loading={wishlist.loading} refresh={async () => { await wishlist.refresh(); }} {...common} />}
          {section === 'payments' && <PaymentsHub orders={orders} query={q} {...common} />}
          {section === 'messages' && <MessagesPanel query={q} {...common} />}
          {section === 'help' && <HelpPanel query={q} orders={orders} {...common} />}
          {section === 'settings' && <SettingsPanel {...common} />}
          {section === 'coupons' && <CouponsPanel query={q} />}
          {section === 'reviews' && <ReviewsPanel reviews={myReviews} orders={orders} query={q} loading={reviews.loading} onReview={id => go('orders', id)} />}
          {section === 'delivery' && <DeliveryPanel orders={orders.filter(isOpenOrder)} preselect={deliverFor} {...common} />}
        </>}
      </section>
    </div>
  </main>;
}
