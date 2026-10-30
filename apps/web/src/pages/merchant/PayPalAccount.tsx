import { useState, type FormEvent } from 'react';
import { messageOf, post, put, remove } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, ErrorLine, Field, Notice, Panel, Spinner } from '../../components/Shared';

type Account = { connected: boolean; can_edit: boolean; client_id_hint?: string; secret_hint?: string; receiving_email?: string; assigned?: boolean; assigned_label?: string; paypal_merchant_id?: string | null; status?: 'saved' | 'verified' | 'failed' | 'assigned'; verified_at?: string | null; ok?: boolean; message?: string };

export function PayPalAccountPanel({ merchantId }: { merchantId: string }) {
  const base = `/merchants/${encodeURIComponent(merchantId)}/paypal-account`;
  const res = useResource<Account>(base);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState(false);
  const acct = res.data;
  async function run(task: () => Promise<unknown>, done: string) {
    setBusy(true); setError(''); setInfo('');
    try { const out = await task(); const result = out as Account | undefined; if (result?.ok === false) setError(result.message || 'Test failed'); else setInfo(result?.message || done); await res.refresh(); return true; }
    catch (issue) { setError(messageOf(issue)); return false; } finally { setBusy(false); }
  }
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; const data = new FormData(form);
    const body: Record<string, string> = { client_id: String(data.get('client_id') || ''), receiving_email: String(data.get('receiving_email') || '') };
    const secret = String(data.get('client_secret') || ''); if (secret) body.client_secret = secret;
    const pid = String(data.get('paypal_merchant_id') || '').trim(); if (pid) body.paypal_merchant_id = pid;
    if (await run(() => put(base, body), 'PayPal sandbox account saved. Run a connection test next.')) { form.reset(); setEditing(false); }
  }
  if (res.loading) return <Spinner />;
  const form = !acct?.connected || editing;
  const canEdit = acct?.can_edit ?? false;
  return <Panel title="PayPal account" description="Your PayPal sandbox receiving account. Shopper payments for your store are routed here instead of the platform sandbox seller." actions={!acct?.connected && acct?.assigned ? <Chip kind="blue" dot>Assigned (sandbox)</Chip> : acct?.connected ? <Chip kind={acct.status === 'verified' ? 'green' : acct.status === 'failed' ? 'red' : 'default'} dot>{acct.status === 'verified' ? 'Verified' : acct.status === 'failed' ? 'Test failed' : 'Saved, not tested'}</Chip> : <Chip>Not connected</Chip>}>
    <div className="space-y-4 max-w-2xl" data-testid="paypal-account">
      <ErrorLine message={error || res.error} />{info && <Notice tone="green">{info}</Notice>}
      {!canEdit && <Notice>Only the store owner can change PayPal settings.</Notice>}
      {acct?.connected && !editing && <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm rounded-[var(--pf-r-md)] bg-canvas p-4">
        <dt className="text-muted">Client ID</dt><dd className="font-mono text-xs break-all">{acct.client_id_hint}</dd>
        <dt className="text-muted">Client secret</dt><dd className="font-mono text-xs" data-testid="secret-hint">{acct.secret_hint}</dd>
        <dt className="text-muted">Receiving email</dt><dd>{acct.receiving_email}</dd>
        <dt className="text-muted">PayPal merchant ID</dt><dd className="font-mono text-xs">{acct.paypal_merchant_id || 'Not set (payee by email)'}</dd>
        {acct.verified_at && <><dt className="text-muted">Last verified</dt><dd>{new Date(acct.verified_at).toLocaleString()}</dd></>}
      </dl>}
      {!acct?.connected && acct?.assigned && <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm rounded-[var(--pf-r-md)] bg-canvas p-4" data-testid="paypal-assigned">
        <dt className="text-muted">Receiving email</dt><dd className="break-all">{acct.receiving_email}</dd>
        <dt className="text-muted">Sandbox account</dt><dd>{acct.assigned_label || 'Sandbox business account'} · assigned automatically</dd>
        <dt className="text-muted">Payments</dt><dd>Created for this email through the platform sandbox app. Add your own client ID and secret below only if you want to use your own PayPal app.</dd></dl>}
      {canEdit && form && <form className="grid gap-4" onSubmit={e => void save(e)} autoComplete="off">
        <Field label="Sandbox client ID" name="client_id" required minLength={10} maxLength={160} spellCheck={false} autoComplete="off" hint="From your PayPal Developer dashboard, Apps & Credentials, Sandbox." />
        <Field label={acct?.connected ? 'Client secret (leave blank to keep the saved one)' : 'Sandbox client secret'} name="client_secret" type="password" required={!acct?.connected} maxLength={300} autoComplete="new-password" hint="Stored encrypted on the server. It is never shown again and never sent to your browser." />
        <Field label="Receiving email" name="receiving_email" type="email" required maxLength={190} defaultValue={!acct?.connected ? acct?.receiving_email : undefined} hint="The PayPal sandbox business account that receives your payments." />
        <Field label="PayPal merchant ID (optional)" name="paypal_merchant_id" maxLength={32} spellCheck={false} hint="If set, payments are routed by merchant ID instead of email." />
        <div className="flex flex-wrap gap-3"><button className="pf-btn accent" disabled={busy}>{busy ? 'Saving…' : 'Save PayPal account'}</button>{acct?.connected && <button type="button" className="pf-btn outline" onClick={() => setEditing(false)}>Cancel</button>}</div>
      </form>}
      {canEdit && acct?.connected && !editing && <div className="flex flex-wrap gap-3">
        <button className="pf-btn" disabled={busy} onClick={() => void run(() => post(`${base}/test`), 'Connection tested.')}>{busy ? 'Working…' : 'Test connection'}</button>
        <button className="pf-btn outline" disabled={busy} onClick={() => setEditing(true)}>Edit</button>
        <button className="pf-btn outline danger" disabled={busy} onClick={() => { if (window.confirm('Disconnect your PayPal account? New payments will go to the platform sandbox seller.')) void run(() => remove(base), 'PayPal account disconnected.'); }}>Disconnect</button>
      </div>}
      <p className="text-xs text-muted leading-relaxed">Sandbox only. Test connection fetches a sandbox OAuth token and discards it. Existing payments are not changed. Real multi-seller payouts need PayPal partner onboarding.</p>
    </div>
  </Panel>;
}
