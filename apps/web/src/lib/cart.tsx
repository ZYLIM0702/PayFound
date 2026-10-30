import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import { api, put, type Product } from './api';
import { useApp } from './app-context';

import { MAX_BASKET_UNITS, MAX_PER_PRODUCT, parseCart, type CartItem } from './basket';
export { parseCart };
export type { CartItem };
const storageKey = 'payfound.cart.v1';
function initialCart() { try { return parseCart(localStorage.getItem(storageKey)); } catch { return []; } }
type CartState = { items: CartItem[]; add: (product: Product, catalog?: Product[]) => string; remove: (ids: string[]) => void; update: (id: string, quantity: number) => void; clear: () => void; replace: (product: Product) => void };
const Context = createContext<CartState | null>(null);
export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>(initialCart);
  useEffect(() => { try { localStorage.setItem(storageKey, JSON.stringify(items)); } catch { /* Cart still works when storage is disabled. */ } }, [items]);

  // The server holds the signed-in (or demo) user's basket, so it follows them across browsers and a cleared cache.
  // localStorage stays as the instant first paint and the fallback when the API is unreachable.
  const { me } = useApp();
  const subject = me?.subject;
  const [syncedFor, setSyncedFor] = useState('');
  const latest = useRef(items); latest.current = items;
  const previous = useRef('');
  const lines = (list: CartItem[]) => ({ items: list.map(({ product_id, quantity }) => ({ product_id, quantity })) });
  useEffect(() => {
    if (!subject) {
      if (previous.current) { setItems([]); previous.current = ''; }
      setSyncedFor('');
      return;
    }
    let alive = true;
    api<{ items: unknown[] }>('/me/basket').then(async data => {
      if (!alive) return;
      const remote = parseCart(JSON.stringify(data.items));
      if (remote.length) setItems(remote);
      else if (!previous.current && latest.current.length) await put('/me/basket', lines(latest.current)).catch(() => undefined);  // first sign-in: keep what was added anonymously
      else setItems([]);  // switching user: never carry the previous user's basket across
      previous.current = subject;
      if (alive) setSyncedFor(subject);
    }).catch(() => undefined);
    return () => { alive = false; };
  }, [subject]);
  useEffect(() => {
    if (!subject || syncedFor !== subject) return;
    const timer = window.setTimeout(() => { void put('/me/basket', lines(items)).catch(() => undefined); }, 400);
    return () => window.clearTimeout(timer);
  }, [items, syncedFor, subject]);
  const update = (id: string, quantity: number) => setItems(current => current.flatMap(x => x.product_id !== id ? [x] : quantity <= 0 ? [] : [{ ...x, quantity: Math.min(MAX_PER_PRODUCT, Math.floor(quantity)) }]));
  /** Items from any number of stores and branches may share a basket; they are grouped (and reserved) per store. Returns an error message or ''. */
  const add = (product: Product, _catalog?: Product[]) => {
    void _catalog;
    const quantity = items.find(x => x.product_id === product.id)?.quantity || 0;
    if (items.reduce((sum, x) => sum + x.quantity, 0) >= MAX_BASKET_UNITS) return `A basket holds up to ${MAX_BASKET_UNITS} items in total.`;
    if (quantity >= product.available_quantity || quantity >= MAX_PER_PRODUCT) return 'No more units available for this basket (maximum 10 per product).';
    setItems(current => quantity ? current.map(x => x.product_id === product.id ? { ...x, quantity: x.quantity + 1, merchant_id: product.merchant_id, location_id: product.location_id ?? undefined } : x) : [...current, { product_id: product.id, quantity: 1, merchant_id: product.merchant_id, location_id: product.location_id ?? undefined }]);
    return '';
  };
  const remove = (ids: string[]) => setItems(current => current.filter(x => !ids.includes(x.product_id)));
  return <Context.Provider value={{ items, add, update, clear: () => setItems([]), remove, replace: product => setItems([{ product_id: product.id, quantity: 1, merchant_id: product.merchant_id, location_id: product.location_id ?? undefined }]) }}>{children}</Context.Provider>;
}
export function useCart() { const value = useContext(Context); if (!value) throw new Error('CartProvider is required'); return value; }
