import { useCallback, useEffect, useRef, useState } from 'react';
import { apiFetch } from '../../../lib/api';
import { toolLabels } from '../data';

export type VoiceState = 'idle' | 'connecting' | 'listening' | 'user_speaking' | 'thinking' | 'assistant_speaking' | 'error';
export type VadMode = 'server' | 'semantic';
export type VoiceLine = { id: string; role: 'user' | 'assistant'; text: string };

const CALLS_URL = 'https://api.openai.com/v1/realtime/calls';
const uid = () => (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2));

type RtEvent = { type: string; [k: string]: unknown };
type OutputItem = { type?: string; name?: string; arguments?: string; call_id?: string };

/** WebRTC session to OpenAI Realtime with an ephemeral secret minted by our API. Tools run server-side through /assistant/realtime/tool. */
export function useRealtimeVoice(getContext: () => Record<string, unknown>) {
  const [state, setState] = useState<VoiceState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [lines, setLines] = useState<VoiceLine[]>([]);
  const [activity, setActivity] = useState<string | null>(null);
  const [muted, setMutedState] = useState(false);
  const pc = useRef<RTCPeerConnection | null>(null);
  const dc = useRef<RTCDataChannel | null>(null);
  const stream = useRef<MediaStream | null>(null);
  const audio = useRef<HTMLAudioElement | null>(null);
  const speaking = useRef(false);
  const seen = useRef(new Set<string>());
  const live = useRef(false);

  const send = useCallback((event: RtEvent) => { if (dc.current?.readyState === 'open') dc.current.send(JSON.stringify(event)); }, []);

  const stop = useCallback(() => {
    live.current = false;
    try { dc.current?.close(); } catch { /* already closed */ }
    try { pc.current?.getSenders().forEach(s => s.track?.stop()); pc.current?.close(); } catch { /* already closed */ }
    stream.current?.getTracks().forEach(t => t.stop());
    if (audio.current) { audio.current.pause(); audio.current.srcObject = null; audio.current.remove(); }
    dc.current = null; pc.current = null; stream.current = null; audio.current = null;
    speaking.current = false; seen.current.clear();
    setActivity(null); setMutedState(false);
    setState(s => (s === 'error' ? s : 'idle'));
  }, []);

  useEffect(() => { const off = () => stop(); window.addEventListener('pagehide', off); return () => { window.removeEventListener('pagehide', off); stop(); }; }, [stop]);

  const addLine = (role: VoiceLine['role'], text: string) => { const t = text.trim(); if (t) setLines(prev => [...prev, { id: uid(), role, text: t }].slice(-60)); };

  const runTool = useCallback(async (item: OutputItem) => {
    const name = item.name || '';
    setActivity(`${(toolLabels[name]?.[0] ?? 'Looking that up')}…`);
    let output: string;
    try {
      const r = await apiFetch('/assistant/realtime/tool', { method: 'POST', body: JSON.stringify({ name, arguments: item.arguments || '{}', forwardedProps: getContext() }) });
      output = r.ok ? ((await r.json()) as { output: string }).output : JSON.stringify({ error: 'tool_unavailable', message: 'That lookup is not available right now.' });
    } catch { output = JSON.stringify({ error: 'tool_failed', message: 'That lookup failed.' }); }
    send({ type: 'conversation.item.create', item: { type: 'function_call_output', call_id: item.call_id, output } });
  }, [getContext, send]);

  const onEvent = useCallback((e: RtEvent) => {
    switch (e.type) {
      case 'input_audio_buffer.speech_started':
        if (speaking.current) { send({ type: 'response.cancel' }); send({ type: 'output_audio_buffer.clear' }); speaking.current = false; }
        setState('user_speaking'); break;
      case 'input_audio_buffer.speech_stopped': setState('thinking'); break;
      case 'conversation.item.input_audio_transcription.completed': addLine('user', String(e.transcript ?? '')); break;
      case 'response.created': setState(s => (s === 'user_speaking' ? s : 'thinking')); break;
      case 'output_audio_buffer.started': speaking.current = true; setActivity(null); setState('assistant_speaking'); break;
      case 'output_audio_buffer.stopped': case 'output_audio_buffer.cleared': speaking.current = false; setState(s => (s === 'assistant_speaking' ? 'listening' : s)); break;
      case 'response.output_audio_transcript.done': addLine('assistant', String(e.transcript ?? '')); break;
      case 'response.done': {
        const items = ((e.response as { output?: OutputItem[] } | undefined)?.output ?? []).filter(i => i.type === 'function_call' && i.call_id && !seen.current.has(i.call_id));
        if (items.length) {
          items.forEach(i => seen.current.add(i.call_id as string));
          void Promise.all(items.map(runTool)).then(() => { if (live.current) { send({ type: 'response.create' }); setActivity(null); } });
        } else if (!speaking.current) setState(s => (s === 'thinking' ? 'listening' : s));
        break;
      }
      case 'error': {
        const code = (e.error as { code?: string } | undefined)?.code;
        if (code === 'response_cancel_not_active') break;
        setError('Voice hit a problem. You can keep talking or end the session and start again.'); break;
      }
      default: break;
    }
  }, [runTool, send]);

  const start = useCallback(async (vad: VadMode) => {
    if (live.current) return;
    live.current = true; setError(null); setLines([]); setState('connecting');
    try {
      if (!navigator.mediaDevices?.getUserMedia || typeof RTCPeerConnection === 'undefined') throw new Error('unsupported');
      const mic = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
      if (!live.current) { mic.getTracks().forEach(t => t.stop()); return; }
      stream.current = mic;
      const res = await apiFetch('/assistant/realtime/session', { method: 'POST', body: JSON.stringify({ vad, forwardedProps: getContext() }) });
      if (!res.ok) throw new Error(res.status === 429 ? 'rate' : res.status === 503 ? 'config' : 'mint');
      const { client_secret: secret } = (await res.json()) as { client_secret: string };
      const peer = new RTCPeerConnection();
      pc.current = peer;
      const el = document.createElement('audio'); el.autoplay = true; document.body.appendChild(el); audio.current = el;
      peer.ontrack = ev => { el.srcObject = ev.streams[0]; };
      mic.getTracks().forEach(t => peer.addTrack(t, mic));
      const channel = peer.createDataChannel('oai-events'); dc.current = channel;
      channel.onopen = () => {
        if (!live.current) return;
        setState('listening');
        // Open the call with a greeting so the user knows they can speak now.
        send({ type: 'response.create', response: { instructions: 'Greet the user in one short sentence and ask what you can help them with today.' } } as RtEvent);
      };
      channel.onmessage = m => { try { onEvent(JSON.parse(m.data as string) as RtEvent); } catch { /* ignore malformed */ } };
      peer.onconnectionstatechange = () => { if (live.current && (peer.connectionState === 'failed' || peer.connectionState === 'disconnected')) { setError('The voice connection dropped.'); setState('error'); stop(); } };
      const offer = await peer.createOffer(); await peer.setLocalDescription(offer);
      const sdp = await fetch(CALLS_URL, { method: 'POST', body: offer.sdp, headers: { Authorization: `Bearer ${secret}`, 'Content-Type': 'application/sdp' } });
      if (!sdp.ok) throw new Error('sdp');
      await peer.setRemoteDescription({ type: 'answer', sdp: await sdp.text() });
    } catch (err) {
      const code = err instanceof Error ? err.message : '';
      const denied = err instanceof DOMException && (err.name === 'NotAllowedError' || err.name === 'NotFoundError');
      setError(denied ? 'Microphone access was blocked. Allow the microphone in your browser and try again.'
        : code === 'unsupported' ? 'This browser does not support live voice.'
          : code === 'rate' ? 'You are asking quickly. Wait a few seconds and try again.'
            : code === 'config' ? 'Voice is not set up on this server yet.'
              : 'Voice is unavailable right now. Please try again in a moment.');
      stop(); setState('error');
    }
  }, [getContext, onEvent, stop]);

  const setMuted = useCallback((value: boolean) => { stream.current?.getAudioTracks().forEach(t => { t.enabled = !value; }); setMutedState(value); }, []);

  return { state, error, lines, activity, muted, start, stop, setMuted, clearLines: () => setLines([]) };
}
