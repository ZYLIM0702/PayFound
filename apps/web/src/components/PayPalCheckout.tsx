import { useEffect, useRef, useState } from 'react';
import { PayPalProvider, PayPalOneTimePaymentButton, PayLaterOneTimePaymentButton, useEligibleMethods } from '@paypal/react-paypal-js/sdk-v6';
import { messageOf, post, type Order } from '../lib/api';
import { ErrorLine, Notice } from './Shared';

function PaymentButtons({ order, onSuccess }: { order: Order; onSuccess: (order: Order) => void }) {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const locked = useRef(false);
  const { eligiblePaymentMethods, isLoading, error: eligibilityError } = useEligibleMethods({
    payload: { amount: (order.amount_cents / 100).toFixed(2), currencyCode: order.currency, paymentFlow: 'ONE_TIME_PAYMENT' },
  });
  const createOrder = async () => {
    if (locked.current) throw new Error('A payment session is already open');
    locked.current = true; setBusy(true); setError(''); setMessage('Creating sandbox payment…');
    try { const created = await post<{ id: string }>(`/orders/${order.id}/paypal/create`); return { orderId: created.id }; }
    catch (issue) { locked.current = false; setBusy(false); setError(messageOf(issue)); throw issue; }
  };
  const onApprove = async () => {
    setMessage('Verifying the capture with PayPal…');
    try { const updated = await post<Order>(`/orders/${order.id}/paypal/capture`); onSuccess(updated); if (updated.payment_status !== 'CAPTURED') throw new Error('Provider review required before fulfilment'); setMessage('Sandbox capture confirmed.'); }
    catch (issue) { setError(`${messageOf(issue)}. Check PayPal status before starting another payment.`); throw issue; }
    finally { locked.current = false; setBusy(false); }
  };
  const onCancel = () => { locked.current = false; setBusy(false); setMessage('PayPal approval cancelled. No new capture requested.'); };
  const onError = (issue: { message: string }) => { locked.current = false; setBusy(false); setError(issue.message); };
  return <div className="space-y-3"><ErrorLine message={error || eligibilityError?.message || ''} />
    {isLoading ? <p role="status" className="text-sm text-muted">Checking eligible payment methods…</p> : <>
      {eligiblePaymentMethods?.isEligible('paypal') && <PayPalOneTimePaymentButton createOrder={createOrder} onApprove={onApprove} onCancel={onCancel} onError={onError} presentationMode="auto" disabled={busy} />}
      {eligiblePaymentMethods?.isEligible('paylater') && <PayLaterOneTimePaymentButton createOrder={createOrder} onApprove={onApprove} onCancel={onCancel} onError={onError} presentationMode="auto" disabled={busy} />}
      {!eligiblePaymentMethods?.isEligible('paypal') && !eligibilityError && <Notice>No eligible PayPal method available for this buyer and order.</Notice>}
    </>}{message && <p role="status" className="text-sm font-medium text-ink-2">{message}</p>}
    <p className="text-xs text-muted leading-relaxed">Sandbox only. The test payment goes to this store's assigned sandbox receiving account, or the platform sandbox seller if none is set.</p>
  </div>;
}

export function PayPalCheckout({ order, clientId, onSuccess }: { order: Order; clientId: string; onSuccess: (order: Order) => void }) {
  return <PayPalProvider clientId={clientId} environment="sandbox" components={['paypal-payments']} pageType="checkout"><PaymentButtons order={order} onSuccess={onSuccess} /></PayPalProvider>;
}

type ResumeResult = { action: 'captured' | 'pay_again' | 'wait'; provider_status: string; order: Order };

/** Mounted once per page load for an order that already has an unfinished PayPal order. The server reads it back from PayPal first. */
export function PayPalPayment({ order, clientId, onSuccess }: { order: Order; clientId: string; onSuccess: (order: Order) => void }) {
  const [stuck] = useState(() => order.payment_mode === 'paypal_sandbox' && Boolean(order.paypal_order_id) && ['CREATED', 'RECONCILIATION_REQUIRED'].includes(order.payment_status));
  const [stage, setStage] = useState<'checking' | 'pay_again' | 'wait' | 'fresh' | 'done'>(stuck ? 'checking' : 'fresh');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const asked = useRef(false);
  useEffect(() => {
    if (!stuck || asked.current) return;
    asked.current = true;
    post<ResumeResult>(`/orders/${order.id}/paypal/resume`)
      .then(result => { onSuccess(result.order); setStage(result.action === 'captured' ? 'done' : result.action); })
      .catch(issue => { setError(messageOf(issue)); setStage('wait'); });
  }, [stuck, order.id, onSuccess]);
  const again = async () => {
    setBusy(true); setError('');
    try { const result = await post<{ order: Order }>(`/orders/${order.id}/paypal/restart`); onSuccess(result.order); setStage('fresh'); }
    catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); }
  };
  if (stage === 'fresh') return <PayPalCheckout order={order} clientId={clientId} onSuccess={onSuccess} />;
  if (stage === 'done') return <p role="status" className="text-sm font-medium text-ink-2">PayPal confirmed your approved payment.</p>;
  return <div className="space-y-3" data-testid="paypal-resume"><ErrorLine message={error} />
    {stage === 'checking' && <p role="status" className="text-sm text-muted">Checking this payment with PayPal…</p>}
    {stage === 'pay_again' && <><Notice>The earlier PayPal window was closed before you approved it, so no money moved. You can start a new PayPal payment for the same reservation.</Notice>
      <button className="pf-btn accent lg w-full" disabled={busy} onClick={() => void again()} data-testid="paypal-pay-again">{busy ? 'Starting…' : 'Pay again with PayPal'}</button></>}
    {stage === 'wait' && <Notice tone="amber">PayPal has not given a final answer yet. Use "Check PayPal status" below before trying again.</Notice>}
  </div>;
}
