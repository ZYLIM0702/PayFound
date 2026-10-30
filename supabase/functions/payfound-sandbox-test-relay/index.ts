// Temporary test ingress, not a production payment handler. Authenticates an
// expiring run nonce against a private hash, stores untrusted ORIGINAL bytes,
// and lets the actual FastAPI handler verify PayPal's signature before trust.
const entity = 'payfound-sandbox-test-relay';
const names = ['paypal-auth-algo', 'paypal-cert-url', 'paypal-transmission-id', 'paypal-transmission-sig', 'paypal-transmission-time'];

function encode(bytes: Uint8Array) {
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

Deno.serve(async (req: Request) => {
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });
  const nonce = new URL(req.url).searchParams.get('run');
  if (!nonce || !/^[A-Za-z0-9_-]{32,100}$/.test(nonce)) return new Response('Unauthorized', { status: 401 });
  const url = Deno.env.get('SUPABASE_URL');
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!url || !key) return new Response('Unavailable', { status: 503 });
  const headers = { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' };
  try {
    const configResponse = await fetch(`${url}/rest/v1/audit_events?select=details&actor=eq.sandbox-test-runner&action=eq.test.paypal_hook_config&entity_id=eq.${entity}&order=id.desc&limit=1`, { headers });
    if (!configResponse.ok) return new Response('Unavailable', { status: 503 });
    const rows = await configResponse.json();
    const config = rows.length ? JSON.parse(rows[0].details) : null;
    const expiry = Date.parse(config?.expires_at || '');
    if (!config?.enabled || !Number.isFinite(expiry) || expiry <= Date.now()) return new Response('Retired', { status: 410 });
    const bytes = new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(nonce)));
    const digest = Array.from(bytes, value => value.toString(16).padStart(2, '0')).join('');
    let mismatch = digest.length ^ String(config.nonce_hash).length;
    for (let i = 0; i < digest.length; i++) mismatch |= digest.charCodeAt(i) ^ String(config.nonce_hash).charCodeAt(i);
    if (mismatch) return new Response('Unauthorized', { status: 401 });
    // Bound reads even if the caller omits or lies about Content-Length.
    const reader = req.body?.getReader();
    if (!reader) return new Response('Missing body', { status: 400 });
    const chunks: Uint8Array[] = [];
    let length = 0;
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      length += value.length;
      if (length > 262144) { await reader.cancel(); return new Response('Too large', { status: 413 }); }
      chunks.push(value);
    }
    const original = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) { original.set(chunk, offset); offset += chunk.length; }
    const event = JSON.parse(new TextDecoder().decode(original));
    if (!/^[A-Za-z0-9_-]{1,160}$/.test(event.id || '') || !['PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.REFUNDED'].includes(event.event_type)) return new Response('Unsupported event', { status: 422 });
    const verificationHeaders: Record<string, string> = {};
    for (const name of names) {
      const value = req.headers.get(name);
      if (!value || value.length > 8192) return new Response('Missing verification data', { status: 400 });
      verificationHeaders[name] = value;
    }
    const stored = await fetch(`${url}/rest/v1/provider_webhooks?on_conflict=id`, {
      method: 'POST', headers: { ...headers, Prefer: 'resolution=ignore-duplicates,return=minimal' },
      body: JSON.stringify({ id: event.id, received_at: new Date().toISOString(), event_type: event.event_type,
        payload: JSON.stringify({ run_id: config.run_id, raw_base64: encode(original), headers: verificationHeaders }),
        processed_at: null, verified: false }),
    });
    return new Response(stored.ok ? 'Received for verification' : 'Unavailable', { status: stored.ok ? 200 : 503 });
  } catch {
    return new Response('Invalid test delivery', { status: 400 });
  }
});
