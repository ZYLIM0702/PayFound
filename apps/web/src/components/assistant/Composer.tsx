import { createContext, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState, type ClipboardEvent, type DragEvent, type ReactNode } from 'react';
import { useThread, useThreadList } from '@openuidev/react-headless';
import { ArrowUp, ImagePlus, Loader2, Mic, Square, X } from 'lucide-react';
import { apiFetch } from '../../lib/api';
import { IMAGE_TYPES, MAX_IMAGES, MAX_IMAGE_BYTES, imagePart } from './format';

type Chip = { id: string; url: string; name: string };
const MAX_RECORD_SECONDS = 120;
const readAsDataUrl = (file: File) => new Promise<string>((resolve, reject) => { const r = new FileReader(); r.onload = () => resolve(String(r.result)); r.onerror = () => reject(r.error); r.readAsDataURL(file); });
/** Phone photos are several MB; shrink to <=1600px JPEG so they send fast and are small enough for the server to keep in chat history. */
async function shrinkImage(file: File): Promise<string> {
  const original = await readAsDataUrl(file);
  if (file.type === 'image/gif' || file.size < 300_000) return original;
  try {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, 1600 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(bitmap.width * scale); canvas.height = Math.round(bitmap.height * scale);
    const ctx = canvas.getContext('2d');
    if (!ctx) return original;
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();
    const out = canvas.toDataURL('image/jpeg', 0.82);
    return out.length < original.length ? out : original;
  } catch { return original; }
}
const clock = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

function pickAudioType() {
  if (typeof MediaRecorder === 'undefined') return '';
  return ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'].find(t => MediaRecorder.isTypeSupported(t)) ?? '';
}

type Voice = 'idle' | 'recording' | 'transcribing';

/** Dictation: records with MediaRecorder, sends the clip to the backend, hands back the transcript for review. */
function useDictation(onText: (t: string) => void, onError: (m: string) => void) {
  const [state, setState] = useState<Voice>('idle');
  const [seconds, setSeconds] = useState(0);
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const tick = useRef(0);
  const supported = typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined';

  const release = useCallback(() => { window.clearInterval(tick.current); recorder.current?.stream.getTracks().forEach(t => t.stop()); }, []);
  useEffect(() => () => { const r = recorder.current; if (r && r.state !== 'inactive') { r.onstop = null; r.stop(); } release(); }, [release]);

  const send = useCallback(async (blob: Blob, type: string) => {
    setState('transcribing');
    try {
      const form = new FormData();
      const ext = type.includes('mp4') ? 'mp4' : type.includes('ogg') ? 'ogg' : 'webm';
      form.append('file', new File([blob], `dictation.${ext}`, { type: type.split(';')[0] || 'audio/webm' }));
      const r = await apiFetch('/assistant/transcribe', { method: 'POST', body: form });
      if (!r.ok) throw new Error(r.status === 429 ? 'Too many voice requests. Wait a moment.' : r.status === 413 ? 'That recording is too long.' : 'Could not transcribe that. Please try again.');
      const { text } = await r.json() as { text: string };
      if (text.trim()) onText(text.trim()); else onError('I did not catch any speech. Try again.');
    } catch (e) { onError(e instanceof Error && e.message ? e.message : 'Could not transcribe that. Please try again.'); }
    finally { setState('idle'); }
  }, [onText, onError]);

  const stop = useCallback(() => { const r = recorder.current; if (r && r.state !== 'inactive') r.stop(); }, []);
  const start = useCallback(async () => {
    if (!supported) { onError('Voice input is not supported in this browser.'); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const type = pickAudioType();
      const rec = new MediaRecorder(stream, type ? { mimeType: type } : undefined);
      chunks.current = []; recorder.current = rec;
      rec.ondataavailable = e => { if (e.data.size) chunks.current.push(e.data); };
      rec.onstop = () => { release(); const blob = new Blob(chunks.current, { type: rec.mimeType || type || 'audio/webm' }); if (blob.size > 200) void send(blob, rec.mimeType || type); else { setState('idle'); onError('That recording was empty.'); } };
      rec.start(); setSeconds(0); setState('recording');
      tick.current = window.setInterval(() => setSeconds(s => { if (s + 1 >= MAX_RECORD_SECONDS) stop(); return s + 1; }), 1000);
    } catch (e) {
      const name = e instanceof DOMException ? e.name : '';
      onError(name === 'NotAllowedError' || name === 'SecurityError' ? 'Microphone access is blocked. Allow it in your browser settings to dictate.' : name === 'NotFoundError' ? 'No microphone was found.' : 'Could not start recording.');
    }
  }, [supported, onError, release, send, stop]);

  return { state, seconds, start, stop, supported };
}

/** Composer: text, pasted/attached images, dictation. `voiceSlot` is rendered in the toolbar (live voice button goes here). */
/** Runs a send only after the location question has been answered (see AssistantSurface). */
export const LocationGateContext = createContext<((go: () => void) => void) | null>(null);
export function useLocationGate() {
  const gate = useContext(LocationGateContext);
  return (go: () => void) => (gate ? gate(go) : go());
}

export function PfComposer({ placeholder, voiceSlot, className = '' }: { placeholder?: string; voiceSlot?: ReactNode; className?: string }) {
  const process = useThread(s => s.processMessage);
  const gated = useLocationGate();
  const cancel = useThread(s => s.cancelMessage);
  const running = useThread(s => s.isRunning);
  const loading = useThread(s => s.isLoadingMessages);
  const selected = useThreadList(s => s.selectedThreadId);
  const [text, setText] = useState('');
  const [chips, setChips] = useState<Chip[]>([]);
  const [note, setNote] = useState('');
  const area = useRef<HTMLTextAreaElement>(null);
  const files = useRef<HTMLInputElement>(null);

  const dictation = useDictation(
    useCallback((t: string) => { setNote(''); setText(prev => (prev.trim() ? `${prev.trimEnd()} ${t}` : t)); window.setTimeout(() => area.current?.focus(), 0); }, []),
    setNote);

  useEffect(() => { if (window.matchMedia('(min-width: 701px)').matches && !loading) area.current?.focus(); }, [selected, loading]);
  useLayoutEffect(() => { const el = area.current; if (!el) return; el.style.height = '0px'; el.style.height = `${Math.min(Math.max(el.scrollHeight, 28), 200)}px`; }, [text]);

  // A photo chosen on the Discover page waits in sessionStorage; attach it once the composer opens.
  useEffect(() => {
    let raw: string | null = null;
    try { raw = sessionStorage.getItem('pf.pendingImages'); sessionStorage.removeItem('pf.pendingImages'); } catch { raw = null; }
    if (!raw) return;
    void (async () => {
      const urls: unknown = (() => { try { return JSON.parse(raw); } catch { return []; } })();
      const files = await Promise.all((Array.isArray(urls) ? urls : []).filter((u): u is string => typeof u === 'string').map(async (u, i) => {
        const blob = await (await fetch(u)).blob();
        return new File([blob], `photo-${i + 1}.${blob.type.split('/')[1] || 'png'}`, { type: blob.type });
      }));
      if (files.length) void addFiles(files);
    })();
  }, []);
  const addFiles = async (list: File[]) => {
    const picked = list.filter(f => f.type.startsWith('image/'));
    if (!picked.length) return;
    setNote('');
    const next = [...chips];
    for (const f of picked) {
      if (!IMAGE_TYPES.includes(f.type)) { setNote('Only PNG, JPEG, WebP or GIF images are supported.'); continue; }
      if (f.size > MAX_IMAGE_BYTES) { setNote('Each image must be 4 MB or smaller.'); continue; }
      if (next.length >= MAX_IMAGES) { setNote(`You can attach up to ${MAX_IMAGES} images.`); break; }
      try { next.push({ id: crypto.randomUUID(), url: await shrinkImage(f), name: f.name || 'Pasted image' }); } catch { setNote('Could not read that image.'); }
    }
    setChips(next);
  };
  const onPaste = (e: ClipboardEvent) => {
    const imgs = [...e.clipboardData.files].filter(f => f.type.startsWith('image/'));
    if (imgs.length) { e.preventDefault(); void addFiles(imgs); }
  };
  const onDrop = (e: DragEvent) => { if (e.dataTransfer.files.length) { e.preventDefault(); void addFiles([...e.dataTransfer.files]); } };

  const canSend = (text.trim().length > 0 || chips.length > 0) && !running && !loading && dictation.state === 'idle';
  const submit = () => {
    if (!canSend) return;
    const body = text.trim();
    gated(() => void process({ role: 'user', content: chips.length ? [{ type: 'text', text: body || 'What is in this image?' }, ...chips.map(c => imagePart(c.url))] : body } as Parameters<typeof process>[0]));
    setText(''); setChips([]); setNote('');
  };

  return <div className={`pf-composer ${className}`} onDragOver={e => e.preventDefault()} onDrop={onDrop} data-testid="assistant-composer">
    {chips.length > 0 && <ul className="pf-composer-chips" aria-label="Attached images">{chips.map(c => <li key={c.id} className="pf-composer-chip">
      <img src={c.url} alt={c.name} /><button type="button" onClick={() => setChips(chips.filter(x => x.id !== c.id))} aria-label={`Remove ${c.name}`}><X size={12} /></button>
    </li>)}</ul>}
    <textarea ref={area} value={text} rows={1} className="pf-composer-input" placeholder={dictation.state === 'recording' ? 'Listening…' : placeholder} aria-label="Message"
      onChange={e => setText(e.target.value)} onPaste={onPaste}
      onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); submit(); } }} />
    <div className="pf-composer-bar">
      <input ref={files} type="file" accept={IMAGE_TYPES.join(',')} multiple hidden onChange={e => { void addFiles([...(e.target.files ?? [])]); e.target.value = ''; }} data-testid="attach-input" />
      <button type="button" className="pf-composer-btn" onClick={() => files.current?.click()} disabled={chips.length >= MAX_IMAGES} aria-label="Attach image" title="Attach image (or paste one)"><ImagePlus size={17} /></button>
      {dictation.state === 'recording'
        ? <button type="button" className="pf-composer-btn rec" onClick={dictation.stop} aria-label="Stop recording" data-testid="mic-stop"><Square size={13} fill="currentColor" /><span className="tabular">{clock(dictation.seconds)}</span></button>
        : dictation.state === 'transcribing'
          ? <span className="pf-composer-btn busy" role="status"><Loader2 size={16} className="pf-spin" />Transcribing…</span>
          : <button type="button" className="pf-composer-btn" onClick={() => void dictation.start()} aria-label="Dictate with your voice" title="Dictate" data-testid="mic-start"><Mic size={17} /></button>}
      {voiceSlot}
      <span className="pf-composer-note" role="status">{note}</span>
      <button type="button" className="pf-composer-send" onClick={running ? () => cancel() : submit} disabled={!running && !canSend} aria-label={running ? 'Stop' : 'Send message'} data-testid="send-message">
        {running ? <Square size={14} fill="currentColor" /> : <ArrowUp size={17} />}
      </button>
    </div>
  </div>;
}
