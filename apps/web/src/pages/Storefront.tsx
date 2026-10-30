import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ChevronRight, Clock3, MapPin, Navigation, Phone, ShieldCheck, Star } from 'lucide-react';
import type { Merchant } from '../lib/api';
import { useResource } from '../lib/use-resource';
import { useApp } from '../lib/app-context';
import { Chip, Empty, ErrorLine, ProductCard, Spinner } from '../components/Shared';
import { useBasketAdd } from '../components/BasketFeedback';
import { StoreMap } from '../components/StoreMap';

export function Storefront() {
  const { slug } = useParams();
  const { demo } = useApp();
  const store = useResource<Merchant>(`/merchants/${encodeURIComponent(slug || '')}`, 15000);
  const basket = useBasketAdd(store.data?.products || []);
  const merchants = useMemo(() => store.data ? [store.data] : [], [store.data]);
  if (store.loading) return <main className="pf-container py-12"><Spinner label="Opening storefront…" /></main>;
  if (!store.data) return <main className="pf-container py-12"><ErrorLine message={store.error || 'Store not found.'} retry={store.refresh} /><Link className="pf-btn mt-5" to="/explore">Find another store</Link></main>;
  const m = store.data;
  return <main className="pf-container pt-6 pb-20">
    <nav className="flex items-center gap-1.5 text-[13px] text-muted" aria-label="Breadcrumb"><Link className="hover:text-ink" to="/explore">Explore</Link><ChevronRight size={13} /><span className="text-ink">{m.name}</span></nav>
    {store.error && <ErrorLine message={store.error} retry={store.refresh} />}
    <header className="mt-8 pb-8 border-b border-line">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <Chip kind={m.is_open ? 'green' : m.is_open === false ? 'default' : 'amber'} dot>{m.is_open ? 'Open now' : m.is_open === false ? 'Closed' : 'Hours unconfirmed'}</Chip>
        <span className="text-sm text-muted">{m.category}</span>
      </div>
      <h1 className="pf-display text-[clamp(44px,6vw,88px)] flex flex-wrap items-center gap-x-4">{m.name}{m.verified && <ShieldCheck size={36} className="text-accent shrink-0" aria-label="Verified merchant" />}</h1>
      <p className="flex items-center gap-1.5 text-[15px] mt-5"><Star size={16} className="fill-ink" aria-hidden /><strong className="font-semibold">{m.rating?.toFixed(1) || 'New'}</strong><span className="text-muted">({m.review_count} reviews)</span></p>
      {m.description && <p className="text-lg text-ink-2 mt-4 max-w-2xl leading-relaxed">{m.description}</p>}
    </header>
    {basket.feedback}
    <div className="grid grid-cols-[minmax(0,1fr)] lg:grid-cols-[minmax(0,1fr)_360px] xl:grid-cols-[minmax(0,1fr)_400px] gap-10 xl:gap-16 mt-10 items-start">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6"><h2 className="pf-heading">In-store products</h2><Chip kind="amber">{demo ? 'Seeded stock' : 'Last known availability'}</Chip></div>
        {m.products?.length ? <div className="grid grid-cols-2 md:grid-cols-3 2xl:grid-cols-4 gap-x-4 gap-y-8">{m.products.map(p => <ProductCard key={p.id} p={{ ...p, merchant_name: m.name, merchant_slug: m.slug, is_open: m.is_open }} onPick={basket.add} />)}</div> : <Empty description="This merchant has not published products yet." />}
        <section className="mt-16" aria-labelledby="reviews-heading"><h2 id="reviews-heading" className="pf-heading mb-2">Customer reviews</h2>
          {m.reviews?.length ? <div className="divide-y divide-line border-y border-line mt-5">{m.reviews.map(r => <article className="py-5" key={r.id}>
            <div className="flex flex-wrap gap-3 items-center"><span className="flex gap-0.5" role="img" aria-label={`${r.rating} out of 5 stars`}>{[1, 2, 3, 4, 5].map(n => <Star key={n} size={15} className={n <= r.rating ? 'fill-ink' : 'text-line-strong'} />)}</span>{r.demo_review && <Chip>Sample review</Chip>}<time className="text-xs text-muted ml-auto">{new Date(r.created_at).toLocaleDateString()}</time></div>
            <p className="text-[15px] mt-3 max-w-prose">{r.body}</p></article>)}</div>
            : <p className="text-sm text-muted mt-3">No reviews yet. Reviews become available after a collected order.</p>}
        </section>
      </div>
      <aside className="lg:sticky lg:top-[calc(var(--pf-header-h)+24px)] flex flex-col gap-5">
        <div className="h-72 rounded-[var(--pf-r-lg)] overflow-hidden border border-line"><StoreMap merchants={merchants} center={[m.latitude, m.longitude]} /></div>
        <section className="pf-card p-5" aria-labelledby="visit-heading"><h2 id="visit-heading" className="pf-title mb-4">Plan your visit</h2>
          <ul className="flex flex-col gap-3.5 text-sm text-ink-2">
            <li className="flex gap-3"><MapPin size={17} className="shrink-0 mt-0.5 text-muted" />{m.address}</li>
            <li className="flex gap-3"><Clock3 size={17} className="shrink-0 mt-0.5 text-muted" /><span>{m.hours || 'Contact the store for opening hours.'}{m.timezone && <span className="block text-xs text-muted mt-0.5">Timezone: {m.timezone}</span>}</span></li>
            {m.phone && <li><a className="flex gap-3 hover:underline" href={`tel:${m.phone.replace(/[^+\d]/g, '')}`}><Phone size={17} className="shrink-0 mt-0.5 text-muted" />{m.phone}</a></li>}
          </ul>
          <p className="text-xs text-muted mt-4 leading-relaxed">Preparation takes about {m.fulfillment_minutes} minutes. Wait for the store to mark your order ready.</p>
          <a className="pf-btn outline w-full mt-5" href={`https://www.openstreetmap.org/directions?to=${m.latitude}%2C${m.longitude}`} target="_blank" rel="noopener noreferrer"><Navigation size={16} />Get directions</a>
        </section>
        <p className="text-xs text-muted leading-relaxed">{demo ? 'Real product photographs. Stores, stock and reviews are seeded demo data.' : 'If inventory is stale or uncertain, contact the branch before travelling.'}</p>
      </aside>
    </div>
  </main>;
}
