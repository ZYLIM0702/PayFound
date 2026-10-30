import { useEffect, useState } from 'react';
import { NavLink, Navigate, Route, Routes } from 'react-router-dom';
import { Activity, AlertTriangle, LayoutDashboard, MessageSquare, RefreshCw, ShoppingBag, Store } from 'lucide-react';
import { api, messageOf, patch, post, type AdminOverview, type IntegrationStatus, type ReconciliationQueue } from '../lib/api';
import { useApp } from '../App';
import { ErrorLine, Notice, Spinner } from '../components/Shared';
import { WorkspaceShell, type WorkspaceNavGroup } from '../components/WorkspaceShell';
import { AccountMenu } from '../App';
import { AdminOverviewPage, AuditPage, MerchantsPage, OrdersAdminPage, ReconciliationPage, ReviewsPage } from './admin/pages';

const groups = (alerts: number): WorkspaceNavGroup[] => [
  { label: 'Platform', items: [{ to: '/admin', label: 'Overview', icon: LayoutDashboard, end: true }, { to: '/admin/merchants', label: 'Merchants', icon: Store }, { to: '/admin/orders', label: 'Orders', icon: ShoppingBag }] },
  { label: 'Trust & safety', items: [{ to: '/admin/reviews', label: 'Reviews', icon: MessageSquare }, { to: '/admin/audit', label: 'Audit log', icon: Activity }, { to: '/admin/reconciliation', label: 'Reconciliation', icon: AlertTriangle, badge: alerts > 0 ? <span className="min-w-5 h-5 px-1.5 rounded-full bg-bad text-white text-[11px] font-semibold grid place-items-center tabular">{alerts}</span> : undefined }] },
];

export function AdminConsole() {
  const { role } = useApp();
  const [data, setData] = useState<AdminOverview | null>(null);
  const [queue, setQueue] = useState<ReconciliationQueue | null>(null);
  const [integrations, setIntegrations] = useState<IntegrationStatus | null>(null);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState('');
  const reload = async () => {
    try {
      const [overview, reconciliation, integrationStatus] = await Promise.all([api<AdminOverview>('/admin/overview'), api<ReconciliationQueue>('/admin/reconciliation'), api<IntegrationStatus>('/integrations/status')]);
      setData(overview); setQueue(reconciliation); setIntegrations(integrationStatus); setError('');
    } catch (issue) { setError(messageOf(issue)); }
  };
  useEffect(() => { if (role === 'admin') void reload(); }, [role]);
  useEffect(() => { if (!info) return; const t = window.setTimeout(() => setInfo(''), 4500); return () => window.clearTimeout(t); }, [info]);
  const run = async (key: string, request: () => Promise<unknown>, message: string) => {
    setBusy(key); setError(''); setInfo('');
    try { await request(); setInfo(message); await reload(); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(''); }
  };
  if (role !== 'admin') return <main className="pf-container py-16"><ErrorLine message="Admin role required. Select Administrator in the account menu." /></main>;
  const alerts = (queue?.orders.length || 0) + (queue?.failed_jobs.length || 0);
  const topbar = <><div className="flex-1 text-sm font-semibold">Platform operations</div>
    <button className="pf-btn sm outline" disabled={Boolean(busy)} onClick={() => void reload()}><RefreshCw size={14} />Refresh</button><AccountMenu /></>;
  return <WorkspaceShell product="Admin" groups={groups(alerts)} topbar={topbar} sidebarFooter={<NavLink className="flex items-center h-9 px-3 rounded-[var(--pf-r-md)] text-sm text-muted hover:bg-sunk hover:text-ink" to="/merchant">Merchant workspace</NavLink>}>
    <div className="space-y-4 empty:hidden mb-4"><ErrorLine message={error} retry={() => void reload()} />{info && <Notice tone="green">{info}</Notice>}</div>
    {!data ? (error ? null : <Spinner label="Loading platform operations…" />) : <Routes>
      <Route index element={<AdminOverviewPage data={data} queue={queue} integrations={integrations} />} />
      <Route path="merchants" element={<MerchantsPage data={data} />} />
      <Route path="orders" element={<OrdersAdminPage data={data} />} />
      <Route path="reviews" element={<ReviewsPage data={data} busy={busy} onToggle={review => void run(`review-${review.id}`, () => patch(`/admin/reviews/${review.id}`, { visible: !review.visible }), review.visible ? 'Review hidden.' : 'Review restored.')} />} />
      <Route path="audit" element={<AuditPage data={data} />} />
      <Route path="reconciliation" element={<ReconciliationPage queue={queue} integrations={integrations} busy={busy} onReconcile={id => void run(`order-${id}`, () => post(`/orders/${id}/paypal/reconcile`), `Reconciliation requested for order ${id}.`)} onRetry={id => void run(`job-${id}`, () => post(`/admin/jobs/${id}/retry`), `Retry queued for job ${id}.`)} />} />
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>}
  </WorkspaceShell>;
}
