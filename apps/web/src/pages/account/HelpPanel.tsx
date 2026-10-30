import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown } from 'lucide-react';
import { messageOf, post, type Order } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, Spinner } from '../../components/Shared';
import { Pane, PaneHeader, Quiet, Scroll, fmtDate, type Ticket } from './shared';

type Faq = { cat: string; q: string; a: string };
const FAQ: Faq[] = [
  { cat: 'Orders and pickup', q: 'How does pickup work?', a: 'You reserve items from one store, pay, and collect them in your pickup window. The store marks the order Ready when it is packed. Show your order id at the counter.' },
  { cat: 'Orders and pickup', q: 'My reservation is about to expire.', a: 'Reservations hold stock for a short time while you pay. If the hold ends, the order expires and the stock is released; you can reserve again if it is still available.' },
  { cat: 'Orders and pickup', q: 'Can I change or cancel an order?', a: 'Open the order from Orders and use its actions, or message the store. Cancelling after payment is handled through a refund.' },
  { cat: 'Refunds', q: 'How do refunds work?', a: 'Refunds go back to the original PayPal payment and are issued by the store or an admin, never automatically by an assistant. Status shows as Refund pending, then Refunded.' },
  { cat: 'Refunds', q: 'How long does a refund take?', a: 'In this sandbox demo no money moves. In a live setup PayPal decides timing, usually a few days.' },
  { cat: 'Stock accuracy', q: 'Why was an item out of stock after I saw it?', a: 'Stock is the store\'s own count and can change between refreshes. Stock is checked again when you reserve. Online offers from other retailers never prove a local store has the item.' },
  { cat: 'Payments and PayPal', q: 'Is this real money?', a: 'No. Payments run in demo or PayPal sandbox mode, so no funds move. Order pages say which mode applied.' },
  { cat: 'Payments and PayPal', q: 'Can I link my PayPal account?', a: 'Payments has a clearly labelled sandbox link that saves only a masked label. Real linking needs PayPal\'s own login and Vault flow, and checkout always uses PayPal\'s approval window.' },
  { cat: 'Payments and PayPal', q: 'Is Pay Later available?', a: 'PayPal alone decides Pay Later eligibility and shows it in its own window. PayFound never lends money or holds a balance.' },
  { cat: 'Demo disclaimers', q: 'Are the stores and reviews real?', a: 'Stores, stock, reviews and messages in this demo are synthetic samples unless a store has connected its own data. Sample items are labelled.' },
  { cat: 'Delivery partners', q: 'Can a courier bring my order?', a: 'You can request a quote from a sample provider list. It is a local record only: no courier is contacted and no money moves.' },
  { cat: 'Privacy and location', q: 'How is my location used?', a: 'Your location only orders nearby stores. You can stop sharing in Settings and the app falls back to an approximate city from your IP address. See the Privacy policy for details.' },
];

export function HelpPanel({ query, orders, onError, onInfo }: { query: string; orders: Order[]; onError: (m: string) => void; onInfo: (m: string) => void }) {
  const tickets = useResource<{ tickets: Ticket[]; note: string }>('/me/support-tickets');
  const [topic, setTopic] = useState('orders');
  const [orderId, setOrderId] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const q = query.toLowerCase();
  const rows = FAQ.filter(f => !q || `${f.cat} ${f.q} ${f.a}`.toLowerCase().includes(q));
  const cats = [...new Set(rows.map(r => r.cat))];
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); onError('');
    try { await post('/me/support-tickets', { topic, subject, message, order_id: orderId || null }); setSubject(''); setMessage(''); setOrderId(''); onInfo('Request sent. It is saved to your account; no agent is connected in this demo.'); await tickets.refresh(); }
    catch (issue) { onError(messageOf(issue)); } finally { setBusy(false); }
  }
  return <Pane>
    <PaneHeader title="Help center" hint="Search answers, or send a request." right={<span className="text-[13px] flex gap-3"><Link className="pf-link pf-tap" to="/privacy">Privacy</Link><Link className="pf-link pf-tap" to="/terms">Terms</Link></span>} />
    <Scroll className="p-4 sm:p-5 grid grid-cols-[minmax(0,1fr)] gap-6 content-start lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] lg:items-start">
      <section aria-label="Frequently asked questions" data-testid="faq">
        {!rows.length ? <Quiet>No answers match your search. Send us a request instead.</Quiet> : cats.map(cat => <div key={cat} className="mb-4"><h3 className="text-sm font-semibold mb-1.5">{cat}</h3>
          <div className="pf-card divide-y divide-line">{rows.filter(r => r.cat === cat).map(f => <details key={f.q} className="group px-4 py-2.5"><summary className="flex items-center justify-between gap-3 cursor-pointer list-none text-sm font-medium">{f.q}<ChevronDown size={16} className="shrink-0 transition-transform group-open:rotate-180" /></summary><p className="text-[13.5px] text-ink-2 mt-2 leading-relaxed">{f.a}</p></details>)}</div></div>)}
      </section>
      <div className="space-y-6">
        <form onSubmit={e => void submit(e)} className="pf-card p-4 space-y-3" aria-label="Contact support"><h3 className="text-sm font-semibold">Contact support</h3>
          <div className="grid grid-cols-2 gap-2">
            <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Topic</span><select className="pf-select" value={topic} onChange={e => setTopic(e.target.value)}>{[['orders', 'Orders and pickup'], ['refunds', 'Refunds'], ['payments', 'Payments'], ['stock', 'Stock accuracy'], ['delivery', 'Delivery'], ['account', 'Account'], ['other', 'Other']].map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></label>
            <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Order (optional)</span><select className="pf-select" value={orderId} onChange={e => setOrderId(e.target.value)}><option value="">None</option>{orders.slice(0, 30).map(o => <option key={o.id} value={o.id}>{o.merchant_name} · {o.id.slice(-6)}</option>)}</select></label></div>
          <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Subject</span><input className="pf-input" required maxLength={120} value={subject} onChange={e => setSubject(e.target.value)} /></label>
          <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">How can we help?</span><textarea className="pf-textarea" required rows={4} maxLength={2000} value={message} onChange={e => setMessage(e.target.value)} /></label>
          <div className="flex items-center justify-between gap-3"><Quiet>Demo help desk: saved to your account, no live agent.</Quiet><button className="pf-btn sm" disabled={busy}>{busy ? 'Sending…' : 'Send request'}</button></div></form>
        <section aria-label="Your requests"><h3 className="text-sm font-semibold mb-2">Your requests</h3>
          {tickets.loading ? <Spinner inline /> : !tickets.data?.tickets.length ? <Quiet>No requests yet.</Quiet> : <ul className="pf-card divide-y divide-line">{tickets.data.tickets.map(t => <li key={t.id} className="p-3 text-sm" data-testid={`ticket-${t.id}`}>
            <div className="flex items-center justify-between gap-2"><strong className="truncate">{t.subject}</strong><Chip kind={t.status === 'open' ? 'blue' : 'green'}>{t.status === 'open' ? 'Open' : 'Closed'}</Chip></div>
            <p className="text-[12.5px] text-muted mt-0.5">{t.topic} · {fmtDate(t.created_at)}</p></li>)}</ul>}</section>
      </div>
    </Scroll>
  </Pane>;
}
