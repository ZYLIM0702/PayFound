import { useState } from 'react';
import { Package } from 'lucide-react';
import { safeExternalUrl } from '../lib/api';

export function productImageSrc(value?: string | null) {
  if (value && /^\/images\/products\/[a-z0-9-]+\.webp$/.test(value)) return value;
  return safeExternalUrl(value);
}

export function ProductPhoto({ name, imageUrl, className = '', eager = false, merchantId }: {
  name: string; imageUrl?: string | null; className?: string; eager?: boolean; merchantId?: string;
}) {
  const [failed, setFailed] = useState('');
  const src = productImageSrc(imageUrl);
  const tone = merchantId ? [...merchantId].reduce((sum, c) => sum + c.charCodeAt(0), 0) % 5 : -1;
  return <span className={`pf-product-photo ${tone >= 0 ? `merchant-tone-${tone}` : ''} ${className}`}>{src && failed !== src
    ? <img src={src} alt={name} loading={eager ? 'eager' : 'lazy'} decoding="async" onError={() => setFailed(src)} />
    : <span className="pf-photo-unavailable" role="img" aria-label={`${name} — photo unavailable`}><Package size={26} strokeWidth={1.4} /></span>}</span>;
}
