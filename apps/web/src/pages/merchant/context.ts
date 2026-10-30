import { createContext, useContext } from 'react';
import type { Dashboard, Order } from '../../lib/api';

export type MerchantNotice = { id: string; merchant_id: string; order_id: string; event_type: string; message: string; seen_at: string | null; created_at: string; order_status: string; payment_status: string; buyer_name: string; quantity: number };
export type MerchantNotices = { unread: number; notifications: MerchantNotice[] };

export type MerchantCtx = {
  /** In-app notifications for the signed-in staff member (new reservations to prepare). */
  notices: MerchantNotices;
  markNoticeRead: (id: string) => Promise<void>;
  refreshNotices: () => Promise<void>;
  merchantId: string;
  dashboard: Dashboard;
  refresh: () => Promise<void>;
  busy: boolean;
  /** POST an order action (confirm, fulfilment, refund) and refresh the dashboard. */
  run: (path: string, body?: object) => Promise<void>;
  requestRefund: (order: Order) => void;
  flash: (message: string) => void;
  fail: (message: string) => void;
};

export const MerchantContext = createContext<MerchantCtx | null>(null);
export function useMerchant() {
  const value = useContext(MerchantContext);
  if (!value) throw new Error('useMerchant must be used inside the merchant workspace');
  return value;
}

export const FULFILMENT_NEXT: Record<string, string> = { PAID: 'ACCEPTED', ACCEPTED: 'PREPARING', PREPARING: 'READY', READY: 'COLLECTED' };
export const LOW_STOCK_AT = 3;
