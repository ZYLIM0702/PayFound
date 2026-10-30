import { Link } from 'react-router-dom';
import { Popover } from 'radix-ui';
import { Bell, ChefHat } from 'lucide-react';
import { Panel } from '../../components/Shared';
import { useMerchant, type MerchantNotice, type MerchantNotices } from './context';

const ACTIONABLE = ['RESERVED', 'PAID', 'ACCEPTED'];
const ago = (iso: string) => { const m = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000)); return m < 1 ? 'just now' : m < 60 ? `${m} min ago` : `${Math.round(m / 60)} h ago`; };

/** Bell with unread count for the workspace top bar. */
export function NotificationBell({ notices, markRead }: { notices: MerchantNotices; markRead: (id: string) => Promise<void> }) {
  return <Popover.Root>
    <Popover.Trigger asChild><button className="pf-btn ghost icon relative" data-testid="merchant-bell" aria-label={notices.unread ? `Notifications, ${notices.unread} unread` : 'Notifications'}>
      <Bell size={18} />{notices.unread > 0 && <span className="absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 rounded-full bg-accent text-white text-[10px] font-semibold grid place-items-center tabular" data-testid="merchant-bell-count">{notices.unread}</span>}
    </button></Popover.Trigger>
    <Popover.Portal><Popover.Content className="z-50 w-[min(360px,calc(100vw-24px))] max-h-[70vh] overflow-y-auto rounded-[var(--pf-r-lg)] bg-surface border border-line shadow-[var(--pf-shadow-float)] pf-enter" align="end" sideOffset={8}>
      <p className="px-4 py-3 text-sm font-semibold border-b border-line">Notifications</p>
      {notices.notifications.length === 0 ? <p className="px-4 py-6 text-sm text-muted">Nothing yet. New reservations appear here.</p> : <ul className="divide-y divide-line">
        {notices.notifications.slice(0, 8).map(n => <li key={n.id} className="px-4 py-3 flex gap-3" data-testid="merchant-notice">
          <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${n.seen_at ? 'bg-line-strong' : 'bg-accent'}`} aria-hidden />
          <div className="min-w-0 flex-1"><p className="text-sm leading-snug">{n.message}</p><p className="text-xs text-muted mt-1">{ago(n.created_at)}{!n.seen_at && <> · <button className="underline underline-offset-2" onClick={() => void markRead(n.id)}>Mark read</button></>}</p></div>
        </li>)}
      </ul>}
      <div className="px-4 py-3 border-t border-line"><Link className="pf-link text-sm" to="/merchant">Open overview</Link></div>
    </Popover.Content></Popover.Portal>
  </Popover.Root>;
}

function Row({ n }: { n: MerchantNotice }) {
  const { busy, run, markNoticeRead, refreshNotices } = useMerchant();
  const paid = n.payment_status === 'CAPTURED';
  async function start() {
    // Reuse the existing fulfilment transitions: PAID -> ACCEPTED -> PREPARING.
    if (n.order_status === 'PAID') await run(`/orders/${n.order_id}/fulfilment`, { status: 'ACCEPTED' });
    await run(`/orders/${n.order_id}/fulfilment`, { status: 'PREPARING' });
    await markNoticeRead(n.id); await refreshNotices();
  }
  return <li className="py-3 flex items-center gap-3" data-testid={`reservation-${n.order_id}`}>
    <span className="w-8 h-8 rounded-full grid place-items-center shrink-0 bg-accent-soft text-accent"><ChefHat size={16} /></span>
    <div className="min-w-0 flex-1"><p className="text-sm font-semibold leading-snug">{n.message.replace(/^New reservation: /, '').replace(/ — please prepare$/, '')}</p>
      <p className="text-xs text-muted">{ago(n.created_at)} · {paid ? n.order_status === 'ACCEPTED' ? 'Paid, accepted' : 'Paid' : 'Awaiting payment'}</p></div>
    {paid ? <button className="pf-btn sm accent" disabled={busy} data-testid={`start-preparing-${n.order_id}`} onClick={() => void start()}>Start preparing</button>
      : n.seen_at ? null : <button className="pf-btn sm outline" onClick={() => void markNoticeRead(n.id)}>Dismiss</button>}
  </li>;
}

/** Reservations the store has been asked to prepare, shown at the top of the Overview. */
export function ReservationsToPrepare() {
  const { notices } = useMerchant();
  const rows = notices.notifications.filter(n => ACTIONABLE.includes(n.order_status));
  if (!rows.length) return null;
  return <Panel title="Reservations to prepare" description="Shoppers have set these aside. Paid orders can be prepared now.">
    <ul className="divide-y divide-line -my-2" aria-label="Reservations to prepare">{rows.map(n => <Row key={n.id} n={n} />)}</ul>
  </Panel>;
}
