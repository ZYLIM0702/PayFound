import { lazy, Suspense, useEffect, useRef, useState, type ReactNode } from 'react';
import { BrowserRouter, NavLink, Route, Routes, Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { DropdownMenu } from 'radix-ui';
import { Check, ChevronDown, LogOut, ShoppingBag, Sparkles, Store, UserRound } from 'lucide-react';
import { AppProvider, useApp } from './lib/app-context';
import { CartProvider, useCart } from './lib/cart';
import { LocationProvider } from './lib/location';
import { messageOf, type Role } from './lib/api';
import { Empty, ErrorLine, FeatureBoundary, Notice, Spinner } from './components/Shared';
import { Brand } from './components/Brand';
import { PlacementGate } from './components/PlacementGate';
import { AccessGate } from './components/AccessGate';
import { ConsumerTabs, MobileSearch, usePhone, useTabbarSpace } from './components/MobileShell';
import { MerchantOnboarding } from './pages/MerchantSettings';
import { AuthPage, AuthCallback } from './pages/Auth';
const Home = lazy(() => import('./pages/Home').then(m => ({ default: m.Home })));
const Explore = lazy(() => import('./pages/Explore').then(m => ({ default: m.Explore })));
const Storefront = lazy(() => import('./pages/Storefront').then(m => ({ default: m.Storefront })));
const Checkout = lazy(() => import('./pages/Checkout').then(m => ({ default: m.Checkout })));
const Orders = lazy(() => import('./pages/Orders').then(m => ({ default: m.Orders })));
const ShopAgent = lazy(() => import('./pages/ShopAgent').then(m => ({ default: m.ShopAgent })));
const Basket = lazy(() => import('./pages/Basket').then(m => ({ default: m.Basket })));
const MerchantConsole = lazy(() => import('./pages/Merchant').then(m => ({ default: m.MerchantConsole })));
const AdminConsole = lazy(() => import('./pages/Admin').then(m => ({ default: m.AdminConsole })));
const PosSimulator = lazy(() => import('./pages/PosSimulator').then(m => ({ default: m.PosSimulator })));
const ProductPage = lazy(() => import('./pages/Product').then(m => ({ default: m.ProductPage })));
const Landing = lazy(() => import('./pages/Landing').then(m => ({ default: m.Landing })));
const MapPolicies = lazy(() => import('./pages/MapPolicies').then(m => ({ default: m.MapPolicies })));
export { useApp } from './lib/app-context';

const roleLabels: Record<Role, string> = { consumer: 'Shopper', merchant: 'Merchant', admin: 'Administrator' };

/** Demo role switcher or signed-in account menu. */
export function AccountMenu({ align = 'end' }: { align?: 'start' | 'end' }) {
  const { role, demo, changeRole, session, logout, ready } = useApp();
  const [error, setError] = useState('');
  const navigate = useNavigate();
  if (!demo && !session) return <Link className="pf-btn sm" to="/login">{ready ? 'Log in' : 'Loading…'}</Link>;
  return <><DropdownMenu.Root><DropdownMenu.Trigger className="pf-btn sm outline gap-2 !pl-1.5 max-sm:!px-1.5 max-sm:!border-0 max-sm:min-w-11" aria-label="Account and role">
    <span className="w-6 h-6 rounded-full bg-ink text-white grid place-items-center"><UserRound size={13} /></span><span className="hidden sm:inline">{demo ? `Demo ${roleLabels[role].toLowerCase()}` : 'Account'}</span><ChevronDown size={14} className="max-sm:hidden" />
  </DropdownMenu.Trigger><DropdownMenu.Portal><DropdownMenu.Content align={align} sideOffset={8} className="z-[1100] min-w-60 rounded-[var(--pf-r-lg)] bg-surface border border-line p-1.5 shadow-[var(--pf-shadow-float)]">
    {demo ? <>
      <DropdownMenu.Label className="px-3 pt-2 pb-1.5 text-xs text-muted">View the demo as</DropdownMenu.Label>
      {(['consumer', 'merchant', 'admin'] as Role[]).map(value => <DropdownMenu.Item key={value} className="flex items-center justify-between gap-3 h-9 px-3 rounded-[var(--pf-r-sm)] text-sm outline-none cursor-pointer data-[highlighted]:bg-sunk" onSelect={() => { changeRole(value); navigate(value === 'consumer' ? '/' : `/${value}`); }}>{roleLabels[value]}{role === value && <Check size={15} />}</DropdownMenu.Item>)}
    </> : <>
      <DropdownMenu.Label className="px-3 pt-2 pb-1.5 text-xs text-muted truncate max-w-64">{session?.user.email}</DropdownMenu.Label>
      <DropdownMenu.Item className="flex items-center h-9 px-3 rounded-[var(--pf-r-sm)] text-sm outline-none cursor-pointer data-[highlighted]:bg-sunk" onSelect={() => navigate('/account/orders')}>Your orders</DropdownMenu.Item>
      {role !== 'consumer' && <DropdownMenu.Item className="flex items-center h-9 px-3 rounded-[var(--pf-r-sm)] text-sm outline-none cursor-pointer data-[highlighted]:bg-sunk" onSelect={() => navigate('/merchant')}>Business workspace</DropdownMenu.Item>}
      {role === 'admin' && <DropdownMenu.Item className="flex items-center h-9 px-3 rounded-[var(--pf-r-sm)] text-sm outline-none cursor-pointer data-[highlighted]:bg-sunk" onSelect={() => navigate('/admin')}>Administration</DropdownMenu.Item>}
      <DropdownMenu.Separator className="h-px bg-line my-1.5" />
      <DropdownMenu.Item className="flex items-center gap-2 h-9 px-3 rounded-[var(--pf-r-sm)] text-sm outline-none cursor-pointer data-[highlighted]:bg-sunk" onSelect={async () => { try { await logout(); navigate('/login'); } catch (e) { setError(messageOf(e)); } }}><LogOut size={15} />Log out</DropdownMenu.Item>
    </>}
  </DropdownMenu.Content></DropdownMenu.Portal></DropdownMenu.Root>{error && <span className="sr-only" role="alert">{error}</span>}</>;
}

/** Header prompt: asks the assistant (assistant-first), which opens expanded on the home surface. */
function HeaderAsk() {
  const navigate = useNavigate();
  const [term, setTerm] = useState('');
  return <form role="search" className="relative hidden md:block flex-1 max-w-[560px]" onSubmit={e => { e.preventDefault(); const q = term.trim(); if (q) { setTerm(''); navigate('/agent', { state: { ask: q, fresh: true } }); } }}>
    <Sparkles size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-accent pointer-events-none" />
    <input className="w-full h-10 rounded-full bg-sunk border border-transparent pl-11 pr-4 text-sm placeholder:text-subtle focus:bg-surface focus:border-ink focus:outline-none transition-colors" placeholder="Ask PayFound — “a 65W charger I can pick up tonight”" aria-label="Ask the PayFound assistant" value={term} onChange={e => setTerm(e.target.value)} />
  </form>;
}

function Header() {
  const { role } = useApp();
  const { items } = useCart();
  const location = useLocation();
  const phone = usePhone();
  const count = items.reduce((n, x) => n + x.quantity, 0);
  const nav = [['/', 'Ask'], ['/explore', 'Browse'], ['/landing', 'Join us'], ['/account/orders', 'Account']] as const;
  return <header id="pf-header" className="sticky top-0 z-[1000] bg-surface/95 backdrop-blur border-b border-line">
    <div className="pf-container h-[var(--pf-header-h)] flex items-center gap-2 md:gap-4 lg:gap-8">
      <Link to="/" className="shrink-0 inline-flex items-center min-h-11" aria-label="PayFound home"><Brand /></Link>
      <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">{nav.map(([href, label]) => <NavLink key={href} to={href} end={href === '/'} className={({ isActive }) => `px-3 h-9 inline-flex items-center rounded-full text-sm font-semibold transition-colors ${isActive ? 'text-ink bg-sunk' : 'text-muted hover:text-ink'}`}>{label === 'Ask' ? <span className="pf-ask-shimmer">{label}</span> : label}</NavLink>)}</nav>
      {location.pathname !== '/' && location.pathname !== '/agent' ? <HeaderAsk /> : <div className="flex-1" />}
      <div className="flex items-center gap-1 md:gap-2 ml-auto shrink-0">
        {role !== 'consumer' && <Link to="/merchant" className="pf-btn sm ghost hidden lg:inline-flex"><Store size={15} />Business</Link>}
        {phone ? <MobileSearch /> : <Link className="pf-btn sm outline icon relative" to="/basket" data-testid="cart-link" aria-label={`Basket, ${count} items`}><ShoppingBag size={17} />{count > 0 && <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-accent text-white text-[11px] font-semibold grid place-items-center tabular">{count}</span>}</Link>}
        <AccountMenu />
      </div>
    </div>
  </header>;
}

function Footer({ flush = false }: { flush?: boolean }) {
  const { demo, session } = useApp();
  const signedOut = demo || !session;
  return <footer className={`pf-footer bg-ink text-white ${flush ? '' : 'mt-24'}`}>
    <div className="pf-container py-14 grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
      <div><Brand inverted /><p className="text-white/60 text-sm mt-4 max-w-xs leading-relaxed">Find it nearby. Pay directly. Get it today.</p>
        {signedOut && <div className="mt-6 flex flex-wrap gap-3" data-testid="footer-auth"><Link to="/login" className="inline-flex items-center justify-center h-11 px-6 rounded-full bg-white text-ink text-sm font-semibold hover:bg-white/90">Log in</Link><Link to="/signup" className="inline-flex items-center justify-center h-11 px-6 rounded-full border border-white/40 text-white text-sm font-semibold hover:bg-white/10">Sign up</Link></div>}</div>
      <div className="flex flex-col gap-2.5 text-sm"><span className="text-white/45 text-xs font-semibold mb-1">Shop</span><Link to="/" className="text-white/80 hover:text-white">Ask PayFound</Link><Link to="/explore" className="text-white/80 hover:text-white">Browse nearby</Link><Link to="/account" className="text-white/80 hover:text-white">Your account</Link></div>
      <div className="flex flex-col gap-2.5 text-sm"><span className="text-white/45 text-xs font-semibold mb-1">Business</span><Link to="/merchant/onboard" className="text-white/80 hover:text-white">Bring your store</Link><Link to="/landing#pricing" className="text-white/80 hover:text-white">Pricing</Link><a href="/developers/api/index.html" className="text-white/80 hover:text-white">API docs</a><Link to="/merchant" className="text-white/80 hover:text-white">Merchant workspace</Link><Link to="/pos/sell" className="text-white/80 hover:text-white">POS simulator</Link></div>
      <div className="flex flex-col gap-2.5 text-sm"><span className="text-white/45 text-xs font-semibold mb-1">Legal</span><Link to="/privacy" className="text-white/80 hover:text-white">Privacy</Link><Link to="/terms" className="text-white/80 hover:text-white">Terms</Link><a href="/image-credits.html" target="_blank" rel="noreferrer" className="text-white/80 hover:text-white">Photo credits</a></div>
    </div>
    <div className="pf-container py-5 border-t border-white/10 flex flex-wrap justify-between gap-2 text-xs text-white/45"><span>© PayFound</span></div>
  </footer>;
}

function Guard({ children, allow }: { children: ReactNode; allow?: Role[] }) {
  const { ready, session, demo, role, error, retry } = useApp();
  const location = useLocation();
  if (error) return <div className="pf-container py-12"><ErrorLine message={error} retry={retry} /></div>;
  if (!ready) return <Spinner label="Checking your session…" />;
  if (!session && !demo) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname + location.search)}`} replace />;
  if (allow && !allow.includes(role)) return <div className="pf-container py-12"><Empty title="Access restricted" description="Your account does not have access to this workspace."><Link className="pf-btn" to="/">Back to PayFound</Link><Link className="pf-btn outline" to="/merchant/onboard">Register a business</Link></Empty></div>;
  return children;
}

/** Consumer chrome: header, demo strip, footer and (phones) the bottom tab bar. */
function ConsumerLayout({ children, footer = true }: { children: ReactNode; footer?: boolean }) {
  const { demo } = useApp();
  const { pathname, search } = useLocation();
  // PayPal sends the user back here after the subscription approval window: /?billing=return or /?billing=cancel.
  const billing = new URLSearchParams(search).get('billing');
  const billingNote = billing === 'return' ? 'Back from PayPal. Your plan changes once PayPal confirms the subscription. Check its status in Plan.'
    : billing === 'cancel' ? 'Subscription approval was cancelled. Your plan is unchanged.' : '';
  const phone = usePhone();
  const banner = useRef<HTMLDivElement>(null);
  // Checkout keeps its pay buttons clear of the bar.
  const tabs = phone && !pathname.startsWith('/checkout');
  useTabbarSpace(tabs);
  useEffect(() => {
    const header = document.getElementById('pf-header');
    const measure = () => document.documentElement.style.setProperty('--pf-top-h', `${(header?.offsetHeight || 64) + (banner.current?.offsetHeight || 0)}px`);
    measure();
    const observer = new ResizeObserver(measure);
    if (header) observer.observe(header);
    if (banner.current) observer.observe(banner.current);
    return () => observer.disconnect();
  }, [demo]);
  const section = pathname.split('/')[1] || 'home';
  return <><a className="pf-skip" href="#main-content">Skip to content</a><Header />{demo && <div ref={banner} className="pf-demo-banner">Simulated payments move no funds.</div>}{billingNote && <div className="pf-container pt-3"><Notice tone={billing === 'return' ? 'blue' : 'amber'}>{billingNote}</Notice></div>}<div id="main-content" tabIndex={-1} className="outline-none"><PlacementGate><div key={section} className="pf-route">{children}</div></PlacementGate></div>{footer && <Footer flush={pathname === '/landing'} />}{tabs && <ConsumerTabs />}</>;
}

function Layout() {
  const { config, ready, error, retry, recovery } = useApp();
  const location = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [location.pathname]);
  if (error && !ready) return <div className="pf-container py-12"><ErrorLine message={error} retry={retry} /></div>;
  if (!config || !ready) return <div className="min-h-dvh grid place-items-center"><div className="flex flex-col items-center gap-6"><Brand /><Spinner inline label="Preparing PayFound…" /></div></div>;
  if (recovery && location.pathname !== '/reset-password' && location.pathname !== '/auth/callback') return <Navigate to="/reset-password" replace />;
  const c = (node: ReactNode, footer = true) => <ConsumerLayout footer={footer}>{node}</ConsumerLayout>;
  return <Routes>
    <Route path="/" element={c(<Home />)} /><Route path="/explore" element={c(<Explore />, false)} /><Route path="/map" element={<Navigate to="/explore" replace />} />
    <Route path="/stores/:slug" element={c(<Storefront />)} /><Route path="/products/:productId" element={c(<ProductPage />)} />
    <Route path="/basket" element={c(<Basket />)} /><Route path="/cart" element={<Navigate to="/basket" replace />} />
    <Route path="/landing" element={c(<Suspense fallback={<Spinner />}><Landing /></Suspense>)} />
    <Route path="/privacy" element={c(<MapPolicies privacy />)} /><Route path="/terms" element={c(<MapPolicies />)} />
    <Route path="/checkout/:orderId" element={c(<Guard><Checkout /></Guard>)} /><Route path="/account" element={<Navigate to="/account/orders" replace />} /><Route path="/account/:section" element={c(<Guard><Orders /></Guard>)} /><Route path="/orders" element={<Navigate to="/account/orders" replace />} />
    <Route path="/agent" element={c(<ShopAgent />, false)} />
    <Route path="/merchant/onboard" element={c(<Guard><MerchantOnboarding /></Guard>)} />
    <Route path="/merchant/*" element={<Guard allow={['merchant', 'admin']}><MerchantConsole /></Guard>} />
    <Route path="/admin/*" element={<Guard allow={['admin']}><AdminConsole /></Guard>} />
    <Route path="/pos" element={<Navigate to="/pos/sell" replace />} /><Route path="/pos/:view" element={<Guard><PosSimulator /></Guard>} />
    <Route path="/login" element={<AuthPage mode="login" />} /><Route path="/signup" element={<AuthPage mode="signup" />} /><Route path="/forgot-password" element={<AuthPage mode="forgot" />} /><Route path="/reset-password" element={<AuthPage mode="reset" />} /><Route path="/auth/callback" element={<AuthCallback />} />
    <Route path="*" element={c(<main className="pf-container py-24"><Empty title="Page not found" description="This page may have moved."><Link to="/" className="pf-btn">Back to PayFound</Link></Empty></main>)} />
  </Routes>;
}

export function App() { return <FeatureBoundary name="PayFound"><AccessGate><AppProvider><LocationProvider><CartProvider><BrowserRouter><Suspense fallback={<Spinner label="Loading…" />}><Layout /></Suspense></BrowserRouter></CartProvider></LocationProvider></AppProvider></AccessGate></FeatureBoundary>; }
