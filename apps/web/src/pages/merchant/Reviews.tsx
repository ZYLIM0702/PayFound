import { useState } from 'react';
import { Star } from 'lucide-react';
import { messageOf, post } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { Chip, Empty, ErrorLine, PageHeader, Panel, Spinner } from '../../components/Shared';
import { fmtDate, fmtTime } from '../account/shared';

export type ShopperReview = {
  id: string; rating: number; body: string; visible: boolean; order_id: string; buyer_name: string;
  products: { product_id: string; name: string; quantity: number }[];
  reply: string; replied_at: string | null; created_at: string | null; order_date: string | null;
};
type ReviewList = { average: number | null; count: number; unanswered: number; reviews: ShopperReview[] };

const MAX = 1500;

function Stars({ value }: { value: number }) {
  return <span className="inline-flex items-center gap-0.5" aria-label={`${value} out of 5 stars`}>
    {[1, 2, 3, 4, 5].map(n => <Star key={n} size={14} className={n <= value ? 'fill-ink text-ink' : 'text-line-strong'} />)}
  </span>;
}

/** One review with its own reply draft, so typing in one card never touches another. */
function ReviewCard({ review, merchantId, onSaved }: { review: ShopperReview; merchantId: string; onSaved: () => void }) {
  const [editing, setEditing] = useState(!review.reply);
  const [draft, setDraft] = useState(review.reply);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function save() {
    if (!draft.trim()) return;
    setBusy(true); setError('');
    try {
      await post(`/merchants/${encodeURIComponent(merchantId)}/reviews/${encodeURIComponent(review.id)}/reply`, { body: draft });
      setEditing(false);
      onSaved();
    } catch (issue) { setError(messageOf(issue)); } finally { setBusy(false); }
  }
  return <article className="pf-card p-5 space-y-3" data-testid={`review-${review.id}`}>
    <div className="flex flex-wrap items-center justify-between gap-2">
      <div className="min-w-0">
        <div className="flex items-center gap-2"><Stars value={review.rating} /><span className="text-sm font-semibold">{review.buyer_name}</span></div>
        <p className="text-[12.5px] text-muted tabular" data-testid="review-date">Reviewed {review.created_at ? `${fmtDate(review.created_at)} ${fmtTime(review.created_at)}` : ''}{review.order_date ? ` · Ordered ${fmtDate(review.order_date)}` : ''} · Order {review.order_id.slice(-8)}</p>
      </div>
      <div className="flex items-center gap-2">
        {!review.visible && <Chip kind="amber">Hidden</Chip>}
        {!review.reply ? <Chip kind="blue">Needs reply</Chip> : <Chip kind="green">Replied</Chip>}
      </div>
    </div>
    {review.products.length > 0 && <ul className="flex flex-wrap gap-1.5" aria-label="Products in this order">
      {review.products.map(item => <li key={item.product_id} className="pf-chip !h-auto !py-1 text-[12.5px]">{item.name}{item.quantity > 1 ? ` × ${item.quantity}` : ''}</li>)}
    </ul>}
    <p className="text-sm whitespace-pre-wrap break-words">{review.body || <span className="text-muted">No written comment.</span>}</p>

    {review.reply && !editing && <div className="rounded-[var(--pf-r-md)] bg-sunk p-3.5">
      <p className="text-[12.5px] font-semibold text-muted mb-1">Your reply{review.replied_at ? ` · ${fmtDate(review.replied_at)}` : ''}</p>
      <p className="text-sm whitespace-pre-wrap break-words">{review.reply}</p>
      <button type="button" className="pf-link text-sm mt-2" onClick={() => { setDraft(review.reply); setEditing(true); }}>Edit reply</button>
    </div>}

    {editing && <form onSubmit={e => { e.preventDefault(); void save(); }} className="space-y-2">
      <label className="block"><span className="sr-only">Reply to {review.buyer_name}</span>
        <textarea className="pf-textarea" rows={3} maxLength={MAX} value={draft} onChange={e => setDraft(e.target.value)} placeholder="Thank the shopper or answer their question" data-testid={`reply-box-${review.id}`} /></label>
      <ErrorLine message={error} />
      <div className="flex items-center justify-between gap-3">
        <span className="text-[11.5px] text-muted tabular">{draft.length}/{MAX}</span>
        <div className="flex gap-2">
          {review.reply && <button type="button" className="pf-btn sm ghost" onClick={() => { setDraft(review.reply); setEditing(false); }}>Cancel</button>}
          <button className="pf-btn sm" disabled={busy || !draft.trim()} data-testid={`reply-send-${review.id}`}>{busy ? 'Saving…' : review.reply ? 'Save reply' : 'Reply'}</button>
        </div>
      </div>
    </form>}
  </article>;
}

export function ReviewsPage({ merchantId }: { merchantId: string }) {
  const list = useResource<ReviewList>(`/merchants/${encodeURIComponent(merchantId)}/reviews`, 20000);
  const data = list.data;
  return <div className="space-y-6 pf-enter" data-testid="merchant-reviews">
    <PageHeader title="Reviews" description="Shopper reviews from verified pickups. Reply to each one below." />
    {list.loading && !data ? <Spinner /> : !data?.count ? <Empty title="No reviews yet" description="Shoppers can review a store after a collected order." />
      : <>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Panel><p className="text-sm text-muted">Average rating</p><p className="font-display text-3xl tabular mt-1">{data.average?.toFixed(1)} <span className="text-base text-muted">/ 5</span></p></Panel>
          <Panel><p className="text-sm text-muted">Reviews</p><p className="font-display text-3xl tabular mt-1">{data.count}</p></Panel>
          <Panel><p className="text-sm text-muted">Waiting for your reply</p><p className="font-display text-3xl tabular mt-1" data-testid="unanswered-count">{data.unanswered}</p></Panel>
        </div>
        <div className="space-y-4">{data.reviews.map(review => <ReviewCard key={review.id} review={review} merchantId={merchantId} onSaved={() => void list.refresh()} />)}</div>
      </>}
  </div>;
}
