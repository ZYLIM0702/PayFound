import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Send } from 'lucide-react';
import { messageOf, post } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Empty, Spinner } from '../../components/Shared';
import { Pane, PaneHeader, Quiet, fmtDate, fmtTime, type Thread, type ThreadDetail } from './shared';

const MAX = 1000;
type Notify = { onError: (m: string) => void; onInfo: (m: string) => void };

function Conversation({ id, onBack, onChanged, onError }: { id: string; onBack: () => void; onChanged: () => void; onError: (m: string) => void }) {
  const res = useResource<ThreadDetail>(`/me/messages/${encodeURIComponent(id)}`, 10000);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  const count = res.data?.messages.length || 0;
  useEffect(() => { end.current?.scrollIntoView({ block: 'end' }); }, [count, id]);
  async function send(e: React.FormEvent) {
    e.preventDefault(); if (!text.trim()) return;
    setBusy(true); onError('');
    try { await post(`/me/messages/${encodeURIComponent(id)}`, { body: text }); setText(''); await res.refresh(); onChanged(); }
    catch (issue) { onError(messageOf(issue)); } finally { setBusy(false); }
  }
  const t = res.data;
  return <div className="flex flex-col h-full min-h-0">
    <div className="flex items-center gap-2 px-4 py-3 border-b border-line">
      <button className="pf-btn sm ghost icon md:hidden" aria-label="Back to conversations" onClick={onBack}><ArrowLeft size={16} /></button>
      <div className="min-w-0"><h3 className="text-sm font-semibold truncate">{t?.merchant_name || 'Conversation'}</h3><p className="text-[12.5px] text-muted truncate">{t?.subject}</p></div>
    </div>
    <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-4 py-3 space-y-2.5" aria-live="polite" data-testid="message-list">
      {res.loading ? <Spinner /> : t?.messages.map(m => <div key={m.id} className={`flex ${m.sender === 'buyer' ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm whitespace-pre-wrap break-words ${m.sender === 'buyer' ? 'bg-ink text-white' : 'bg-sunk text-ink'}`}>{m.body}
          <span className={`block text-[11px] mt-0.5 ${m.sender === 'buyer' ? 'text-white/60' : 'text-muted'}`}>{m.sender === 'buyer' ? 'You' : t.merchant_name} · {fmtDate(m.created_at, false)} {fmtTime(m.created_at)}</span></div></div>)}
      <div ref={end} />
    </div>
    <form onSubmit={e => void send(e)} className="border-t border-line p-3 flex items-end gap-2">
      <label className="flex-1 min-w-0"><span className="sr-only">Message</span>
        <textarea className="pf-textarea !min-h-[44px]" rows={2} maxLength={MAX} placeholder="Write a message to the store" value={text} onChange={e => setText(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} />
        <span className="text-[11.5px] text-muted tabular">{text.length}/{MAX}</span></label>
      <button className="pf-btn" disabled={busy || !text.trim()}><Send size={15} />Send</button>
    </form>
  </div>;
}

export function MessagesPanel({ query, onError }: Notify & { query: string }) {
  const list = useResource<{ threads: Thread[]; note: string }>('/me/messages');
  const [params, setParams] = useSearchParams();
  const [active, setActive] = useState('');
  const started = useRef('');
  const wantMerchant = params.get('merchant') || '';
  const wantOrder = params.get('order') || '';
  useEffect(() => {
    if (!wantMerchant || started.current === `${wantMerchant}:${wantOrder}`) return;
    started.current = `${wantMerchant}:${wantOrder}`;
    post<Thread>('/me/messages/start', { merchant_id: wantMerchant, order_id: wantOrder || null })
      .then(t => { setActive(t.id); setParams({}, { replace: true }); return list.refresh(); })
      .catch(issue => onError(messageOf(issue)));
  }, [wantMerchant, wantOrder]);
  const q = query.toLowerCase();
  const groups = useMemo(() => {
    const m = new Map<string, Thread[]>();
    for (const t of (list.data?.threads || []).filter(t => !q || `${t.merchant_name} ${t.subject} ${t.last_message?.body || ''}`.toLowerCase().includes(q))) m.set(t.merchant_name || t.merchant_id, [...(m.get(t.merchant_name || t.merchant_id) || []), t]);
    return [...m.entries()];
  }, [list.data, q]);
  const total = list.data?.threads.length || 0;
  return <Pane>
    <PaneHeader title="Messages" hint="Conversations with stores about your orders. Replies appear here once the store answers." />
    {list.loading ? <Spinner /> : !total && !active ? <Empty title="No conversations yet" description="Open an order and choose Message store to ask the store a question."><Link className="pf-btn" to="/account/orders">View orders</Link></Empty>
      : <div className="flex-1 min-h-0 grid grid-cols-[minmax(0,1fr)] md:grid-cols-[300px_minmax(0,1fr)]">
        <nav aria-label="Conversations" className={`min-h-0 overflow-y-auto overscroll-contain border-r border-line ${active ? 'hidden md:block' : ''}`}>
          {!groups.length && <div className="p-4"><Quiet>No conversations match your search.</Quiet></div>}
          {groups.map(([store, threads]) => <section key={store} aria-label={store}><h3 className="px-4 pt-3 pb-1 text-[12.5px] font-semibold text-muted">{store}</h3>
            <ul>{threads.map(t => <li key={t.id}><button type="button" aria-current={active === t.id} onClick={() => setActive(t.id)} data-testid={`thread-${t.id}`}
              className={`w-full text-left px-4 py-2.5 border-l-2 hover:bg-sunk ${active === t.id ? 'bg-sunk border-ink' : 'border-transparent'}`}>
              <span className="flex justify-between gap-2 text-sm font-medium"><span className="truncate">{t.subject}</span><span className="text-[11.5px] text-muted shrink-0">{fmtDate(t.updated_at, false)}</span></span>
              <span className="block text-[12.5px] text-muted truncate">{t.last_message ? `${t.last_message.sender === 'buyer' ? 'You: ' : ''}${t.last_message.body}` : 'No messages yet'}</span></button></li>)}</ul></section>)}
        </nav>
        <div className={`min-h-0 ${active ? '' : 'hidden md:grid place-items-center'}`}>{active ? <Conversation key={active} id={active} onBack={() => setActive('')} onChanged={() => void list.refresh()} onError={onError} /> : <Quiet>Select a conversation.</Quiet>}</div>
      </div>}
  </Pane>;
}
