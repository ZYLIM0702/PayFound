"""Verify real JWT signatures and trust boundaries; only JWKS transport is faked."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import select
from app import auth
from app.database import SessionLocal
from app.models import MerchantMembership


def signer(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    issuer = 'https://auth-test.supabase.co'
    jwks = issuer + '/auth/v1/.well-known/jwks.json'
    monkeypatch.setenv('DEMO_MODE', 'false')
    monkeypatch.setenv('SUPABASE_PROJECT_URL', issuer)
    monkeypatch.setenv('SUPABASE_JWKS_URL', jwks)
    monkeypatch.setattr(auth, '_jwks', SimpleNamespace(uri=jwks,
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=key.public_key())))
    now = datetime.now(timezone.utc)
    claims = {'sub': 'signed-user', 'iss': issuer + '/auth/v1', 'aud': 'authenticated',
              'iat': now, 'exp': now + timedelta(minutes=10), 'app_metadata': {}}
    return key, claims


def headers(key, claims):
    return {'Authorization': 'Bearer ' + jwt.encode(claims, key, algorithm='ES256')}


def test_admin_requires_valid_signed_app_claims_not_user_metadata(client, monkeypatch):
    key, claims = signer(monkeypatch)
    claims['user_metadata'] = {'payfound_role': 'admin'}
    assert client.get('/api/me', headers=headers(key, claims)).json()['role'] == 'consumer'
    assert client.get('/api/admin/overview', headers=headers(key, claims)).status_code == 403
    claims['app_metadata'] = {'payfound_role': 'admin'}
    assert client.get('/api/admin/overview', headers=headers(key, claims)).status_code == 200
    foreign_key = ec.generate_private_key(ec.SECP256R1())
    assert client.get('/api/admin/overview', headers=headers(foreign_key, claims)).status_code == 401
    claims['exp'] = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert client.get('/api/admin/overview', headers=headers(key, claims)).status_code == 401


def test_revocation_is_checked_fresh_even_with_same_signed_merchant_token(client, monkeypatch):
    key, claims = signer(monkeypatch)
    claims['app_metadata'] = {'payfound_role': 'merchant'}
    with SessionLocal() as db:
        db.add(MerchantMembership(id='signed-membership', merchant_id='m1', subject='signed-user', role='staff'))
        db.commit()
    token_headers = headers(key, claims)
    assert client.get('/api/merchant/dashboard?merchant_id=m1', headers=token_headers).status_code == 200
    assert client.get('/api/merchant/dashboard?merchant_id=m2', headers=token_headers).status_code == 403
    with SessionLocal() as db:
        row = db.scalar(select(MerchantMembership).where(MerchantMembership.id == 'signed-membership'))
        row.active = False
        db.commit()
    assert client.get('/api/merchant/dashboard?merchant_id=m1', headers=token_headers).status_code == 403
