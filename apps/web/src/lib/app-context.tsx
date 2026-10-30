import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import type { Session } from '@supabase/supabase-js';
import { api, configureSupabase, isLocalDemo, messageOf, setRole, setDemoRole, setToken, supabase, type Config, type Identity, type Role } from './api';

type AppState = {
  config: Config | null; session: Session | null; me: Identity | null; role: Role;
  ready: boolean; authReady: boolean; error: string; demo: boolean; recovery: boolean;
  merchantId: string; setMerchantId: (id: string) => void; changeRole: (role: Role) => void;
  refreshMe: () => Promise<Identity | null>; retry: () => void; logout: () => Promise<void>;
};
const Context = createContext<AppState | null>(null);
export function useApp() {
  const value = useContext(Context);
  if (!value) throw new Error('AppProvider is required');
  return value;
}

const DEMO_ROLE_KEY = 'pf.demoRole';
const ROLES: Role[] = ['consumer', 'merchant', 'admin'];
/** The demo role survives refreshes, so /merchant/* does not fall back to shopper on reload. */
function rememberDemoRole(value: Role) { try { localStorage.setItem(DEMO_ROLE_KEY, value); } catch { /* storage may be blocked */ } }
function storedDemoRole(): Role {
  try { const value = localStorage.getItem(DEMO_ROLE_KEY) as Role | null; return value && ROLES.includes(value) ? value : 'consumer'; } catch { return 'consumer'; }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<Config | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [me, setMe] = useState<Identity | null>(null);
  const [role, setLocalRole] = useState<Role>('consumer');
  const [merchantId, setMerchantId] = useState('');
  const [authReady, setAuthReady] = useState(false);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [recovery, setRecovery] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const version = useRef(0);
  const demo = isLocalDemo(config);

  const refreshMe = useCallback(async () => {
    const current = ++version.current;
    const value = await api<Identity>('/me');
    if (current === version.current) {
      setMe(value); setRole(value.role); setLocalRole(value.role);
      setMerchantId(id => value.merchant_ids.includes(id) ? id : value.memberships[0]?.merchant_id || value.merchant_ids[0] || '');
    }
    return value;
  }, []);

  useEffect(() => {
    let alive = true;
    let unsubscribe: (() => void) | undefined;
    setError(''); setReady(false); setAuthReady(false);
    (async () => {
      try {
        const value = await api<Config>('/config');
        if (isLocalDemo(value)) { const saved = storedDemoRole(); setDemoRole(saved); setLocalRole(saved); }
        const client = await configureSupabase(value);
        if (!alive) return;
        setConfig(value);
        if (client) {
          const { data } = client.auth.onAuthStateChange((event, next) => {
            if (!alive) return;
            setToken(next?.access_token || null); setSession(next);
            if (event === 'PASSWORD_RECOVERY') setRecovery(true);
            if (event === 'SIGNED_OUT') { version.current++; setMe(null); setRole('consumer'); setLocalRole('consumer'); setMerchantId(''); }
          });
          unsubscribe = () => data.subscription.unsubscribe();
          const { data: auth, error: authError } = await client.auth.getSession();
          if (authError) throw authError;
          if (!alive) return;
          setToken(auth.session?.access_token || null); setSession(auth.session);
        }
        if (alive) setAuthReady(true);
      } catch (e) { if (alive) setError(messageOf(e)); }
    })();
    return () => { alive = false; unsubscribe?.(); };
  }, [attempt]);

  const subject = session?.user.id;
  useEffect(() => {
    if (!authReady) return;
    let alive = true;
    setReady(false);
    if (!subject && !demo) { setMe(null); setReady(true); return; }
    refreshMe().then(() => { if (alive) { setError(''); setReady(true); } }).catch(e => { if (alive) setError(messageOf(e)); });
    return () => { alive = false; version.current++; };
  }, [authReady, subject, demo, refreshMe, attempt]);

  const changeRole = (next: Role) => {
    if (!demo) return;
    rememberDemoRole(next);
    setDemoRole(next); setLocalRole(next); setReady(false);
    refreshMe().then(() => setReady(true)).catch(e => setError(messageOf(e)));
  };
  const logout = async () => {
    if (supabase) { const { error: signOutError } = await supabase.auth.signOut(); if (signOutError) throw signOutError; }
    version.current++; setToken(null); setSession(null); setMe(null); setRole('consumer'); setLocalRole('consumer'); setRecovery(false); setMerchantId('');
  };
  return <Context.Provider value={{ config, session, me, role, ready, authReady, error, demo, recovery, merchantId, setMerchantId, changeRole, refreshMe, retry: () => { setError(''); setAttempt(v => v + 1); }, logout }}>{children}</Context.Provider>;
}
