import { useEffect, useState } from 'react';
import { LogOut } from 'lucide-react';
import { messageOf, put } from '../../lib/api';
import { useApp } from '../../lib/app-context';
import { useUserLocation } from '../../lib/location';
import { useResource } from '../../lib/use-resource';
import { Chip, Spinner } from '../../components/Shared';
import { Pane, PaneHeader, Quiet, Scroll, type Address, type Profile } from './shared';

const NOTIFY: [string, string, string][] = [['order_updates', 'Order updates', 'Ready for pickup, cancellations and refunds.'], ['price_drops', 'Wishlist alerts', 'Price drops and restocks.'], ['promotions', 'Offers and coupons', 'Occasional deals from nearby stores.']];
const PREFS_KEY = 'pf.prefs.v1';
type Prefs = { language: string; currency: string };
function loadPrefs(): Prefs {
  try { const raw = JSON.parse(localStorage.getItem(PREFS_KEY) || 'null'); if (raw && typeof raw.language === 'string' && typeof raw.currency === 'string') return raw; } catch { /* storage unavailable */ }
  return { language: 'en', currency: 'store' };
}
function savePrefs(value: Prefs) { try { localStorage.setItem(PREFS_KEY, JSON.stringify(value)); } catch { /* optional convenience */ } }

function LocationCard() {
  const loc = useUserLocation();
  const shared = Boolean(loc.position);
  const status = shared ? 'Sharing precise location' : loc.permission === 'denied' ? 'Blocked in your browser' : loc.permission === 'unavailable' ? 'Not available on this device' : 'Not shared';
  return <section className="pf-card p-4 space-y-3" aria-label="Location"><div className="flex items-start justify-between gap-3"><div><h3 className="text-sm font-semibold">Location</h3><p className="text-[12.5px] text-muted">Used only to order nearby stores.</p></div><Chip kind={shared ? 'green' : 'default'} dot={shared}>{status}</Chip></div>
    <p className="text-[13px]">Showing stores around <strong className="font-semibold">{loc.anchor.label}</strong> <span className="text-muted">({loc.anchor.source === 'precise' ? 'your shared position' : loc.anchor.source === 'ip' ? 'approximate city from your IP address' : loc.anchor.source === 'saved' ? 'your last position' : 'your time zone'})</span>.</p>
    <div className="flex flex-wrap gap-2">
      {shared ? <button className="pf-btn sm outline" onClick={loc.clear}>Stop using location</button> : <button className="pf-btn sm outline" disabled={loc.locating || loc.permission === 'denied' || loc.permission === 'unavailable'} onClick={() => void loc.request()}>{loc.locating ? 'Locating…' : 'Share my location'}</button>}
    </div>
    <Quiet>{shared ? 'Stopping falls back to an approximate city from your IP address (Use IP city instead), which is less precise. ' : 'Without a shared position PayFound uses an approximate city from your IP address or time zone. '}{loc.permission === 'denied' ? 'To share again, allow location for this site in your browser settings.' : ''}</Quiet>
    {loc.error && <p className="text-[13px] text-bad" role="alert">{loc.error}</p>}</section>;
}

export function SettingsPanel({ onError, onInfo }: { onError: (m: string) => void; onInfo: (m: string) => void }) {
  const res = useResource<Profile>('/me/profile');
  const { logout, me, demo } = useApp();
  const [draft, setDraft] = useState<Profile | null>(null);
  const [prefs, setPrefs] = useState<Prefs>(loadPrefs);
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (res.data) setDraft(res.data); }, [res.data]);
  const setPref = (patch: Partial<Prefs>) => { const next = { ...prefs, ...patch }; setPrefs(next); savePrefs(next); };
  if (!draft) return <Pane><PaneHeader title="Settings" /><Spinner /></Pane>;
  const setAddr = (i: number, patch: Partial<Address>) => setDraft({ ...draft, addresses: draft.addresses.map((a, n) => n === i ? { ...a, ...patch } : a) });
  return <form className="flex flex-col h-full min-h-0" onSubmit={async e => { e.preventDefault(); setBusy(true); onError(''); try { const saved = await put<Profile>('/me/profile', draft); setDraft(saved); onInfo('Settings saved.'); } catch (issue) { onError(messageOf(issue)); } finally { setBusy(false); } }}>
    <PaneHeader title="Settings" hint={me ? `Signed in as ${demo ? 'the demo shopper' : me.subject}` : undefined} right={<button className="pf-btn sm" disabled={busy}>{busy ? 'Saving…' : 'Save changes'}</button>} />
    <Scroll className="p-4 sm:p-5 grid gap-6 content-start lg:grid-cols-2 lg:items-start">
      <div className="space-y-6">
        <label className="pf-field"><span className="text-[13px] font-semibold text-ink-2">Display name</span><input className="pf-input" maxLength={130} value={draft.display_name} onChange={e => setDraft({ ...draft, display_name: e.target.value })} /></label>
        <fieldset className="space-y-3"><legend className="text-[13px] font-semibold text-ink-2 mb-1">Notifications</legend>
          {NOTIFY.map(([key, label, hint]) => <label key={key} className="flex items-start gap-3 text-sm"><input type="checkbox" className="pf-check mt-0.5" checked={Boolean(draft.notifications[key])} onChange={e => setDraft({ ...draft, notifications: { ...draft.notifications, [key]: e.target.checked } })} /><span><span className="font-medium block">{label}</span><span className="text-[12.5px] text-muted">{hint}</span></span></label>)}</fieldset>
        <fieldset className="space-y-2"><legend className="text-[13px] font-semibold text-ink-2 mb-1">Language and currency display</legend>
          <div className="grid grid-cols-2 gap-2">
            <label className="pf-field"><span className="text-[12.5px] text-muted">Language</span><select className="pf-select" value={prefs.language} onChange={e => setPref({ language: e.target.value })}><option value="en">English</option><option value="ms">Bahasa Melayu (preview)</option><option value="zh">中文 (preview)</option></select></label>
            <label className="pf-field"><span className="text-[12.5px] text-muted">Currency</span><select className="pf-select" value={prefs.currency} onChange={e => setPref({ currency: e.target.value })}><option value="store">Store currency</option><option value="USD">USD</option><option value="SGD">SGD</option><option value="MYR">MYR</option></select></label></div>
          <Quiet>Saved on this device only. Translations are not available yet and prices are never converted: you always pay in the store's currency.</Quiet></fieldset>
        <LocationCard />
      </div>
      <div className="space-y-6">
        <fieldset className="space-y-3"><legend className="text-[13px] font-semibold text-ink-2 mb-1">Saved addresses ({draft.addresses.length}/10)</legend>
          {draft.addresses.map((a, i) => <div key={a.id || i} className="pf-card p-3 grid grid-cols-2 gap-2">
            <input className="pf-input sm" aria-label="Label" placeholder="Label" maxLength={40} value={a.label} onChange={e => setAddr(i, { label: e.target.value })} />
            <input className="pf-input sm" aria-label="Postcode" placeholder="Postcode" maxLength={20} value={a.postal} onChange={e => setAddr(i, { postal: e.target.value })} />
            <input className="pf-input sm col-span-2" aria-label="Street address" placeholder="Street address" required minLength={3} maxLength={200} value={a.line1} onChange={e => setAddr(i, { line1: e.target.value })} />
            <input className="pf-input sm" aria-label="City" placeholder="City" maxLength={80} value={a.city} onChange={e => setAddr(i, { city: e.target.value })} />
            <button type="button" className="pf-link text-[13px] justify-self-end" onClick={() => setDraft({ ...draft, addresses: draft.addresses.filter((_, n) => n !== i) })}>Remove</button></div>)}
          {draft.addresses.length < 10 && <button type="button" className="pf-btn sm outline" onClick={() => setDraft({ ...draft, addresses: [...draft.addresses, { id: '', label: draft.addresses.length ? 'Other' : 'Home', line1: '', city: '', postal: '' }] })}>Add address</button>}
          <Quiet>Used to prefill delivery requests.</Quiet></fieldset>
        <section className="pf-card p-4 space-y-2" aria-label="Session"><h3 className="text-sm font-semibold">Session</h3><Quiet>Sign out of this browser.</Quiet>
          <button type="button" className="pf-btn sm outline" onClick={() => void logout()}><LogOut size={15} />Sign out</button></section>
      </div>
    </Scroll>
  </form>;
}
