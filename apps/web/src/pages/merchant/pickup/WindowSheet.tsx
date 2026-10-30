import { useEffect, useState, type FormEvent } from 'react';
import { messageOf, post, type MerchantLocation } from '../../../lib/api';
import { ErrorLine, Field, SelectField, Sheet } from '../../../components/Shared';
import { toLocalInput } from './model';

export type WindowDraft = { locationId?: string; start: Date; end: Date };

const durations = [{ label: '30 min', minutes: 30 }, { label: '1 hour', minutes: 60 }, { label: '2 hours', minutes: 120 }, { label: '4 hours', minutes: 240 }];

/** Editor for a new pickup window. Existing windows are server-owned (no update/delete API), so this only creates. */
export function WindowSheet({ draft, merchantId, locations, onClose, onSaved }: {
  draft: WindowDraft | null; merchantId: string; locations: MerchantLocation[]; onClose: () => void; onSaved: () => Promise<void>;
}) {
  const [location, setLocation] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [capacity, setCapacity] = useState(5);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const branches = locations.filter(l => l.active !== false);
  useEffect(() => {
    if (!draft) return;
    setLocation(draft.locationId && branches.some(b => b.id === draft.locationId) ? draft.locationId : branches[0]?.id || '');
    setStart(toLocalInput(draft.start)); setEnd(toLocalInput(draft.end)); setError(''); setBusy(false);
  }, [draft]);
  const startDate = start ? new Date(start) : null;
  const endDate = end ? new Date(end) : null;
  const setDuration = (minutes: number) => { if (startDate && !Number.isNaN(startDate.getTime())) setEnd(toLocalInput(new Date(startDate.getTime() + minutes * 60000))); };
  const problem = !startDate || !endDate || Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime()) ? 'Choose a start and end time.'
    : startDate.getTime() <= Date.now() ? 'The window must start in the future.'
      : endDate <= startDate ? 'The end must be after the start.'
        : endDate.getTime() - startDate.getTime() > 86400000 ? 'A window can be at most one day long.' : '';
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (problem || !startDate || !endDate) { setError(problem); return; }
    setBusy(true); setError('');
    try {
      await post('/merchant/pickup-slots', { merchant_id: merchantId, location_id: location, start_at: startDate.toISOString(), end_at: endDate.toISOString(), capacity });
      await onSaved(); onClose();
    } catch (issue) { setError(messageOf(issue)); setBusy(false); }
  };
  return <Sheet open={Boolean(draft)} onClose={() => { if (!busy) onClose(); }} title="New pickup window" description="Customers can reserve a collection time inside this window until its capacity is used up."
    footer={<><button type="button" className="pf-btn outline" disabled={busy} onClick={onClose}>Cancel</button><button type="submit" form="pickup-window-form" className="pf-btn accent" disabled={busy || !location || Boolean(problem)} data-testid="publish-pickup-window">{busy ? 'Publishing…' : 'Publish window'}</button></>}>
    <form id="pickup-window-form" className="flex flex-col gap-5" onSubmit={submit}>
      <SelectField label="Branch" value={location} onChange={e => setLocation(e.target.value)} required>{branches.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}</SelectField>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Starts" type="datetime-local" value={start} onChange={e => setStart(e.target.value)} required />
        <Field label="Ends" type="datetime-local" value={end} onChange={e => setEnd(e.target.value)} required />
      </div>
      <div className="flex flex-wrap items-center gap-2 -mt-2"><span className="text-[13px] text-muted mr-1">Length</span>{durations.map(d => <button key={d.minutes} type="button" className="pf-btn sm soft" onClick={() => setDuration(d.minutes)}>{d.label}</button>)}</div>
      <Field label="Capacity" type="number" min={1} max={10000} value={capacity} onChange={e => setCapacity(Math.max(1, Math.min(10000, Number(e.target.value) || 1)))} required hint="How many orders can be collected in this window." />
      <p className="text-[13px] text-muted">Times are in your browser time zone. Once published, a window is managed by the server and can't be edited or removed here.</p>
      {(error || (start && end && problem)) && <ErrorLine message={error || problem} />}
    </form>
  </Sheet>;
}
