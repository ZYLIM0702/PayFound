import { useState } from 'react';
import { Check, ExternalLink, RefreshCw } from 'lucide-react';
import { cash, messageOf, post } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, type Tone, ErrorLine, Notice, PageHeader, Panel, Spinner } from '../../components/Shared';

type PlanInfo = {
  id: string; name: string; monthly_cents: number; listing_limit: number | null; monthly_sales_cents: number | null;
  platform_fee_bps: number; pos_registers: number | null; features: string[];
};
type Subscription = {
  plan: PlanInfo; usage: { active_listings: number; month_sales_cents: number }; plans: PlanInfo[]; billing_note: string;
};

type Billing = { plan: PlanInfo; status: string | null; approval_url?: string | null; next_billing_time?: string | null };
type Subscribed = { subscription_id: string; status: string; approval_url?: string | null };
const STATUS_TONE: Record<string, Tone> = { ACTIVE: 'green', APPROVAL_PENDING: 'amber', APPROVED: 'blue', SUSPENDED: 'red', CANCELLED: 'default', EXPIRED: 'default' };
const when = (value?: string | null) => { if (!value) return 'Not scheduled'; const d = new Date(value); return Number.isNaN(d.getTime()) ? value : d.toLocaleString(); };

const fee = (bps: number) => `${(bps / 100).toFixed(bps % 100 ? 2 : 1)}%`;
const limit = (value: number | null, unit = '') => (value === null ? 'Unlimited' : `${value.toLocaleString()}${unit}`);
const money = (cents: number | null) => (cents === null ? 'Unlimited' : cash(cents, 'USD'));

function Meter({ label, used, max, detail }: { label: string; used: number; max: number | null; detail: string }) {
  const pct = max ? Math.min(100, Math.round((used / max) * 100)) : 0;
  const over = max !== null && used > max;
  return <div>
    <div className="flex items-baseline justify-between gap-3 text-sm">
      <span className="font-medium">{label}</span>
      <span className="tabular text-muted">{detail}</span>
    </div>
    {max !== null && <div className="mt-2 h-2 rounded-full bg-sunk overflow-hidden" role="meter" aria-label={label} aria-valuemin={0} aria-valuemax={max} aria-valuenow={used}>
      <div className={`h-full rounded-full ${over ? 'bg-bad' : pct > 80 ? 'bg-accent' : 'bg-ink'}`} style={{ width: `${pct}%` }} />
    </div>}
    {over && <p className="text-[12.5px] text-bad mt-1.5">Over your plan limit. Upgrade to keep adding listings.</p>}
  </div>;
}

export function PlanPage({ merchantId }: { merchantId: string }) {
  const sub = useResource<Subscription>(`/merchants/${encodeURIComponent(merchantId)}/subscription`);
  const billing = useResource<Billing>(`/merchants/${encodeURIComponent(merchantId)}/billing/subscription`);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const base = `/merchants/${encodeURIComponent(merchantId)}`;
  function openApproval(url?: string | null) {
    if (url) window.open(url, '_blank', 'noopener');
  }
  async function choose(planId: string) {
    setBusy(planId); setError(''); setInfo('');
    try {
      if (planId === 'free') {
        await post(`${base}/subscription`, { plan_id: planId });
        setInfo('Plan changed to Free. Demo billing: nothing was charged.');
      } else {
        const out = await post<Subscribed>(`${base}/billing/subscribe`, { plan_id: planId });
        openApproval(out.approval_url);
        setInfo('Approve the subscription in the PayPal sandbox window. Your plan changes when PayPal confirms it.');
      }
      await Promise.all([sub.refresh(), billing.refresh()]);
    } catch (issue) { setError(messageOf(issue)); } finally { setBusy(''); }
  }
  async function cancel() {
    if (!window.confirm('Cancel the PayPal sandbox subscription?')) return;
    setBusy('cancel'); setError(''); setInfo('');
    try {
      await post(`${base}/billing/cancel`, {});
      setInfo('Subscription cancellation requested.');
      await Promise.all([sub.refresh(), billing.refresh()]);
    } catch (issue) { setError(messageOf(issue)); } finally { setBusy(''); }
  }
  async function refreshStatus() {
    setBusy('refresh'); setError('');
    try { await Promise.all([sub.refresh(), billing.refresh()]); } finally { setBusy(''); }
  }
  if (sub.loading && !sub.data) return <Spinner />;
  const data = sub.data;
  if (!data) return <ErrorLine message={sub.error || 'Plan unavailable'} retry={sub.refresh} />;
  const { plan, usage } = data;
  return <div className="space-y-6 pf-enter" data-testid="merchant-plan">
    <PageHeader title="Plan" description="Your plan covers every store on this business account. Fees below are PayFound's platform fee, charged on top of PayPal's processing." />
    <ErrorLine message={error} />{info && <Notice tone="green">{info}</Notice>}
    <Panel title={<span className="inline-flex items-center gap-2">Current plan <Chip kind="ink">{plan.name}</Chip></span>} description={data.billing_note}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-5">
          <Meter label="Active listings" used={usage.active_listings} max={plan.listing_limit} detail={`${usage.active_listings.toLocaleString()} of ${limit(plan.listing_limit)}`} />
          <Meter label="Captured sales this month" used={usage.month_sales_cents} max={plan.monthly_sales_cents} detail={`${cash(usage.month_sales_cents, 'USD')} of ${money(plan.monthly_sales_cents)}`} />
        </div>
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div><dt className="text-muted">Monthly price</dt><dd className="font-display text-xl tabular">{plan.monthly_cents ? cash(plan.monthly_cents, 'USD') : 'Free'}</dd></div>
          <div><dt className="text-muted">Platform fee</dt><dd className="font-display text-xl tabular" data-testid="platform-fee">{fee(plan.platform_fee_bps)}</dd></div>
          <div><dt className="text-muted">POS registers</dt><dd className="font-display text-xl tabular">{limit(plan.pos_registers)}</dd></div>
          <div><dt className="text-muted">Sales limit</dt><dd className="font-display text-xl tabular">{money(plan.monthly_sales_cents)}</dd></div>
        </dl>
      </div>
    </Panel>

    <Panel title={<span className="inline-flex items-center gap-2">Subscription <Chip kind="default">PayPal sandbox</Chip></span>} description="Paid plans are billed through a PayPal sandbox subscription. Nothing real is charged."
      actions={<button className="pf-btn sm outline" disabled={Boolean(busy) || billing.refreshing} onClick={() => void refreshStatus()} data-testid="refresh-subscription"><RefreshCw size={14} />Refresh status</button>}>
      {billing.loading && !billing.data ? <Spinner /> : !billing.data ? <ErrorLine message={billing.error || 'Subscription status unavailable'} retry={billing.refresh} /> : (() => {
        const b = { ...billing.data, status: billing.data.status === 'NONE' ? null : billing.data.status };
        const pending = b.status === 'APPROVAL_PENDING' || b.status === 'APPROVED';
        const live = b.status === 'ACTIVE' || b.status === 'SUSPENDED' || pending;
        return <div className="space-y-3 text-sm" data-testid="paypal-subscription">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-muted">PayPal status</span>
            {b.status ? <Chip kind={STATUS_TONE[b.status] ?? 'default'} dot>{b.status.replaceAll('_', ' ')}</Chip> : <Chip>No PayPal subscription</Chip>}
          </div>
          <p className="text-muted">Next billing: <b className="text-ink-2">{when(b.next_billing_time)}</b></p>
          {pending && <div className="space-y-2">
            <Notice tone="amber">{b.status === 'APPROVAL_PENDING' ? 'Waiting for your approval in the PayPal sandbox.' : 'Approved. Waiting for PayPal to activate it.'} Refresh the status after approving.</Notice>
            {b.approval_url && <button className="pf-btn sm" onClick={() => openApproval(b.approval_url)}><ExternalLink size={14} />Open PayPal sandbox approval</button>}
          </div>}
          {live && <button className="pf-btn sm outline" disabled={Boolean(busy)} onClick={() => void cancel()} data-testid="cancel-subscription">{busy === 'cancel' ? 'Cancelling…' : 'Cancel subscription'}</button>}
        </div>;
      })()}
    </Panel>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {data.plans.map(option => {
        const current = option.id === plan.id;
        return <article key={option.id} className={`pf-card p-5 flex flex-col gap-4 ${current ? 'ring-2 ring-ink' : ''}`} data-testid={`plan-${option.id}`}>
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-display text-xl font-semibold">{option.name}</h3>
            {current ? <Chip kind="green">Current</Chip> : option.id === 'pro' ? <Chip kind="blue">Most popular</Chip> : null}
          </div>
          <p className="font-display text-3xl tabular">{option.monthly_cents ? cash(option.monthly_cents, 'USD') : '$0'}<span className="text-base text-muted"> / month</span></p>
          <p className="text-sm text-muted">Platform fee <b className="text-ink tabular">{fee(option.platform_fee_bps)}</b> per captured sale</p>
          <ul className="space-y-2 text-sm flex-1">
            {option.features.map(item => <li key={item} className="flex gap-2"><Check size={15} className="shrink-0 mt-0.5 text-accent" />{item}</li>)}
          </ul>
          <button className={`pf-btn w-full ${current ? 'outline' : ''}`} disabled={current || Boolean(busy)} onClick={() => void choose(option.id)} data-testid={`choose-${option.id}`}>
            {current ? 'Current plan' : busy === option.id ? 'Changing…' : `Choose ${option.name}`}
          </button>
        </article>;
      })}
    </div>
    <p className="text-[12.5px] text-muted">Card processing is charged by PayPal at its own rates (PayPal POS: 2.29% + 9c card-present and QR, 3.49% + 9c keyed-in). Plan prices are a proposal for the pilot.</p>
  </div>;
}
