from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from ..access import accessible_merchant_ids, require_merchant_access
from ..auth import Principal, current_principal
from ..database import db_session
from ..models import Audit, utcnow
from .catalog import iso
from .models import ConsentGrant, MerchantReport
from .schemas import ConsentInput, ReportCreate, ReportUpdate

router = APIRouter()
MAX_REPORT_BYTES = 262144


def merchant_scope(db, principal, merchant_id: str | None, minimum_role='staff') -> str:
    if not merchant_id:
        ids = list(accessible_merchant_ids(db, principal))
        if not ids:
            raise HTTPException(403, 'Merchant membership required')
        if len(ids) != 1:
            raise HTTPException(422, 'merchant_id is required when merchant scope is not unique')
        merchant_id = ids[0]
    require_merchant_access(db, principal, merchant_id, minimum_role=minimum_role)
    return merchant_id


def _state(state: dict) -> dict:
    # Round-trip validates finite JSON and depth. Never interpret AG Studio's own version.
    try:
        encoded = json.dumps(state, allow_nan=False, ensure_ascii=True, separators=(',', ':'))
        if len(encoded.encode()) > MAX_REPORT_BYTES:
            raise HTTPException(413, 'Report state exceeds 256 KiB')
        stack = [(state, 0)]
        while stack:
            value, depth = stack.pop()
            if depth > 40:
                raise HTTPException(422, 'Report state exceeds maximum nesting depth')
            if isinstance(value, dict):
                stack.extend((v, depth + 1) for v in value.values())
            elif isinstance(value, list):
                stack.extend((v, depth + 1) for v in value)
        return json.loads(encoded)
    except (ValueError, TypeError, RecursionError):
        raise HTTPException(422, 'Report state must be finite JSON') from None


def _name(name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(422, 'Report name must not be blank')
    return name


def report_json(report):
    return {'id': report.id, 'merchant_id': report.merchant_id, 'name': report.name,
            'state': report.state, 'updated_at': iso(report.updated_at), 'version': report.version}


def _report(db, principal, report_id):
    # Scope the SELECT itself; other tenants' IDs and absent IDs are indistinguishable.
    ids = list(accessible_merchant_ids(db, principal))
    report = db.scalar(select(MerchantReport).where(MerchantReport.id == report_id,
                                                   MerchantReport.merchant_id.in_(ids)))
    if report is None:
        raise HTTPException(404, 'Report not found')
    require_merchant_access(db, principal, report.merchant_id, minimum_role='staff')
    return report


@router.get('/merchant/reports')
def list_reports(merchant_id: str | None = Query(default=None, max_length=48),
                 db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mid = merchant_scope(db, p, merchant_id)
    rows = db.scalars(select(MerchantReport).where(MerchantReport.merchant_id == mid)
                      .order_by(MerchantReport.updated_at.desc(), MerchantReport.id).limit(101)).all()
    return {'reports': [report_json(r) for r in rows[:100]], 'truncated': len(rows) > 100}


@router.post('/merchant/reports', status_code=201)
def create_report(body: ReportCreate, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mid = merchant_scope(db, p, body.merchant_id)
    if len(db.scalars(select(MerchantReport.id).where(MerchantReport.merchant_id == mid).limit(100)).all()) >= 100:
        raise HTTPException(409, 'Merchant report limit reached')
    report = MerchantReport(merchant_id=mid, name=_name(body.name), state=_state(body.state))
    db.add(report)
    db.commit()
    return report_json(report)


@router.put('/merchant/reports/{report_id}')
def update_report(report_id: str, body: ReportUpdate, db: Session = Depends(db_session),
                  p: Principal = Depends(current_principal)):
    report = _report(db, p, report_id)
    if body.version is not None and body.version != report.version:
        raise HTTPException(409, 'Report version conflict; reload before saving')
    if body.name is not None:
        report.name = _name(body.name)
    if body.state is not None:
        report.state = _state(body.state)
    report.updated_at = utcnow()
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(409, 'Report version conflict; reload before saving') from None
    return report_json(report)


@router.delete('/merchant/reports/{report_id}', status_code=204)
def delete_report(report_id: str, version: int | None = Query(default=None, ge=1),
                  db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    report = _report(db, p, report_id)
    if version is not None and version != report.version:
        raise HTTPException(409, 'Report version conflict; reload before deleting')
    db.delete(report)
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(409, 'Report version conflict; reload before deleting') from None
    return Response(status_code=204)


def consent_granted(db, merchant_id: str) -> bool:
    return bool(db.scalar(select(ConsentGrant.granted).where(ConsentGrant.merchant_id == merchant_id,
                      ConsentGrant.purpose == 'remote_merchant_inference', ConsentGrant.policy_version == 1)))


def consent_json(grant, mid):
    return {'merchant_id': mid, 'granted': bool(grant and grant.granted),
            'purpose': 'remote_merchant_inference', 'policy_version': 1,
            'updated_at': iso(grant.updated_at) if grant else None,
            'scope': 'Aggregate merchant analytics and listed product facts for inference; not model training.'}


@router.get('/merchant/ai-consent')
def get_consent(merchant_id: str | None = Query(default=None, max_length=48),
                db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mid = merchant_scope(db, p, merchant_id)
    grant = db.scalar(select(ConsentGrant).where(ConsentGrant.merchant_id == mid,
                                               ConsentGrant.purpose == 'remote_merchant_inference'))
    return consent_json(grant, mid)


@router.post('/merchant/ai-consent')
def set_consent(body: ConsentInput, merchant_id: str = Query(min_length=1, max_length=48),
                db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mid = merchant_scope(db, p, merchant_id, minimum_role='owner')
    # Merchant row serializes concurrent grants on databases supporting FOR UPDATE.
    from ..models import Merchant
    db.scalar(select(Merchant).where(Merchant.id == mid).with_for_update())
    grant = db.scalar(select(ConsentGrant).where(ConsentGrant.merchant_id == mid,
                                               ConsentGrant.purpose == 'remote_merchant_inference'))
    if grant is None:
        grant = ConsentGrant(merchant_id=mid)
        db.add(grant)
    grant.granted, grant.policy_version, grant.updated_at = body.granted, 1, utcnow()
    db.add(Audit(actor=p.subject, action='ai.consent_granted' if body.granted else 'ai.consent_revoked',
                 entity_id=mid, details='remote_merchant_inference; policy_version=1'))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Consent changed concurrently; reload and retry') from None
    return consent_json(grant, mid)
