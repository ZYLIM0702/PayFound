import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Bell, BarChart3, Bot, CalendarClock, Check, Clock, ClipboardList, Code2, MapPin, MessageSquare, Mic, Navigation, PackageCheck, Search, ShieldCheck, ShoppingBag, Sparkles, Store, Tag, TrendingUp, Wallet, Zap } from 'lucide-react';

const SHOPPER_FEATURES = [
  { icon: Bot, title: 'An assistant that shops with you', text: 'Ask in plain words or by voice. It finds products, builds a basket, plans a recipe, and checks the route and weather before you go.' },
  { icon: Navigation, title: 'Nearest stores first', text: 'Results are ranked by distance and driving time from where you are. Each store shows open hours and a route link.' },
  { icon: Zap, title: 'Fast from search to pickup', text: 'See live in-store stock, reserve in one tap, or pay online and choose a pickup window. The store prepares it for you.' },
];

const STEPS = [
  { icon: Search, title: 'Ask', text: 'Search, or just say what you need. The assistant looks at stores near you.' },
  { icon: Wallet, title: 'Reserve or pay', text: 'Reserve what is on the shelf, or pay with PayPal sandbox and keep your place.' },
  { icon: PackageCheck, title: 'Pick up', text: 'Choose a time window. The store has it ready, and you confirm when you collect.' },
];

const MERCHANT_FEATURES = [
  { icon: TrendingUp, title: 'AI demand forecast', text: 'Projects next week from your recent sales, weather, local events and payday patterns. Every number shows the driver behind it, and you can test what-if scenarios.' },
  { icon: BarChart3, title: 'Analytics that answer questions', text: 'Revenue, top products, orders by hour and stock cover, with saved reports and PDF or CSV export. Ask the assistant to build a report for you.' },
  { icon: ClipboardList, title: 'Inventory and count sheets', text: 'Live stock across branches, low-stock and stale-stock alerts, and a count sheet for stock checks.' },
  { icon: CalendarClock, title: 'Pickup calendar and queue', text: 'Branch rows, hourly capacity and a live queue, so pickups never pile up at the counter.' },
  { icon: MessageSquare, title: 'Reviews and shopper chats', text: 'Reply to every review, and answer each shopper in their own separate conversation.' },
  { icon: Store, title: 'POS software included', text: 'Sell in store on the same stock. Orders and stock sync with your online store on every plan.' },
];

const INTELLIGENCE = [
  { title: 'Assistant', text: 'Understands shopping requests and answers store questions. It never moves money or confirms payments on its own.' },
  { title: 'Forecast', text: 'Explainable arithmetic over your own sales history, not a black box. You see each driver and can change it.' },
  { title: 'Placement', text: 'Nearby stores rank first, with stock checked at the time you ask, so a result is something you can act on.' },
];

const PLANS = [
  { name: 'Free', price: '$0', fee: '2.5%', listings: '15', sales: 'Up to $5,000', pos: '1', featured: false, cta: 'Start free' },
  { name: 'Pro', price: '$49/mo', fee: '1.5%', listings: '300', sales: 'Up to $50,000', pos: '3', featured: true, cta: 'Choose Pro' },
  { name: 'Diamond', price: '$199/mo', fee: '0.75%', listings: 'Unlimited', sales: 'Unlimited', pos: 'Unlimited', featured: false, cta: 'Choose Diamond' },
];

const MOTION = `
@keyframes pf-land-rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes pf-land-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
.pf-land-rise { animation: pf-land-rise 0.7s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
.pf-land-card { transition: transform 0.25s ease, box-shadow 0.25s ease; }
.pf-land-card:hover { transform: translateY(-4px); box-shadow: var(--pf-shadow-card-hover); }
.pf-land-photo { overflow: hidden; }
.pf-land-photo img { transition: transform 0.9s ease; }
.pf-land-photo:hover img { transform: scale(1.04); }
.pf-land-float { animation: pf-land-float 3.2s ease-in-out infinite; }
@keyframes pf-land-grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
.pf-land-bar { transform-origin: bottom; animation: pf-land-grow 0.9s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
@keyframes pf-land-pin { from { opacity: 0; transform: translate(-50%, -100%) scale(0.6); } to { opacity: 1; transform: translate(-50%, -100%) scale(1); } }
.pf-land-pin { animation: pf-land-pin 0.6s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
@keyframes pf-land-glow-shift { to { background-position: 300% 50%; } }
@keyframes pf-land-glow-pulse {
  0%, 100% { box-shadow: 0 0 14px rgb(66 133 244 / 0.45), 0 0 28px rgb(155 114 203 / 0.25); }
  50% { box-shadow: 0 0 22px rgb(155 114 203 / 0.7), 0 0 44px rgb(217 101 112 / 0.4); }
}
/* Gemini-style: a slowly moving blue-violet-coral gradient with a breathing glow */
.pf-land-glow {
  border: 0;
  color: #fff;
  background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570, #f5a623, #4285f4) 0 50% / 300% 100%;
  animation: pf-land-glow-shift 5s linear infinite, pf-land-glow-pulse 2.8s ease-in-out infinite;
}
.pf-land-glow:hover { filter: brightness(1.08); }
@media (prefers-reduced-motion: reduce) {
  .pf-land-rise, .pf-land-float, .pf-land-glow, .pf-land-bar, .pf-land-pin { animation: none; }
  .pf-land-card, .pf-land-photo img { transition: none; }
  .pf-land-card:hover, .pf-land-photo:hover img { transform: none; box-shadow: none; }
}
`;

const SHOPPER_REASONS = [
  { icon: Navigation, title: 'Nearest first, always', text: 'Stores are sorted by real distance and driving time from where you are, not by who paid for the top spot.' },
  { icon: ShieldCheck, title: 'Stock you can trust', text: 'Shelf stock is checked at the moment you ask. Online offers are shown separately and never claim to be in store.' },
  { icon: Bot, title: 'Say it in your own words', text: 'Type or speak a need like "a 65W charger I can pick up tonight". The assistant finds it, compares options and explains the trade-offs.' },
  { icon: Zap, title: 'Quick from search to bag', text: 'Reserve in one tap, or pay and choose a pickup window. Your order is prepared before you arrive.' },
];

const NEARBY = [
  { name: 'Northside Electronics', km: '0.3 km', top: '34%', left: '46%' },
  { name: 'Civic Home & Living', km: '0.8 km', top: '58%', left: '28%' },
  { name: 'Cole Valley Pets', km: '1.2 km', top: '24%', left: '70%' },
  { name: 'Cedar Row Pantry', km: '2.1 km', top: '70%', left: '66%' },
];

const SHOWCASE = [
  { src: '/landing/app-explore.png', alt: 'PayFound browse page with stores on a map and products beside it', title: 'Browse and map', text: 'Products beside a live map. Pins show stores, and each card shows stock and distance.' },
  { src: '/landing/app-assistant.png', alt: 'PayFound assistant answering a shopping question', title: 'The assistant', text: 'Ask for what you need. It answers with product cards, routes and weather, and you decide what to reserve.' },
];

const MERCHANT_REASONS = [
  { icon: Store, title: 'Shoppers who are already close', text: 'Your listings show to people nearby who want to buy today. Pickup brings them through the door.' },
  { icon: TrendingUp, title: 'Know what sells before it does', text: 'The forecast projects next week from your own sales, weather, events and payday, so you order less and sell out less.' },
  { icon: Sparkles, title: 'One workspace, not five tools', text: 'Orders, stock, pickup, analytics, reviews and chats live in one place, and the assistant can answer questions about them.' },
  { icon: Wallet, title: 'Your fees go down as you grow', text: 'Free covers small shops. Pro and Diamond lower PayFound\'s fee on every captured sale, with POS software on every plan.' },
];

const EXTRAS = [
  { icon: Clock, title: 'Shortest-queue pickup', text: 'The checkout suggests the three open windows with the shortest queues, so you collect without waiting.', tag: 'All shoppers' },
  { icon: TrendingUp, title: 'Stock-up suggestions', text: 'The forecast flags what is likely to sell out this week, with an order quantity and a supplier email draft to review. Nothing is sent for you.', tag: 'All businesses' },
  { icon: Tag, title: 'Online price check', text: 'See each local product beside its online price, so you know when the store is competitive.', tag: 'Pro and Diamond' },
  { icon: Bell, title: 'Price watch', text: 'Save a product and see when the local price beats the online price, or when an online deal drops.', tag: 'All shoppers' },
  { icon: PackageCheck, title: 'Order tracking', text: 'Follow each order from reserved to collected: when the store confirms stock, accepts, prepares and marks it ready, with the times for each step.', tag: 'All shoppers' },
  { icon: Code2, title: 'API and SDKs', text: 'An OpenAPI spec of 130 endpoints, with TypeScript and Python SDKs for building on PayFound.', tag: 'Diamond' },
];

const FORECAST_BARS = [46, 58, 52, 74, 88, 66, 81];
const FORECAST_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function Landing() {
  const { hash } = useLocation();
  useEffect(() => {
    if (hash) document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [hash]);
  return (
    <div className="mx-auto w-full max-w-[1180px] overflow-x-hidden">
      <style>{MOTION}</style>
      <main>
        <section className="pf-container pt-10 pb-14 md:pt-16 md:pb-20 grid gap-10 lg:grid-cols-[1fr_1.4fr] lg:items-stretch">
          <div>
            <p className="pf-eyebrow mb-4">AI-powered local commerce</p>
            <h1 className="pf-heading text-4xl md:text-5xl">Find it nearby. Know it is in stock. Pick it up today.</h1>
            <p className="mt-5 text-muted text-[17px] max-w-xl">PayFound is an assistant that shops with you. It ranks the nearest stores, checks live stock, and gets you from search to pickup in minutes. Stores get AI forecasts, analytics and a full workspace on the same data.</p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link to="/agent" className="pf-btn lg pf-land-glow"><Sparkles size={17} />Ask the assistant</Link>
              <Link to="/explore" className="pf-btn outline lg"><MapPin size={17} />Find nearby stores</Link>
              <Link to="/merchant/onboard" className="pf-btn ghost lg">Join as a business</Link>
            </div>
          </div>
          <div className="pf-land-photo pf-land-rise relative min-h-[360px] lg:min-h-0 rounded-[var(--pf-r-lg)] w-full" style={{ animationDelay: "0.15s" }}><img src="/landing/hero-shopper.jpg" alt="A shopper carrying purchases out of a local store" className="absolute inset-0 w-full h-full object-cover rounded-[var(--pf-r-lg)]" loading="eager" /></div>
        </section>

        <section className="pf-container pb-14 grid gap-4 md:grid-cols-3" aria-label="Highlights">
          {[
            { icon: Mic, label: 'Ask by voice or text' },
            { icon: Navigation, label: 'Nearest stores, with driving time' },
            { icon: Zap, label: 'Reserve or pay in a few taps' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="pf-card p-5 flex items-center gap-3 pf-land-card pf-land-rise"><Icon size={20} className="text-accent shrink-0 pf-land-float" /><span className="font-semibold">{label}</span></div>
          ))}
        </section>

        <section className="py-16">
        <div className="pf-container grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-center">
          <div>
            <p className="pf-eyebrow mb-2">Why shoppers choose PayFound</p>
            <h2 className="pf-heading text-3xl md:text-4xl">The closest store with what you need, in seconds.</h2>
            <ul className="mt-6 grid gap-4 sm:grid-cols-2">
              {SHOPPER_REASONS.map(({ icon: Icon, title, text }) => (
                <li key={title} className="pf-card p-5 pf-land-card">
                  <Icon size={20} className="text-accent" />
                  <h3 className="mt-3 font-semibold">{title}</h3>
                  <p className="mt-1.5 text-muted text-[14.5px]">{text}</p>
                </li>
              ))}
            </ul>
          </div>
          <div className="pf-card p-4 md:p-5 pf-land-card" aria-label="Map example: stores near you">
            <div className="flex items-center justify-between mb-3">
              <p className="font-semibold text-sm">Nearest now</p>
              <span className="pf-chip green">Live stock</span>
            </div>
            <div className="relative aspect-[4/3] rounded-[var(--pf-r-md)] bg-canvas overflow-hidden border border-line">
              <svg viewBox="0 0 400 300" className="absolute inset-0 w-full h-full" aria-hidden="true">
                <path d="M0 120 C120 100 220 150 400 110" stroke="#d8dadf" strokeWidth="14" fill="none" />
                <path d="M90 0 C130 120 160 200 150 300" stroke="#d8dadf" strokeWidth="10" fill="none" />
                <path d="M260 0 L300 300" stroke="#e6e7ea" strokeWidth="8" fill="none" />
                <path d="M0 230 L400 200" stroke="#e6e7ea" strokeWidth="8" fill="none" />
                <circle cx="180" cy="150" r="9" fill="var(--pf-blue)" opacity="0.2" />
                <circle cx="180" cy="150" r="5" fill="var(--pf-blue)" />
              </svg>
              {NEARBY.map((store, i) => (
                <div key={store.name} className="pf-land-pin absolute" style={{ top: store.top, left: store.left, animationDelay: `${0.15 * i}s` }}>
                  <span className="block whitespace-nowrap text-[11.5px] font-semibold bg-surface border border-line rounded-full px-2 py-1 shadow-sm">{store.name.split(' ')[0]} · {store.km}</span>
                </div>
              ))}
            </div>
            <ol className="mt-4 divide-y divide-line text-sm">
              {NEARBY.map(store => (
                <li key={store.name} className="flex items-center justify-between py-2.5"><span className="font-medium">{store.name}</span><span className="tabular text-muted">{store.km}</span></li>
              ))}
            </ol>
          </div>
        </div>
        </section>

        <section className="bg-sunk py-16 my-6 rounded-[var(--pf-r-lg)]">
        <div className="pf-container">
          <p className="pf-eyebrow mb-2">For shoppers</p>
          <h2 className="pf-heading text-3xl md:text-4xl max-w-2xl">Ask once. Get the nearest stores, with stock you can trust.</h2>
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {SHOPPER_FEATURES.map(({ icon: Icon, title, text }) => (
              <article key={title} className="pf-card p-6 pf-land-card">
                <Icon size={22} className="text-accent" />
                <h3 className="mt-4 font-semibold text-lg">{title}</h3>
                <p className="mt-2 text-muted text-[15px]">{text}</p>
              </article>
            ))}
          </div>
          <ol className="mt-10 grid gap-4 md:grid-cols-3">
            {STEPS.map(({ icon: Icon, title, text }, i) => (
              <li key={title} className="flex gap-4 items-start pf-land-rise" style={{ animationDelay: `${0.1 * i}s` }}>
                <span className="w-10 h-10 rounded-full bg-ink text-white grid place-items-center shrink-0 font-semibold">{i + 1}</span>
                <div><p className="font-semibold flex items-center gap-2"><Icon size={16} className="text-muted" />{title}</p><p className="text-muted text-[15px] mt-1">{text}</p></div>
              </li>
            ))}
          </ol>
        </div>
        </section>

        <section className="bg-ink text-white py-16 my-6 rounded-[var(--pf-r-lg)]">
        <div className="pf-container grid gap-10 lg:grid-cols-2 lg:items-center">
          <div className="pf-land-photo relative min-h-[360px] lg:min-h-[480px] rounded-[var(--pf-r-lg)] w-full"><img src="/landing/grocery-shoppers.jpg" alt="Shoppers browsing a local grocery store" className="absolute inset-0 w-full h-full object-cover rounded-[var(--pf-r-lg)]" loading="lazy" /></div>
          <div>
            <p className="pf-eyebrow mb-2 text-white/60">Built on intelligent systems</p>
            <h2 className="pf-heading text-3xl text-white">One data layer behind the assistant, the forecast and the analytics.</h2>
            <ul className="mt-6 space-y-4">
              {INTELLIGENCE.map(item => (
                <li key={item.title} className="flex gap-3"><ShieldCheck size={18} className="text-accent shrink-0 mt-0.5" /><div><p className="font-semibold">{item.title}</p><p className="text-white/70 text-[15px]">{item.text}</p></div></li>
              ))}
            </ul>
          </div>
        </div>
        </section>

        <section className="py-16">
        <div className="pf-container">
          <p className="pf-eyebrow mb-2">See it in the app</p>
          <h2 className="pf-heading text-3xl md:text-4xl max-w-2xl">Real screens, the same ones you will use.</h2>
          <div className="mt-8 grid gap-5 md:grid-cols-2">
            {SHOWCASE.map(({ src, alt, title, text }) => (
              <figure key={title} className="pf-card overflow-hidden pf-land-card">
                <div className="pf-land-photo bg-sunk border-b border-line"><img src={src} alt={alt} className="w-full aspect-[16/10] object-cover object-top" loading="lazy" /></div>
                <figcaption className="p-5"><p className="font-semibold">{title}</p><p className="mt-1 text-muted text-[14.5px]">{text}</p></figcaption>
              </figure>
            ))}
          </div>
        </div>
        </section>

        <section className="py-16">
        <div className="pf-container">
          <p className="pf-eyebrow mb-2">For businesses</p>
          <h2 className="pf-heading text-3xl md:text-4xl max-w-2xl">Know what sells tomorrow, and run the counter without the spreadsheets.</h2>
          <div className="mt-8 grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] lg:items-start">
            <div className="pf-land-photo relative min-h-[360px] lg:min-h-[480px] rounded-[var(--pf-r-lg)] w-full lg:sticky lg:top-24"><img src="/landing/store-counter.jpg" alt="A store employee standing at the counter" className="absolute inset-0 w-full h-full object-cover rounded-[var(--pf-r-lg)]" loading="lazy" /></div>
            <div className="grid gap-4 sm:grid-cols-2">
              {MERCHANT_FEATURES.map(({ icon: Icon, title, text }) => (
                <article key={title} className="pf-card p-5 pf-land-card">
                  <Icon size={20} className="text-accent" />
                  <h3 className="mt-3 font-semibold">{title}</h3>
                  <p className="mt-1.5 text-muted text-[14.5px]">{text}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
        </section>

        <section className="py-16">
        <div className="pf-container">
          <p className="pf-eyebrow mb-2">Smarter pickups, stock and prices</p>
          <h2 className="pf-heading text-3xl md:text-4xl max-w-2xl">Details that save time for shoppers and stores.</h2>
          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {EXTRAS.map(({ icon: Icon, title, text, tag }) => (
              <article key={title} className="pf-card p-6 pf-land-card flex flex-col">
                <div className="flex items-center justify-between gap-3">
                  <Icon size={22} className="text-accent" />
                  <span className="pf-chip">{tag}</span>
                </div>
                <h3 className="mt-4 font-semibold text-lg">{title}</h3>
                <p className="mt-2 text-muted text-[15px]">{text}</p>
              </article>
            ))}
          </div>
          <p className="mt-6 text-[14px] text-muted">Developers can read the <a className="pf-link" href="/developers/api/index.html">API reference</a>. Queue times are estimates from booking levels, not measured waits.</p>
        </div>
        </section>

        <section className="bg-sunk py-16 my-6 rounded-[var(--pf-r-lg)]">
        <div className="pf-container grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-center">
          <div>
            <p className="pf-eyebrow mb-2">Why businesses join</p>
            <h2 className="pf-heading text-3xl md:text-4xl">Shoppers who are close, and the numbers to serve them.</h2>
            <ul className="mt-6 space-y-5">
              {MERCHANT_REASONS.map(({ icon: Icon, title, text }) => (
                <li key={title} className="flex gap-4">
                  <span className="w-10 h-10 rounded-full bg-surface border border-line grid place-items-center shrink-0"><Icon size={18} className="text-accent" /></span>
                  <div><p className="font-semibold">{title}</p><p className="text-muted text-[15px] mt-1">{text}</p></div>
                </li>
              ))}
            </ul>
          </div>
          <div className="pf-card p-5 md:p-6 pf-land-card" aria-label="Forecast example for the next seven days">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-sm">Next 7 days · orders forecast</p>
              <span className="pf-chip blue">AI forecast</span>
            </div>
            <div className="mt-6 flex items-end gap-3 h-44" role="img" aria-label="Bar chart: forecast orders by day">
              {FORECAST_BARS.map((value, i) => (
                <div key={FORECAST_DAYS[i]} className="flex-1 flex flex-col items-center justify-end h-full gap-2">
                  <div className={`pf-land-bar w-full rounded-t-[var(--pf-r-sm)] ${i === 4 ? 'bg-accent' : 'bg-ink'}`} style={{ height: `${value}%`, animationDelay: `${0.08 * i}s` }} />
                  <span className="text-[11.5px] text-muted">{FORECAST_DAYS[i]}</span>
                </div>
              ))}
            </div>
            <p className="mt-5 text-[13.5px] text-muted">Example: Friday is highest, payday and a local event. Every driver is shown, and you can change any of them.</p>
          </div>
        </div>
        </section>

        <section id="pricing" className="bg-surface py-16 my-6 rounded-[var(--pf-r-lg)] scroll-mt-24" aria-labelledby="pricing-title">
        <div className="pf-container">
          <p className="pf-eyebrow mb-2">Pricing</p>
          <h2 id="pricing-title" className="pf-heading text-3xl md:text-4xl">Start free. Grow into the plan you need.</h2>
          <p className="mt-3 text-muted max-w-2xl">Plans cover every store on your business account. The platform fee is charged on captured sales on top of PayPal's own processing fees. PayPal POS card rates are 2.29% + 9c card-present and QR, 3.49% + 9c keyed-in, per PayPal's published rates.</p>
          <div className="mt-8 grid gap-5 lg:grid-cols-3">
            {PLANS.map(plan => (
              <article key={plan.name} className={`pf-card p-6 flex flex-col gap-4 pf-land-card ${plan.featured ? 'ring-2 ring-ink' : ''}`}>
                <div className="flex items-center justify-between">
                  <h3 className="font-display text-xl font-semibold">{plan.name}</h3>
                  {plan.featured && <span className="pf-chip ink">Most popular</span>}
                </div>
                <p className="font-display text-3xl tabular">{plan.price}</p>
                <dl className="grid grid-cols-2 gap-3 text-sm">
                  <div><dt className="text-muted">Platform fee</dt><dd className="font-semibold tabular">{plan.fee}</dd></div>
                  <div><dt className="text-muted">Listings</dt><dd className="font-semibold">{plan.listings}</dd></div>
                  <div><dt className="text-muted">Sales a month</dt><dd className="font-semibold">{plan.sales}</dd></div>
                  <div><dt className="text-muted">POS registers</dt><dd className="font-semibold">{plan.pos}</dd></div>
                </dl>
                <p className="text-sm text-muted flex gap-2"><Check size={15} className="text-accent shrink-0 mt-0.5" />POS software and the AI assistant on every plan</p>
                <Link to="/merchant/onboard" className={`pf-btn ${plan.featured ? 'accent' : 'outline'} w-full mt-auto`}>{plan.cta}</Link>
              </article>
            ))}
          </div>
        </div>
        </section>

        <section className="bg-accent text-white py-16 my-6 rounded-[var(--pf-r-lg)]">
        <div className="pf-container grid gap-6 md:grid-cols-[1fr_auto] md:items-center">
          <div>
            <h2 className="pf-heading text-3xl text-white">Open your store in minutes, or try the shopper side now.</h2>
            <p className="mt-3 text-white/80">Set your hours and stock, and shoppers nearby can find you. Or ask the assistant what is around you.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/merchant/onboard" className="pf-btn lg !bg-white !text-ink"><ShoppingBag size={17} />Join as a business</Link>
            <Link to="/agent" className="pf-btn lg !bg-transparent !text-white !border-white/60 hover:!bg-white/10"><Sparkles size={17} />Try the assistant</Link>
          </div>
        </div>
        </section>
      </main>

    </div>
  );
}
