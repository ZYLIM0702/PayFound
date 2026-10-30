import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { Brand } from './Brand';
import { ErrorLine, Field, Spinner } from './Shared';
import { ApiError, accessStatus, messageOf, onAccessLost, unlockAccess } from '../lib/api';

/**
 * Optional access key in front of the whole app (SITE_ACCESS_KEY on the API). Nothing below it renders, or calls the
 * API, until the key is accepted. Without the setting the API reports it isn't required and the app opens directly.
 */
export function AccessGate({ children }: { children: ReactNode }) {
  const [state, setState] = useState<'checking' | 'locked' | 'open'>('checking');
  const [key, setKey] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let alive = true;
    // If the API can't be reached the app shows its own errors; a locked API still answers 401 and relocks below.
    accessStatus().then(s => { if (alive) setState(!s.required || s.ok ? 'open' : 'locked'); }).catch(() => { if (alive) setState('open'); });
    const off = onAccessLost(() => { setError('The access key has changed. Enter the new key.'); setState('locked'); });
    return () => { alive = false; off(); };
  }, []);
  if (state === 'checking') return <Spinner label="Loading…" />;
  if (state === 'open') return <>{children}</>;
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy || !key.trim()) return;
    setBusy(true); setError('');
    try { await unlockAccess(key.trim()); setKey(''); setState('open'); }
    catch (e) { setError(e instanceof ApiError && e.status === 401 ? 'That access key isn’t right. Check it and try again.' : messageOf(e)); }
    finally { setBusy(false); }
  };
  return <div className="relative min-h-screen grid lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)]">
    <aside className="hidden lg:flex flex-col justify-between bg-ink text-white p-12 xl:p-16">
      <Brand inverted />
      <div><p className="pf-display-xl !text-[clamp(44px,5vw,84px)]">Find it nearby.<br />Pay directly.<br />Get it today.</p><p className="mt-6 text-white/70 text-base max-w-md leading-relaxed">This PayFound preview is private, so live AI, maps and payment sandboxes are only used by invited reviewers.</p></div>
      <p className="text-sm text-white/50">PayFound private preview</p>
    </aside>
    <main className="flex flex-col px-[var(--pf-gutter)] py-8">
      <div className="lg:hidden mb-10 inline-flex min-h-11 items-center self-start"><Brand /></div>
      <div className="flex-1 flex items-center justify-center"><div className="w-full max-w-[400px] py-6">
        <h1 className="pf-heading">Enter the access key</h1>
        <p className="text-sm text-muted mt-3">PayFound is in a private preview. Enter the key you were given to continue.</p>
        {error && <div className="mt-6"><ErrorLine message={error} /></div>}
        <form className="space-y-4 mt-6" onSubmit={submit} aria-label="Enter the access key">
          <Field label="Access key" type="password" autoComplete="off" autoFocus value={key} onChange={e => setKey(e.target.value)} required maxLength={256} data-testid="access-key" />
          <button className="pf-btn lg w-full" disabled={busy || !key.trim()} data-testid="access-submit">{busy ? 'Checking…' : 'Continue'}</button>
        </form>
      </div></div>
    </main>
  </div>;
}
