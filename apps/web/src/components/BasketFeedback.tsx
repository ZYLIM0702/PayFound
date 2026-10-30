import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, X } from 'lucide-react';
import { messageOf, type Product } from '../lib/api';
import { storeCount } from '../lib/basket';
import { useCart } from '../lib/cart';
import { ErrorLine } from './Shared';

export function useBasketAdd(_catalog?: Product[]) {
  void _catalog;
  const cart = useCart();
  const lock = useRef(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [tick, setTick] = useState(0);
  const add = async (product: Product) => {
    if (lock.current) return;
    lock.current = true; setError(''); setMessage('');
    try {
      const issue = cart.add(product);
      if (issue) setError(issue); else {
        const stores = storeCount([...cart.items, { merchant_id: product.merchant_id }]);
        setMessage(`Added to your basket (${stores} ${stores === 1 ? 'store' : 'stores'}): ${product.name}`); setTick(value => value + 1);
      }
    } catch (e) { setError(messageOf(e)); } finally { lock.current = false; }
  };
  useEffect(() => {
    if (!message) return;
    const timer = window.setTimeout(() => setMessage(''), 6000);
    return () => window.clearTimeout(timer);
  }, [message, tick]);
  return { add, feedback: <BasketFeedback error={error} message={message} onClose={() => { setError(''); setMessage(''); }} /> };
}

/** Floating toast so feedback is visible wherever the shopper has scrolled. */
function BasketFeedback({ error, message, onClose }: { error: string; message: string; onClose: () => void }) {
  if (!error && !message) return null;
  return <div className="fixed z-[1200] left-4 right-4 bottom-20 lg:bottom-6 lg:left-1/2 lg:right-auto lg:-translate-x-1/2 pf-enter flex justify-center pointer-events-none">
    {error
      ? <div className="pointer-events-auto w-full max-w-lg shadow-[var(--pf-shadow-float)] rounded-[var(--pf-r-md)]"><ErrorLine message={error} /><div className="bg-surface rounded-b-[var(--pf-r-md)] px-3.5 pb-2.5 flex justify-between"><Link className="pf-link text-sm" to="/basket">Manage basket</Link><button className="text-sm text-muted" onClick={onClose}>Dismiss</button></div></div>
      : <div className="pointer-events-auto flex items-center gap-3 rounded-full bg-ink text-white pl-4 pr-2 py-2 shadow-[var(--pf-shadow-float)] max-w-full" role="status"><Check size={16} className="shrink-0" /><span className="text-sm truncate">{message}</span><Link to="/basket" className="pf-btn sm !bg-white !text-ink shrink-0">View basket</Link><button className="w-8 h-8 grid place-items-center rounded-full hover:bg-white/15 shrink-0" aria-label="Dismiss" onClick={onClose}><X size={15} /></button></div>}
  </div>;
}
