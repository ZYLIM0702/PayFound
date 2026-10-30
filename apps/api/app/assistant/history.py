"""Server-side assistant chat history: owner-only threads stored as JSON."""
from __future__ import annotations

import base64
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..access import accessible_merchant_ids
from ..auth import Principal, current_principal
from ..database import SessionLocal, db_session
from ..models import AssistantThread, utcnow

log = logging.getLogger('payfound.history')
router = APIRouter()

THREAD_ID = re.compile(r'^[A-Za-z0-9_-]{8,64}$')
MAX_THREADS_PER_USER = 200
MAX_MESSAGES = 200
MAX_TEXT = 24_000
MAX_TOOLS = 12
MAX_THREAD_BYTES = 16_000_000   # over this, image bytes are dropped from the oldest messages first
TITLE_MAX = 80

IMAGE_MIMES = ('image/png', 'image/jpeg', 'image/webp', 'image/gif')
MAX_IMAGES = 3
MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_STORED_IMAGE_CHARS = MAX_IMAGE_BYTES * 4 // 3 + 8   # every accepted upload is kept (the browser also downsizes photos)
_DATA_URL = re.compile(r'^data:(image/(?:png|jpeg|webp|gif));base64,')


def sniff_image(raw: bytes) -> str | None:
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    if raw.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if raw[:6] in (b'GIF87a', b'GIF89a'):
        return 'image/gif'
    if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
        return 'image/webp'
    return None


def validate_image(data_url: Any) -> tuple[str, str]:
    """Return (mime, data_url) for a safe base64 image data URL, or raise 422. Content is verified, not just the label."""
    if not isinstance(data_url, str):
        raise HTTPException(422, 'Images must be data URLs')
    m = _DATA_URL.match(data_url[:40])
    if not m:
        raise HTTPException(422, 'Only PNG, JPEG, WebP or GIF images are supported')
    b64 = data_url[m.end():]
    if len(b64) > MAX_IMAGE_BYTES * 4 // 3 + 8:
        raise HTTPException(422, 'Each image must be 4 MB or smaller')
    try:
        raw = base64.b64decode(b64, validate=True)
    except Exception:
        raise HTTPException(422, 'Image data is not valid base64') from None
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(422, 'Each image must be 4 MB or smaller')
    if sniff_image(raw) != m.group(1):
        raise HTTPException(422, 'The image content does not match its type')
    return m.group(1), data_url


def validate_images(items: Any) -> list[str]:
    if not items:
        return []
    if not isinstance(items, list) or len(items) > MAX_IMAGES:
        raise HTTPException(422, f'Attach at most {MAX_IMAGES} images')
    out = []
    for it in items:
        out.append(validate_image(it.get('data_url') if isinstance(it, dict) else it)[1])
    return out


def iso(d: datetime) -> str:
    return d.isoformat() + 'Z'


def clean_title(text: str) -> str:
    t = re.sub(r'\s+', ' ', text or '').strip()
    return (t[:TITLE_MAX] or 'New chat')


def ensure_surface_column(engine) -> None:
    """Demo databases are built with create_all, which never alters an existing table: add the column once if it is missing."""
    from sqlalchemy import inspect, text
    try:
        if 'surface' not in {c['name'] for c in inspect(engine).get_columns('assistant_threads')}:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE assistant_threads ADD COLUMN surface VARCHAR(16) NOT NULL DEFAULT 'shopper'"))
    except Exception:
        log.warning('assistant_threads surface column check failed')


def has_merchant_rights(db: Session, p: Principal) -> bool:
    return p.role == 'admin' or bool(accessible_merchant_ids(db, p))


def resolve_surface(db: Session, p: Principal, requested: str | None) -> str:
    """Server-decided surface for NEW threads: 'merchant' only when the client asks for it AND the principal has merchant rights."""
    return 'merchant' if requested == 'merchant' and has_merchant_rights(db, p) else 'shopper'


def summary(t: AssistantThread) -> dict:
    return {'id': t.id, 'surface': t.surface, 'title': t.title, 'created_at': iso(t.created_at), 'updated_at': iso(t.updated_at)}


def stored_image(data_url: str) -> dict:
    mime = data_url[5:data_url.index(';')]
    if len(data_url) <= MAX_STORED_IMAGE_CHARS:
        return {'mime': mime, 'data_url': data_url}
    return {'mime': mime, 'placeholder': 'image attached'}


def _trim(messages: list[dict]) -> list[dict]:
    messages = messages[-MAX_MESSAGES:]
    size = lambda: len(json.dumps(messages, separators=(',', ':')))
    if size() > MAX_THREAD_BYTES:      # drop image bytes from the oldest messages first
        for m in messages:
            if m.get('images'):
                m['images'] = [{'mime': i.get('mime', ''), 'placeholder': 'image attached'} for i in m['images']]
                if size() <= MAX_THREAD_BYTES:
                    break
    while len(messages) > 2 and size() > MAX_THREAD_BYTES:
        messages.pop(0)
    return messages


def _owned(db: Session, p: Principal, thread_id: str) -> AssistantThread | None:
    t = db.get(AssistantThread, thread_id)
    if t is None or t.owner_subject != p.subject:
        return None
    if t.surface == 'merchant' and not has_merchant_rights(db, p):
        return None     # merchant-surface threads are never readable without current merchant rights
    return t


def _prune(db: Session, subject: str) -> None:
    rows = db.execute(select(AssistantThread.id).where(AssistantThread.owner_subject == subject)
                      .order_by(AssistantThread.updated_at.desc()).offset(MAX_THREADS_PER_USER)).scalars().all()
    for tid in rows:
        db.delete(db.get(AssistantThread, tid))


def append(subject: str, thread_id: str, items: list[dict], title_hint: str = '', surface: str = 'shopper') -> bool:
    """Append messages to the caller's thread, creating it on first use. False when the id belongs to someone else or is invalid."""
    if not THREAD_ID.match(thread_id or ''):
        return False
    try:
        with SessionLocal() as db:
            t = db.get(AssistantThread, thread_id)
            if t is not None and t.owner_subject != subject:
                return False
            known = {m.get('id') for m in (t.messages if t else [])}
            fresh = [i for i in items if i.get('id') not in known]
            if not fresh and t is not None:
                return True
            if t is None:
                t = AssistantThread(id=thread_id, owner_subject=subject, surface=surface if surface in ('shopper', 'merchant') else 'shopper', title=clean_title(title_hint), messages=[],
                                    created_at=utcnow(), updated_at=utcnow())
                db.add(t)
            t.messages = _trim([*t.messages, *fresh])
            t.updated_at = utcnow()
            db.flush()
            _prune(db, subject)
            db.commit()
        return True
    except Exception:
        return False


def user_item(msg_id: str | None, text: str, images: list[str]) -> dict:
    item: dict = {'id': msg_id or f'msg_{uuid.uuid4().hex[:12]}', 'role': 'user', 'content': (text or '')[:MAX_TEXT]}
    if images:
        item['images'] = [stored_image(i) for i in images]
    return item


def assistant_items(segments: list[str], tools: list[dict]) -> list[dict]:
    out = []
    for n, text in enumerate(s for s in segments if s.strip()):
        item: dict = {'id': f'msg_{uuid.uuid4().hex[:12]}', 'role': 'assistant', 'content': text[:MAX_TEXT]}
        if n == 0 and tools:
            item['tools'] = tools[:MAX_TOOLS]
        out.append(item)
    return out


class ThreadIn(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: str | None = Field(default=None, max_length=64)
    title: str = Field(default='New chat', max_length=200)
    surface: str | None = Field(default=None, max_length=16)


class ThreadPatch(BaseModel):
    model_config = ConfigDict(extra='ignore')
    title: str = Field(min_length=1, max_length=200)


ThreadPath = Path(pattern=r'^[A-Za-z0-9_-]{8,64}$')


@router.get('/assistant/threads')
def list_threads(surface: str | None = Query(default=None, pattern='^(shopper|merchant)$'), p: Principal = Depends(current_principal),
                 db: Session = Depends(db_session)):
    rights = has_merchant_rights(db, p)
    if surface == 'merchant' and not rights:
        raise HTTPException(403, 'Merchant history is not available for this account')
    surface = surface or ('merchant' if rights else 'shopper')
    rows = db.execute(select(AssistantThread).where(AssistantThread.owner_subject == p.subject, AssistantThread.surface == surface)
                      .order_by(AssistantThread.updated_at.desc()).limit(MAX_THREADS_PER_USER)).scalars().all()
    return {'threads': [summary(t) for t in rows]}


@router.post('/assistant/threads', status_code=201)
def create_thread(body: ThreadIn, p: Principal = Depends(current_principal), db: Session = Depends(db_session)):
    tid = body.id or f'thr_{uuid.uuid4().hex[:20]}'
    if not THREAD_ID.match(tid):
        raise HTTPException(422, 'Invalid thread id')
    existing = db.get(AssistantThread, tid)
    if existing is not None:
        if _owned(db, p, tid) is None:
            raise HTTPException(404, 'Thread not found')
        return summary(existing)
    t = AssistantThread(id=tid, owner_subject=p.subject, surface=resolve_surface(db, p, body.surface), title=clean_title(body.title), messages=[])
    db.add(t)
    db.flush()
    _prune(db, p.subject)
    db.commit()
    db.refresh(t)
    return summary(t)


@router.get('/assistant/threads/{thread_id}')
def get_thread(thread_id: str = ThreadPath, p: Principal = Depends(current_principal), db: Session = Depends(db_session)):
    t = _owned(db, p, thread_id)
    if t is None:
        raise HTTPException(404, 'Thread not found')
    return {**summary(t), 'messages': t.messages}


@router.patch('/assistant/threads/{thread_id}')
def rename_thread(body: ThreadPatch, thread_id: str = ThreadPath, p: Principal = Depends(current_principal), db: Session = Depends(db_session)):
    t = _owned(db, p, thread_id)
    if t is None:
        raise HTTPException(404, 'Thread not found')
    t.title = clean_title(body.title)
    db.commit()
    db.refresh(t)
    return summary(t)


@router.delete('/assistant/threads/{thread_id}', status_code=204)
def delete_thread(thread_id: str = ThreadPath, p: Principal = Depends(current_principal), db: Session = Depends(db_session)):
    t = _owned(db, p, thread_id)
    if t is None:
        raise HTTPException(404, 'Thread not found')
    db.delete(t)
    db.commit()
