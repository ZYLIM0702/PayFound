import { useEffect, useState } from 'react';
import { Copy, RefreshCw } from 'lucide-react';
import { messageOf, post } from '../../../lib/api';
import { Empty, ErrorLine, Notice, Panel, Spinner } from '../../../components/Shared';

type Item = { product_id: string; name: string; on_hand: number; projected_units: number; days_cover: number; sell_out_date: string | null; suggested_order_qty: number };
type StockUp = { items: Item[]; supplier_email: { subject: string; body: string; status: 'DRAFT' } };
const DAYS = 7;
const dateText = (v: string | null) => v ? new Date(`${v.slice(0, 10)}T12:00:00`).toLocaleDateString([], { month: 'short', day: 'numeric' }) : 'n/a';

export function StockUpPanel({ merchantId }: { merchantId: string }) {
  const [data, setData] = useState<StockUp | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [note, setNote] = useState('');
  async function load() {
    setBusy(true); setError('');
    try { setData(await post<StockUp>(`/merchants/${encodeURIComponent(merchantId)}/stock-up`, { days: DAYS })); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); }
  }
  useEffect(() => { void load(); }, [merchantId]);
  async function copy() {
    if (!data) return;
    try { await navigator.clipboard.writeText(`Subject: ${data.supplier_email.subject}\n\n${data.supplier_email.body}`); setCopied(true); setNote(''); window.setTimeout(() => setCopied(false), 2000); }
    catch { setNote('Copy failed. Select the text and copy it manually.'); }
  }
  return <Panel title="Likely to sell out" description={`Projected over the next ${DAYS} days`} className="h-full"
    actions={<button className="pf-btn sm outline min-h-[44px]" disabled={busy} onClick={() => void load()}><RefreshCw size={14} />{busy ? 'Refreshing…' : 'Refresh'}</button>}>
    <div className="space-y-4" data-testid="stock-up">
      <ErrorLine message={error} retry={() => void load()} />
      {busy && !data ? <Spinner /> : data && (data.items.length ? <ul className="divide-y divide-line -my-2">{data.items.map(i => <li key={i.product_id} className="py-2.5">
        <p className="text-sm font-semibold break-words">{i.name}</p>
        <p className="text-[13px] text-muted tabular">On hand {i.on_hand} · {i.days_cover.toFixed(1)} days cover · sells out {dateText(i.sell_out_date)} · suggest ordering <b className="text-ink">{i.suggested_order_qty}</b></p></li>)}</ul>
        : <Empty title="Nothing at risk" description="No products are projected to sell out soon." />)}
      {data && <div className="space-y-2 pt-3 border-t border-line">
        <h3 className="pf-title">Supplier email draft</h3>
        <Notice tone="amber">Draft only. Review and send it yourself.</Notice>
        <p className="text-sm"><span className="text-muted">Subject:</span> <span className="font-semibold break-words">{data.supplier_email.subject}</span></p>
        <textarea className="pf-input w-full min-h-[160px]" readOnly value={data.supplier_email.body} aria-label="Supplier email body" />
        <button className="pf-btn sm outline min-h-[44px]" onClick={() => void copy()}><Copy size={14} />{copied ? 'Copied' : 'Copy'}</button>
        {note && <p className="text-xs text-muted" role="status">{note}</p>}
      </div>}
    </div>
  </Panel>;
}
