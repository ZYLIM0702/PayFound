import { cash, orderItems, type Order } from '../../lib/api';
import { fmtDate, paymentLabel } from './shared';

export const esc = (v: string) => v.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] as string);

export function invoiceHtml(order: Order) {
  const rows = orderItems(order).map(i => `<tr><td>${esc(i.product_name || i.name || '')} x ${i.quantity}</td><td style="text-align:right">${i.amount_cents != null ? cash(i.amount_cents, order.currency) : ''}</td></tr>`).join('');
  return `<!doctype html><meta charset="utf-8"><title>Invoice ${esc(order.id)}</title><body style="font:14px system-ui;margin:32px;max-width:480px"><h1 style="font-size:20px">PayFound invoice</h1><p>${esc(order.merchant_name)}<br>${esc(fmtDate(order.created_at))}<br>Order ${esc(order.id)}</p><table style="width:100%;border-collapse:collapse">${rows}<tr><td><b>Total</b></td><td style="text-align:right"><b>${cash(order.amount_cents, order.currency)}</b></td></tr></table><p>${esc(paymentLabel(order))}</p><p style="color:#666">Demo invoice, no tax applied.</p></body>`;
}

export function printInvoice(order: Order) {
  const frame = document.createElement('iframe');
  frame.style.cssText = 'position:fixed;width:0;height:0;border:0;opacity:0';
  document.body.appendChild(frame);
  const doc = frame.contentDocument;
  if (!doc) { frame.remove(); return; }
  doc.open();
  doc.write(invoiceHtml(order));
  doc.close();
  frame.contentWindow?.focus();
  frame.contentWindow?.print();
  setTimeout(() => frame.remove(), 2000);
}

export function downloadInvoice(order: Order) {
  const url = URL.createObjectURL(new Blob([invoiceHtml(order)], { type: 'text/html' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `invoice-${order.id}.html`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
