/**
 * PayFound generative-UI library: schemas, descriptions and prompt options only.
 * No React or CSS is imported here so `npm run agent:prompt` can build the model
 * instructions in plain Node. Renderers are attached in `library.tsx`.
 *
 * Design rule: PayFound components take IDs, never facts. Each renderer fetches
 * live, authorised data itself, so the model cannot show a wrong price, stock
 * level, ETA or order status.
 */
import { z } from 'zod/v4';
import { defineComponent, type ComponentRenderer, type Library } from '@openuidev/react-lang';
import { openuiChatLibrary } from '@openuidev/react-ui/genui-lib';
import { openuiChatPromptOptions } from '@openuidev/react-ui/genui-lib/prompt-options';

const ids = (what: string) => z.array(z.string()).describe(what);

export const specs = {
  OfferGrid: {
    description: 'PRIMARY way to show local products. Live product cards (photo, price, stock freshness, store, distance) with Add to basket / View / Show on map. Never type prices or stock yourself: pass the product ids from search_products / get_product results.',
    props: z.object({
      productIds: ids('Product ids (the `id` field of search_products results), best match first. 1-8 ids. Only ids returned by a tool in this conversation.'),
      title: z.string().optional().describe('Optional short heading, e.g. "Closest in stock".'),
    }),
  },
  Offer: {
    description: 'One live product card, larger than a grid cell. Use when recommending a single best option.',
    props: z.object({ productId: z.string().describe('Product id returned by a tool.') }),
  },
  StoreMap: {
    description: 'Interactive map of stores with the shopper location dot and optional live driving route. Use whenever where-to-go matters. Pins are loaded from the store ids; do not describe coordinates in text.',
    props: z.object({
      storeIds: ids('Store ids (`merchant_id` from tool results) or store slugs to pin. 1-8.'),
      focusProductId: z.string().optional().describe('Product id whose store should be highlighted on the map.'),
      showRoute: z.boolean().optional().describe('true to draw the live driving route to the focused product store (needs the shopper location; the card asks for it).'),
    }),
  },
  RouteCard: {
    description: 'Live driving ETA, distance, traffic delay and arrival time to the store that holds a product. Fetched live, never estimate travel time yourself. Asks the shopper to share location if needed.',
    props: z.object({ productId: z.string().describe('Product id whose store to route to.') }),
  },
  WeatherCard: {
    description: 'Current weather and the next hours at a place, fetched live. Use for trips, bike rides, outdoor pickups.',
    props: z.object({
      latitude: z.number().describe('Latitude from a tool result (store or user location).'),
      longitude: z.number().describe('Longitude from a tool result.'),
      label: z.string().describe('Place name shown on the card, e.g. "Mission Hardware".'),
    }),
  },
  CompareOffers: {
    description: 'The same product across local stores side by side, lowest price highlighted, with distance and stock. Live data.',
    props: z.object({ productId: z.string().describe('Any offer id of the product; the card finds the other stores itself.') }),
  },
  StoreSummary: {
    description: 'Store card: open/closed now, hours, address, rating, typical ready time, with Open store and Directions.',
    props: z.object({ storeSlug: z.string().describe('Store slug from a tool result.') }),
  },
  Reviews: {
    description: 'Recent customer reviews for a store, live.',
    props: z.object({
      storeSlug: z.string().describe('Store slug from a tool result.'),
      limit: z.number().optional().describe('How many reviews, default 3, max 6.'),
    }),
  },
  ReserveAndPay: {
    description: 'Human-in-the-loop checkout card. PROPOSES a pickup reservation: it shows the server-validated basket and total, and the shopper themself taps Reserve then pays (PayPal sandbox, or a labelled demo simulation). You can never reserve or pay for anyone; only offer this card when the shopper clearly wants to buy. All items must come from ONE store.',
    props: z.object({
      productIds: ids('Product ids to reserve, all from the same store and branch.'),
      quantities: z.array(z.number()).optional().describe('Quantity per product id, same order. Defaults to 1 each.'),
    }),
  },
  OrderStatus: {
    description: 'Live status of one of the shopper orders (reserved, paid, preparing, ready for pickup...) with a link to the order page.',
    props: z.object({ orderId: z.string().describe('Order id from my_orders / get_order.') }),
  },
  OrderList: {
    description: 'The shopper recent orders with live status. Use for "where are my orders".',
    props: z.object({}),
  },
  KpiRow: {
    description: 'Row of headline merchant metrics. Numbers must come from tool results (merchant_dashboard, sales_summary). State the currency in the value, and say "recorded" for sales; never present revenue as profit.',
    props: z.object({
      metrics: z.array(z.object({
        label: z.string(), value: z.string().describe('Formatted value, e.g. "$1,240.00" or "12".'),
        hint: z.string().optional().describe('Short context, e.g. "this week".'),
        tone: z.enum(['ok', 'warn', 'bad']).optional(),
      })).describe('2-5 metrics.'),
    }),
  },
  StockAlerts: {
    description: 'Merchant only. Live list of low-stock and stale-stock products with a Record count link to inventory. Fetches itself; no data needed besides the merchant id.',
    props: z.object({ merchantId: z.string().describe('The merchant id given in the conversation context.') }),
  },
  MerchantOrderQueue: {
    description: 'Merchant only. Live queue of orders needing action, with buttons the merchant clicks themself (Confirm stock, Mark preparing / ready / collected). You never change an order yourself.',
    props: z.object({
      merchantId: z.string().describe('The merchant id given in the conversation context.'),
      status: z.string().optional().describe('Optional status filter such as PAID, PREPARING, READY. Default: everything still open.'),
    }),
  },
  ReportCard: {
    description: 'Merchant only. A printable report for the merchant own store (sections with metrics, tables and charts) that offers Open in Analytics and Export PDF. Call build_report first (and save_report if the merchant asked to save it), then show this card with the same kind, days and focus. Fetches its own numbers; type none.',
    props: z.object({
      merchantId: z.string().describe('The merchant id given in the conversation context.'),
      kind: z.enum(['full', 'sales', 'products', 'orders', 'stock', 'pickup']).describe('Report type; the same value passed to build_report.'),
      days: z.number().optional().describe('Days covered, 1-90, default 30.'),
      focus: z.string().optional().describe('Optional category, branch or product the report was narrowed to.'),
      title: z.string().optional().describe('Optional heading, e.g. the name the merchant gave the report.'),
    }),
  },
} as const;

export type SpecName = keyof typeof specs;
export type Renderers = { [K in SpecName]: ComponentRenderer<any> };

const inCard: SpecName[] = Object.keys(specs) as SpecName[];

/** Build the PayFound library; `renderers` supplies React components (stubs in prompt generation). */
export function buildLibrary(renderers: Renderers): Library {
  const defined = inCard.map(name => defineComponent({ name, description: specs[name].description, props: specs[name].props as never, component: renderers[name] as never }));
  return openuiChatLibrary.extend!({ components: { add: defined.map(component => ({ component: component as never, slots: ['Card'] })) } }) as unknown as Library;
}

export const promptOptions = {
  ...openuiChatPromptOptions,
  inlineMode: true,
  preamble: 'You compose PayFound answers as short text plus generative UI written in openui-lang. PayFound shows live local stock, so the UI components below fetch their own live data from ids.',
  additionalRules: [
    ...(openuiChatPromptOptions.additionalRules || []).filter(rule => !/realistic\/plausible data|Quantitative asks get a chart/.test(rule)),
    'NEVER invent data. Prices, stock, distances, ETAs, hours, ratings and order status must come from tool results; prefer PayFound components (OfferGrid, Offer, StoreMap, RouteCard, WeatherCard, CompareOffers, StoreSummary, Reviews, OrderStatus, OrderList, StockAlerts, MerchantOrderQueue, ReportCard) that take IDs and fetch live data themselves, instead of typing numbers into Table, Text or cards.',
    'For shopping questions answer with at most two sentences of text, then ONE fenced openui-lang block: root = Card([...]) with an OfferGrid of the best 3-6 productIds, a StoreMap of their stores when location matters, a RouteCard for the top pick when the shopper wants to go, and FollowUpBlock suggestions last. Do not repeat in prose what the components already show.',
    'Never use Callout or TextCallout for prices, stock or ETAs. Use them only for short, important caveats (for example a stale stock timestamp or that online offers are not local stock).',
    'Online (Channel3) offers are NOT local stock: label them "Online" in the text, never put them in OfferGrid (they have no PayFound product id); link them with Button(label, @OpenUrl(url)) using only URLs from the tool result.',
    'ReserveAndPay only PROPOSES a reservation; the shopper taps Reserve and pays. Never say you reserved, paid or refunded anything. Payments and refunds are never performed by you.',
    'Merchant answers: KpiRow for headline numbers (from tool results, state currency, say "recorded" not profit), StockAlerts / MerchantOrderQueue for live lists (pass the merchant id from context), charts only for numbers returned by a tool.',
    'Report requests ("build me a sales report"): call build_report (and save_report only if asked to save), then answer with one sentence and a Card containing ReportCard(merchantId, kind, days, focus). Never retype report numbers; the ReportCard shows them and offers Open in Analytics and Export PDF. Say amounts are recorded order values per currency, not profit.',
    'Use a Button with @ToAssistant for natural next questions ("Cheaper options", "Open now only"). Never add a button for something you cannot do.',
    'Keep a calm, plain tone; no emoji; money with currency symbol exactly as the tool returned.',
  ],
  examples: [
    `Example — shopper asks "where can I get a USB-C charger tonight?" (after search_products returned ids p_101, p_204, p_377 from stores m_1, m_2):

Three open stores nearby have one in stock. The closest is a 12-minute drive.

\`\`\`openui-lang
root = Card([grid, map, route, follow])
grid = OfferGrid(["p_101", "p_204", "p_377"], "In stock near you")
map = StoreMap(["m_1", "m_2"], "p_101", true)
route = RouteCard("p_101")
follow = FollowUpBlock([f1, f2])
f1 = FollowUpItem("Only show what is open now")
f2 = FollowUpItem("Compare prices for the cheapest one")
\`\`\``,
    `Example — merchant asks "what needs attention today?" (merchant id m_1 from context):

Two things need you today: stock that is running out and orders waiting for confirmation.

\`\`\`openui-lang
root = Card([kpis, stock, queue])
kpis = KpiRow([{label: "Open orders", value: "4", hint: "paid, not collected"}, {label: "Low stock", value: "3", tone: "warn"}])
stock = StockAlerts("m_1")
queue = MerchantOrderQueue("m_1")
\`\`\``,
  ],
};
