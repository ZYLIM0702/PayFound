import { useEffect, useRef, useState } from 'react';
import { Check, Copy } from 'lucide-react';

export async function copyText(text: string): Promise<boolean> {
  try { await navigator.clipboard.writeText(text); return true; } catch { /* fall through to the legacy path */ }
  try {
    const area = document.createElement('textarea');
    area.value = text; area.setAttribute('readonly', ''); area.style.cssText = 'position:fixed;opacity:0;top:0';
    document.body.appendChild(area); area.select();
    const ok = document.execCommand('copy'); area.remove(); return ok;
  } catch { return false; }
}

/** Copies on click and confirms with "Copied". `getText` is read at click time so it can pull rendered text. */
export function CopyButton({ getText, label = 'Copy', className = '' }: { getText: () => string; label?: string; className?: string }) {
  const [state, setState] = useState<'idle' | 'done' | 'failed'>('idle');
  const timer = useRef<number>(0);
  useEffect(() => () => window.clearTimeout(timer.current), []);
  const click = async () => {
    const ok = await copyText(getText());
    setState(ok ? 'done' : 'failed');
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setState('idle'), 1800);
  };
  return <button type="button" className={`pf-copy ${state === 'done' ? 'done' : ''} ${className}`} onClick={() => void click()} aria-label={label} data-testid="copy-message">
    {state === 'done' ? <Check size={13} /> : <Copy size={13} />}
    <span role="status">{state === 'done' ? 'Copied' : state === 'failed' ? 'Copy failed' : ''}</span>
  </button>;
}
