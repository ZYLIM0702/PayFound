import { Check, Circle, Clock, X } from 'lucide-react';
import type { Order } from '../lib/api';
import { fmtDate, fmtTime } from '../pages/account/shared';

type Step = { key: string; label: string; at: string | null; done: boolean };

const ORDER_RANK: Record<string, number> = { RESERVED: 1, PAID: 2, ACCEPTED: 3, PREPARING: 4, READY: 5, COLLECTED: 6 };

/** Shopper-facing timeline built from the order's own status and fulfilment history. Nothing here is guessed. */
export function buildSteps(order: Order): Step[] {
  const proof = (state: string) => order.fulfilment_proof?.find(p => p.state === state)?.created_at ?? null;
  const rank = ORDER_RANK[order.status] ?? 0;
  const paid = order.payment_status === 'CAPTURED';
  return [
    { key: 'reserved', label: 'Reserved', at: order.created_at, done: true },
    { key: 'confirmed', label: 'Store confirmed stock', at: order.confirmed_at ?? null, done: order.confirmation_status === 'CONFIRMED' || rank >= 2 },
    { key: 'paid', label: 'Paid', at: proof('PAID'), done: paid || rank >= 2 },
    { key: 'accepted', label: 'Store accepted', at: proof('ACCEPTED'), done: rank >= 3 },
    { key: 'preparing', label: 'Being prepared', at: proof('PREPARING'), done: rank >= 4 },
    { key: 'ready', label: 'Ready for pickup', at: proof('READY'), done: rank >= 5 },
    { key: 'collected', label: 'Collected', at: proof('COLLECTED'), done: rank >= 6 },
  ];
}

export function OrderTracker({ order }: { order: Order }) {
  const closed = order.status === 'CANCELLED' || order.status === 'EXPIRED';
  const steps = buildSteps(order);
  const current = steps.findIndex(step => !step.done);
  const window = order.pickup_window ?? null;
  return <section aria-label="Order tracking" className="space-y-3" data-testid="order-tracker">
    {closed && <p className="flex items-center gap-2 text-sm text-bad font-semibold"><X size={15} />This order is {order.status === 'EXPIRED' ? 'expired' : 'cancelled'}.</p>}
    <ol className="relative space-y-3">
      {steps.map((step, i) => {
        const isCurrent = !closed && i === current;
        return <li key={step.key} className="flex gap-3 items-start" aria-current={isCurrent ? 'step' : undefined}>
          <span className={`mt-0.5 grid place-items-center w-6 h-6 rounded-full shrink-0 ${step.done ? 'bg-ok text-white' : isCurrent ? 'bg-ink text-white' : 'bg-sunk text-subtle'}`}>
            {step.done ? <Check size={13} /> : isCurrent ? <Clock size={13} /> : <Circle size={8} />}
          </span>
          <div className="min-w-0">
            <p className={`text-sm ${step.done || isCurrent ? 'font-semibold text-ink' : 'text-muted'}`}>{step.label}</p>
            {step.at && <p className="text-[12.5px] text-muted tabular">{fmtDate(step.at, false)} · {fmtTime(step.at)}</p>}
            {step.key === 'collected' && step.done && <p className="text-[12.5px] text-muted">Thanks for picking up. You can leave a review.</p>}
          </div>
        </li>;
      })}
    </ol>
    {window && !closed && <p className="text-[13px] text-muted">Pickup window: <b className="text-ink">{fmtDate(window.start_at, false)} {fmtTime(window.start_at)}</b></p>}
  </section>;
}
