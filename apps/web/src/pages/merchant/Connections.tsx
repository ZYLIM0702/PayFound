import { useState } from 'react';
import { ExternalLink, RefreshCw, Webhook, Unplug } from 'lucide-react';
import { messageOf, post, remove, safeExternalUrl, scoped, type Connection, type MerchantLocation } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, Empty, ErrorLine, Field, Notice, PageHeader, Panel, Sheet } from '../../components/Shared';
import { useMerchant } from './context';
import { PosConnectionCard, PosConnectSheet, PosContractDocs, usePosOverview } from './PosPlugin';

const PROVIDERS = [
  { id: 'woocommerce', name: 'WooCommerce', blurb: 'Import your catalog with a read-only REST key. Generic stock stays online-only.', letter: 'W' },
  { id: 'shopify', name: 'Shopify', blurb: 'Authorize PayFound on your .myshopify.com store. Physical locations can map to branches.', letter: 'S' },
] as const;
const tone = (s: string) => /active|connected|ready|ok/i.test(s) ? 'green' : /error|fail|revoked|disconnect/i.test(s) ? 'red' : 'amber';

export function ConnectionsPage() {
  const { merchantId } = useMerchant();
  const resource = useResource<{ connections: Connection[] }>(scoped('/merchant/connections', merchantId), 10000);
  const [provider, setProvider] = useState<(typeof PROVIDERS)[number] | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [authorization, setAuthorization] = useState('');
  const [posOpen, setPosOpen] = useState(false);
  const pos = usePosOverview(merchantId);
  const connections = resource.data?.connections || [];
  const posConnections = pos.data?.connections || [];
  return <div className="space-y-6 pf-enter">
    <PageHeader title="Connections" description="Connecting imports a private catalog. Public display needs your explicit consent, and physical branch mapping uses verified source locations." />
    <ErrorLine message={resource.error} />
    {authorization && <Notice tone="green">Continue to your store to finish: <a className="pf-link inline-flex items-center gap-1" href={authorization}>Authorize Shopify access<ExternalLink size={13} /></a></Notice>}
    <section aria-label="Available providers" className="grid sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">{PROVIDERS.map(p => <article key={p.id} className="pf-card p-5 flex flex-col gap-4">
      <div className="flex items-center gap-3"><span className="w-11 h-11 rounded-[var(--pf-r-md)] bg-ink text-white grid place-items-center font-display text-xl font-semibold">{p.letter}</span><h2 className="pf-subtitle">{p.name}</h2></div>
      <p className="text-sm text-muted flex-1">{p.blurb}</p><button className="pf-btn sm outline self-start" onClick={() => { setError(''); setProvider(p); }}>Connect {p.name}</button></article>)}
      <article className="pf-card p-5 flex flex-col gap-4"><div className="flex items-center gap-3"><span className="w-11 h-11 rounded-[var(--pf-r-md)] bg-accent text-white grid place-items-center font-display text-xl font-semibold">P</span><h2 className="pf-subtitle">Your POS</h2></div>
        <p className="text-sm text-muted flex-1">Any other point-of-sale: connect its API, or let it push signed updates. Products, branches and stock sync automatically.</p><button className="pf-btn sm outline self-start" data-testid="connect-pos" onClick={() => setPosOpen(true)}>Connect your POS</button></article></section>
    <section aria-label="Connected sources" className="space-y-4">
      <h2 className="pf-title">Connected sources</h2>
      {connections.length === 0 && posConnections.length === 0 ? <Panel><Empty title="Nothing connected yet" description="Connect WooCommerce or Shopify to import your catalog privately." /></Panel> :
        <div className="grid xl:grid-cols-2 gap-4 items-start">{posConnections.map(c => <PosConnectionCard key={c.id} connection={c} refresh={pos.refresh} />)}{connections.map(c => <ConnectionCard key={c.id} connection={c} merchantId={merchantId} refresh={resource.refresh} />)}</div>}
    </section>
    <PosContractDocs />
    <PosConnectSheet open={posOpen} onClose={() => setPosOpen(false)} merchantId={merchantId} demo={pos.data?.demo ?? null} onDone={pos.refresh} />
    <Sheet open={Boolean(provider)} onClose={() => setProvider(null)} title={`Connect ${provider?.name || ''}`} description="Credentials are stored server-side and never shown again." footer={<><button type="button" className="pf-btn outline" onClick={() => setProvider(null)}>Cancel</button><button form="connect-form" className="pf-btn" disabled={busy}>{busy ? 'Connecting…' : 'Connect authorized store'}</button></>}>
      {provider && <form id="connect-form" className="grid gap-4" onSubmit={async e => { e.preventDefault(); const form = e.currentTarget; const data = new FormData(form); setBusy(true); setError(''); try { const result = await post<{ authorization_url?: string }>('/merchant/connections', { merchant_id: merchantId, provider: provider.id, store_url: provider.id === 'woocommerce' ? data.get('store_url') : undefined, shop_domain: provider.id === 'shopify' ? data.get('shop_domain') : undefined, consumer_key: data.get('consumer_key') || undefined, consumer_secret: data.get('consumer_secret') || undefined }); setAuthorization(safeExternalUrl(result.authorization_url) || ''); form.reset(); setProvider(null); await resource.refresh(); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); } }}>
        <ErrorLine message={error} />
        {provider.id === 'woocommerce' ? <><Field label="HTTPS store URL" name="store_url" type="url" required /><Field label="Consumer key" name="consumer_key" type="password" autoComplete="off" required /><Field label="Consumer secret" name="consumer_secret" type="password" autoComplete="off" required /></> : <Field label="Store .myshopify.com domain" name="shop_domain" placeholder="your-store.myshopify.com" required />}
      </form>}
    </Sheet>
  </div>;
}

function ConnectionCard({ connection, merchantId, refresh }: { connection: Connection; merchantId: string; refresh: () => Promise<void> }) {
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [consent, setConsent] = useState(false);
  const [mappings, setMappings] = useState<Record<string, string>>({});
  const locations = useResource<{ locations: { source_location_id: string; name: string; kind: string; location_id?: string }[] }>(`/merchant/connections/${connection.id}/locations`);
  const branches = useResource<MerchantLocation[]>(scoped('/merchant/locations', merchantId));
  const [authorization, setAuthorization] = useState('');
  async function action(suffix: string, body = {}, deleting = false) { setBusy(true); setError(''); try { const path = `/merchant/connections/${connection.id}${suffix}`; const result = deleting ? await remove(path) : await post<{ authorization_url?: string }>(path, body); if (result && typeof result === 'object' && 'authorization_url' in result) setAuthorization(safeExternalUrl(String(result.authorization_url)) || ''); await Promise.all([refresh(), locations.refresh()]); } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); } }
  const physical = locations.data?.locations.filter(l => l.kind === 'physical') || [];
  return <section className="pf-panel">
    <div className="pf-panel-head"><div className="min-w-0"><h3 className="pf-subtitle capitalize">{connection.provider}</h3><p className="text-[13px] text-muted truncate">{connection.shop_domain || connection.store_url}</p></div><Chip kind={tone(connection.status)} dot>{connection.status}</Chip></div>
    <div className="pf-panel-body space-y-5">
      <ErrorLine message={error || connection.last_error || ''} />
      <p className="text-sm text-muted">Last completed sync: {connection.last_synced_at ? new Date(connection.last_synced_at).toLocaleString() : 'Not synced'}</p>
      <div className="flex flex-wrap gap-2"><button className="pf-btn sm outline" disabled={busy} onClick={() => action('/sync')}><RefreshCw size={14} />Sync catalog</button><button className="pf-btn sm outline" disabled={busy} onClick={() => action('/webhooks')}><Webhook size={14} />Register signed webhooks</button>{connection.provider === 'shopify' && <button className="pf-btn sm outline" disabled={busy} onClick={() => action('/authorize')}>Reauthorize</button>}<button className="pf-btn sm danger" disabled={busy} onClick={() => action('', {}, true)}><Unplug size={14} />Disconnect &amp; unpublish</button></div>
      {authorization && <a className="pf-btn sm" href={authorization}>Authorize store<ExternalLink size={13} /></a>}
      {physical.length > 0 && <div className="space-y-3 border-t border-line pt-4"><h4 className="pf-subtitle">Branch mapping</h4>{physical.map(l => <div className="pf-field" key={l.source_location_id}><label htmlFor={`m-${l.source_location_id}`}>Map {l.name}</label><select id={`m-${l.source_location_id}`} className="pf-select" value={mappings[l.source_location_id] || l.location_id || ''} onChange={e => setMappings(m => ({ ...m, [l.source_location_id]: e.target.value }))}><option value="">Choose verified branch</option>{branches.data?.map(b => <option value={b.id} key={b.id}>{b.name}</option>)}</select></div>)}</div>}
      <div className="border-t border-line pt-4 space-y-3"><label className="pf-check"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} />I authorize public product display for this source</label>
        <div><button className="pf-btn sm accent" disabled={!consent || busy} onClick={() => action('/publish', { consent, mappings: Object.entries(mappings).filter(([, value]) => value).map(([source_location_id, location_id]) => ({ source_location_id, location_id })) })}>Publish authorized offers</button></div></div>
    </div>
  </section>;
}
