import { Link } from 'react-router-dom';

const link = 'text-accent underline underline-offset-2';
type Section = { id: string; title: string; body: React.ReactNode[] };

const privacy: Section[] = [
  { id: 'location', title: 'When we use your location', body: [<>PayFound requests browser location only when you choose a location or directions action. You can decline, revoke permission in your browser, or stop using location from the Explore page. Shared coordinates remain in the app session and are not written to PayFound’s application database.</>, <>So the fictional demo stores appear near you wherever you are, every request also carries an approximate area (rounded to about 1 km, from your shared location, your last shared location on this device, or your browser time zone) and your time zone. The server uses them to pick street addresses near that area and keeps the resulting layout in memory only; nothing is saved to the database. Before you share a location, your IP address is sent once to an IP geolocation service (ipapi.co, falling back to ipwho.is) to find your city; PayFound keeps the result in memory only, rounded, and never stores your IP address. Address lookups for that area go to Google Maps Geocoding (or OpenStreetMap Nominatim when no Google key is set).</>] },
  { id: 'google', title: 'Maps and directions', body: [<>Coordinates are sent to the PayFound API for nearby search and to Google Maps for requested driving directions. Google Maps also processes map-view and device information when its maps are loaded. Traffic estimates change over time and are not a record of your movements.</>, <>Google’s processing is described in its <a className={link} href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Privacy Policy</a>. Product photo attribution is available in <a className={link} href="/image-credits.html">Image credits</a>.</>] },
];
const terms: Section[] = [
  { id: 'pilot', title: 'A development pilot', body: [<>PayFound is a development pilot. Demo stores, prices, stock and transactions are fictional. Catalogue photos retain the licenses identified in Image credits. Stock and pickup readiness must be confirmed through the application’s supported merchant workflow.</>] },
  { id: 'maps', title: 'Maps content', body: [<>Google Maps content and directions are provided subject to the <a className={link} href="https://www.google.com/help/terms_maps/" target="_blank" rel="noreferrer">Google Maps/Google Earth Additional Terms of Service</a> and Google’s Privacy Policy. Route and arrival estimates depend on available provider data and current conditions.</>] },
  { id: 'payments', title: 'Payments', body: [<>Simulated payments move no funds; PayPal sandbox transactions are labeled separately. This pilot does not establish a live connection with any pictured product brand or fictional retailer.</>] },
];

export function MapPolicies({ privacy: isPrivacy = false }: { privacy?: boolean }) {
  const sections = isPrivacy ? privacy : terms;
  return <main className="pf-container py-10 sm:py-14"><div className="pf-readable lg:grid lg:grid-cols-[200px_minmax(0,1fr)] lg:gap-16">
    <nav aria-label="On this page" className="hidden lg:block"><div className="sticky top-24"><p className="pf-label mb-3">On this page</p><ul className="space-y-2 border-l border-line">{sections.map(s => <li key={s.id}><a className="block -ml-px pl-4 border-l border-transparent text-sm text-muted hover:text-ink hover:border-ink" href={`#${s.id}`}>{s.title}</a></li>)}</ul></div></nav>
    <article>
      <p className="text-sm text-muted mb-3">PayFound development pilot</p>
      <h1 className="pf-display-xl !text-[clamp(40px,5vw,72px)] mb-12">{isPrivacy ? 'Location and privacy' : 'Terms of use'}</h1>
      <div className="space-y-12 max-w-[68ch]">{sections.map(s => <section key={s.id} id={s.id} className="scroll-mt-24"><h2 className="pf-title mb-3">{s.title}</h2><div className="space-y-4 text-[16px] leading-[1.75] text-ink-2">{s.body.map((p, i) => <p key={i}>{p}</p>)}</div></section>)}</div>
      <Link className="pf-btn outline mt-14" to="/explore">Back to Explore</Link>
    </article>
  </div></main>;
}
