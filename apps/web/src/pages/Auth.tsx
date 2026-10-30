import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { Brand } from '../components/Brand';
import { supabase, messageOf } from '../lib/api';
import { useApp } from '../lib/app-context';
import { ErrorLine, Field, Notice, Spinner } from '../components/Shared';
import { safeNext } from '../lib/navigation';
import { AccountMenu } from '../App';  // used only at render time, so the import cycle with App is harmless

export { safeNext };

function AuthShell({ children }: { children: ReactNode }) {
  const { demo } = useApp();
  return <div className="relative min-h-screen grid lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)]">
    {demo && <div className="absolute top-4 right-[var(--pf-gutter)] z-10" data-testid="auth-role-switcher"><AccountMenu /></div>}
    <aside className="hidden lg:flex flex-col justify-between bg-ink text-white p-12 xl:p-16">
      <Link to="/" aria-label="PayFound home" className="inline-flex min-h-11 items-center"><Brand inverted /></Link>
      <div><p className="pf-display-xl !text-[clamp(44px,5vw,84px)]">Find it nearby.<br />Pick it up today.</p><p className="mt-6 text-white/70 text-base max-w-md leading-relaxed">Reserve from local stores, pay securely and collect when it is ready. One account for shoppers and merchants.</p></div>
      <p className="text-sm text-white/50">PayFound development pilot</p>
    </aside>
    <main className="flex flex-col px-[var(--pf-gutter)] py-8"><Link to="/" className="lg:hidden mb-10 inline-flex min-h-11 items-center self-start" aria-label="PayFound home"><Brand /></Link><div className="flex-1 flex items-center justify-center"><div className="w-full max-w-[400px] py-6">{children}</div></div></main>
  </div>;
}
export function AuthPage({ mode }: { mode: 'login' | 'signup' | 'forgot' | 'reset' }) {
  const { demo, session, refreshMe, logout } = useApp();
  const [params] = useSearchParams();
  const next = safeNext(params.get('next'));
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [demoNotice, setDemoNotice] = useState(false);
  useEffect(() => { setError(''); setInfo(''); setPassword(''); setConfirm(''); setDemoNotice(false); }, [mode]);
  const titles = { login: 'Welcome back', signup: 'Create your PayFound account', forgot: 'Reset your password', reset: 'Choose a new password' };
  if (session && (mode === 'login' || mode === 'signup')) return <Navigate to={next} replace />;
  const submit = async (event: FormEvent) => {
    event.preventDefault(); if (busy) return;
    setError(''); setInfo('');
    if (demo) return setDemoNotice(true);  // mock form: nothing is sent and no account is created
    if (!supabase) return setError('Account sign-in is not configured. Contact the pilot operator.');
    if ((mode === 'reset' || mode === 'signup') && password !== confirm) return setError('Passwords must match.');
    setBusy(true);
    try {
      const callback = `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`;
      if (mode === 'login') {
        const { error: issue } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
        if (issue) throw issue;
        await refreshMe(); navigate(next, { replace: true });
      } else if (mode === 'signup') {
        const { data, error: issue } = await supabase.auth.signUp({ email: email.trim(), password, options: { emailRedirectTo: callback } });
        if (issue) throw issue;
        if (data.session) { await refreshMe(); navigate(next, { replace: true }); }
        else setInfo('Check your email to confirm your account. Open the link in this browser, then return to PayFound.');
      } else if (mode === 'forgot') {
        const { error: issue } = await supabase.auth.resetPasswordForEmail(email.trim(), { redirectTo: `${window.location.origin}/auth/callback?recovery=1` });
        if (issue) throw issue;
        setInfo('If an account exists for this email, a reset link is on its way. Check your inbox.');
      } else {
        if (!session) throw new Error('Open the password reset link from your email first.');
        const { error: issue } = await supabase.auth.updateUser({ password });
        if (issue) throw issue;
        await logout(); navigate('/login?reset=success', { replace: true });
      }
    } catch (e) { setError(messageOf(e)); } finally { setBusy(false); }
  };
  return <AuthShell><h1 className="pf-heading">{titles[mode]}</h1><p className="text-sm text-muted mt-3">{mode === 'login' ? 'Sign in to reserve items and track your orders.' : mode === 'signup' ? 'One account to discover local products and manage your business.' : mode === 'forgot' ? 'Enter your email and we will send a reset link.' : 'Use at least 8 characters.'}</p>
    <div className="space-y-3 mt-6 empty:hidden">{demo && <Notice>This is a demo, so there are no real accounts. Anything you enter here is ignored.</Notice>}{demoNotice && <div data-testid="demo-auth-notice"><Notice tone="amber"><strong>Nothing was signed in or created.</strong> To explore PayFound, open the account menu at the <strong>top right</strong> (shown as &ldquo;Demo shopper&rdquo;) and switch between Shopper, Merchant and Administrator. <Link className="pf-link" to="/">Start exploring</Link></Notice></div>}{params.get('reset') === 'success' && <Notice tone="green">Password updated. Sign in with your new password.</Notice>}{info && <Notice>{info}</Notice>}{error && <ErrorLine message={error} />}</div>
    <form className="space-y-4 mt-6" onSubmit={submit} aria-label={titles[mode]} noValidate={demo}>
      {mode !== 'reset' && <Field label="Email address" type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} required maxLength={254} data-testid="auth-email" />}
      {mode !== 'forgot' && <Field label={mode === 'reset' ? 'New password' : 'Password'} type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={mode === 'login' ? 1 : 8} maxLength={128} value={password} onChange={e => setPassword(e.target.value)} required hint={mode !== 'login' ? 'Use at least 8 characters.' : undefined} data-testid="auth-password" />}
      {(mode === 'signup' || mode === 'reset') && <Field label="Confirm password" type="password" autoComplete="new-password" value={confirm} onChange={e => setConfirm(e.target.value)} required minLength={8} />}
      <button className="pf-btn lg w-full" data-testid="auth-submit" disabled={busy || (!demo && !supabase) || (!demo && mode === 'reset' && !session)}>{busy ? 'Please wait…' : { login: 'Sign in', signup: 'Create account', forgot: 'Send reset link', reset: 'Update password' }[mode]}</button>
    </form>
    <div className="text-sm mt-6 flex flex-wrap gap-x-5 gap-y-2">{mode === 'login' ? <><Link className="pf-link" to={`/signup?next=${encodeURIComponent(next)}`}>Create account</Link><Link className="pf-link" to="/forgot-password">Forgot password?</Link></> : <Link className="pf-link" to={`/login?next=${encodeURIComponent(next)}`}>Back to sign in</Link>}</div>
    <p className="text-xs text-muted mt-10 leading-relaxed">Business access comes from your verified server membership. Register a store after sign-in.</p>
  </AuthShell>;
}

// PKCE code exchange is performed once by the configured Supabase client during
// initialization. getSession waits for that initialization; no duplicate exchange.
export function AuthCallback() {
  const { session, recovery } = useApp();
  const [params] = useSearchParams();
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);
  useEffect(() => {
    let alive = true;
    (async () => {
      const hash = new URLSearchParams(window.location.hash.slice(1));
      const issue = params.get('error_description') || hash.get('error_description');
      if (issue) { setError(issue); return; }
      if (!supabase) { setError('Sign-in is not configured.'); return; }
      const { data, error: authError } = await supabase.auth.getSession();
      if (!alive) return;
      if (authError) setError(authError.message);
      else if (!data.session) setError('This email link has expired or was opened in a different browser. Request a new link.');
      else setDone(true);
    })();
    return () => { alive = false; };
  }, [params]);
  if (error) return <AuthShell><h1 className="pf-heading mb-6">Link problem</h1><ErrorLine message={error} /><div className="flex gap-3 mt-6"><Link className="pf-btn" to="/forgot-password">Request reset link</Link><Link className="pf-btn outline" to="/login">Sign in</Link></div></AuthShell>;
  if (done && session) return <Navigate to={recovery || params.get('recovery') === '1' ? '/reset-password' : safeNext(params.get('next'))} replace />;
  return <AuthShell><Spinner label="Confirming your email link…" /></AuthShell>;
}
