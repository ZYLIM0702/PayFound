import { useState } from 'react';
import { Link } from 'react-router-dom';
import { cash, messageOf, post, remove, type Order } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, OrderStatus, Spinner } from '../../components/Shared';
import { Pane, PaneHeader, Quiet, Scroll, fmtDate, paymentLabel, type PaymentMethod } from './shared';

type Notify = { onError: (m: string) => void; onInfo: (m: string) => void };

function PayPalCard({ onError, onInfo }: Notify) {
  const res = useResource<{ methods: (PaymentMethod & { stored?: boolean; assigned?: boolean; preferred?: boolean; paypal_merchant_id?: string | null })[]; note: string }>('/me/payment-methods');
  const [email, setEmail] = useState('');
  const [payerId, setPayerId] = useState('');
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const linked = res.data?.methods.find(m => m.provider === 'paypal');
  async function link(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); onError('');
    try { await post('/me/payment-methods/paypal-sandbox', { email, ...(payerId.trim() ? { paypal_merchant_id: payerId.trim() } : {}) }); setEmail(''); setPayerId(''); setEditing(false); onInfo('PayPal details saved as your preferred payer.'); await res.refresh(); }
    catch (issue) { onError(messageOf(issue)); } finally { setBusy(false); }
  }
  async function unlink(id: string) {
    setBusy(true); onError('');
    try { await remove(`/me/payment-methods/${encodeURIComponent(id)}`); onInfo('PayPal sandbox link removed.'); await res.refresh(); }
    catch (issue) { onError(messageOf(issue)); } finally { setBusy(false); }
  }
  return <section className="pf-card p-4 space-y-3" aria-label="Connected payment methods" data-testid="paypal-card">
    <div className="flex items-start justify-between gap-3"><div><h3 className="text-sm font-semibold">PayPal</h3><p className="text-[12.5px] text-muted">Sandbox payer label. No real account is connected</p></div>
      {res.loading ? null : linked ? <Chip kind="green" dot>Preferred (sandbox)</Chip> : <Chip>Not linked</Chip>}</div>
    {res.loading ? <Spinner inline /> : linked && !editing ? <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-canvas px-3 py-2.5">
      <div><p className="text-sm font-medium">{linked.label}</p><p className="text-[12.5px] text-muted">Linked {fmtDate(linked.created_at)} · status {linked.status.replaceAll('_', ' ')}{linked.paypal_merchant_id ? ` · PayPal ID ${linked.paypal_merchant_id}` : ''}{linked.assigned ? ' · assigned automatically (sandbox demo)' : ''}{linked.stored ? ' · stored encrypted' : ''}</p></div>
      <div className="flex gap-2"><button className="pf-btn sm outline" disabled={busy} onClick={() => setEditing(true)}>Change</button><button className="pf-btn sm outline" disabled={busy} onClick={() => void unlink(linked.id)}>Remove</button></div></div>
      : <form onSubmit={e => void link(e)} className="space-y-2.5">
        <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">PayPal sandbox email</span>
          <input className="pf-input" type="email" required maxLength={190} autoComplete="off" placeholder="sandbox-buyer@example.com" value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">PayPal sandbox account ID (optional)</span>
          <input className="pf-input" maxLength={32} autoComplete="off" spellCheck={false} placeholder="13-character sandbox ID" value={payerId} onChange={e => setPayerId(e.target.value)} /></label>
        <div className="flex gap-2"><button className="pf-btn sm" disabled={busy || !email}>{busy ? 'Saving…' : 'Save as preferred payer'}</button>{editing && <button type="button" className="pf-btn sm outline" onClick={() => setEditing(false)}>Cancel</button>}</div></form>}
    <Quiet>{res.data?.note || 'Sandbox only. PayFound never asks for or stores your PayPal password, tokens or card numbers.'}</Quiet>
    <p className="text-[12.5px] font-medium text-ink-2">Never enter your PayPal password or card number here. You sign in to PayPal in its own window when you pay.</p>
  </section>;
}

export function PaymentsHub({ orders, query, onError, onInfo }: Notify & { orders: Order[]; query: string }) {
  const q = query.toLowerCase();
  const rows = orders.filter(o => !q || `${o.merchant_name} ${o.product_name} ${o.id}`.toLowerCase().includes(q));
  const pending = rows.filter(o => ['CREATED', 'CREATING', 'CAPTURING', 'RECONCILIATION_REQUIRED', 'REFUND_PENDING'].includes(o.payment_status));
  return <Pane>
    <PaneHeader title="Payments" hint="Connected payment methods and the payment state of your orders. There is no balance or loan on this account." />
    <Scroll className="p-4 sm:p-5 grid grid-cols-[minmax(0,1fr)] gap-6 content-start lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)] lg:items-start">
      <div className="space-y-4">
        <PayPalCard onError={onError} onInfo={onInfo} />
        <section className="pf-card p-4 space-y-2" aria-label="Default at checkout"><h3 className="text-sm font-semibold">Default at checkout</h3>
          <Quiet>Checkout still opens PayPal's own approval screen each time, whether or not a sandbox link is saved here. This page never pays for anything.</Quiet></section>
        <section className="pf-card p-4 space-y-2" aria-label="About PayPal Pay Later"><h3 className="text-sm font-semibold">PayPal Pay Later</h3>
          <Quiet>Pay Later is offered at checkout for eligible orders. PayPal alone decides eligibility from the amount, your country and your PayPal profile, and shows the offer in its own window. PayFound never lends, holds a balance or sees your credit check. Sandbox accounts may not show Pay Later offers at all.</Quiet>
          {pending.length > 0 && <p className="text-[13px]">{pending.length} order{pending.length > 1 ? 's' : ''} below {pending.length > 1 ? 'are' : 'is'} waiting on a payment step.</p>}</section>
      </div>
      <section aria-label="Order payments"><h3 className="text-sm font-semibold mb-2">Payments by order</h3>
        {!rows.length ? <Quiet>No payments to show.</Quiet> : <ul className="pf-card divide-y divide-line">{rows.map(o => <li key={o.id} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 p-3 text-sm">
          <div className="min-w-0 flex-1"><p className="font-medium truncate">{o.merchant_name} · {o.product_name}</p><p className="text-[12.5px] text-muted">{fmtDate(o.created_at)} · {paymentLabel(o)}</p>
            {o.payment_status === 'CREATED' && <Link className="pf-link text-[12.5px]" to={`/checkout/${o.id}`}>Open checkout to see if Pay Later is offered</Link>}</div>
          <OrderStatus order={o} /><strong className="tabular w-20 text-right">{cash(o.amount_cents, o.currency)}</strong></li>)}</ul>}</section>
    </Scroll>
  </Pane>;
}
