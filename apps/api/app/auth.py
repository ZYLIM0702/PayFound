import os
import jwt
from fastapi import Depends, Header, HTTPException, Request
from dataclasses import dataclass
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import db_session
from .models import MerchantMembership, Merchant
from .limits import allowed

@dataclass
class Principal:
    subject: str
    role: str
    merchant_id: str | None = None
    email: str | None = None

_jwks = None

def current_principal(request: Request, authorization: str | None = Header(None), x_demo_role: str | None = Header(None), db: Session = Depends(db_session)) -> Principal:
    """Demo impersonation is only allowed from localhost in DEMO_MODE=true."""
    if os.getenv('DEMO_MODE','false').lower() == 'true':
        if request.client and request.client.host not in {'127.0.0.1','::1','testclient','localhost'}:
            raise HTTPException(403,'Demo mode must only be accessed through localhost. Disable it for deployment.')
        role = x_demo_role or 'consumer'
        if role not in {'consumer','merchant','admin'}:raise HTTPException(401,'Unknown demo role')
        return Principal(f'demo-{role}',role,'m1' if role == 'merchant' else None)
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(401,'Supabase access token required')
    url = os.getenv('SUPABASE_JWKS_URL','')
    issuer = os.getenv('SUPABASE_PROJECT_URL','').rstrip('/') + '/auth/v1'
    if not url or not os.getenv('SUPABASE_PROJECT_URL'):
        raise HTTPException(503,'Production Supabase JWT configuration missing')
    global _jwks
    if _jwks is None or getattr(_jwks, 'uri', url) != url:
        # Individual-key LRU caching has no expiry. Cache the JWKS only so
        # provider rotation/revocation is observed within a bounded interval.
        _jwks=PyJWKClient(url,cache_keys=False,cache_jwk_set=True,lifespan=300,timeout=5)
    token = authorization.split(' ',1)[1]
    try:
        key=_jwks.get_signing_key_from_jwt(token)
        data=jwt.decode(token,key.key,algorithms=['RS256','ES256'],issuer=issuer,audience=os.getenv('SUPABASE_JWT_AUDIENCE','authenticated'),options={'require':['sub','exp','iat','iss','aud']})
        metadata=data.get('app_metadata') or {}
        role=metadata.get('payfound_role','consumer') if isinstance(metadata,dict) else 'consumer'
        if role not in {'consumer','merchant','admin'}:role='consumer'
        if not isinstance(data['sub'], str) or not data['sub']:raise ValueError('Missing subject')
    except Exception as e:
        raise HTTPException(401,'Invalid access token') from e
    if not allowed('subject', data['sub']):
        raise HTTPException(429, 'Account request rate limit exceeded', headers={'Retry-After': '60'})
    # Membership is checked afresh, even when a signed JWT still says "merchant".
    # user_metadata is deliberately never used for authorization.
    membership=db.scalar(select(MerchantMembership).where(MerchantMembership.subject==data['sub'],MerchantMembership.active.is_(True)).order_by(MerchantMembership.created_at))
    owned=db.scalar(select(Merchant.id).where(Merchant.owner_subject==data['sub']).order_by(Merchant.id).limit(1))
    if role != 'admin':role='merchant' if membership or owned else 'consumer'
    return Principal(data['sub'],role,membership.merchant_id if membership else owned,data.get('email'))

def require_role(*roles):
    def _check(p:Principal=Depends(current_principal)):
        if p.role not in roles:raise HTTPException(403,'Insufficient role')
        return p
    return _check
