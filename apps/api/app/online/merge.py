"""Channel3 online offers, kept online offers strictly apart from local stock."""
from __future__ import annotations

import re

DISCLOSURE = 'Online offers are not local stock and never confirm in-store availability or pickup.'


def _tokens(title: str) -> set[str]:
    return set(re.findall(r'[a-z0-9]+', title.lower()))


def similar(a: str, b: str) -> bool:
    x, y = _tokens(a), _tokens(b)
    return bool(x and y) and len(x & y) / len(x | y) >= 0.8


def dedupe(offers: list[dict]) -> list[dict]:
    """Display-only: drop near-identical titles from the same source-agnostic list (first wins)."""
    out: list[dict] = []
    for offer in offers:
        if any(similar(offer['title'], kept['title']) and offer.get('merchant') == kept.get('merchant') for kept in out):
            continue
        out.append(offer)
    return out


async def online_combined(q: str, channel3_module, page_token: str | None = None, *, limit: int = 8) -> dict:
    """Channel3-only online offers with a `sources` status. Online offers never prove local stock."""
    c3 = await channel3_module.search(q, page_token)
    status = 'ok' if c3.get('enabled') else 'not_configured'
    offers = [{**o, 'source': 'channel3', 'label': 'ONLINE'} for o in c3.get('offers', [])]
    result = {**c3, 'offers': dedupe(offers), 'enabled': bool(c3.get('enabled')),
              'online_only': True, 'verified_local_stock': False, 'disclosure': DISCLOSURE,
              'sources': {'channel3': {'status': status}}}
    if not result['enabled']:
        result.setdefault('status', 'not_configured')
        result['message'] = 'Online offers are not set up yet.'
    return result


def browse_response(mode: str, local: list[dict], online: dict | None) -> dict:
    """Local and online results stay in separate sections; counts never mix."""
    return {'mode': mode, 'verified_local_stock_applies_to': 'local only',
            'local': {'count': len(local), 'products': local} if mode != 'online' else None,
            'online': ({'count': len(online['offers']), 'label': 'ONLINE', 'verified_local_stock': False,
                        'disclosure': DISCLOSURE, 'offers': online['offers'], 'sources': online['sources'],
                        'enabled': online['enabled']} if online is not None else None)}
