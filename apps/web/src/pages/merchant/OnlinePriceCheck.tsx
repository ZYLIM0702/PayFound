import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Lock } from 'lucide-react';
import { ApiError, api, cash, messageOf, safeExternalUrl } from '../../lib/api';
import { Empty, ErrorLine, Panel, Spinner } from '../../components/Shared';

type Row = { product_id: string; name: string; local_cents: number; online_cents: number | null; retailer: string | null; url: string | null; difference_cents: number | null; checked_at: string | null; source: string };

export function OnlinePriceCheck({ merchantId, currency = 'USD' }: { merchantId: string; currency?: string }) {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [locked, setLocked] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true); setError('');
    try { setRows((await api<{ items: Row[] }>(`/merchants/${encodeURIComponent(merchantId)}/competitor-prices`)).items); setLocked(''); }
    catch (issue) { if (issue instanceof ApiError && issue.status === 402) setLocked(issue.message); else setError(messageOf(issue)); }
    finally { setLoading(false); }
  }, [merchantId]);
  useEffect(() => { void load(); }, [load]);
  return <Panel title="Online price check" description="Your prices next to what online retailers charge">
    <div data-testid="online-price-check">
      {loading ? <Spinner /> : locked ? <div className="pf-card p-5 flex items-start gap-3" data-testid="online-price-locked"><Lock size={18} className="mt-0.5 shrink-0" /><div className="space-y-2"><p className="font-semibold">Online price check is included in Pro and Diamond</p><p className="text-sm text-muted">{locked}</p><Link className="pf-btn sm min-h-[44px]" to="/merchant/plan">See plans</Link></div></div>
        : error ? <ErrorLine message={error} retry={() => void load()} />
        : !rows?.length ? <Empty title="No prices to compare" description="Add products to compare them with online retailers." />
        : <div className="overflow-x-auto -mx-1"><table className="w-full text-sm min-w-[620px]"><thead><tr className="text-left text-xs text-muted"><th className="py-2 px-1 font-semibold">Product</th><th className="px-1 font-semibold">Local</th><th className="px-1 font-semibold">Online</th><th className="px-1 font-semibold">Difference</th><th className="px-1 font-semibold">Retailer</th><th className="px-1 font-semibold">Checked</th></tr></thead>
          <tbody className="divide-y divide-line">{rows.map(r => { const na = r.source === 'unavailable' || r.online_cents == null; const d = r.difference_cents; const localCheaper = r.online_cents != null && r.local_cents <= r.online_cents;
            const url = safeExternalUrl(r.url);
            return <tr key={r.product_id}><td className="py-2.5 px-1 font-semibold">{r.name}</td><td className="px-1 tabular">{cash(r.local_cents, currency)}</td>
              {na ? <td colSpan={2} className="px-1 text-muted">Online price not available right now</td> : <><td className="px-1 tabular">{cash(r.online_cents!, currency)}</td>
                <td className={`px-1 tabular font-semibold ${localCheaper ? 'text-ok' : 'text-warn'}`}>{d == null ? 'n/a' : d === 0 ? 'Same' : `${cash(Math.abs(d), currency)} ${localCheaper ? 'cheaper locally' : 'cheaper online'}`}</td></>}
              <td className="px-1">{url ? <a className="pf-link inline-flex items-center gap-1 min-h-[44px]" href={url} target="_blank" rel="noopener noreferrer">{r.retailer || 'View'}<ArrowUpRight size={12} /></a> : <span className="text-muted">{r.retailer || 'n/a'}</span>}</td>
              <td className="px-1 text-muted">{r.checked_at ? new Date(r.checked_at).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : 'n/a'}</td></tr>; })}</tbody></table></div>}
    </div>
  </Panel>;
}
