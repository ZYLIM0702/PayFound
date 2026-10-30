import { useEffect, useState } from 'react';
import { Check, Copy, Pause, Play, PlugZap, RefreshCw, Unplug } from 'lucide-react';
import { messageOf, patch, post, remove, scoped } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, ConfirmDialog, ErrorLine, Field, Notice, Panel, SelectField, Sheet, type Tone } from '../../components/Shared';

export type PosConnection = {
  id: string; name: string; mode: 'api' | 'push'; status: string; base_url: string | null; products_path: string; branches_path: string | null;
  health_path: string; auth_scheme: string; credential_hint: string | null; schedule: string; last_synced_at: string | null; next_sync_at: string | null;
  last_error: string | null; failure_count: number; demo: boolean; endpoint_url?: string;
};
export type PosOverview = { connections: PosConnection[]; demo: { base_url: string; token: string; name: string } | null };
type PosRun = { id: string; trigger: string; status: string; started_at: string; finished_at: string | null; created: number; updated: number; skipped: number; failed: number; error: string | null; row_errors: { external_id: string | null; error: string }[]; next_run_at: string | null };
type Created = { connection: PosConnection; secret?: string; endpoint_url?: string };

const statusTone = (s: string): Tone => s === 'connected' ? 'green' : s === 'error' ? 'red' : s === 'paused' || s === 'syncing' ? 'amber' : 'default';
const runTone = (s: string): Tone => s === 'ok' ? 'green' : s === 'failed' ? 'red' : 'amber';
const when = (v: string | null) => v ? new Date(v + (v.endsWith('Z') ? '' : 'Z')).toLocaleString() : '—';
const SCHEDULES = [['15m', 'Every 15 minutes'], ['1h', 'Every hour'], ['manual', 'Manual only']] as const;

export function usePosOverview(merchantId: string) {
  return useResource<PosOverview>(scoped('/merchant/pos-plugin', merchantId), 10000);
}

function CopyRow({ label, value }: { label: string; value: string }) {
  const [done, setDone] = useState(false);
  return <div className="pf-field"><label>{label}</label><div className="flex gap-2"><input className="pf-input font-mono text-[13px]" readOnly value={value} onFocus={e => e.currentTarget.select()} />
    <button type="button" className="pf-btn outline icon" aria-label={`Copy ${label}`} onClick={async () => { try { await navigator.clipboard.writeText(value); setDone(true); window.setTimeout(() => setDone(false), 1500); } catch { /* clipboard unavailable */ } }}>{done ? <Check size={15} /> : <Copy size={15} />}</button></div></div>;
}

export function PosConnectSheet({ open, onClose, merchantId, demo, onDone }: { open: boolean; onClose: () => void; merchantId: string; demo: PosOverview['demo']; onDone: () => Promise<void> }) {
  const [mode, setMode] = useState<'api' | 'push'>('api');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [created, setCreated] = useState<Created | null>(null);
  const [form, setForm] = useState({ name: '', base_url: '', token: '', auth_scheme: 'bearer', products_path: '/products', branches_path: '/branches', health_path: '/health', schedule: '15m' });
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm(f => ({ ...f, [k]: e.target.value }));
  useEffect(() => { if (open) { setCreated(null); setError(''); } }, [open]);
  const close = () => { setForm(f => ({ ...f, token: '' })); onClose(); };
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError('');
    try {
      const body = mode === 'api' ? { merchant_id: merchantId, mode, ...form, branches_path: form.branches_path || null } : { merchant_id: merchantId, mode, name: form.name };
      const result = await post<Created>('/merchant/pos-plugin/connections', body);
      setForm(f => ({ ...f, token: '' }));
      await onDone();
      if (result.secret) setCreated(result); else close();
    } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); }
  }
  return <Sheet open={open} onClose={close} title="Connect your POS" description="Credentials are encrypted on the server and never shown again."
    footer={created ? <button className="pf-btn" onClick={close}>I have saved the secret</button> : <><button type="button" className="pf-btn outline" onClick={close}>Cancel</button><button form="pos-connect-form" className="pf-btn" disabled={busy}>{busy ? 'Connecting…' : mode === 'api' ? 'Test and connect' : 'Create webhook'}</button></>}>
    {created ? <div className="grid gap-4" data-testid="pos-secret-once">
      <Notice tone="amber">Copy the secret now. For your security it is shown once and cannot be retrieved later.</Notice>
      <CopyRow label="Endpoint URL" value={created.endpoint_url || ''} /><CopyRow label="Signing secret" value={created.secret || ''} />
      <p className="text-sm text-muted">Sign each POST with <code>HMAC-SHA256(secret, timestamp + "." + body)</code> and send it in <code>X-PayFound-Signature</code>, with the unix time in <code>X-PayFound-Timestamp</code>. Deliveries older than 5 minutes are rejected.</p>
    </div> : <form id="pos-connect-form" className="grid gap-4" onSubmit={submit}>
      <ErrorLine message={error} />
      <div className="pf-segmented" role="group" aria-label="How should your POS connect?">
        <button type="button" aria-pressed={mode === 'api'} onClick={() => setMode('api')}>API connection</button>
        <button type="button" aria-pressed={mode === 'push'} onClick={() => setMode('push')}>Webhook (your POS pushes)</button>
      </div>
      <Field label="Connection name" value={form.name} onChange={set('name')} placeholder="Front counter till" required maxLength={80} />
      {mode === 'api' ? <>
        <p className="text-sm text-muted -mt-1">PayFound calls your POS over HTTPS to read products, branches and stock. Private or local addresses are refused.</p>
        {demo && <div><button type="button" className="pf-btn sm outline" data-testid="load-demo-pos" onClick={() => setForm(f => ({ ...f, name: demo.name, base_url: demo.base_url, token: demo.token, schedule: '15m' }))}><PlugZap size={14} />Load demo POS</button><p className="text-xs text-muted mt-1.5">Demo only: fills in the local fake POS at {demo.base_url}. Start it with <code>python scripts/fake_pos.py</code>.</p></div>}
        <Field label="Base URL" type="text" inputMode="url" value={form.base_url} onChange={set('base_url')} placeholder="https://pos.example.com/api" required hint="HTTPS only." />
        <div className="grid grid-cols-2 gap-3">
          <SelectField label="Credential type" value={form.auth_scheme} onChange={set('auth_scheme')}><option value="bearer">Bearer token</option><option value="api_key">API key (X-API-Key)</option></SelectField>
          <Field label="API key or token" type="password" autoComplete="off" value={form.token} onChange={set('token')} required />
        </div>
        <div className="grid sm:grid-cols-3 gap-3">
          <Field label="Products path" value={form.products_path} onChange={set('products_path')} required />
          <Field label="Branches path" value={form.branches_path} onChange={set('branches_path')} hint="Optional" />
          <Field label="Health path" value={form.health_path} onChange={set('health_path')} required />
        </div>
        <SelectField label="Sync schedule" value={form.schedule} onChange={set('schedule')}>{SCHEDULES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</SelectField>
      </> : <p className="text-sm text-muted">PayFound creates a private endpoint URL and signing secret. Your POS sends signed events whenever products, branches or stock change.</p>}
    </form>}
  </Sheet>;
}

export function PosConnectionCard({ connection: c, refresh }: { connection: PosConnection; refresh: () => Promise<void> }) {
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [note, setNote] = useState('');
  const [confirm, setConfirm] = useState(false);
  const runs = useResource<{ runs: PosRun[] }>(`/merchant/pos-plugin/${c.id}/runs`, 10000);
  const base = `/merchant/pos-plugin/${c.id}`;
  async function act(name: string, fn: () => Promise<unknown>) {
    setBusy(name); setError(''); setNote('');
    try { await fn(); await Promise.all([refresh(), runs.refresh()]); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(''); }
  }
  const latest = runs.data?.runs[0];
  const live = c.status !== 'disconnected';
  return <section className="pf-panel" data-testid="pos-connection-card">
    <div className="pf-panel-head"><div className="min-w-0"><h3 className="pf-subtitle truncate">{c.name}</h3><p className="text-[13px] text-muted truncate">{c.mode === 'api' ? c.base_url : 'Webhook push'}{c.credential_hint ? ` · ${c.credential_hint}` : ''}</p></div><Chip kind={statusTone(c.status)} dot>{c.status}</Chip></div>
    <div className="pf-panel-body space-y-5">
      <ErrorLine message={error || (c.status === 'error' ? c.last_error || '' : '')} />
      {note && <Notice tone="green">{note}</Notice>}
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <div><dt className="text-muted">Last successful sync</dt><dd>{when(c.last_synced_at)}</dd></div>
        <div><dt className="text-muted">{c.mode === 'api' ? 'Next run' : 'Receiving'}</dt><dd>{c.mode === 'api' ? (c.schedule === 'manual' ? 'Manual only' : c.status === 'error' ? `Retry ${when(c.next_sync_at)}` : when(c.next_sync_at)) : 'Signed pushes'}</dd></div>
      </dl>
      {c.mode === 'push' && c.endpoint_url && <CopyRow label="Endpoint URL" value={c.endpoint_url} />}
      {live && <div className="flex flex-wrap items-end gap-2">
        {c.mode === 'api' && <>
          <button className="pf-btn sm" disabled={Boolean(busy) || c.status === 'paused'} onClick={() => act('sync', () => post(`${base}/sync`))}><RefreshCw size={14} className={busy === 'sync' ? 'animate-spin' : ''} />{busy === 'sync' ? 'Syncing…' : 'Sync now'}</button>
          <button className="pf-btn sm outline" disabled={Boolean(busy)} onClick={() => act('test', async () => { const r = await post<{ ok: boolean; message: string; latency_ms?: number }>(`${base}/test`); if (r.ok) setNote(`Connection works (${r.latency_ms} ms).`); else throw new Error(r.message); })}>Test connection</button>
          <div className="min-w-[10rem]"><SelectField label="Schedule" value={c.schedule} disabled={Boolean(busy)} onChange={e => act('schedule', () => patch(base, { schedule: e.target.value }))}>{SCHEDULES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</SelectField></div>
        </>}
        <button className="pf-btn sm outline" disabled={Boolean(busy)} onClick={() => act('pause', () => patch(base, { paused: c.status !== 'paused' }))}>{c.status === 'paused' ? <><Play size={14} />Resume</> : <><Pause size={14} />Pause</>}</button>
        <button className="pf-btn sm danger" disabled={Boolean(busy)} onClick={() => setConfirm(true)}><Unplug size={14} />Disconnect</button>
      </div>}
      {c.status === 'paused' && <p className="text-sm text-muted">Paused: sync is stopped and listings are unavailable online until you resume.</p>}
      <div className="border-t border-line pt-4 space-y-2">
        <h4 className="pf-subtitle">Sync log</h4>
        {!runs.data?.runs.length ? <p className="text-sm text-muted">No syncs yet.</p> : <ul className="divide-y divide-line text-sm" data-testid="pos-run-log">
          {runs.data.runs.slice(0, 6).map(r => <li key={r.id} className="py-2.5 flex flex-wrap items-center gap-x-4 gap-y-1">
            <Chip kind={runTone(r.status)}>{r.status}</Chip><span className="text-muted">{when(r.started_at)} · {r.trigger}</span>
            <span className="tabular ml-auto">{r.created} created · {r.updated} updated · {r.skipped} skipped · {r.failed} failed</span>
            {r.error && <span className="basis-full text-bad">{r.error}</span>}
            {r.row_errors.length > 0 && <details className="basis-full text-muted"><summary className="cursor-pointer">{r.row_errors.length} rejected row{r.row_errors.length > 1 ? 's' : ''}</summary><ul className="mt-1 space-y-0.5">{r.row_errors.slice(0, 10).map((e, i) => <li key={i}><code>{e.external_id || 'row'}</code> {e.error}</li>)}</ul></details>}
          </li>)}</ul>}
        {latest && c.mode === 'api' && latest.next_run_at && <p className="text-xs text-muted">Next scheduled run {when(latest.next_run_at)}.</p>}
      </div>
    </div>
    <ConfirmDialog open={confirm} destructive title={`Disconnect ${c.name}?`} confirmLabel="Disconnect" busy={busy === 'disconnect'} onClose={() => setConfirm(false)}
      description="Sync stops and the stored credentials are deleted. Your synced listings stay in PayFound but are marked unavailable online until you connect again."
      onConfirm={() => { setConfirm(false); void act('disconnect', () => remove(base)); }} />
  </section>;
}

const CONTRACT = `GET {base}/health                      -> 2xx
GET {base}/branches                    -> {"branches": [{external_id, name, address, latitude, longitude, timezone}]}
GET {base}/products?updated_since=ISO&cursor=…&limit=500
                                       -> {"products": [{external_id, sku, name, price, currency, quantity,
                                            branch_external_id, updated_at, active}], "next_cursor": null}
Auth: Authorization: Bearer <token>   (or X-API-Key)

Webhook: POST /api/pos-plugin/<id>/events   {"branches":[…], "products":[…], "stock_events":[{external_id, quantity, updated_at}]}
  X-PayFound-Timestamp: <unix seconds>   X-PayFound-Signature: sha256=hex(HMAC_SHA256(secret, timestamp + "." + rawBody))`;

export function PosContractDocs() {
  return <Panel title="POS plugin contract" description="What your POS must send. Unknown fields are ignored; bad rows are reported, never fatal.">
    <pre className="text-[12.5px] leading-relaxed bg-sunk rounded-[var(--pf-r-md)] p-4 overflow-x-auto" tabIndex={0}>{CONTRACT}</pre>
    <p className="text-sm text-muted mt-3">Limits: 1000 rows per request, price in major units with up to 2 decimals, quantity is on-hand stock. A sync never overwrites reservation holds, and a webhook is rejected after 5 minutes or on replay. Full spec: <code>apps/api/docs/pos-plugin.md</code>.</p>
  </Panel>;
}
