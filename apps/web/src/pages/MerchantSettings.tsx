import { useState, type FormEvent } from 'react';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api, messageOf, patch, post, scoped, type Merchant, type MerchantLocation } from '../lib/api';
import { useApp } from '../lib/app-context';
import { useResource } from '../lib/use-resource';
import { Chip, ErrorLine, Field, Notice, PageHeader, Panel, SelectField, Sheet, Spinner, TextAreaField } from '../components/Shared';
import { PayPalAccountPanel } from './merchant/PayPalAccount';
import { SpecialDates, WeeklyHours, type WeekHours } from './merchant/HoursEditor';

const defaultBranch = { name: '', address: '', latitude: '37.7749', longitude: '-122.4194', timezone: 'America/Los_Angeles' };

export function MerchantOnboarding() {
  const [form, setForm] = useState({ ...defaultBranch, slug: '', category: 'Retail' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const { refreshMe, setMerchantId } = useApp();
  const navigate = useNavigate();
  const set = (key: keyof typeof form) => (e: { target: { value: string } }) => setForm(f => ({ ...f, [key]: e.target.value }));
  const section = 'grid lg:grid-cols-[240px_minmax(0,1fr)] gap-x-12 gap-y-5 py-8 border-t border-line';
  return <main className="pf-container py-8 sm:py-12"><div className="pf-readable"><h1 className="pf-heading">Bring your store to PayFound</h1><p className="text-muted text-[15px] mt-2 max-w-2xl">Create your business profile and first branch, then connect your authorized catalog.</p>
    <div className="mt-6 empty:hidden"><ErrorLine message={error} /></div>
    <form className="mt-8" onSubmit={async e => { e.preventDefault(); setBusy(true); setError(''); try { const created = await post<Merchant>('/merchant/onboard', { ...form, latitude: Number(form.latitude), longitude: Number(form.longitude) }); await refreshMe(); setMerchantId(created.id); navigate('/merchant'); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); } }}>
      <section className={section}><div><h2 className="pf-title">Business</h2><p className="text-sm text-muted mt-1">How shoppers will see you.</p></div><div className="grid sm:grid-cols-2 gap-4">
        <Field label="Business name" value={form.name} required onChange={set('name')} />
        <Field label="Category" value={form.category} required onChange={set('category')} hint="For example Retail, Grocery or Electronics." />
        <div className="sm:col-span-2"><Field label="Store URL slug" value={form.slug} required onChange={set('slug')} hint="Lowercase letters, numbers and dashes. Your store lives at /stores/your-slug." /></div>
      </div></section>
      <section className={section}><div><h2 className="pf-title">First branch</h2><p className="text-sm text-muted mt-1">The pickup location shoppers will visit. You can add more branches later.</p></div><div className="grid sm:grid-cols-2 gap-4">
        <div className="sm:col-span-2"><Field label="Branch address" value={form.address} required onChange={set('address')} autoComplete="street-address" /></div>
        <Field label="Latitude" value={form.latitude} required onChange={set('latitude')} inputMode="decimal" />
        <Field label="Longitude" value={form.longitude} required onChange={set('longitude')} inputMode="decimal" hint="Used to place the branch on the map and sort by distance." />
      </div></section>
      <section className={section}><div><h2 className="pf-title">Time zone</h2><p className="text-sm text-muted mt-1">Opening hours and pickup windows follow this zone.</p></div><div className="max-w-md"><Field label="IANA time zone" value={form.timezone} required onChange={set('timezone')} hint="For example America/Los_Angeles or Europe/London." /></div></section>
      <div className="border-t border-line pt-8 flex flex-wrap items-center justify-between gap-4"><p className="text-sm text-muted max-w-xl">Registration creates an owner membership. Payment and source capabilities are enabled separately after authorization.</p><button className="pf-btn accent lg" disabled={busy}>{busy ? 'Creating…' : 'Create merchant account'}</button></div>
    </form></div></main>;
}

type SettingsSection = 'profile' | 'branches' | 'staff' | 'paypal' | 'ai';
const SECTIONS: [SettingsSection, string][] = [['profile', 'Profile'], ['branches', 'Branches & hours'], ['staff', 'Staff'], ['paypal', 'PayPal account'], ['ai', 'AI data consent']];

export function MerchantSettings({ merchantId }: { merchantId: string }) {
  const profile = useResource<Merchant>(scoped('/merchant/profile', merchantId));
  const branches = useResource<MerchantLocation[]>(scoped('/merchant/locations', merchantId));
  const staff = useResource<{ memberships: { id: string; subject: string; role: string; active: boolean }[]; invitations: { id: string; email?: string; subject?: string; role: string; status: string }[] }>(scoped('/merchant/staff', merchantId));
  const consent = useResource<{ granted: boolean }>(scoped('/merchant/ai-consent', merchantId));
  const [section, setSection] = useState<SettingsSection>('profile');
  const [addingBranch, setAddingBranch] = useState(false);
  const [branch, setBranch] = useState(defaultBranch);
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [staffRole, setStaffRole] = useState('staff');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState(false);
  async function action(run: () => Promise<unknown>) { setBusy(true); setError(''); try { await run(); setInfo('Saved.'); await Promise.all([profile.refresh(), branches.refresh(), staff.refresh(), consent.refresh()]); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); } }
  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const data = new FormData(event.currentTarget);
    await action(() => patch(scoped('/merchant/profile', merchantId), { name: data.get('name'), description: data.get('description'), phone: data.get('phone') }));
  }
  if (profile.loading) return <Spinner />;
  return <div className="space-y-6 pf-enter">
    <PageHeader title="Settings" description="Your business profile, branches and opening hours, team and data sharing." />
    <ErrorLine message={error || profile.error} />{info && <Notice tone="green">{info}</Notice>}
    <div className="grid lg:grid-cols-[200px_minmax(0,1fr)] gap-6 items-start">
      <nav className="flex lg:flex-col gap-1 overflow-x-auto" aria-label="Settings sections">{SECTIONS.map(([id, label]) => <button key={id} aria-current={section === id ? 'page' : undefined} className={`h-10 px-3 rounded-[var(--pf-r-md)] text-sm font-medium text-left whitespace-nowrap ${section === id ? 'bg-sunk text-ink' : 'text-muted hover:text-ink hover:bg-sunk'}`} onClick={() => { setSection(id); setInfo(''); }}>{label}</button>)}</nav>
      <div className="min-w-0 space-y-6">
        {section === 'profile' && profile.data && <Panel title="Business profile" description="Shown to shoppers on your storefront."><form className="grid gap-4 max-w-2xl" onSubmit={saveProfile}><Field label="Business name" name="name" required defaultValue={profile.data.name} /><Field label="Phone" name="phone" defaultValue={profile.data.phone} /><TextAreaField label="Description" name="description" defaultValue={profile.data.description} maxLength={5000} /><div><button className="pf-btn" disabled={busy}>Save profile</button></div></form></Panel>}
        {section === 'branches' && <>
          <Panel title="Branches & opening hours" description="Hours use each branch's time zone. Special dates override the weekly pattern." actions={<button className="pf-btn sm" onClick={() => setAddingBranch(true)}><Plus size={15} />Add branch</button>}>
            <ErrorLine message={branches.error} />
            <div className="space-y-3">{branches.data?.map((location, i) => <BranchEditor key={location.id} location={location} onSaved={async () => { setInfo('Branch hours saved.'); await branches.refresh(); }} defaultOpen={i === 0 && branches.data?.length === 1} />)}</div>
          </Panel>
          <Sheet open={addingBranch} onClose={() => setAddingBranch(false)} title="Add a branch" description="Starts with 09:00 to 18:00 every day; edit hours after saving." footer={<><button type="button" className="pf-btn outline" onClick={() => setAddingBranch(false)}>Cancel</button><button form="add-branch" className="pf-btn" disabled={busy}>Add branch</button></>}>
            <form id="add-branch" className="grid gap-4" onSubmit={async e => { e.preventDefault(); await action(() => post(scoped('/merchant/locations', merchantId), { ...branch, latitude: Number(branch.latitude), longitude: Number(branch.longitude), hours: Object.fromEntries(Array.from({ length: 7 }, (_, i) => [String(i), [{ start: '09:00', end: '18:00' }]])) })); setAddingBranch(false); }}>
              {Object.entries(branch).map(([key, value]) => <Field key={key} label={{ name: 'Branch name', address: 'Address', latitude: 'Latitude', longitude: 'Longitude', timezone: 'IANA time zone' }[key] || key} value={value} required onChange={e => setBranch(b => ({ ...b, [key]: e.target.value }))} />)}
            </form>
          </Sheet></>}
        {section === 'staff' && <Panel title="Staff & invitations" description="Managers can run the store; staff handle orders and stock.">
          <ErrorLine message={staff.error} />
          <ul className="divide-y divide-line border border-line rounded-[var(--pf-r-md)] mb-6">{staff.data?.memberships.map(member => <li className="flex items-center justify-between gap-3 px-4 py-3 text-sm" key={member.id}><span className="break-all">{member.subject}</span><Chip kind={member.active ? 'default' : 'red'}>{member.role}{!member.active ? ' (revoked)' : ''}</Chip></li>)}{staff.data?.invitations.map(invite => <li key={invite.id} className="flex items-center justify-between gap-3 px-4 py-3 text-sm text-muted"><span className="break-all">{invite.email || invite.subject}</span><span>{invite.role} · {invite.status}</span></li>)}</ul>
          <form className="grid sm:grid-cols-2 gap-4 max-w-2xl" onSubmit={e => { e.preventDefault(); void action(() => post(scoped('/merchant/staff', merchantId), { email: email || undefined, subject: subject || undefined, role: staffRole })); }}><Field label="Staff email" type="email" value={email} onChange={e => setEmail(e.target.value)} /><Field label="Existing user ID (optional)" value={subject} onChange={e => setSubject(e.target.value)} /><SelectField label="Staff role" value={staffRole} onChange={e => setStaffRole(e.target.value)}><option value="staff">Staff</option><option value="manager">Manager</option></SelectField><div className="flex items-end"><button className="pf-btn" disabled={busy || (!email && !subject)}>Invite staff</button></div></form>
        </Panel>}
        {section === 'paypal' && <PayPalAccountPanel merchantId={merchantId} />}
        {section === 'ai' && <Panel title="AI data consent" description="Controls whether configured cloud AI may read aggregate facts about this store."><label className="pf-check items-start max-w-2xl"><input type="checkbox" className="mt-0.5" checked={consent.data?.granted || false} onChange={e => void action(() => post(scoped('/merchant/ai-consent', merchantId), { granted: e.target.checked }))} /><span>Allow configured cloud AI to use aggregate merchant facts for this store. No AI can move money, change stock or roles.</span></label></Panel>}
      </div>
    </div>
  </div>;
}

function BranchEditor({ location, onSaved, defaultOpen = false }: { location: MerchantLocation; onSaved: () => Promise<void>; defaultOpen?: boolean }) {
  const [hours, setHours] = useState<WeekHours>(() => ({ ...(location.hours || {}) }));
  const [special, setSpecial] = useState<WeekHours>(() => ({ ...(location.special_hours || {}) }));
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const summary = Array.from({ length: 7 }, (_, i) => (hours[String(i)] || []).length > 0).filter(Boolean).length;
  return <details className="pf-card" open={defaultOpen}><summary className="cursor-pointer px-4 py-3.5 flex flex-wrap items-center justify-between gap-2 font-semibold"><span>{location.name}</span><span className="text-[13px] font-normal text-muted">{location.timezone} · open {summary} days a week</span></summary>
    <form className="px-4 pb-5 space-y-5 border-t border-line pt-4" onSubmit={async e => { e.preventDefault(); setBusy(true); setError(''); try { await patch(`/merchant/locations/${location.id}`, { hours, special_hours: special }); await onSaved(); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); } }}>
      <div><h4 className="pf-subtitle mb-2">Weekly hours</h4><WeeklyHours value={hours} onChange={setHours} /></div>
      <div><h4 className="pf-subtitle mb-2">Special dates</h4><SpecialDates value={special} onChange={setSpecial} /></div>
      <ErrorLine message={error} /><button className="pf-btn" disabled={busy}>Save branch hours</button>
    </form></details>;
}

export function StaffInvitations() {
  const invitations = useResource<{ invitations: { id: string; merchant_name: string; role: string }[] }>('/me/invitations');
  const { refreshMe } = useApp();
  const [error, setError] = useState('');
  if (!invitations.data?.invitations.length) return null;
  return <section className="pf-card p-5 sm:p-6"><h2 className="pf-subtitle">Business invitations</h2><p className="text-[13px] text-muted mt-0.5 mb-2">You have been invited to join a business on PayFound.</p><ErrorLine message={error} /><ul className="divide-y divide-line">{invitations.data.invitations.map(invite => <li key={invite.id} className="flex items-center justify-between gap-4 py-3"><span className="text-sm"><b className="font-semibold">{invite.merchant_name}</b> <span className="text-muted">as {invite.role}</span></span><button className="pf-btn sm accent" onClick={async () => { try { await api(`/merchant/staff/invitations/${invite.id}/accept`, { method: 'POST' }); await refreshMe(); await invitations.refresh(); } catch (issue) { setError(messageOf(issue)); } }}>Accept invitation</button></li>)}</ul></section>;
}
