import { Zap } from 'lucide-react';
import { useResource } from '../lib/use-resource';
import { ErrorLine, Spinner } from './Shared';

type Suggestion = { slot_id: string; start_at: string; end_at: string; capacity: number; booked: number; remaining: number; queue_estimate_minutes: number };
const time = (value: string) => new Date(value).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });

/** "Shortest queue" chips for one merchant and day. Tapping a chip selects that slot through the page's own select code. */
export function PickupSuggestions({ merchantId, day, selectedId, disabled, onSelect }: { merchantId: string; day: string; selectedId?: string; disabled?: boolean; onSelect: (slotId: string) => void }) {
  const res = useResource<{ suggestions: Suggestion[]; generated_at: string }>(`/pickup-suggestions?merchant_id=${encodeURIComponent(merchantId)}&day=${encodeURIComponent(day)}`);
  const list = (res.data?.suggestions || []).filter(s => s.remaining > 0 && Date.parse(s.start_at) >= Date.now());
  return <div className="space-y-2" data-testid="pickup-suggestions" aria-label="Shortest queue">
    <p className="flex items-center gap-1.5 text-sm font-semibold"><Zap size={15} />Shortest queue</p>
    {res.loading ? <Spinner label="Finding quiet windows…" inline /> : res.error ? <ErrorLine message="Queue suggestions are unavailable right now." retry={res.refresh} />
      : list.length ? <>
        <div className="flex flex-wrap gap-2">{list.slice(0, 3).map(s => { const chosen = selectedId === s.slot_id;
          return <button key={s.slot_id} type="button" aria-pressed={chosen} disabled={disabled} onClick={() => onSelect(s.slot_id)}
            className={`min-h-[44px] rounded-[var(--pf-r-md)] border px-3 py-2 text-left transition-colors disabled:opacity-40 ${chosen ? 'border-accent bg-accent-soft' : 'border-line-strong hover:border-ink'}`}>
            <span className="block text-sm font-semibold tabular">{time(s.start_at)} – {time(s.end_at)}</span>
            <span className="block text-xs text-muted">about {s.queue_estimate_minutes} min queue</span></button>; })}</div>
        <p className="text-xs text-muted">estimate from bookings</p></>
      : <p className="text-sm text-muted">No open windows to suggest for this day.</p>}
  </div>;
}
