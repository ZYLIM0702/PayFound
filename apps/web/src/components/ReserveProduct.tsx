import { useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Minus, Plus, ShoppingBag } from 'lucide-react';
import { messageOf, post, type Order, type Product } from '../lib/api';
import { useApp } from '../lib/app-context';
import { Sheet, ErrorLine, Field } from './Shared';
import { useBuyerName } from '../lib/use-buyer-name';

type Line = { product_id: string; quantity: number };

/** Why a product cannot be reserved right now (short, plain), or '' when it can. */
export function reserveBlock(p: Pick<Product, 'in_stock' | 'available_quantity' | 'is_open'>, quantity = 1) {
  if (!p.in_stock || p.available_quantity <= 0) return 'Out of stock';
  if (p.is_open === false) return 'Store closed';
  if (quantity > p.available_quantity) return `Only ${p.available_quantity} available`;
  return '';
}

/**
 * The one reserve action used everywhere a product appears: opens a sheet for quantity (single product) and a pickup
 * name, the store sets the items aside, then the checkout page takes over (payment and pickup time are chosen there).
 * Uses the same reservation endpoint and idempotency key as the basket, so a double tap cannot reserve twice.
 */
export function ReserveAction({ lines, title, description, maxQuantity, blockedReason = '', className = 'pf-btn sm', label = 'Reserve', testId, confirmLabel = 'Reserve and continue', onReserved, note }: {
  lines: Line[]; title: string; description?: string;
  /** When set, the sheet shows a quantity stepper for the single line (up to this many). */
  maxQuantity?: number; blockedReason?: string; className?: string; label?: string; testId?: string; confirmLabel?: string;
  onReserved?: () => void; note?: string;
}) {
  const { session, demo } = useApp();
  const navigate = useNavigate();
  const here = useLocation();
  const [open, setOpen] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [buyerName, setBuyerName] = useBuyerName();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const lock = useRef(false);
  const intent = useRef({ fingerprint: '', key: '' });
  const stepper = maxQuantity != null;
  const items = stepper ? [{ product_id: lines[0].product_id, quantity }] : lines;

  async function reserve(payNow = false) {
    if (lock.current) return;
    lock.current = true; setBusy(true); setError('');
    const pickupName = buyerName.trim() || 'Local shopper';
    const fingerprint = JSON.stringify({ items, buyer_name: pickupName });
    if (intent.current.fingerprint !== fingerprint) intent.current = { fingerprint, key: crypto.randomUUID() };
    try {
      const order = await post<Order>('/orders/reserve', { items, buyer_name: pickupName, idempotency_key: intent.current.key });
      setOpen(false);
      onReserved?.();
      navigate(`/checkout/${order.id}${payNow ? '?pay=1' : ''}`);
    } catch (issue) { setError(messageOf(issue)); }
    finally { lock.current = false; setBusy(false); }
  }

  if (!session && !demo) return <a className={className} data-testid={testId && `${testId}-signin`} href={`/login?next=${encodeURIComponent(here.pathname + here.search)}`}>Sign in to reserve</a>;
  return <>
    <button className={className} data-testid={testId} disabled={Boolean(blockedReason) || !lines.length} title={blockedReason || undefined} onClick={() => setOpen(true)}>{label}</button>
    <Sheet open={open} onClose={() => setOpen(false)} title={title} description={description}
      footer={<div className="grid w-full gap-2 sm:grid-cols-2">
        <button className="pf-btn accent lg w-full" data-testid="reserve-product-pay" disabled={busy} onClick={() => void reserve(true)}><ShoppingBag size={17} />{busy ? 'Working…' : 'Pay online & pick up'}</button>
        <button className="pf-btn outline lg w-full" data-testid="reserve-product-confirm" disabled={busy} onClick={() => void reserve(false)}>{busy ? 'Reserving…' : confirmLabel}</button>
      </div>}>
      <div className="space-y-6">
        {stepper && <div className="flex items-center justify-between gap-4 rounded-[var(--pf-r-md)] border border-line p-4">
          <div><p className="text-sm font-semibold">Quantity</p><p className="text-xs text-muted">{maxQuantity} available at this branch</p></div>
          <div className="flex items-center gap-3">
            <button className="pf-btn outline icon sm" aria-label="Fewer" disabled={quantity <= 1} onClick={() => setQuantity(q => Math.max(1, q - 1))}><Minus size={14} /></button>
            <span className="w-6 text-center font-semibold tabular" aria-live="polite">{quantity}</span>
            <button className="pf-btn outline icon sm" aria-label="More" disabled={quantity >= Math.min(10, maxQuantity)} onClick={() => setQuantity(q => Math.min(Math.min(10, maxQuantity), q + 1))}><Plus size={14} /></button>
          </div>
        </div>}
        <Field label="Pickup name" autoComplete="name" maxLength={100} value={buyerName} onChange={e => setBuyerName(e.target.value)} data-testid="reserve-product-name" hint="Optional. The store uses this name to find your order." />
        <p className="text-xs text-muted leading-relaxed">The store is notified to prepare your order. {note ?? 'A reservation does not charge you. Payment and your pickup time are chosen on the next step.'} {demo ? 'Demo stock: no funds move.' : 'The store confirms stock before payment.'}</p>
        <ErrorLine message={error} />
      </div>
    </Sheet>
  </>;
}

/** Reserve one product, on its own page (large primary button). */
export function ReserveProduct({ product, disabled }: { product: Product; disabled?: boolean }) {
  const reason = disabled ? reserveBlock(product) || 'Unavailable' : '';
  return <>
    <ReserveAction lines={[{ product_id: product.id, quantity: 1 }]} title="Reserve this item" description={`${product.name} at ${product.merchant_name}`}
      maxQuantity={Math.max(1, product.available_quantity)} blockedReason={reason}
      className="pf-btn accent lg w-full" label="Reserve for pickup" testId={`reserve-product-${product.id}`} />
    {reason && <p className="text-xs text-muted text-center -mt-1" data-testid="reserve-blocked-reason">{reason}: reserving is unavailable right now.</p>}
  </>;
}

/** Compact reserve button for cards and lists. */
export function ReserveCompact({ product, className = 'pf-btn sm flex-1', label = 'Reserve' }: { product: Product; className?: string; label?: string }) {
  return <ReserveAction lines={[{ product_id: product.id, quantity: 1 }]} title="Reserve this item" description={`${product.name} at ${product.merchant_name}`}
    maxQuantity={Math.max(1, product.available_quantity)} blockedReason={reserveBlock(product)} className={className} label={label} testId={`reserve-card-${product.id}`} />;
}
