/**
 * Dev-only SSE fixture. Enabled when `import.meta.env.DEV && localStorage['pf.mockAssistant'] === '1'`.
 * Emits AG-UI events with openui-lang that uses the PayFound components, against real catalogue ids.
 */
import type { Product } from '../../lib/api';
import { api } from '../../lib/api';

const enc = new TextEncoder();
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

export const mockEnabled = () => { try { return import.meta.env.DEV && localStorage.getItem('pf.mockAssistant') === '1'; } catch { return false; } };

export async function mockAssistantResponse(question: string, merchantId?: string): Promise<Response> {
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (event: object) => controller.enqueue(enc.encode(`data: ${JSON.stringify(event)}\n\n`));
      const runId = crypto.randomUUID(), messageId = crypto.randomUUID();
      send({ type: 'RUN_STARTED', threadId: 't', runId });
      const tool = async (name: string, args: object, result: object, ms = 700) => {
        const id = crypto.randomUUID();
        send({ type: 'TOOL_CALL_START', toolCallId: id, toolCallName: name, parentMessageId: messageId });
        send({ type: 'TOOL_CALL_ARGS', toolCallId: id, delta: JSON.stringify(args) });
        send({ type: 'TOOL_CALL_END', toolCallId: id });
        await sleep(ms);
        send({ type: 'TOOL_CALL_RESULT', messageId: crypto.randomUUID(), toolCallId: id, content: JSON.stringify(result) });
      };
      let text: string;
      if (merchantId) {
        await tool('merchant_dashboard', {}, { ok: true });
        await tool('low_stock', {}, { ok: true }, 500);
        text = `Two things need you today: stock that is running low and orders waiting on you.\n\n\`\`\`openui-lang\nroot = Card([kpis, stock, queue])\nkpis = KpiRow([{label: "Open orders", value: "4", hint: "paid, not collected"}, {label: "Low stock", value: "3", tone: "warn"}])\nstock = StockAlerts("${merchantId}")\nqueue = MerchantOrderQueue("${merchantId}")\n\`\`\`\n`;
      } else {
        const term = question.replace(/[^\w ]/g, ' ').split(' ').filter(w => w.length > 3).slice(0, 2).join(' ');
        const found = await api<Product[]>(`/products?q=${encodeURIComponent(term)}&in_stock=true&radius_km=60&limit=6`).catch(() => [] as Product[]);
        const list = found.length ? found : await api<Product[]>('/products?in_stock=true&radius_km=60&limit=4');
        await tool('search_products', { query: term }, { count: list.length }, 900);
        await tool('get_route', { product_id: list[0].id }, { ok: true }, 700);
        const ids = list.slice(0, 4).map(p => JSON.stringify(p.id)).join(', ');
        const stores = [...new Set(list.slice(0, 4).map(p => p.merchant_id))].map(s => JSON.stringify(s)).join(', ');
        text = `I found ${Math.min(4, list.length)} in stock close by. The nearest is ${list[0].merchant_name}.\n\n\`\`\`openui-lang\nroot = Card([grid, map, route, follow])\ngrid = OfferGrid([${ids}], "In stock near you")\nmap = StoreMap([${stores}], ${JSON.stringify(list[0].id)}, true)\nroute = RouteCard(${JSON.stringify(list[0].id)})\nfollow = FollowUpBlock([f1, f2])\nf1 = FollowUpItem("Only show what is open now")\nf2 = FollowUpItem("Reserve the closest one")\n\`\`\`\n`;
      }
      send({ type: 'TEXT_MESSAGE_START', messageId, role: 'assistant' });
      for (let i = 0; i < text.length; i += 14) { send({ type: 'TEXT_MESSAGE_CONTENT', messageId, delta: text.slice(i, i + 14) }); await sleep(18); }
      send({ type: 'TEXT_MESSAGE_END', messageId });
      send({ type: 'RUN_FINISHED', threadId: 't', runId });
      controller.close();
    },
  });
  return new Response(stream, { headers: { 'content-type': 'text/event-stream' } });
}
