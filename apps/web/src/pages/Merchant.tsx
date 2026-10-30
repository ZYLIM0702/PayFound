import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { Link, Navigate, Route, Routes } from 'react-router-dom';
import { BadgeDollarSign, BarChart3, CalendarClock, LayoutDashboard, Link2, MessageCircle, Star, Wallet, MonitorSmartphone, Package, Settings, ShoppingBag, Sparkles, Store, TrendingUp } from 'lucide-react';
import { messageOf, patch, post, scoped, type Dashboard, type Merchant, type Order } from '../lib/api';
import { useApp } from '../lib/app-context';
import { useResource } from '../lib/use-resource';
import { ConfirmDialog, Empty, ErrorLine, FeatureBoundary, Notice, Spinner } from '../components/Shared';
import { WorkspaceShell, type WorkspaceNavGroup } from '../components/WorkspaceShell';
import { AccountMenu } from '../App';
import { MerchantContext, type MerchantCtx, type MerchantNotices } from './merchant/context';
import { Overview } from './merchant/Overview';
import { NotificationBell } from './merchant/Notifications';
import { OrdersPage } from './merchant/Orders';
import { InventoryPage } from './merchant/Inventory';
import { PickupSchedule } from './merchant/PickupSchedule';
import { MerchantAssistant } from './agent/MerchantAssistant';
import { ConnectionsPage } from './merchant/Connections';
import { MerchantSettings } from './MerchantSettings';
import { PaymentsPage } from './merchant/Payments';
import { ReviewsPage } from './merchant/Reviews';
import { PlanPage } from './merchant/Plan';
import { MessagesPage } from './merchant/Messages';

const ForecastPage = lazy(() => import('./merchant/ForecastPage').then(m => ({ default: m.ForecastPage })));
const AnalyticsPage = lazy(() => import('./merchant/Analytics').then(m => ({ default: m.AnalyticsPage })));
type StoreStatus = 'auto' | 'open' | 'closed';

export function MerchantConsole() {
  const { merchantId, setMerchantId, me, demo } = useApp();
  // The demo shows one business only: Northside Electronics. Other demo stores stay in the data but are not offered.
  const DEMO_STORE = 'm1';
  const demoStore = demo && Boolean(me?.memberships.some(m => m.merchant_id === DEMO_STORE));
  useEffect(() => { if (demoStore && merchantId !== DEMO_STORE) setMerchantId(DEMO_STORE); }, [demoStore, merchantId, setMerchantId]);
  const resource = useResource<Dashboard>(merchantId ? scoped('/merchant/dashboard', merchantId) : null, 15000);
  const noticeRes = useResource<MerchantNotices>(merchantId ? scoped('/merchant/notifications', merchantId) : null, 8000);
  const profile = useResource<Merchant>(merchantId ? scoped('/merchant/profile', merchantId) : null);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState(false);
  const [refundOrder, setRefundOrder] = useState<Order | null>(null);
  useEffect(() => { setRefundOrder(null); setError(''); setInfo(''); }, [merchantId]);
  useEffect(() => { if (!info) return; const timer = window.setTimeout(() => setInfo(''), 4500); return () => window.clearTimeout(timer); }, [info]);
  const { refresh } = resource;
  const refreshNotices = noticeRes.refresh;
  const notices = useMemo<MerchantNotices>(() => noticeRes.data || { unread: 0, notifications: [] }, [noticeRes.data]);
  const markNoticeRead = useCallback(async (id: string) => { try { await post(`/merchant/notifications/${encodeURIComponent(id)}/read`, {}); } catch { /* the next poll shows the true state */ } await refreshNotices(); }, [refreshNotices]);
  const run = useCallback(async (path: string, body: object = {}) => {
    setBusy(true); setError('');
    try { await post(path, body); setInfo('Order updated.'); await refresh(); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); }
  }, [refresh]);
  const setStatus = async (status: StoreStatus) => {
    if (!merchantId) return;
    try { await patch(scoped('/merchant/status', merchantId), { status }); setInfo(`Store status set to ${status}.`); await Promise.all([profile.refresh(), refresh()]); } catch (issue) { setError(messageOf(issue)); }
  };
  const data = resource.data;
  const ctx = useMemo<MerchantCtx | null>(() => merchantId && data ? { merchantId, dashboard: data, notices, markNoticeRead, refreshNotices, refresh, busy, run, requestRefund: setRefundOrder, flash: setInfo, fail: setError } : null, [merchantId, data, notices, markNoticeRead, refreshNotices, refresh, busy, run]);
  if (!merchantId) return <main className="pf-container py-10"><Empty title="Choose or create a business" description="A merchant membership is needed for this workspace."><Link className="pf-btn" to="/merchant/onboard">Register a store</Link></Empty></main>;

  const pending = data?.pending_count || 0;
  const groups: WorkspaceNavGroup[] = [
    { label: 'Operate', items: [
      { to: '/merchant', label: 'Overview', icon: LayoutDashboard, end: true },
      { to: '/merchant/orders', label: 'Orders', icon: ShoppingBag, badge: pending > 0 ? <span className="min-w-5 h-5 px-1.5 rounded-full bg-accent text-white text-[11px] font-semibold grid place-items-center tabular">{pending}</span> : undefined },
      { to: '/merchant/payments', label: 'Payments', icon: Wallet },
      { to: '/merchant/inventory', label: 'Inventory', icon: Package },
      { to: '/merchant/pickup', label: 'Pickup', icon: CalendarClock },
      { to: '/merchant/reviews', label: 'Reviews', icon: Star },
      { to: '/merchant/messages', label: 'Messages', icon: MessageCircle },
    ] },
    { label: 'Insight', items: [
      { to: '/merchant/forecast', label: 'Forecast', icon: TrendingUp },
      { to: '/merchant/analytics', label: 'Analytics', icon: BarChart3 },
      { to: '/merchant/assistant', label: 'Assistant', icon: Sparkles },
    ] },
    { label: 'Business', items: [
      { to: '/merchant/plan', label: 'Plan', icon: BadgeDollarSign },
      { to: '/merchant/connections', label: 'Connections', icon: Link2 },
      { to: '/merchant/settings', label: 'Settings', icon: Settings },
    ] },
  ];
  const current = (profile.data?.status_override || 'auto') as StoreStatus;
  const statusControl = <div className="pf-segmented" role="group" aria-label="Store status">{(['auto', 'open', 'closed'] as const).map(status => <button key={status} aria-pressed={current === status} title={status === 'auto' ? 'Follow branch opening hours' : `Mark the store ${status}`} onClick={() => void setStatus(status)}>{status[0].toUpperCase() + status.slice(1)}</button>)}</div>;
  const topbar = <>
    <div className="flex items-center gap-2 min-w-0 flex-1"><Store size={16} className="text-muted shrink-0 hidden sm:block" />
      {demoStore
        ? <span className="font-semibold text-sm truncate" data-testid="demo-store-name">{me?.memberships.find(m => m.merchant_id === DEMO_STORE)?.merchant_name}</span>
        : <select className="pf-select sm !w-auto max-w-[260px] min-w-0 !h-9 md:!h-9 font-semibold" value={merchantId} disabled={busy} onChange={e => setMerchantId(e.target.value)} aria-label="Business">{me?.memberships.map(m => <option key={m.merchant_id} value={m.merchant_id}>{m.merchant_name}</option>)}</select>}
      </div>
    <div className="hidden md:block">{statusControl}</div>
    {demo && <Link className="pf-btn sm outline hidden md:inline-flex" to="/pos/sell"><MonitorSmartphone size={15} />Open POS</Link>}
    <NotificationBell notices={notices} markRead={markNoticeRead} />
    <AccountMenu />
  </>;
  return <WorkspaceShell product="Business" groups={groups} topbar={topbar} phoneExtra={<div className="px-5 pb-3"><p className="text-xs text-muted mb-2">Store status</p>{statusControl}</div>} sidebarFooter={<Link className="flex items-center gap-2 h-9 px-3 rounded-[var(--pf-r-md)] text-sm text-muted hover:bg-sunk hover:text-ink" to="/explore">Back to PayFound</Link>}>
    <div className="space-y-4 empty:hidden mb-4">{error || resource.error ? <ErrorLine message={error || resource.error} retry={() => { setError(''); void refresh(); }} /> : null}{info && <Notice tone="green">{info}</Notice>}</div>
    {resource.loading || !ctx ? <Spinner label="Loading your workspace…" /> :
      <MerchantContext.Provider value={ctx}><FeatureBoundary name="This page" key={merchantId}><Suspense fallback={<Spinner />}><Routes>
        <Route index element={<Overview />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="payments" element={<PaymentsPage merchantId={merchantId} />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="pickup" element={<PickupSchedule merchantId={merchantId} orders={ctx.dashboard.orders} />} />
        <Route path="reviews" element={<ReviewsPage merchantId={merchantId} />} />
        <Route path="plan" element={<PlanPage merchantId={merchantId} />} />
        <Route path="messages" element={<MessagesPage merchantId={merchantId} />} />
        <Route path="forecast" element={<ForecastPage merchantId={merchantId} />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="assistant" element={<MerchantAssistant merchantId={merchantId} />} />
        <Route path="connections" element={<ConnectionsPage />} />
        <Route path="settings" element={<MerchantSettings merchantId={merchantId} />} />
        <Route path="*" element={<Navigate to="/merchant" replace />} />
      </Routes></Suspense></FeatureBoundary></MerchantContext.Provider>}
    <ConfirmDialog open={Boolean(refundOrder)} destructive title="Refund this order?" description="A provider refund will be requested. Stock is released only after the refund is confirmed." confirmLabel="Request refund" busy={busy} onClose={() => setRefundOrder(null)} onConfirm={async () => { if (refundOrder) await run(`/orders/${refundOrder.id}/refund`); setRefundOrder(null); }} />
  </WorkspaceShell>;
}
