import '@openuidev/react-ui/layered/styles/index.css';
import './assistant.css';
import { useCallback, useEffect, useMemo, useRef, useState, type ComponentProps, type CSSProperties, type ReactNode } from 'react';
import { Popover } from 'radix-ui';
import { AgentInterface, ToolLabelsProvider, createTheme, type ConversationStarterProps, type ToolLabels } from '@openuidev/react-ui';
import { agUIAdapter, useThread, useThreadList, type ChatLLM } from '@openuidev/react-headless';
import { History, LocateFixed, Plus, X } from 'lucide-react';
import { apiFetch } from '../../lib/api';
import { useCart } from '../../lib/cart';
import { useUserLocation } from '../../lib/location';
import { AgentAvatar } from '../Brand';
import { payfoundLibrary } from '../../pages/agent/library';
import { mockAssistantResponse, mockEnabled } from './mock';
import { serverStorage } from './serverStorage';
import { HistoryList } from './HistoryList';
import { LocationGateContext, PfComposer, useLocationGate } from './Composer';
import { PfAssistantMessage, PfUserMessage } from './Messages';
import { imagesOf, textOf } from './format';
import { toolLabels } from './data';
import { RealtimeVoice } from './realtime/RealtimeVoice';

export type Surface = 'shopper' | 'merchant';

const theme = createTheme({
  fontBody: 'var(--pf-font-text)', fontHeading: 'var(--pf-font-display)', fontLabel: 'var(--pf-font-text)', fontNumbers: 'var(--pf-font-text)',
  background: '#ffffff', foreground: '#ffffff', popoverBackground: '#ffffff',
  textNeutralPrimary: '#0a0a0b', textNeutralSecondary: '#62656d', textNeutralTertiary: '#8e9199', textBrand: '#0057ff',
  interactiveAccentDefault: '#0a0a0b', interactiveAccentHover: '#2b2c30', interactiveAccentPressed: '#000000', interactiveAccentDisabled: '#cfd1d6',
  borderDefault: '#e7e8eb', borderInteractive: '#cfd1d6', borderInteractiveEmphasis: '#0a0a0b', borderInteractiveSelected: '#0057ff',
  chatUserResponseBg: '#0a0a0b', chatUserResponseText: '#ffffff',
  radiusM: '10px', radiusL: '14px', radiusXl: '20px',
});

const labels: ToolLabels = Object.fromEntries(Object.entries(toolLabels).map(([k, [running, done]]) => [k, { running: `${running}…`, done, failed: `Couldn't finish: ${running.toLowerCase()}` }]));
labels['paypal'] = { running: 'Checking PayPal…', done: 'Checked PayPal', failed: 'PayPal check failed' };
for (const n of ['list_transactions', 'list_disputes', 'get_dispute', 'list_invoices', 'get_invoice']) labels[n] = { running: 'Checking PayPal sandbox…', done: 'Checked PayPal sandbox', failed: 'PayPal check failed' };

/** Friendly, status-free error delivered through the normal AG-UI error event (never raw HTTP text). */
function failure(status: number): Response {
  const message = status === 401 || status === 403 ? 'Please sign in again to use the assistant.'
    : status === 429 ? 'You are asking quickly. Wait a few seconds and try again.'
      : 'The assistant is unavailable right now. Please try again in a moment.';
  const body = [{ type: 'RUN_STARTED', threadId: 't', runId: 'r' }, { type: 'RUN_ERROR', message }].map(e => `data: ${JSON.stringify(e)}\n\n`).join('');
  return new Response(body, { status: 200, headers: { 'content-type': 'text/event-stream' } });
}

/** Sends the opening question once, after the chat provider is ready. */
function AutoAsk({ question, onSent }: { question: string; onSent?: () => void }) {
  const process = useThread(s => s.processMessage);
  const gate = useLocationGate();
  const sent = useRef(false);
  const done = useRef(onSent);
  useEffect(() => { done.current = onSent; });
  useEffect(() => {
    if (sent.current || !question) return;
    const t = window.setTimeout(() => { if (sent.current) return; sent.current = true; gate(() => void process({ role: 'user', content: question })); done.current?.(); }, 60);
    return () => window.clearTimeout(t);
  }, [question, process]);
  return null;
}

function HeaderActions({ onExit, locate = true, history = false, showNew = true }: { onExit?: () => void; locate?: boolean; history?: boolean; showNew?: boolean }) {
  const location = useUserLocation();
  const newChat = useThreadList(s => s.switchToNewThread);
  const [open, setOpen] = useState(false);
  return <div className="pf-ag-header-actions">
    {locate && (location.position
      ? <span className="pf-ag-pill on"><LocateFixed size={13} />Near you</span>
      : <button type="button" className="pf-ag-pill" onClick={() => void location.request()} disabled={location.locating} title="Share your location so distance, ETA and the map work"><LocateFixed size={13} />{location.locating ? 'Locating…' : 'Use my location'}</button>)}
    {history && <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger asChild><button type="button" className="pf-ag-pill" data-testid="history-popover"><History size={13} />History</button></Popover.Trigger>
      <Popover.Portal><Popover.Content className="pf-hist-pop pf-agent" align="end" sideOffset={6}><HistoryList onPick={() => setOpen(false)} /></Popover.Content></Popover.Portal>
    </Popover.Root>}
    {showNew && <button type="button" className="pf-ag-pill" onClick={() => newChat()}><Plus size={13} />New chat</button>}
    {onExit && <button type="button" className="pf-ag-pill icon" onClick={onExit} aria-label="Close assistant"><X size={14} /></button>}
  </div>;
}

/** Live (realtime) voice button in the composer toolbar. */
function LiveVoice({ surface, merchantId }: { surface: Surface; merchantId?: string }) {
  return <RealtimeVoice surface={surface} merchantId={merchantId} buttonClassName="pf-composer-btn" />;
}

/** The empty-thread screen: greeting, composer and starters. */
function WelcomeBody({ title, description, starters, composer }: { title: string; description: string; starters: ConversationStarterProps[]; composer: ReactNode }) {
  const process = useThread(s => s.processMessage);
  const running = useThread(s => s.isRunning);
  const gate = useLocationGate();
  return <div className="pf-welcome">
    <span className="pf-ag-welcome-mark"><AgentAvatar size={88} /></span>
    <h2 className="openui-agent-welcome-screen__title">{title}</h2>
    <p className="openui-agent-welcome-screen__description">{description}</p>
    <div className="pf-welcome-composer">{composer}</div>
    <div className="pf-welcome-starters">{starters.map(st => <button key={st.displayText} type="button" disabled={running} onClick={() => gate(() => void process({ role: 'user', content: st.prompt }))}>{st.displayText}</button>)}</div>
  </div>;
}

const SIDEBAR_KEY = 'openui-agent-sidebar-open';

function AssistantSurfaceInner({ surface, merchantId, starters, title, description, initialQuestion, onSent, onExit, variant = 'page', voiceSlot, className = '', style }: {
  surface: Surface; merchantId?: string; starters: ConversationStarterProps[]; title: string; description: string;
  initialQuestion?: string; onSent?: () => void; onExit?: () => void; variant?: 'page' | 'embedded' | 'hero'; className?: string; style?: CSSProperties;
  /** Rendered in the composer toolbar next to the mic (e.g. a "Live voice" button). */
  voiceSlot?: ReactNode;
}) {
  const location = useUserLocation();
  const cart = useCart();
  // Before the first search, ask once per session for location so stores and routes are near the user.
  const [pendingAsk, setPendingAsk] = useState<(() => void) | null>(null);
  const shouldAsk = surface !== 'merchant';
  const gate = useCallbackGate(location.position, location.permission, shouldAsk, setPendingAsk);
  // Browser already allows location (e.g. after a reload): fetch it quietly so the first search is near the user.
  useEffect(() => { if (shouldAsk && location.permission === 'granted' && !location.position) void location.request(); }, [shouldAsk, location.permission]);
  const answer = async (share: boolean) => {
    const go = pendingAsk;
    if (!share) { setPendingAsk(null); markAsked(); go?.(); return; }
    const fresh = location.permission === 'denied' ? null : await location.request();
    if (!fresh) return;  // card stays open with the reason; "Not now" continues without location
    setPendingAsk(null); markAsked();
    // State has not re-rendered yet: put the new fix straight into the request context so this first message carries it.
    context.current = { ...context.current, location: { latitude: fresh.latitude, longitude: fresh.longitude, accuracy: fresh.accuracy } };
    go?.();
  };
  const context = useRef<Record<string, unknown>>({});
  context.current = {
    surface, ...(merchantId ? { merchant_id: merchantId } : {}), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ...(location.position ? { location: { latitude: location.position.latitude, longitude: location.position.longitude, accuracy: location.position.accuracy } } : {}),
    ...(cart.items.length ? { basket: cart.items.map(i => ({ product_id: i.product_id, quantity: i.quantity })) } : {}),
  };
  const llm = useMemo<ChatLLM>(() => ({
    streamProtocol: agUIAdapter(),
    send: ({ threadId, messages, signal }) => {
      const turns = messages.filter(m => m.role === 'user' || m.role === 'assistant').slice(-20)
        .map(m => {
          const images = m.role === 'user' ? imagesOf(m).slice(0, 3).map(data_url => ({ data_url })) : [];
          return { id: m.id, role: m.role, content: textOf(m).slice(0, 4000), ...(images.length ? { images } : {}) };
        }).filter(m => m.content || m.images);
      if (mockEnabled()) return mockAssistantResponse([...turns].reverse().find(t => t.role === 'user')?.content || '', merchantId);
      return apiFetch('/assistant/stream', { method: 'POST', signal, body: JSON.stringify({ threadId, runId: crypto.randomUUID(), state: {}, tools: [], context: [], forwardedProps: context.current, messages: turns }) })
        .then(r => r.ok && r.body ? r : failure(r.status), () => signal.aborted ? Promise.reject(new DOMException('Aborted', 'AbortError')) : failure(0));
    },
  }), [merchantId]);
  const storage = useMemo(() => serverStorage(surface === 'merchant' ? 'merchant' : 'shopper'), [surface]);
  if (variant === 'page') { try { localStorage.setItem(SIDEBAR_KEY, 'true'); } catch { /* preference is optional */ } }
  const name = surface === 'merchant' ? 'Store assistant' : 'PayFound';
  const composer = <>{pendingAsk && <LocationAsk onAnswer={answer} error={location.permission === 'denied' ? 'Location is blocked for this site. Click the icon left of the address bar, set Location to Allow, reload, then try again.' : location.error} busy={location.locating} />}<PfComposer placeholder={surface === 'merchant' ? 'Ask about your store…' : 'Ask for anything nearby…'} voiceSlot={voiceSlot ?? <LiveVoice surface={surface} merchantId={merchantId} />} /></>;
  const locate = surface !== 'merchant';
  const showHistory = variant !== 'page';
  return <div className={`pf-agent pf-agent-${variant} ${className}`} style={style} data-testid="assistant-surface">
    <LocationGateContext.Provider value={gate}><ToolLabelsProvider labels={labels}>
      <AgentInterface llm={llm} storage={storage} componentLibrary={payfoundLibrary} components={{ AssistantMessage: PfAssistantMessage, UserMessage: PfUserMessage }} agentName={name} starters={starters} starterVariant="short" scrollVariant="user-message-anchor" theme={{ mode: 'light', lightTheme: theme, cssSelector: '.pf-agent' }}>
        {variant === 'page' && <AgentInterface.Sidebar><HistoryList /></AgentInterface.Sidebar>}
        <AgentInterface.MobileHeader logo={<AgentAvatar size={30} />} agentName={variant === 'page' ? name : ''} actions={<HeaderActions onExit={onExit} locate={locate} history={showHistory} showNew={variant !== 'page'} />} {...(variant === 'page' ? {} : { menuButton: false as const, newChatButton: false as const })} />
        <AgentInterface.ThreadHeader showChatActions={false} showChatTitle={false} end={<HeaderActions onExit={onExit} locate={locate} history={showHistory} />} />
        <AgentInterface.Welcome><WelcomeBody title={title} description={description} starters={starters} composer={composer} /></AgentInterface.Welcome>
        <AgentInterface.Composer><div className="pf-composer-slot">{composer}</div></AgentInterface.Composer>
        {initialQuestion && <AutoAsk question={initialQuestion} onSent={onSent} />}
      </AgentInterface>
    </ToolLabelsProvider></LocationGateContext.Provider>
  </div>;
}

/**
 * Each surface and store gets its own chat state. The chat store lives inside AgentInterface, and React reuses the
 * same instance when two routes render this component in the same place, so the key forces a fresh conversation list.
 */
export function AssistantSurface(props: ComponentProps<typeof AssistantSurfaceInner>) {
  return <AssistantSurfaceInner key={`${props.surface}:${props.merchantId ?? ''}`} {...props} />;
}

// In memory only: a stale session flag must never silently suppress the question. Asked at most once per page load.
let askedThisLoad = false;
function markAsked(): void { askedThisLoad = true; }

/** Builds the send gate: runs immediately if location is known, refused or unavailable; fetches silently if the browser already allows it; otherwise asks. */
function useCallbackGate(position: unknown, permission: string, enabled: boolean, setPending: (go: (() => void) | null) => void) {
  return useCallback((go: () => void) => {
    if (!enabled || position || permission === 'unavailable' || askedThisLoad) { go(); return; }
    setPending(() => go);
  }, [enabled, position, permission, setPending]);
}

/** Inline question shown above the composer before the first search. */
function LocationAsk({ onAnswer, error, busy }: { onAnswer: (share: boolean) => void; error?: string; busy?: boolean }) {
  return <div role="group" aria-label="Share your location" className="mx-auto mb-2 w-full max-w-[560px] rounded-[var(--pf-r-lg)] border border-line bg-surface p-4 text-center shadow-[var(--pf-shadow-card-hover)]" data-testid="location-ask">
    <p className="text-[14px] font-semibold">Share your location?</p>
    <p className="mt-1 text-[13px] text-muted">So I can find stores near you, show distances and the driving time. Your location stays in this session.</p>
    {error && <p role="alert" className="mt-2 text-[12px] text-[#b42318]">{error}</p>}
    <div className="mt-3 flex flex-wrap justify-center gap-2">
      <button type="button" className="pf-btn sm" onClick={() => onAnswer(true)} disabled={busy} data-testid="location-share"><LocateFixed size={14} />{busy ? 'Locating…' : 'Share my location'}</button>
      <button type="button" className="pf-btn sm outline" onClick={() => onAnswer(false)} data-testid="location-skip">Not now</button>
    </div>
  </div>;
}
