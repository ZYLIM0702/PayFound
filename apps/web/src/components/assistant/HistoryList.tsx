import { useEffect, useMemo, useState } from 'react';
import { useThreadList, type Thread } from '@openuidev/react-headless';
import { Check, MessageSquare, Pencil, Plus, Trash2, X } from 'lucide-react';

const GROUPS = ['Today', 'Yesterday', 'Earlier'] as const;
type Group = typeof GROUPS[number];

function groupOf(at: string | number): Group {
  const d = new Date(at), now = new Date();
  const start = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const days = Math.round((start(now) - start(d)) / 86_400_000);
  return days <= 0 ? 'Today' : days === 1 ? 'Yesterday' : 'Earlier';
}

function Row({ thread, active, onOpen }: { thread: Thread; active: boolean; onOpen: () => void }) {
  const update = useThreadList(s => s.updateThread);
  const remove = useThreadList(s => s.deleteThread);
  const [mode, setMode] = useState<'view' | 'rename' | 'delete'>('view');
  const [title, setTitle] = useState(thread.title);
  if (mode === 'rename') return <li className="pf-hist-row editing">
    <form onSubmit={e => { e.preventDefault(); const t = title.trim(); if (t) update({ ...thread, title: t.slice(0, 80) }); setMode('view'); }}>
      <input autoFocus value={title} maxLength={80} aria-label="Chat title" onChange={e => setTitle(e.target.value)} onKeyDown={e => { if (e.key === 'Escape') setMode('view'); }} />
      <button type="submit" aria-label="Save title"><Check size={14} /></button>
      <button type="button" aria-label="Cancel" onClick={() => setMode('view')}><X size={14} /></button>
    </form></li>;
  if (mode === 'delete') return <li className="pf-hist-row confirm" role="alertdialog" aria-label="Delete chat">
    <span>Delete this chat?</span>
    <button type="button" className="danger" onClick={() => remove(thread.id)}>Delete</button>
    <button type="button" onClick={() => setMode('view')}>Keep</button></li>;
  return <li className={`pf-hist-row ${active ? 'active' : ''}`} data-testid="history-thread">
    <button type="button" className="pf-hist-open" onClick={onOpen} aria-current={active ? 'true' : undefined} title={thread.title}><MessageSquare size={14} /><span>{clip(thread.title)}</span></button>
    <span className="pf-hist-actions">
      <button type="button" aria-label={`Rename ${thread.title}`} onClick={() => { setTitle(thread.title); setMode('rename'); }}><Pencil size={13} /></button>
      <button type="button" aria-label={`Delete ${thread.title}`} onClick={() => setMode('delete')}><Trash2 size={13} /></button>
    </span></li>;
}

/** Server-backed chat history grouped by Today / Yesterday / Earlier, with New chat. */
/** Titles are shown up to 32 characters; the full title stays in the tooltip. */
const clip = (text: string) => (text.length > 32 ? `${text.slice(0, 31).trimEnd()}…` : text);

export function HistoryList({ onPick }: { onPick?: () => void }) {
  const threads = useThreadList(s => s.threads);
  const loading = useThreadList(s => s.isLoadingThreads);
  const error = useThreadList(s => s.threadListError);
  const selected = useThreadList(s => s.selectedThreadId);
  const select = useThreadList(s => s.selectThread);
  const newChat = useThreadList(s => s.switchToNewThread);
  const load = useThreadList(s => s.loadThreads);
  useEffect(() => { load(); }, [load]);
  const grouped = useMemo(() => {
    const out: Record<Group, Thread[]> = { Today: [], Yesterday: [], Earlier: [] };
    for (const t of threads) out[groupOf(t.createdAt)].push(t);
    return out;
  }, [threads]);
  return <div className="pf-hist">
    <button type="button" className="pf-hist-new" onClick={() => { newChat(); onPick?.(); }} data-testid="new-chat"><Plus size={15} />New chat</button>
    <nav aria-label="Chat history" className="pf-hist-scroll">
      {loading && !threads.length && <p className="pf-hist-empty">Loading chats…</p>}
      {error && <p className="pf-hist-empty">Could not load your chats.</p>}
      {!loading && !error && !threads.length && <p className="pf-hist-empty">Your conversations appear here.</p>}
      {GROUPS.map(g => grouped[g].length > 0 && <section key={g}>
        <h3>{g}</h3>
        <ul>{grouped[g].map(t => <Row key={t.id} thread={t} active={t.id === selected} onOpen={() => { select(t.id); onPick?.(); }} />)}</ul>
      </section>)}
    </nav>
  </div>;
}
