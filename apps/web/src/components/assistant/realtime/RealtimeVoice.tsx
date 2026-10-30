import { useCallback, useEffect, useRef, useState } from 'react';
import { AudioLines, Mic, MicOff, PhoneOff, X } from 'lucide-react';
import { useUserLocation } from '../../../lib/location';
import { useRealtimeVoice, type VoiceState } from './useRealtimeVoice';

const STATUS: Record<VoiceState, string> = {
  idle: '', connecting: 'Connecting', listening: 'Listening', user_speaking: 'Listening', thinking: 'Thinking', assistant_speaking: 'Speaking', error: 'Couldn’t connect',
};

/** Voice calls are capped at 2 minutes (the server secret expires on the same limit). */
export const MAX_CALL_SECONDS = 120;

export type RealtimeVoiceProps = {
  surface: 'shopper' | 'merchant';
  merchantId?: string;
  buttonClassName?: string;
  buttonLabel?: string;
};

/**
 * "Live voice" button. Opens a full-screen conversation like a voice assistant: starts listening
 * immediately with natural turn-taking, one orb shows the state, and only mute and end are offered.
 * Mic and peer connection are closed on End, Escape, close, unmount and page hide.
 */
export function RealtimeVoice({ surface, merchantId, buttonClassName = 'pf-btn soft sm', buttonLabel = 'Live voice' }: RealtimeVoiceProps) {
  const location = useUserLocation();
  const [open, setOpen] = useState(false);
  const ctxRef = useRef<Record<string, unknown>>({});
  ctxRef.current = {
    surface, ...(merchantId ? { merchant_id: merchantId } : {}), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ...(location.position ? { location: { latitude: location.position.latitude, longitude: location.position.longitude, accuracy: location.position.accuracy } } : {}),
  };
  const getContext = useCallback(() => ctxRef.current, []);
  const voice = useRealtimeVoice(getContext);
  const { state, stop, start } = voice;
  const closeBtn = useRef<HTMLButtonElement>(null);
  const [secondsLeft, setSecondsLeft] = useState(MAX_CALL_SECONDS);
  const [timedOut, setTimedOut] = useState(false);

  const close = useCallback(() => { stop(); setOpen(false); }, [stop]);
  // Opening the conversation starts it right away, with natural turn-taking (no settings to choose).
  useEffect(() => { if (open) { closeBtn.current?.focus(); setSecondsLeft(MAX_CALL_SECONDS); setTimedOut(false); void start('semantic'); } }, [open, start]);
  // Hard 2-minute cap: a one-second countdown that ends the call and closes the microphone.
  useEffect(() => {
    if (!open) return;
    const timer = window.setInterval(() => {
      setSecondsLeft(left => {
        if (left <= 1) { window.clearInterval(timer); stop(); setTimedOut(true); setOpen(false); return 0; }
        return left - 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [open, stop]);
  useEffect(() => { if (!open) return; const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') close(); }; window.addEventListener('keydown', onKey); return () => window.removeEventListener('keydown', onKey); }, [open, close]);

  const speaking = state === 'assistant_speaking';
  const hearing = state === 'user_speaking';
  const busy = state === 'connecting' || state === 'thinking';
  const lastLine = voice.lines[voice.lines.length - 1];
  // One orb: a soft blue halo while you talk, ink while it answers, gentle breathing otherwise.
  const orbScale = hearing ? 1.12 : speaking ? 1.06 : 1;
  const orbColor = hearing ? 'var(--pf-blue)' : speaking ? 'var(--pf-ink)' : 'var(--pf-sky)';

  return <>
    {timedOut && !open && <p role="status" className="sr-only">Voice call ended after 2 minutes.</p>}
    <button type="button" className={buttonClassName} onClick={() => setOpen(true)} aria-label="Start live voice conversation" data-testid="voice-open"><AudioLines size={14} aria-hidden />{buttonLabel}</button>
    {open && <div role="dialog" aria-modal="true" aria-label="Live voice" data-testid="voice-panel" className="fixed inset-0 z-[80] flex flex-col items-center justify-between bg-surface text-ink px-6 py-5">
      <div className="flex w-full items-center justify-between">
        <span className="text-sm font-semibold text-muted">PayFound Live</span>
        <span className="text-sm tabular-nums text-muted" aria-live="off" data-testid="voice-timer">{Math.floor(secondsLeft / 60)}:{String(secondsLeft % 60).padStart(2, '0')} left</span>
        <button ref={closeBtn} type="button" className="pf-btn ghost icon" onClick={close} aria-label="Close live voice"><X size={18} aria-hidden /></button>
      </div>

      <div className="flex flex-col items-center gap-6">
        <div aria-hidden className="relative grid size-56 place-items-center">
          <span className="absolute inset-0 rounded-full opacity-30 blur-2xl transition-colors duration-500" style={{ background: orbColor }} />
          <span className={`relative size-40 rounded-full transition-transform duration-300 ease-out motion-reduce:transition-none ${busy || state === 'listening' ? 'motion-safe:animate-pulse' : ''}`}
            style={{ transform: `scale(${orbScale})`, background: `radial-gradient(circle at 32% 28%, #ffffff 0%, ${orbColor} 58%, ${orbColor} 100%)`, boxShadow: `0 20px 60px -20px ${orbColor}` }} />
        </div>
        <p role="status" aria-live="polite" className="font-display text-2xl" data-testid="voice-state" data-state={state}>{STATUS[state]}</p>
        <p className="min-h-5 max-w-md px-4 text-center text-sm text-muted" aria-live="polite">{voice.activity ?? (lastLine ? lastLine.text : '')}</p>
        {voice.error && <div className="flex flex-col items-center gap-3"><p role="alert" className="pf-alert red max-w-md text-sm">{voice.error}</p><button type="button" className="pf-btn accent" onClick={() => void start('semantic')}>Try again</button></div>}
      </div>

      <div className="flex w-full flex-col items-center gap-3">
        <div className="flex items-start justify-center gap-10">
          <div className="flex flex-col items-center gap-2">
            <button type="button" className={`grid size-16 place-items-center rounded-full transition-colors ${voice.muted ? 'bg-ink text-white' : 'bg-sunk text-ink hover:bg-line'}`} aria-pressed={voice.muted} onClick={() => voice.setMuted(!voice.muted)} aria-label={voice.muted ? 'Unmute microphone' : 'Mute microphone'}>{voice.muted ? <MicOff size={24} aria-hidden /> : <Mic size={24} aria-hidden />}</button>
            <span className="text-xs font-medium text-muted" aria-hidden>{voice.muted ? 'Unmute' : 'Mute'}</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <button type="button" className="grid size-16 place-items-center rounded-full bg-bad text-white shadow-[0_8px_24px_-8px_rgb(195_37_45/0.6)] transition-transform active:scale-95" onClick={close} aria-label="End voice conversation and close the microphone" data-testid="voice-stop"><PhoneOff size={24} aria-hidden /></button>
            <span className="text-xs font-medium text-muted" aria-hidden>End</span>
          </div>
        </div>
        <p className="text-center text-xs text-muted">Answers use live catalogue data. Voice never makes payments.</p>
      </div>
    </div>}
  </>;
}
