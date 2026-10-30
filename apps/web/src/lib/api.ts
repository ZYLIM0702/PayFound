import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { invitationSessionFromHash } from './navigation';

export type Role = 'consumer' | 'merchant' | 'admin';
export type Membership = { merchant_id: string; merchant_name: string; role: string };
export type Identity = { subject: string; role: Role; memberships: Membership[]; merchant_ids: string[] };
export type Merchant = {
  id: string; slug: string; name: string; description: string; category: string;
  address: string; latitude: number; longitude: number; phone: string; hours: string;
  timezone?: string; is_open: boolean | null; status_override: string;
  fulfillment_minutes: number; verified: boolean; emoji: string; rating: number | null;
  review_count: number; products?: Product[]; reviews?: Review[];
};
export type MerchantLocation = {
  id: string; merchant_id: string; name: string; address: string; latitude: number;
  longitude: number; timezone: string; phone?: string; hours?: Record<string, {start: string; end: string}[]>;
  special_hours?: Record<string, {start: string; end: string}[]>;
  status_override?: string; active?: boolean;
};
export type Staff = { id: string; subject: string; email?: string; role: string; merchant_id: string };
export type Product = {
  id: string; merchant_id: string; name: string; description: string; category: string;
  sku: string; price_cents: number; currency: string; quantity: number; available_quantity: number;
  stock_updated_at: string; image_emoji: string; image_url?: string | null; active: boolean;
  in_stock: boolean; freshness: 'fresh' | 'stale'; merchant_name?: string;
  merchant_slug?: string; merchant_address?: string; is_open?: boolean | null; distance_km?: number;
  location_id?: string | null; location_name?: string | null;
  availability_state?: string; availability_source?: string; source?: string;
  source_metadata?: Record<string, unknown> | null;
  checkout_mode?: 'payfound' | 'merchant_native' | string | null;
  checkout_connection_id?: string | null;
  latitude?: number; longitude?: number; comparison_count?: number; brand?: string | null;
};
export type Review = { id: string; rating: number; body: string; created_at: string; demo_review?: boolean; visible?: boolean; merchant_id?: string };
export type PickupSlot = { id: string; start_at: string; end_at: string; capacity: number; remaining: number; location_id?: string; timezone?: string };
export type OrderItem = { product_id: string; product_name?: string; name?: string; image_url?: string | null; quantity: number; price_cents?: number; unit_price_cents?: number; amount_cents?: number; location_id?: string; location_name?: string };
export type Order = {
  id: string; merchant_id: string; merchant_name: string; merchant_slug: string; product_id: string;
  product_name: string; quantity: number; amount_cents: number; currency: string; status: string;
  payment_status: string; payment_mode?: string; paypal_order_id?: string; hold_expires_at: string;
  created_at: string; buyer_name: string; can_review: boolean; items?: OrderItem[];
  pickup?: PickupSlot | null; pickup_slot?: PickupSlot | null; pickup_window?: PickupSlot | null;
  confirmation_status?: string; confirmed_at?: string | null; location_id?: string; timezone?: string;
  fulfilment_proof?: { state: string; actor: string; proof: string; created_at: string }[];
};
export type Config = {
  demo_mode: boolean; paypal_sandbox_enabled: boolean; paypal_client_id: string | null;
  paypal_environment: string; channel3_enabled: boolean; ag_studio_enabled: boolean;
  supabase_auth_enabled: boolean; supabase_url?: string; supabase_publishable_key?: string;
  remote_ai_enabled?: boolean; shopify_enabled?: boolean; woocommerce_enabled?: boolean;
  routing?: { road_routes: boolean; traffic_configured: boolean; provider: string; refresh_seconds: number;
    google_maps_browser_key?: string; google_maps_map_id?: string };
  integration_capabilities?: Record<string, unknown>; [key: string]: unknown;
};
export type Dashboard = { merchant_id: string | null; product_count: number; low_stock_count: number; revenue_cents: number; order_count: number; pending_count: number; products: Product[]; orders: Order[] };
export type AdminOverview = { merchants: Merchant[]; orders: Order[]; reviews: Review[]; audit: { id: number; action: string; actor: string; entity_id: string; created_at: string }[] };
export type ReconciliationJob = {
  id: string; order_id?: string | null; status?: string; attempts?: number; max_attempts?: number;
  error?: string | null; last_error?: string | null; created_at?: string; updated_at?: string;
  [key: string]: unknown;
};
export type ReconciliationQueue = { orders: Order[]; failed_jobs: ReconciliationJob[] };
export type IntegrationStatus = { integrations: { id: string; name: string; status: string; detail: string }[] };
export type ConnectorCheckout = { url: string; mode: string };
export type AgentResult = { reply: string; products?: Product[]; mode: string; tools_used: string[] };
export type OnlineOffer = { title: string; price: string | number | null; currency?: string; merchant: string; image: string | null; url: string; product_id?: string;
  source?: 'channel3'; condition?: string | null; shipping_summary?: string; seller?: string | null };
export type OnlineSources = Record<string, { status: 'ok' | 'not_configured' | 'unavailable'; message?: string }>;
export type Connection = { id: string; provider: string; status: string; merchant_id: string; capabilities: string[] | Record<string, boolean>; last_synced_at?: string | null; last_error?: string | null; shop_domain?: string; store_url?: string; authorization_url?: string };
export type Provider = { id?: string; provider?: string; name?: string; enabled?: boolean; available?: boolean; configured?: boolean; status?: string; capabilities?: string[] | Record<string, boolean>; reason?: string };

let config: Config | null = null;
let role: Role = 'consumer';
let demoRole: Role = 'consumer';
let token: string | null = null;
export let supabase: SupabaseClient | null = null;
let clientSettings = '';
let clientReady: Promise<SupabaseClient> | null = null;

export function isLocalDemo(value: Config | null = config) {
  return value?.demo_mode === true && ['localhost', '127.0.0.1', '[::1]', '::1'].includes(window.location.hostname);
}
export function configureApi(value: Config) { config = value; }
// Called after /config, before any auth subscription or session read.
export async function configureSupabase(value: Config): Promise<SupabaseClient | null> {
  configureApi(value);
  const url = value.supabase_url || import.meta.env.VITE_SUPABASE_URL || '';
  const key = value.supabase_publishable_key || import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY || '';
  if (!url || !key) return null;
  const settings = `${url}:${key}`;
  if (!supabase || settings !== clientSettings) {
    const invitation = invitationSessionFromHash(window.location.hash);
    const client = createClient(url, key, { auth: { flowType: 'pkce', detectSessionInUrl: !invitation, persistSession: true, autoRefreshToken: true } });
    supabase = client;
    clientSettings = settings;
    // Admin invitations are implicit links, not PKCE exchanges. Install their
    // session explicitly while retaining PKCE for signup and recovery requests.
    clientReady = (async () => {
      if (invitation) {
        try {
          const { error } = await client.auth.setSession(invitation);
          if (error) throw error;
        } finally {
          window.history.replaceState(window.history.state, '', window.location.pathname + window.location.search);
        }
      }
      return client;
    })().catch(issue => {
      // Let a later retry read the SDK's normal session state without repeatedly
      // consuming an expired invitation fragment.
      if (supabase === client) clientReady = Promise.resolve(client);
      throw issue;
    });
  }
  return clientReady ? await clientReady : supabase;
}
export const setRole = (value: Role) => { role = value; };
export const setDemoRole = (value: Role) => { demoRole = value; role = value; };
export const getRole = () => role;
export const setToken = (value: string | null) => { token = value; };
// Approximate (2 dp, about 1 km) viewer area and time zone. The API places the fictional demo stores around it per request.
let anchor: { latitude: number; longitude: number } | null = null;
let anchorVersion = 0;
const anchorListeners = new Set<() => void>();
const browserTimeZone = () => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch { return ''; } };
export function setAnchor(value: { latitude: number; longitude: number } | null) {
  const next = value ? { latitude: Math.round(value.latitude * 100) / 100, longitude: Math.round(value.longitude * 100) / 100 } : null;
  if (anchor?.latitude === next?.latitude && anchor?.longitude === next?.longitude) return;
  anchor = next; anchorVersion++;
  anchorListeners.forEach(listener => listener());
}
export const subscribeAnchor = (listener: () => void) => { anchorListeners.add(listener); return () => { anchorListeners.delete(listener); }; };
export const getAnchorVersion = () => anchorVersion;
/** Re-fetch every useResource without changing the anchor (used when a cell's layout finishes computing). */
export function bumpAnchorVersion() { anchorVersion++; anchorListeners.forEach(listener => listener()); }
// Boot gate: store/product data waits until the viewer's demo-store layout is known, so nothing is fetched with the wrong anchor.
const GATED = ['/products', '/merchants', '/catalogue', '/assistant', '/routing', '/online'];
let gate: Promise<void> | null = null;
let releaseGate: (() => void) | null = null;
export function openGate() { gate = new Promise<void>(resolve => { releaseGate = resolve; }); }
export function closeGate() { releaseGate?.(); gate = null; releaseGate = null; }
const waitForGate = (path: string) => gate && GATED.some(prefix => path.startsWith(prefix)) ? gate : undefined;
// Responses report whether the server had the layout ready (x-pf-placement: relocated|original|pending).
let placementSignal: ((state: string) => void) | null = null;
export const onPlacementSignal = (fn: ((state: string) => void) | null) => { placementSignal = fn; };
const noteResponse = (response: Response) => { const state = response.headers.get('x-pf-placement'); if (state && state !== 'relocated') placementSignal?.(state); };
function placementHeaders(headers: Headers) {
  if (anchor) headers.set('x-pf-anchor', `${anchor.latitude.toFixed(2)},${anchor.longitude.toFixed(2)}`);
  const zone = browserTimeZone();
  if (zone) headers.set('x-pf-timezone', zone);
}
export const cash = (cents: number, currency = 'USD') => new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(cents / 100);
export const localDateKey = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
export const messageOf = (error: unknown) => error instanceof Error ? error.message : 'Something went wrong. Try again.';
export const scoped = (path: string, merchantId: string) => `${path}${path.includes('?') ? '&' : '?'}merchant_id=${encodeURIComponent(merchantId)}`;
export function safeExternalUrl(value?: string | null) {
  if (!value) return undefined;
  try { const url = new URL(value); return url.protocol === 'https:' ? url.href : undefined; } catch { return undefined; }
}
export const orderItems = (order: Order): OrderItem[] => order.items?.length ? order.items : [{ product_id: order.product_id, product_name: order.product_name, quantity: order.quantity, amount_cents: order.amount_cents }];

export class ApiError extends Error {
  constructor(message: string, public status: number, public debugId?: string) { super(message); }
}
const apiOrigin = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
// Optional site access key (SITE_ACCESS_KEY on the API): the token from POST /api/access rides on every call.
const ACCESS_STORE = 'pf-access';
let accessToken: string | null = (() => { try { return localStorage.getItem(ACCESS_STORE); } catch { return null; } })();
const accessListeners = new Set<() => void>();
function setAccessToken(value: string | null) {
  accessToken = value;
  try { if (value) localStorage.setItem(ACCESS_STORE, value); else localStorage.removeItem(ACCESS_STORE); } catch { /* storage blocked: keep it for this tab */ }
}
/** Called when the API stops accepting the access token (expired, or the key was changed). */
export const onAccessLost = (listener: () => void) => { accessListeners.add(listener); return () => { accessListeners.delete(listener); }; };
const accessHeader = (headers: Headers) => { if (accessToken) headers.set('x-pf-access', accessToken); };
const noteAccess = (response: Response) => {
  if (response.status === 401 && response.headers.get('x-pf-access') === 'required') { setAccessToken(null); accessListeners.forEach(listener => listener()); }
};
export async function accessStatus(): Promise<{ required: boolean; ok: boolean }> {
  const headers = new Headers();
  accessHeader(headers);
  const response = await fetch(`${apiOrigin}/api/access`, { headers });
  if (!response.ok) throw new ApiError(`Request failed (${response.status}). Please try again.`, response.status);
  return response.json();
}
export async function unlockAccess(key: string): Promise<void> {
  const response = await fetch(`${apiOrigin}/api/access`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key }) });
  const json = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(typeof json?.detail === 'string' ? json.detail : `Request failed (${response.status}). Please try again.`, response.status);
  setAccessToken(json?.token ?? null);
}
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  await waitForGate(path);
  const headers = new Headers(options.headers);
  if (options.body) headers.set('Content-Type', 'application/json');
  if (isLocalDemo()) headers.set('x-demo-role', demoRole);
  else if (token) headers.set('Authorization', `Bearer ${token}`);
  placementHeaders(headers);
  accessHeader(headers);
  const response = await fetch(`${apiOrigin}/api${path}`, { ...options, headers });
  noteAccess(response);
  noteResponse(response);
  const json = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = json?.detail;
    const text = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((x: { msg: string }) => x.msg).join('; ') : json?.message;
    throw new ApiError(text || `Request failed (${response.status}). Please try again.`, response.status, json?.debug_id);
  }
  return json as T;
}
/** Raw authenticated fetch against the API (for streaming responses). */
export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  await waitForGate(path);
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  if (isLocalDemo()) headers.set('x-demo-role', demoRole);
  else if (token) headers.set('Authorization', `Bearer ${token}`);
  placementHeaders(headers);
  accessHeader(headers);
  const response = await fetch(`${apiOrigin}/api${path}`, { ...init, headers });
  noteAccess(response);
  noteResponse(response);
  return response;
}
export const post = <T>(path: string, body: unknown = {}) => api<T>(path, { method: 'POST', body: JSON.stringify(body) });
export const patch = <T>(path: string, body: unknown) => api<T>(path, { method: 'PATCH', body: JSON.stringify(body) });
export const put = <T>(path: string, body: unknown) => api<T>(path, { method: 'PUT', body: JSON.stringify(body) });
export const remove = <T>(path: string) => api<T>(path, { method: 'DELETE' });
