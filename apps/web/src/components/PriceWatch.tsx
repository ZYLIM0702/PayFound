import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, BellOff, Trash2 } from 'lucide-react';
import { ApiError, cash, messageOf, post, remove } from '../lib/api';
import { useResource } from '../lib/use-resource';
import { Chip, Empty, ErrorLine, Spinner, type Tone } from './Shared';

export type PriceWatch = { id: string; product_id: string; name: string; local_cents: number | null; online_cents: number | null; retailer?: string | null; status: 'LOCAL_CHEAPER' | 'ONLINE_CHEAPER' | 'ONLINE_DEAL_DROPPED' | 'NO_ONLINE_PRICE'; message: string };
type Watches = { items: PriceWatch[] };

const TONE: Record<PriceWatch['status'], [Tone, string]> = {
  LOCAL_CHEAPER: ['green', 'Local is cheaper'], ONLINE_CHEAPER: ['amber', 'Online is cheaper'],
  ONLINE_DEAL_DROPPED: ['red', 'Online deal dropped'], NO_ONLINE_PRICE: ['default', 'No online price'],
};

/** Product page toggle. The list is fetched first because DELETE needs the watch id. */
export function WatchPriceButton({ productId }: { productId: string }) {
  const list = useResource<Watches>('/me/price-watches');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const watch = list.data?.items.find(w => w.product_id === productId);
  async function toggle() {
    setBusy(true); setError('');
    try {
      if (watch) await remove(`/me/price-watches/${encodeURIComponent(watch.id)}`); else await post('/me/price-watches', { product_id: productId });
      await list.refresh();
    } catch (issue) {
      // Already removed elsewhere (the list was stale): just show the current state.
      if (issue instanceof ApiError && issue.status === 404) await list.refresh();
      else setError(messageOf(issue));
    } finally { setBusy(false); }
  }
  return <div className="space-y-2">
    <button type="button" className="pf-btn outline lg w-full" aria-pressed={Boolean(watch)} disabled={busy || list.loading || (!list.data && Boolean(list.error))} onClick={() => void toggle()} data-testid="watch-price">
      {watch ? <BellOff size={17} /> : <Bell size={17} />}{busy ? 'Saving…' : watch ? 'Watching price' : 'Watch price'}</button>
    <ErrorLine message={error || (!list.data ? list.error : '')} retry={error ? undefined : list.refresh} />
  </div>;
}

export function PriceAlerts() {
  const res = useResource<Watches>('/me/price-watches');
  const [error, setError] = useState('');
  const watches = res.data?.items || [];
  async function drop(w: PriceWatch) {
    setError('');
    try { await remove(`/me/price-watches/${encodeURIComponent(w.id)}`); await res.refresh(); } catch (issue) { setError(messageOf(issue)); }
  }
  return <section className="p-4 sm:p-5 border-t border-line space-y-3" aria-label="Price alerts" data-testid="price-alerts">
    <h3 className="pf-title">Price alerts</h3>
    <ErrorLine message={error || res.error} retry={res.refresh} />
    {res.loading ? <Spinner /> : !res.error && (watches.length ? <ul className="grid sm:grid-cols-2 gap-3">{watches.map(w => { const [kind, label] = TONE[w.status] || TONE.NO_ONLINE_PRICE;
      return <li key={w.id} className="pf-card p-3 flex gap-3 min-w-0">
        <div className="min-w-0 flex-1 space-y-1.5">
          <Link to={`/products/${w.product_id}`} className="text-sm font-semibold hover:underline line-clamp-2">{w.name}</Link>
          <p className="text-[13px] text-ink-2 tabular">Local {w.local_cents != null ? cash(w.local_cents) : 'n/a'} · Online {w.online_cents != null ? cash(w.online_cents) : 'n/a'}{w.retailer ? ` (${w.retailer})` : ''}</p>
          <div className="flex flex-wrap items-center gap-1.5"><Chip kind={kind}>{label}</Chip><span className="text-[13px] text-muted">{w.message}</span></div></div>
        <button className="pf-btn sm ghost icon min-h-[44px] min-w-[44px]" aria-label={`Stop watching ${w.name}`} onClick={() => void drop(w)}><Trash2 size={15} /></button></li>; })}</ul>
      : <Empty title="No price alerts" description="Watch a product to get told when online deals beat the local price." />)}
  </section>;
}
