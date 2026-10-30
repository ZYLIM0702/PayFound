import type { CustomCellRendererProps } from 'ag-grid-react';
import type { ColDef, ValueFormatterParams } from 'ag-grid-community';
import { Chip, OrderStatus, statusLabel, type Tone } from './Shared';
import { cash, type Order } from '../lib/api';

export const orderStatusCell = (p: CustomCellRendererProps<Order>) => p.value ? <OrderStatus order={{ status: p.value }} /> : null;

const paymentTone: Record<string, Tone> = { CAPTURED: 'green', PAID: 'green', REFUNDED: 'red', FAILED: 'red', VOIDED: 'red', PENDING: 'amber', CREATED: 'amber', APPROVED: 'amber', REFUND_PENDING: 'amber' };
export const paymentCell = (p: CustomCellRendererProps<Order>) => p.value ? <Chip kind={paymentTone[p.value] || 'default'} dot>{statusLabel(p.value)}</Chip> : null;

export const moneyFormatter = (p: ValueFormatterParams<Order>) => p.data ? cash(p.data.amount_cents, p.data.currency) : '';
export const dateTimeFormatter = (p: ValueFormatterParams) => p.value ? new Date(p.value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '';
export const shortId = (id: string) => id.length > 14 ? `${id.slice(0, 8)}…${id.slice(-4)}` : id;

/** Order id with a muted monospace feel; doubles as the master/detail expander. */
export const orderIdColumn: ColDef<Order> = {
  field: 'id', headerName: 'Order', minWidth: 170, cellRenderer: 'agGroupCellRenderer',
  cellRendererParams: { innerRenderer: (p: CustomCellRendererProps<Order>) => <span className="font-semibold tabular text-[13px]">{p.value ? shortId(p.value) : ''}</span> },
};

export const statusSetFilter = { filter: 'agSetColumnFilter', floatingFilter: true } satisfies ColDef;

/** Rows that need attention get a subtle left edge marker. */
export const orderRowClass = (order?: Order) => order?.confirmation_status === 'PENDING' && order.status === 'RESERVED' ? 'pf-row-attention' : '';
