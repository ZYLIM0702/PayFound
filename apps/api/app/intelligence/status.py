import os

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import llm
from ..access import accessible_merchant_ids
from ..auth import Principal, current_principal
from ..database import db_session
from . import channel3
from .reports import consent_granted, merchant_scope

router = APIRouter()


@router.get('/integrations/status')
def integrations_status(merchant_id: str | None = Query(default=None, max_length=48),
                        db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    settings = llm.Settings.load()
    managed = p.role == 'admin' or bool(accessible_merchant_ids(db, p))
    mid = merchant_scope(db, p, merchant_id) if merchant_id else None
    ai_status = settings.status()
    ai_detail = 'Configuration status only; inference connectivity has not been probed.'
    if managed:
        if ai_status == 'configured':
            ai_detail += f' Provider: {settings.provider}; model: {settings.model}.'
        ai_detail += ' Private merchant analytics require a current merchant consent grant.'
        if mid and ai_status == 'configured' and not consent_granted(db, mid):
            ai_status = 'consent_required'
    integrations = [
        {'id': 'ai', 'name': 'AI inference', 'status': ai_status, 'detail': ai_detail},
        {'id': 'channel3', 'name': 'Channel3', 'status': 'configured' if channel3.configured() else 'unconfigured',
         'detail': 'Online catalog only; local stock is not verified. Configuration does not prove connectivity.'},
        {'id': 'ag-studio', 'name': 'AG Studio',
         'status': 'configured' if os.getenv('AG_STUDIO_LICENSE_KEY') else 'unconfigured',
         'detail': 'Server license configuration only; browser licensing has not been verified.'},
    ]
    return {'integrations': integrations}
