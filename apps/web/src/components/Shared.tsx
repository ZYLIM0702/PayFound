import { Component, useId, useState, type ComponentProps, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Dialog } from 'radix-ui';
import { AlertCircle, ArrowUpRight, CheckCircle2, Info, LoaderCircle, MapPin, Package, Search, ShieldCheck, Star, X } from 'lucide-react';
import type { Product, Merchant, Order } from '../lib/api';
import { api, cash, messageOf, safeExternalUrl, type ConnectorCheckout } from '../lib/api';
import { ProductPhoto } from './ProductPhoto';
import { ReserveCompact } from './ReserveProduct';
import { straightLineKm, useUserLocation } from '../lib/location';
import { formatDistance } from '../lib/directions';

/* ------------------------------------------------------------------ */
/* Primitives                                                          */
/* ------------------------------------------------------------------ */

export type Tone = 'default' | 'green' | 'amber' | 'red' | 'blue' | 'ink';

export function Chip({ children, kind = 'default', dot = false }: { children: ReactNode; kind?: Tone; dot?: boolean }) {
  return <span className={`pf-chip ${kind === 'default' ? '' : kind}`}>{dot && <span className="pf-dot" />}{children}</span>;
}

export function Spinner({ label = 'Loading…', inline = false }: { label?: string; inline?: boolean }) {
  if (inline) return <span className="inline-flex items-center gap-2 text-muted text-sm" role="status"><LoaderCircle size={16} className="animate-spin" />{label}</span>;
  return <div className="flex items-center justify-center gap-3 py-16 text-muted text-sm" role="status"><LoaderCircle size={18} className="animate-spin" />{label}</div>;
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`pf-skeleton ${className}`} aria-hidden="true" />;
}

export function ErrorLine({ message, retry }: { message: string; retry?: () => void }) {
  if (!message) return null;
  return <div className="pf-alert red" role="alert"><AlertCircle size={16} /><span className="flex-1">{message}</span>{retry && <button className="pf-btn sm outline" onClick={retry}>Try again</button>}</div>;
}

export function Notice({ children, tone = 'blue' }: { children: ReactNode; tone?: 'blue' | 'amber' | 'green' | 'default' }) {
  const Icon = tone === 'green' ? CheckCircle2 : Info;
  return <div className={`pf-alert ${tone === 'default' ? '' : tone}`} role="status"><Icon size={16} /><div className="flex-1">{children}</div></div>;
}

export function Field({ label, hint, ...props }: ComponentProps<'input'> & { label: string; hint?: string }) {
  const id = useId();
  const inputId = props.id || id;
  return <div className="pf-field"><label htmlFor={inputId}>{label}</label><input {...props} id={inputId} className={`pf-input ${props.className || ''}`} aria-describedby={hint ? `${id}-hint` : props['aria-describedby']} />{hint && <p id={`${id}-hint`} className="pf-field-hint">{hint}</p>}</div>;
}

export function SelectField({ label, hint, children, ...props }: ComponentProps<'select'> & { label: string; hint?: string }) {
  const id = useId();
  return <div className="pf-field"><label htmlFor={props.id || id}>{label}</label><select {...props} id={props.id || id} className={`pf-select ${props.className || ''}`}>{children}</select>{hint && <p className="pf-field-hint">{hint}</p>}</div>;
}

export function TextAreaField({ label, hint, ...props }: ComponentProps<'textarea'> & { label: string; hint?: string }) {
  const id = useId();
  return <div className="pf-field"><label htmlFor={props.id || id}>{label}</label><textarea {...props} id={props.id || id} className={`pf-textarea ${props.className || ''}`} />{hint && <p className="pf-field-hint">{hint}</p>}</div>;
}

export function ConfirmDialog({ open, title, description, confirmLabel, busy, onClose, onConfirm, destructive = false }: { open: boolean; title: string; description: string; confirmLabel: string; busy?: boolean; onClose: () => void; onConfirm: () => void; destructive?: boolean }) {
  return <Dialog.Root open={open} onOpenChange={value => { if (!value && !busy) onClose(); }}><Dialog.Portal><Dialog.Overlay className="pf-dialog-overlay" /><Dialog.Content className="pf-dialog"><Dialog.Title className="pf-title">{title}</Dialog.Title><Dialog.Description className="text-sm text-muted mt-2 leading-relaxed">{description}</Dialog.Description><div className="flex justify-end gap-2 mt-7"><button className="pf-btn outline" disabled={busy} onClick={onClose}>Cancel</button><button className={`pf-btn ${destructive ? 'danger' : ''}`} disabled={busy} onClick={onConfirm}>{busy ? 'Working…' : confirmLabel}</button></div><Dialog.Close className="pf-dialog-close" aria-label="Close" disabled={busy}><X size={18} /></Dialog.Close></Dialog.Content></Dialog.Portal></Dialog.Root>;
}

/** Right-side drawer for detail/edit flows. */
export function Sheet({ open, onClose, title, description, children, footer }: { open: boolean; onClose: () => void; title: string; description?: string; children: ReactNode; footer?: ReactNode }) {
  return <Dialog.Root open={open} onOpenChange={value => { if (!value) onClose(); }}><Dialog.Portal><Dialog.Overlay className="pf-dialog-overlay" /><Dialog.Content className="pf-sheet" aria-describedby={undefined}>
    <div className="flex items-start justify-between gap-4 px-6 py-5 border-b border-line"><div><Dialog.Title className="pf-title">{title}</Dialog.Title>{description && <p className="text-sm text-muted mt-1">{description}</p>}</div><Dialog.Close className="pf-btn ghost sm icon" aria-label="Close"><X size={18} /></Dialog.Close></div>
    <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>
    {footer && <div className="px-6 py-4 border-t border-line flex justify-end gap-2">{footer}</div>}
  </Dialog.Content></Dialog.Portal></Dialog.Root>;
}

export class FeatureBoundary extends Component<{ children: ReactNode; name: string }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <ErrorLine message={`${this.props.name} could not load. Refresh the page to retry.`} /> : this.props.children; }
}

export function PageHeader({ eyebrow, title, description, right }: { eyebrow?: string; title: string; description?: ReactNode; right?: ReactNode }) {
  return <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-4 mb-8"><div className="min-w-0">{eyebrow && <div className="pf-eyebrow mb-2">{eyebrow}</div>}<h1 className="pf-heading">{title}</h1>{description && <p className="text-muted text-[15px] mt-2 max-w-2xl leading-relaxed">{description}</p>}</div>{right && <div className="flex flex-wrap items-center gap-2">{right}</div>}</div>;
}

export function SectionHeader({ title, description, right }: { title: string; description?: ReactNode; right?: ReactNode }) {
  return <div className="flex flex-wrap items-end justify-between gap-3 mb-5"><div><h2 className="pf-title">{title}</h2>{description && <p className="text-sm text-muted mt-1">{description}</p>}</div>{right}</div>;
}

export function Panel({ title, description, actions, children, flush = false, className = '' }: { title?: ReactNode; description?: ReactNode; actions?: ReactNode; children: ReactNode; flush?: boolean; className?: string }) {
  return <section className={`pf-panel ${className}`}>{(title || actions) && <div className="pf-panel-head"><div className="min-w-0">{title && <h2 className="pf-subtitle">{title}</h2>}{description && <p className="text-[13px] text-muted mt-0.5">{description}</p>}</div>{actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}</div>}<div className={flush ? '' : 'pf-panel-body'}>{children}</div></section>;
}

export function Stat({ label, value, hint, tone }: { label: string; value: ReactNode; hint?: ReactNode; tone?: Tone }) {
  return <div className="pf-stat"><span className="pf-stat-label">{label}</span><strong className={`pf-stat-number ${tone === 'red' ? 'text-bad' : tone === 'amber' ? 'text-warn' : tone === 'green' ? 'text-ok' : tone === 'blue' ? 'text-accent' : ''}`}>{value}</strong>{hint && <span className="text-xs text-muted">{hint}</span>}</div>;
}

export function Empty({ search = false, description, title = 'Nothing here yet', children }: { search?: boolean; description: string; title?: string; children?: ReactNode }) {
  return <div className="flex flex-col items-center text-center py-16 px-6"><div className="w-12 h-12 rounded-full bg-sunk grid place-items-center mb-4">{search ? <Search size={20} /> : <Package size={20} />}</div><h3 className="pf-subtitle">{title}</h3><p className="text-sm text-muted mt-1.5 max-w-sm">{description}</p>{children && <div className="mt-6 flex flex-wrap justify-center gap-2">{children}</div>}</div>;
}

/* ------------------------------------------------------------------ */
/* Commerce                                                            */
/* ------------------------------------------------------------------ */

export function availabilityTone(p: Pick<Product, 'in_stock' | 'freshness'>): Tone {
  return p.in_stock ? p.freshness === 'stale' ? 'amber' : 'green' : 'red';
}

export function ProductCard({ p, onPick, actionLabel = 'Add to basket', onLocate, selected = false, compact = false }: {
  p: Product; onPick?: (p: Product) => void; actionLabel?: string; onLocate?: (p: Product) => void; selected?: boolean; compact?: boolean;
}) {
  const { position } = useUserLocation();
  const distance = position && p.latitude != null && p.longitude != null ? straightLineKm(position, { latitude: p.latitude, longitude: p.longitude }) : p.distance_km;
  const availability = p.in_stock ? p.freshness === 'stale' ? 'Check stock' : `${p.available_quantity} in stock` : 'Out of stock';
  const disabled = !p.in_stock || p.available_quantity <= 0 || p.is_open === false;
  return <article className={`group relative flex flex-col ${selected ? 'outline-2 outline-ink outline-offset-4 rounded-[var(--pf-r-lg)]' : ''}`} data-testid={`product-${p.id}`} aria-current={selected ? 'true' : undefined}>
    <div className="relative aspect-square rounded-[var(--pf-r-lg)] overflow-hidden">
      <Link className="block w-full h-full" to={`/products/${p.id}`} aria-label={`View ${p.name}`}><ProductPhoto name={p.name} imageUrl={p.image_url} merchantId={p.merchant_id} className="transition-transform duration-300 group-hover:scale-[1.03]" /></Link>
      {onLocate && <button className="pf-btn sm icon absolute right-3 bottom-3 !bg-white/95 !text-ink shadow-sm" aria-label={selected ? 'Store selected on map' : 'Show on map'} title="Show on map" onClick={() => onLocate(p)}><MapPin size={15} /></button>}
      <span className="absolute left-3 top-3"><Chip kind={availabilityTone(p)} dot>{availability}</Chip></span>
      {(p.comparison_count || 1) > 1 && <Link to={`/products/${p.id}#compare`} className="absolute right-3 top-3 pf-chip pf-tap-chip !bg-white/90 backdrop-blur">{p.comparison_count} stores</Link>}
    </div>
    <div className="pt-3 flex flex-col gap-1 flex-1">
      <div className="flex items-start justify-between gap-3"><h3 className="text-[15px] font-semibold leading-snug line-clamp-2"><Link className="hover:underline underline-offset-2 pf-tap" to={`/products/${p.id}`}>{p.name}</Link></h3><strong className="text-[15px] font-semibold tabular shrink-0">{cash(p.price_cents, p.currency)}</strong></div>
      <div className="flex items-center gap-1.5 text-[13px] text-muted min-w-0"><Link className="truncate hover:text-ink pf-tap" to={`/stores/${p.merchant_slug || p.merchant_id}`}>{p.merchant_name || 'View store'}</Link>{distance != null && <><span aria-hidden>·</span><span className="shrink-0 tabular">{formatDistance(distance)}</span></>}</div>
      {!compact && <p className="text-xs text-subtle mt-0.5">{p.freshness === 'stale' ? 'Stock may be outdated' : 'Updated'} {new Date(p.stock_updated_at).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</p>}
      <div className="mt-auto pt-3 flex flex-wrap gap-2">
        {p.checkout_mode === 'merchant_native' && p.checkout_connection_id ? <MerchantNativeCheckout product={p} />
          : <>
            <ReserveCompact product={p} className="pf-btn sm flex-1 whitespace-nowrap min-w-fit" />
            {onPick ? <button className="pf-btn sm outline flex-1 whitespace-nowrap min-w-fit" data-testid={`add-to-cart-${p.id}`} disabled={disabled} onClick={() => onPick(p)}>{actionLabel}</button>
              : <Link className="pf-btn sm outline flex-1 whitespace-nowrap min-w-fit" to={`/products/${p.id}`}>View product</Link>}
          </>}
      </div>
    </div>
  </article>;
}

function MerchantNativeCheckout({ product }: { product: Product }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const continueToMerchant = async () => {
    if (busy || !product.checkout_connection_id) return;
    setBusy(true); setError('');
    try {
      const result = await api<ConnectorCheckout>(`/connectors/${encodeURIComponent(product.checkout_connection_id)}/checkout?product_id=${encodeURIComponent(product.id)}`);
      if (result.mode !== 'merchant_native') throw new Error('The merchant checkout method was unavailable. Please try again later.');
      const href = safeExternalUrl(result.url);
      if (!href) throw new Error('The merchant checkout link was unavailable. Please try again later.');
      window.location.assign(href);
    } catch (issue) { setError(messageOf(issue)); setBusy(false); }
  };
  return <div className="flex-1 flex flex-col gap-1"><button className="pf-btn sm outline w-full" data-testid={`merchant-checkout-${product.id}`} disabled={!product.in_stock || product.available_quantity <= 0 || product.is_open === false || busy} onClick={continueToMerchant}>{busy ? 'Opening…' : 'Buy on merchant site'}<ArrowUpRight size={14} /></button>{error && <p className="text-xs text-bad" role="alert">{error}</p>}</div>;
}

export function StoreCard({ m }: { m: Merchant }) {
  return <Link to={`/stores/${m.slug}`} className="pf-card interactive p-5 flex flex-col gap-4 h-full">
    <div className="flex items-start justify-between gap-3"><div className="w-11 h-11 rounded-full bg-ink text-white grid place-items-center font-display text-lg font-semibold shrink-0" aria-hidden>{m.name.slice(0, 1)}</div><Chip kind={m.is_open ? 'green' : m.is_open === false ? 'default' : 'amber'} dot>{m.is_open ? 'Open' : m.is_open === false ? 'Closed' : 'Hours unconfirmed'}</Chip></div>
    <div><h3 className="text-[15px] font-semibold flex items-center gap-1.5">{m.name}{m.verified && <ShieldCheck size={15} className="text-accent" aria-label="Verified" />}</h3><p className="text-[13px] text-muted mt-0.5">{m.category}</p></div>
    <div className="mt-auto flex items-center justify-between text-[13px] text-muted"><span className="flex items-center gap-1"><Star size={13} className="fill-ink text-ink" /><span className="text-ink font-semibold">{m.rating?.toFixed(1) || 'New'}</span>{m.review_count > 0 && <span>({m.review_count})</span>}</span><span>Ready in ~{m.fulfillment_minutes} min</span></div>
  </Link>;
}

const statusTone: Record<string, Tone> = { COLLECTED: 'green', READY: 'blue', PAID: 'default', ACCEPTED: 'default', PREPARING: 'amber', RESERVED: 'default', CANCELLED: 'red', EXPIRED: 'amber', REFUNDED: 'red' };
export const statusLabel = (value: string) => value.charAt(0) + value.slice(1).toLowerCase().replaceAll('_', ' ');
export function OrderStatus({ order }: { order: Pick<Order, 'status'> }) {
  return <Chip kind={statusTone[order.status] || 'default'} dot>{statusLabel(order.status)}</Chip>;
}
