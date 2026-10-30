import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, Send } from 'lucide-react';
import { messageOf, post } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Empty, ErrorLine, PageHeader, Spinner } from '../../components/Shared';
import { fmtDate, fmtTime } from '../account/shared';

type Conversation = { id: string; subject: string; buyer_name: string; order_id: string | null; updated_at: string; last_message: { sender: string; body: string } | null };
type ConversationList = { threads: Conversation[]; count: number };
type Message = { id: string; sender: 'buyer' | 'merchant'; body: string; created_at: string };
type ThreadDetail = Conversation & { messages: Message[] };

const MAX = 1000;

/** One conversation. Keyed by thread id by the parent, so its messages and draft never leak into another chat. */
function Chat({ thread, onBack, onSent }: { thread: Conversation; onBack: () => void; onSent: () => void }) {
  const res = useResource<ThreadDetail>(`/me/messages/${encodeURIComponent(thread.id)}`, 8000);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const end = useRef<HTMLDivElement>(null);
  const count = res.data?.messages.length || 0;
  useEffect(() => { end.current?.scrollIntoView({ block: 'end' }); }, [count]);
  async function send() {
    if (!text.trim()) return;
    setBusy(true); setError('');
    try { await post(`/me/messages/${encodeURIComponent(thread.id)}`, { body: text }); setText(''); await res.refresh(); onSent(); }
    catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); }
  }
  return <div className="flex flex-col h-full min-h-0" data-testid="merchant-chat">
    <div className="flex items-center gap-2 px-4 py-3 border-b border-line">
      <button className="pf-btn sm ghost icon lg:hidden" aria-label="Back to conversations" onClick={onBack}><ArrowLeft size={16} /></button>
      <div className="min-w-0"><h3 className="text-sm font-semibold truncate">{thread.buyer_name}</h3><p className="text-[12.5px] text-muted truncate">{thread.subject}{thread.order_id ? ` · Order ${thread.order_id.slice(-8)}` : ''}</p></div>
    </div>
    <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-4 py-3 space-y-2.5" aria-live="polite" data-testid="merchant-message-list">
      {res.loading && !res.data ? <Spinner /> : res.data?.messages.map(m => <div key={m.id} className={`flex ${m.sender === 'merchant' ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm whitespace-pre-wrap break-words ${m.sender === 'merchant' ? 'bg-ink text-white' : 'bg-sunk text-ink'}`}>{m.body}
          <span className={`block text-[11px] mt-0.5 ${m.sender === 'merchant' ? 'text-white/60' : 'text-muted'}`}>{m.sender === 'merchant' ? 'Your store' : thread.buyer_name} · {fmtDate(m.created_at, false)} {fmtTime(m.created_at)}</span></div></div>)}
      <div ref={end} />
    </div>
    <form onSubmit={e => { e.preventDefault(); void send(); }} className="border-t border-line p-3 space-y-2">
      <ErrorLine message={error} />
      <div className="flex items-end gap-2">
        <label className="flex-1 min-w-0"><span className="sr-only">Message to {thread.buyer_name}</span>
          <textarea className="pf-textarea !min-h-[44px]" rows={2} maxLength={MAX} placeholder={`Reply to ${thread.buyer_name}`} value={text} onChange={e => setText(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); void send(); } }} data-testid="merchant-message-input" />
          <span className="text-[11.5px] text-muted tabular">{text.length}/{MAX}</span></label>
        <button className="pf-btn" disabled={busy || !text.trim()} data-testid="merchant-message-send"><Send size={15} />Send</button>
      </div>
    </form>
  </div>;
}

export function MessagesPage({ merchantId }: { merchantId: string }) {
  const list = useResource<ConversationList>(`/merchants/${encodeURIComponent(merchantId)}/messages`, 10000);
  const [activeId, setActiveId] = useState('');
  const threads = list.data?.threads || [];
  const active = threads.find(t => t.id === activeId);
  return <div className="space-y-6 pf-enter" data-testid="merchant-messages">
    <PageHeader title="Messages" description="Chats with shoppers about their orders. Each conversation is kept separate." />
    {list.loading && !list.data ? <Spinner /> : !threads.length ? <Empty title="No messages yet" description="When a shopper messages your store from an order, it appears here." />
      : <div className="pf-card overflow-hidden h-[70dvh] min-h-[420px] grid grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)]">
        <nav aria-label="Conversations" className={`min-h-0 overflow-y-auto overscroll-contain border-r border-line ${active ? 'hidden lg:block' : ''}`}>
          <ul>{threads.map(t => <li key={t.id}><button type="button" aria-current={activeId === t.id} onClick={() => setActiveId(t.id)} data-testid={`merchant-thread-${t.id}`}
            className={`w-full text-left px-4 py-3 border-l-2 hover:bg-sunk ${activeId === t.id ? 'bg-sunk border-ink' : 'border-transparent'}`}>
            <span className="flex justify-between gap-2 text-sm font-semibold"><span className="truncate">{t.buyer_name}</span><span className="text-[11.5px] text-muted shrink-0">{fmtDate(t.updated_at, false)}</span></span>
            <span className="block text-[12.5px] text-muted truncate">{t.subject}</span>
            <span className="block text-[12.5px] text-muted truncate">{t.last_message ? `${t.last_message.sender === 'merchant' ? 'You: ' : ''}${t.last_message.body}` : 'No messages yet'}</span></button></li>)}</ul>
        </nav>
        <div className={`min-h-0 ${active ? '' : 'hidden lg:grid place-items-center'}`}>
          {active ? <Chat key={active.id} thread={active} onBack={() => setActiveId('')} onSent={() => void list.refresh()} />
            : <p className="text-sm text-muted">Select a conversation.</p>}
        </div>
      </div>}
  </div>;
}
