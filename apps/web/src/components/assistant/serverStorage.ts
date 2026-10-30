import type { ChatStorage, Message, Thread } from '@openuidev/react-headless';
import { apiFetch } from '../../lib/api';
import { textOf, toMessages, type StoredMessage } from './format';

type Row = { id: string; title: string; created_at: string; updated_at: string };

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await apiFetch(path, init);
  if (!r.ok) throw new Error(`History request failed (${r.status})`);
  return (r.status === 204 ? undefined : await r.json()) as T;
}
// Grouping in the sidebar is by last activity, so the "created" slot carries the last update time.
const toThread = (r: Row): Thread => ({ id: r.id, title: r.title, createdAt: Date.parse(r.updated_at) || Date.now() });

/** Chat history stored on the server per signed-in user (survives reloads and devices). */
export function serverStorage(surface: 'shopper' | 'merchant' = 'shopper'): ChatStorage {
  return { thread: {
    listThreads: async () => ({ threads: (await call<{ threads: Row[] }>(`/assistant/threads?surface=${surface}`)).threads.map(toThread) }),
    createThread: async (first: Message) => toThread(await call<Row>('/assistant/threads', { method: 'POST', body: JSON.stringify({ id: crypto.randomUUID(), title: textOf(first).slice(0, 80) || 'New chat', surface }) })),
    getMessages: async id => toMessages((await call<{ messages: StoredMessage[] }>(`/assistant/threads/${encodeURIComponent(id)}`)).messages),
    updateThread: async thread => { await call(`/assistant/threads/${encodeURIComponent(thread.id)}`, { method: 'PATCH', body: JSON.stringify({ title: thread.title }) }); return thread; },
    deleteThread: async id => { await call(`/assistant/threads/${encodeURIComponent(id)}`, { method: 'DELETE' }); },
  } };
}
