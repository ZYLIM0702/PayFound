import { FileText } from 'lucide-react';
import { useResource } from '../lib/use-resource';
import { Chip, type Tone } from './Shared';

type InvoiceInfo = { status: 'PENDING' | 'SENT' | 'PAID' | 'DEMO' | 'FAILED'; number?: string; invoice_id?: string; demo?: boolean };

const TONE: Record<InvoiceInfo['status'], Tone> = { PENDING: 'amber', SENT: 'blue', PAID: 'green', DEMO: 'default', FAILED: 'red' };
const NOTE: Record<InvoiceInfo['status'], string> = {
  PENDING: 'Invoice is being prepared',
  SENT: 'PayPal sandbox invoice issued',
  PAID: 'PayPal sandbox invoice paid',
  DEMO: 'Demo invoice · no PayPal invoice sent',
  FAILED: 'The PayPal invoice could not be created. The printable copy below still works.',
};

/** Read-only PayPal invoice status row. The printable copy is rendered locally elsewhere. */
export function InvoiceStatus({ orderId }: { orderId: string }) {
  const invoice = useResource<InvoiceInfo>(`/orders/${encodeURIComponent(orderId)}/invoice`);
  const data = invoice.data;
  return <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px]" data-testid="paypal-invoice">
    <FileText size={14} className="text-muted shrink-0" />
    <span className="font-semibold text-ink-2">PayPal invoice</span>
    {data && <Chip kind={TONE[data.status] ?? 'default'}>{data.status}</Chip>}
    <span className="text-muted">
      {invoice.loading && !data ? 'Checking…' : data ? (NOTE[data.status] ?? data.status) : 'Invoice status unavailable right now.'}
      {data?.number ? ` · No. ${data.number}` : data?.invoice_id ? ` · ${data.invoice_id}` : ''}
    </span>
    {data && data.status !== 'DEMO' && <span className="text-[11px] uppercase tracking-wide text-muted">PayPal sandbox</span>}
    {!data && invoice.error && <button className="pf-tap underline underline-offset-4 text-muted" onClick={() => void invoice.refresh()}>Retry</button>}
  </div>;
}
