import { useEffect, useMemo, useState } from 'react';
import type { Merchant, Product } from '../../lib/api';
import { useResource } from '../../lib/use-resource';
import { useUserLocation } from '../../lib/location';

const ID = /^[a-zA-Z0-9_-]{1,48}$/;

/** Ids arrive token by token while the model streams; only settled, well-formed ids are fetched. */
export function useSettledIds(raw: unknown, max = 12): string[] {
  const key = useMemo(() => (Array.isArray(raw) ? raw : []).filter((x): x is string => typeof x === 'string' && ID.test(x)).slice(0, max).join(','), [raw, max]);
  const [settled, setSettled] = useState(key);
  useEffect(() => { const t = window.setTimeout(() => setSettled(key), 220); return () => window.clearTimeout(t); }, [key]);
  return useMemo(() => settled ? settled.split(',') : [], [settled]);
}

/** Live products for ids (price, stock and distance always come from the API), in the order the model gave. */
export function useProductsByIds(ids: string[]) {
  const { position } = useUserLocation();
  const origin = position ? `&latitude=${position.latitude}&longitude=${position.longitude}` : '';
  const resource = useResource<Product[]>(ids.length ? `/products?radius_km=20040&ids=${ids.map(encodeURIComponent).join(',')}${origin}` : null);
  const products = useMemo(() => ids.map(id => resource.data?.find(p => p.id === id)).filter((p): p is Product => Boolean(p)), [ids, resource.data]);
  return { ...resource, products };
}

export function useStores() { return useResource<Merchant[]>('/merchants'); }

/** "Show on map" bus: a StoreMap in the thread claims the event; otherwise the caller navigates to Explore. */
export const FOCUS_EVENT = 'pf-agent-focus';
export function requestMapFocus(productId: string): boolean {
  return !window.dispatchEvent(new CustomEvent(FOCUS_EVENT, { detail: { productId }, cancelable: true }));
}

export const toolLabels: Record<string, [string, string]> = {
  search_products: ['Searching nearby stores', 'Searched nearby stores'],
  get_product: ['Checking this product', 'Checked this product'],
  get_store: ['Looking up the store', 'Looked up the store'],
  read_reviews: ['Reading reviews', 'Read reviews'],
  store_reviews: ['Reading reviews', 'Read reviews'],
  get_route: ['Checking traffic & ETA', 'Checked traffic & ETA'],
  get_weather: ['Checking the weather', 'Checked the weather'],
  my_orders: ['Opening your orders', 'Opened your orders'],
  get_order: ['Checking your order', 'Checked your order'],
  check_basket: ['Checking your basket', 'Checked your basket'],
  online_offers: ['Looking at online offers', 'Looked at online offers'],
  paypal_order_status: ['Checking PayPal', 'Checked PayPal'],
  merchant_dashboard: ['Reading your dashboard', 'Read your dashboard'],
  low_stock: ['Checking low stock', 'Checked low stock'],
  stale_stock: ['Checking stale stock', 'Checked stale stock'],
  order_queue: ['Checking the order queue', 'Checked the order queue'],
  sales_summary: ['Adding up recorded sales', 'Added up recorded sales'],
  pickup_capacity: ['Checking pickup capacity', 'Checked pickup capacity'],
  reconciliation_queue: ['Checking reconciliation', 'Checked reconciliation'],
  integration_status: ['Checking integrations', 'Checked integrations'],
};
export function toolLabel(name: string, done: boolean): string {
  const known = toolLabels[name];
  if (known) return known[done ? 1 : 0];
  if (/paypal|transaction|dispute|invoice/i.test(name)) return done ? 'Checked PayPal' : 'Checking PayPal';
  const human = name.replaceAll('_', ' ');
  return done ? `Finished ${human}` : `Working on ${human}`;
}
