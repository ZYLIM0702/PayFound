import { useState, type ReactNode } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { type LucideIcon } from 'lucide-react';
import { Brand, Monogram } from './Brand';
import { BottomSheet, BottomTabs, usePhone, type TabItem } from './MobileShell';

export type WorkspaceNavItem = { to: string; label: string; icon: LucideIcon; end?: boolean; badge?: ReactNode };
export type WorkspaceNavGroup = { label?: string; items: WorkspaceNavItem[] };

const PRIMARY_TABS = 4;

/**
 * Application shell for merchant and admin workspaces. Desktop (>=1024px): fixed labelled sidebar.
 * Tablet (768-1023px): icon rail. Phone (<768px): bottom tab bar with the four main sections and a
 * "More" sheet for the rest.
 */
export function WorkspaceShell({ product, groups, sidebarTop, sidebarFooter, topbar, phoneExtra, children }: {
  phoneExtra?: ReactNode; product: string; groups: WorkspaceNavGroup[]; sidebarTop?: ReactNode; sidebarFooter?: ReactNode; topbar?: ReactNode; children: ReactNode;
}) {
  const [more, setMore] = useState(false);
  const phone = usePhone();
  const location = useLocation();
  const [lastPath, setLastPath] = useState(location.pathname);
  if (lastPath !== location.pathname) { setLastPath(location.pathname); setMore(false); }
  const all = groups.flatMap(g => g.items);
  const isOn = (item: WorkspaceNavItem) => item.end ? location.pathname === item.to : location.pathname === item.to || location.pathname.startsWith(`${item.to}/`);
  const primary = all.slice(0, PRIMARY_TABS);
  const rest = all.slice(PRIMARY_TABS);
  const badgeCount = (item: WorkspaceNavItem) => (typeof item.badge === 'object' && item.badge && 'props' in item.badge ? Number((item.badge.props as { children?: unknown }).children) || 0 : 0);
  const tabs: TabItem[] = primary.map(item => ({ to: item.to, label: item.label, icon: item.icon, end: item.end, badge: badgeCount(item) }));
  const moreBadge = rest.reduce((n, item) => n + badgeCount(item), 0);

  const link = (item: WorkspaceNavItem, mode: 'full' | 'rail') => {
    const { to, label, icon: Icon, end, badge } = item;
    return <NavLink key={to} to={to} end={end} title={mode === 'rail' ? label : undefined} aria-label={mode === 'rail' ? label : undefined}
      className={({ isActive }) => `group relative flex items-center ${mode === 'rail' ? 'justify-center h-11 w-11 mx-auto' : 'gap-3 h-10 px-3'} rounded-[var(--pf-r-md)] text-[14px] font-medium transition-colors ${isActive ? 'bg-ink text-white' : 'text-ink-2 hover:bg-sunk'}`}>
      <Icon size={mode === 'rail' ? 19 : 17} strokeWidth={1.9} className="shrink-0" />
      {mode === 'full' ? <><span className="flex-1 truncate">{label}</span>{badge}</> : badge && <span className="absolute -top-0.5 -right-0.5 scale-75 origin-top-right">{badge}</span>}
    </NavLink>;
  };
  const sidebar = <nav className="flex flex-col h-full" aria-label={`${product} navigation`}>
    <div className="h-16 flex items-center px-5 shrink-0"><Link to="/" className="flex items-center gap-2"><Brand /><span className="text-[13px] text-muted font-medium pl-2 ml-1 border-l border-line">{product}</span></Link></div>
    {sidebarTop && <div className="px-3 pb-3">{sidebarTop}</div>}
    <div className="flex-1 overflow-y-auto px-3 pb-4">{groups.map((group, i) => <div key={group.label || i} className="mt-3 first:mt-0">{group.label && <div className="px-3 pt-2 pb-1.5 text-[12px] font-semibold text-subtle">{group.label}</div>}
      {group.items.map(item => link(item, 'full'))}
    </div>)}</div>
    {sidebarFooter && <div className="border-t border-line p-3">{sidebarFooter}</div>}
  </nav>;
  const rail = <nav className="flex flex-col items-center h-full py-3 gap-1" aria-label={`${product} navigation`}>
    <Link to="/" className="h-12 grid place-items-center shrink-0" aria-label={`PayFound ${product}`}><Monogram size={30} /></Link>
    <div className="flex-1 overflow-y-auto w-full flex flex-col gap-1 px-2 pt-1">{groups.map((group, i) => <div key={group.label || i} className={`flex flex-col gap-1 ${i > 0 ? 'mt-2 pt-2 border-t border-line' : ''}`}>{group.items.map(item => link(item, 'rail'))}</div>)}</div>
  </nav>;
  return <div className="min-h-dvh bg-canvas md:pl-[72px] lg:pl-[var(--pf-sidebar-w)]">
    <aside className="hidden md:block lg:hidden fixed inset-y-0 left-0 w-[72px] bg-surface border-r border-line z-30">{rail}</aside>
    <aside className="hidden lg:block fixed inset-y-0 left-0 w-[var(--pf-sidebar-w)] bg-surface border-r border-line z-30">{sidebar}</aside>
    <header className="pf-ws-bar sticky top-0 z-20 h-14 md:h-16 backdrop-blur border-b border-line flex items-center gap-2 md:gap-3 px-[var(--pf-gutter)] bg-surface/90"><Link to="/" className="md:hidden shrink-0 inline-flex items-center min-h-11" aria-label={`PayFound ${product}`}><Monogram size={28} /></Link>{topbar}</header>
    <main id="main-content" tabIndex={-1} className={`pf-ws-main outline-none ${location.pathname.endsWith('/assistant') ? '' : 'px-[var(--pf-gutter)] py-5 md:py-8'}`}>{children}</main>
    {phone && <>
      <BottomTabs items={tabs} label={`${product} sections`} onMore={() => setMore(true)} moreActive={rest.some(isOn)} className="pf-ws-tabs" />
      <BottomSheet open={more} onOpenChange={setMore} title={`${product} menu`}>
        {phoneExtra}
        <nav aria-label={`${product} more sections`} className="px-3 pb-2">
          {moreBadge > 0 && <span className="sr-only">{moreBadge} pending in other sections</span>}
          {rest.map(item => <div key={item.to} className="[&_a]:!h-12">{link(item, 'full')}</div>)}
        </nav>
        {sidebarFooter && <div className="border-t border-line mt-2 p-3 [&_a]:!h-12">{sidebarFooter}</div>}
      </BottomSheet>
    </>}
  </div>;
}
