import { useMemo, useRef, useState } from 'react';
import { AgStudio, AgStudioProvider } from 'ag-studio-react';
import type { AgReportState } from 'ag-studio';
import { messageOf, post, put, remove, scoped } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { ErrorLine, Notice, Panel } from '../../components/Shared';
import { useMerchant } from './context';

type Report = { id: string; name: string; state: AgReportState; version: number };

/** The AG Studio report builder, kept as the advanced option under the ready-made reports. */
export default function AdvancedBuilder() {
  return <AgStudioProvider licenseKey={import.meta.env.VITE_AG_STUDIO_LICENSE_KEY}><Builder /></AgStudioProvider>;
}

function Builder() {
  const { merchantId, dashboard } = useMerchant();
  const ref = useRef<AgStudio>(null);
  const reports = useResource<{ reports: Report[] }>(scoped('/merchant/reports', merchantId));
  const [selected, setSelected] = useState<Report | null>(null);
  const [name, setName] = useState('Merchant operations');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const data = useMemo(() => ({ sources: [{ id: 'inventory', data: dashboard.products.map(p => ({ product: p.name, category: p.category, price: p.price_cents / 100, currency: p.currency, physicalStock: p.quantity, available: p.available_quantity, freshness: p.freshness })) }, { id: 'orders', data: dashboard.orders.map(o => ({ product: o.product_name, status: o.status, payment: o.payment_status, currency: o.currency, amount: o.amount_cents / 100 })) }] }), [dashboard]);
  return <div className="flex flex-col gap-4">
    <Notice tone="default">Amounts are recorded order values. Filter by currency; captures are not profit or bank settlement.</Notice>
    <ErrorLine message={error || reports.error} />{info && <Notice tone="green">{info}</Notice>}
    <Panel flush actions={<div className="flex flex-wrap items-center gap-2">
      <select className="pf-select sm !w-auto" aria-label="Saved report" value={selected?.id || ''} onChange={e => { const report = reports.data?.reports.find(r => r.id === e.target.value) || null; setSelected(report); setName(report?.name || 'Merchant operations'); }}><option value="">New report</option>{reports.data?.reports.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}</select>
      <input className="pf-input sm !w-48" aria-label="Report name" value={name} maxLength={120} onChange={e => setName(e.target.value)} />
      <button className="pf-btn sm" onClick={async () => { setError(''); try { const state = ref.current?.api.getState(); if (!state) return; const result = selected ? await put<Report>(`/merchant/reports/${selected.id}`, { name, state, version: selected.version }) : await post<Report>('/merchant/reports', { merchant_id: merchantId, name, state }); setSelected(result); await reports.refresh(); setInfo('Report saved.'); } catch (issue) { setError(messageOf(issue)); } }}>Save report</button>
      {selected && <button className="pf-btn sm outline" onClick={async () => { try { await remove(`/merchant/reports/${selected.id}?version=${selected.version}`); setSelected(null); await reports.refresh(); } catch (issue) { setError(messageOf(issue)); } }}>Delete report</button>}</div>} title="Custom chart builder">
      <div style={{ height: 'calc(100dvh - 330px)', minHeight: 560 }}><AgStudio key={selected?.id || 'new'} ref={ref} data={data} initialState={selected?.state} mode="edit" /></div>
    </Panel>
  </div>;
}
