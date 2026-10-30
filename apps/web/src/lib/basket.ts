/** Pure basket helpers (no React) so they can be unit-tested with node --test. */
export type CartItem = { product_id: string; quantity: number; merchant_id?: string; location_id?: string };
export const MAX_BASKET_UNITS = 30;
export const MAX_PER_PRODUCT = 10;

export function parseCart(raw: string | null): CartItem[] {
  try {
    const value: unknown = JSON.parse(raw || '[]');
    if (!Array.isArray(value)) return [];
    const ids = new Set<string>();
    const out: CartItem[] = [];
    let units = 0;
    for (const x of value) {
      if (!x || typeof x.product_id !== 'string' || !Number.isInteger(x.quantity) || x.quantity < 1 || x.quantity > 99 || ids.has(x.product_id)) continue;
      const quantity = Math.min(MAX_PER_PRODUCT, x.quantity);
      if (units + quantity > MAX_BASKET_UNITS) continue;
      ids.add(x.product_id); units += quantity;
      const line: CartItem = { product_id: x.product_id, quantity };
      if (typeof x.merchant_id === 'string' && x.merchant_id) line.merchant_id = x.merchant_id;
      if (typeof x.location_id === 'string' && x.location_id) line.location_id = x.location_id;
      out.push(line);
    }
    return out;
  } catch { return []; }
}

type Listed = { merchant_id?: string; location_id?: string | null; currency?: string } | undefined;
export type Group<T> = { key: string; merchant_id: string; location_id: string; currency: string; lines: T[] };

/** Groups lines by store then branch, keeping first-seen order. Lines without a known product go in an "unknown" group. */
export function groupByStore<T extends { product?: Listed }>(lines: T[]): Group<T>[] {
  const groups = new Map<string, Group<T>>();
  for (const line of lines) {
    const merchant_id = line.product?.merchant_id || '';
    const location_id = line.product?.location_id || '';
    const key = merchant_id ? `${merchant_id}:${location_id}` : 'unknown';
    let group = groups.get(key);
    if (!group) { group = { key, merchant_id, location_id, currency: line.product?.currency || '', lines: [] }; groups.set(key, group); }
    group.lines.push(line);
  }
  return [...groups.values()];
}

export function storeCount(items: { merchant_id?: string }[]) { return new Set(items.map(x => x.merchant_id).filter(Boolean)).size; }

const pendingKey = 'payfound.pending-reservations.v1';
export type PendingReservation = { id: string; store: string };
export function readPending(raw: string | null): PendingReservation[] {
  try {
    const v: unknown = JSON.parse(raw || '[]');
    return Array.isArray(v) ? v.filter((x): x is PendingReservation => x && typeof x.id === 'string' && typeof x.store === 'string') : [];
  } catch { return []; }
}
export function loadPending(): PendingReservation[] { try { return readPending(sessionStorage.getItem(pendingKey)); } catch { return []; } }
export function savePending(list: PendingReservation[]) { try { sessionStorage.setItem(pendingKey, JSON.stringify(list)); } catch { /* optional */ } }
