export type PosProduct = {
  id: string; name: string; sku: string; category: string; price_cents: number;
  currency: string; quantity: number; reserved: number; available_quantity: number;
  platform_quantity: number | null; platform_reserved: number | null; location_id: string | null;
  image_url?: string | null;
};
export type PosReceipt = {
  id: string; number: string; created_at: string; simulated: boolean;
  items: { product_id: string; name: string; sku: string; unit_price_cents: number; quantity: number }[];
  subtotal_cents: number; discount_cents: number; total_cents: number; currency: string;
  payment_method: 'card' | 'cash'; status: 'COMPLETED' | 'DECLINED'; sync_status: string;
};
export type PosEvent = {
  id: string; kind: string; direction: string; summary: string; status: string;
  created_at: string; acknowledged_at?: string; error: string | null;
};
export type PosLive = {
  server_time: string; captured_cents: number; captured_count: number; reservation_count: number;
  products: { id: string; name: string; sku: string; category: string; price_cents: number; currency: string; quantity: number; held: number; available: number; branch: string; source: string; image_url: string | null; updated_at: string | null }[];
  orders: { id: string; kind: 'reservation' | 'paid' | 'closed'; product_name: string; buyer_name: string; quantity: number; amount_cents: number; currency: string; status: string; payment_status: string; branch: string; hold_expires_at: string | null; created_at: string | null }[];
  pickup_slots: { id: string; branch: string; start_at: string; end_at: string; capacity: number; booked: number }[];
  plugin: { name: string; mode: string; status: string; last_synced_at: string | null; last_error: string | null } | null;
};
export type PosState = {
  live: PosLive;
  connected: boolean; online: boolean; merchant_id: string; merchant_name: string;
  merchant_slug: string; currency: string; simulated: boolean; pending_count: number;
  conflict_count: number; last_synced_at: string | null; catalog: PosProduct[];
  events: PosEvent[]; receipts: PosReceipt[];
};
export type PosCartLine = { product_id: string; quantity: number };
export type PosDiscount = { kind: 'percent' | 'fixed'; value: number };
export const productGroup = (p: PosProduct) => /headphone|speaker|audio/i.test(p.name) ? 'Audio'
  : /cable/i.test(p.name) ? 'Cables' : /charg|power bank/i.test(p.name) ? 'Charging' : 'Accessories';
export const discountCents = (subtotal: number, discount: PosDiscount) => discount.kind === 'percent'
  ? Math.floor((subtotal * discount.value + 5000) / 10000) : discount.value;

export function loadPosDraft(key: string): { items: PosCartLine[]; discount: PosDiscount } {
  try {
    const draft = JSON.parse(localStorage.getItem(key) || '{}');
    const items = Array.isArray(draft.items) ? draft.items.filter((line: PosCartLine) =>
      line && typeof line.product_id === 'string' && Number.isInteger(line.quantity) && line.quantity > 0 && line.quantity <= 10).slice(0, 30) : [];
    const discount = draft.discount?.kind === 'fixed' || draft.discount?.kind === 'percent' ? draft.discount : { kind: 'percent', value: 0 };
    return { items, discount: Number.isInteger(discount.value) && discount.value >= 0 ? discount : { kind: 'percent', value: 0 } };
  } catch { return { items: [], discount: { kind: 'percent', value: 0 } }; }
}
