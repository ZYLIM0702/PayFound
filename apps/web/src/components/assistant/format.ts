import type { Message } from '@openuidev/react-headless';
import { parseMessage } from '@openuidev/react-lang';

export const IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'];
export const MAX_IMAGES = 3;
export const MAX_IMAGE_BYTES = 4 * 1024 * 1024;

type Part = { type?: string; text?: string; source?: { type?: string; value?: string; mimeType?: string } };
const parts = (m: Message): Part[] | null => { const c = (m as { content?: unknown }).content; return Array.isArray(c) ? c as Part[] : null; };

/** Plain text of a message (user text, or the raw OpenUI Lang of an assistant message). */
export function textOf(m: Message): string {
  const c = (m as { content?: unknown }).content;
  if (typeof c === 'string') return c;
  return (parts(m) ?? []).filter(p => p.type === 'text').map(p => p.text ?? '').join(' ');
}

/** Data URLs of the images attached to a user message. */
export function imagesOf(m: Message): string[] {
  return (parts(m) ?? []).filter(p => p.type === 'image' && p.source?.type === 'data' && p.source.value && p.source.mimeType)
    .map(p => `data:${p.source!.mimeType};base64,${p.source!.value}`);
}

/** The text a person sees in a user bubble (action-click turns carry hidden context markers). */
export function visibleUserText(m: Message): string {
  const t = textOf(m);
  try { return parseMessage(t).content || t; } catch { return t; }
}

export function imagePart(dataUrl: string) {
  const [head, value] = dataUrl.split(',');
  return { type: 'image' as const, source: { type: 'data' as const, value, mimeType: head.slice(5, head.indexOf(';')) } };
}

export type StoredMessage = { id: string; role: 'user' | 'assistant'; content: string; images?: { mime: string; data_url?: string; placeholder?: string }[]; tools?: { id: string; name: string }[] };

/** Server JSON -> OpenUI messages. Stored tool summaries become a completed tool-call step before the answer. */
export function toMessages(stored: StoredMessage[]): Message[] {
  const out: Message[] = [];
  for (const m of stored) {
    if (m.role === 'user') {
      const imgs = (m.images ?? []).filter(i => i.data_url).map(i => imagePart(i.data_url!));
      const missing = (m.images ?? []).length - imgs.length;
      const text = missing > 0 ? `${m.content}${m.content ? ' ' : ''}[${missing} image${missing > 1 ? 's' : ''} attached]` : m.content;
      out.push({ id: m.id, role: 'user', content: imgs.length ? [{ type: 'text', text }, ...imgs] : text } as Message);
      continue;
    }
    if (m.tools?.length) {
      out.push({ id: `${m.id}-tools`, role: 'assistant', content: '', toolCalls: m.tools.map(t => ({ id: t.id, type: 'function', function: { name: t.name, arguments: '{}' } })) } as Message);
      for (const t of m.tools) out.push({ id: `${m.id}-r-${t.id}`, role: 'tool', toolCallId: t.id, content: '{"status":"done"}' } as Message);
    }
    out.push({ id: m.id, role: 'assistant', content: m.content } as Message);
  }
  return out;
}
