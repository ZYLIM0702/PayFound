from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from ..auth import Principal, current_principal
from . import merge

router = APIRouter()


@router.get('/browse')
async def browse(response: Response, q: str = Query(default='', max_length=200), mode: str = Query(default='both', pattern='^(local|online|both)$'),
                 latitude: float | None = Query(None, ge=-90, le=90), longitude: float | None = Query(None, ge=-180, le=180),
                 radius_km: float = Query(100, ge=0, le=20040), limit: int = Query(40, ge=1, le=200),
                 p: Principal = Depends(current_principal)):
    """Read-only. Local products (real stock, distance) and online offers are returned in separate sections."""
    from .. import main
    from ..intelligence import channel3
    response.headers['Cache-Control'] = 'no-store'
    local: list[dict] = []
    if mode != 'online':
        with main.SessionLocal() as db:
            local = main.products(q=q, category='', merchant_id='', latitude=latitude, longitude=longitude, radius_km=radius_km,
                                  open_now=False, in_stock=False, location_id=None, ids='', limit=limit, offset=0, db=db)
    online = None
    if mode != 'local':
        channel3.rate_limit(p)
        online = (await merge.online_combined(q, channel3)) if len(q.strip()) >= 2 else {'offers': [], 'enabled': False, 'sources': {}}
    return merge.browse_response(mode, local, online)
