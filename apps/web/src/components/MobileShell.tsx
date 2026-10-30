import { useEffect, useState, useSyncExternalStore, type ReactNode } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Dialog } from 'radix-ui';
import { Compass, House, Search, ShoppingBag, Sparkles, UserRound, X, type LucideIcon } from 'lucide-react';
import { useCart } from '../lib/cart';
import '../styles/responsive.css';

/** Subscribes to a CSS media query. SSR-safe default is "not matching". */
export function useMediaQuery(query: string) {
  return useSyncExternalStore(
    notify => { const list = window.matchMedia(query); list.addEventListener('change', notify); return () => list.removeEventListener('change', notify); },
    () => window.matchMedia(query).matches, () => false);
}
/** True below the 768px tablet breakpoint: the phone "app" shell. */
export const usePhone = () => useMediaQuery('(max-width: 767px)');

export type TabItem = { to: string; label: string; icon: LucideIcon; end?: boolean; badge?: number; featured?: boolean; testId?: string; match?: (path: string) => boolean };

/** Fixed bottom tab bar (phones only). Safe-area aware; every target is at least 48px tall. */
export function BottomTabs({ items, label, onMore, moreActive, className = '' }: { items: TabItem[]; label: string; onMore?: () => void; moreActive?: boolean; className?: string }) {
  const { pathname } = useLocation();
  return <nav aria-label={label} className={`pf-tabbar ${className}`}>
    <ul>
      {items.map(({ to, label: text, icon: Icon, end, badge, featured, testId, match }) => {
        const active = match ? match(pathname) : end ? pathname === to : pathname === to || pathname.startsWith(`${to}/`);
        return <li key={to} className={featured ? 'is-featured' : undefined}>
          <NavLink to={to} end={end} data-testid={testId} aria-current={active ? 'page' : undefined} className={`pf-tab${active ? ' on' : ''}`} aria-label={badge ? `${text}, ${badge} items` : undefined}>
            <span className="pf-tab-icon"><Icon size={featured ? 22 : 22} strokeWidth={active || featured ? 2.2 : 1.8} />{!!badge && <span className="pf-tab-badge tabular" aria-hidden="true">{badge > 99 ? '99+' : badge}</span>}</span>
            <span className="pf-tab-label">{text}</span>
          </NavLink>
        </li>;
      })}
      {onMore && <li><button type="button" className={`pf-tab${moreActive ? ' on' : ''}`} onClick={onMore} aria-haspopup="dialog"><span className="pf-tab-icon"><span className="pf-tab-dots" aria-hidden="true"><i /><i /><i /></span></span><span className="pf-tab-label">More</span></button></li>}
    </ul>
  </nav>;
}

/** Consumer tab bar: Home, Browse, Assistant (centre), Basket, Account. */
export function ConsumerTabs() {
  const { items } = useCart();
  const phone = usePhone();
  const count = items.reduce((n, x) => n + x.quantity, 0);
  const tabs: TabItem[] = [
    { to: '/', label: 'Home', icon: House, end: true },
    { to: '/explore', label: 'Browse', icon: Compass },
    { to: '/agent', label: 'Assistant', icon: Sparkles, featured: true },
    { to: '/basket', label: 'Basket', icon: ShoppingBag, badge: count, testId: phone ? 'cart-link' : undefined },
    { to: '/account/orders', label: 'Account', icon: UserRound, match: p => p.startsWith('/account') || p.startsWith('/checkout') },
  ];
  return <BottomTabs items={tabs} label="App navigation" />;
}

/** Full-width search sheet opened from the compact phone top bar. */
export function MobileSearch({ children }: { children?: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [term, setTerm] = useState('');
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [last, setLast] = useState(pathname);
  if (last !== pathname) { setLast(pathname); setOpen(false); }
  const go = (kind: 'search' | 'ask') => {
    const q = term.trim(); if (!q) return;
    setOpen(false); setTerm('');
    if (kind === 'ask') navigate('/agent', { state: { ask: q, fresh: true } });
    else navigate(`/explore?q=${encodeURIComponent(q)}`);
  };
  return <Dialog.Root open={open} onOpenChange={setOpen}>
    <Dialog.Trigger asChild><button type="button" className="pf-btn ghost icon" aria-label="Search"><Search size={20} /></button></Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay className="pf-msheet-overlay" />
      <Dialog.Content className="pf-search-sheet" aria-describedby={undefined}>
        <Dialog.Title className="sr-only">Search PayFound</Dialog.Title>
        <form role="search" onSubmit={e => { e.preventDefault(); go('search'); }}>
          <div className="pf-search-row">
            <Search size={18} className="text-muted shrink-0" aria-hidden="true" />
            <input autoFocus type="search" enterKeyHint="search" className="pf-search-input" aria-label="Search products or ask a question" placeholder="Search products near you" value={term} onChange={e => setTerm(e.target.value)} />
            <Dialog.Close className="pf-btn ghost icon" aria-label="Close search"><X size={20} /></Dialog.Close>
          </div>
          <div className="pf-search-actions">
            <button type="submit" className="pf-btn w-full" disabled={!term.trim()}><Search size={17} />Search nearby</button>
            <button type="button" className="pf-btn soft w-full" disabled={!term.trim()} onClick={() => go('ask')}><Sparkles size={17} />Ask the assistant</button>
          </div>
        </form>
        {children}
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>;
}

/** Bottom sheet used for the workspace "More" menu. */
export function BottomSheet({ open, onOpenChange, title, children }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; children: ReactNode }) {
  return <Dialog.Root open={open} onOpenChange={onOpenChange}>
    <Dialog.Portal>
      <Dialog.Overlay className="pf-msheet-overlay" />
      <Dialog.Content className="pf-bottom-sheet" aria-describedby={undefined}>
        <span className="pf-sheet-grip" aria-hidden="true" />
        <div className="flex items-center justify-between px-5 pb-1"><Dialog.Title className="pf-title !text-[17px]">{title}</Dialog.Title><Dialog.Close className="pf-btn ghost icon" aria-label="Close"><X size={18} /></Dialog.Close></div>
        {children}
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>;
}

/** Marks <html> while a tab bar is mounted so pages can reserve space for it. */
export function useTabbarSpace(active: boolean) {
  useEffect(() => {
    if (!active) return;
    document.documentElement.classList.add('pf-has-tabbar');
    return () => document.documentElement.classList.remove('pf-has-tabbar');
  }, [active]);
}

/** Height (px) the fixed tab bar currently occupies, 0 when hidden. Used by viewport-fill pages. */
export function tabbarHeight() {
  const el = document.querySelector<HTMLElement>('.pf-tabbar');
  return el && getComputedStyle(el).display !== 'none' ? el.getBoundingClientRect().height : 0;
}
