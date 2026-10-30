"""Account hub: sandbox payment-method link, merchant message threads and support tickets."""
from __future__ import annotations
import re
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, desc, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from .access import merchant_role
from .auth import Principal, current_principal
from .database import Base, db_session
from .models import Merchant, Order, utcnow
from .paypal_accounts import PAYPAL_ID, ShopperPayPalDetail, mask_id, seal, throttle

router = APIRouter(tags=['account-hub'])
MAX_MESSAGE = 1000
MESSAGES_PER_MINUTE = 20


class PaymentMethod(Base):
    """A demo link record only: provider, a masked label and a status. Never a credential."""
    __tablename__ = 'payment_methods'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    owner_subject: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    masked_email: Mapped[str] = mapped_column(String(160), nullable=False, default='')
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='sandbox_linked')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class MessageThread(Base):
    __tablename__ = 'message_threads'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    buyer_subject: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    order_id: Mapped[str | None] = mapped_column(ForeignKey('orders.id'), nullable=True)
    subject: Mapped[str] = mapped_column(String(160), nullable=False, default='')
    buyer_name: Mapped[str] = mapped_column(String(130), nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ThreadMessage(Base):
    __tablename__ = 'thread_messages'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey('message_threads.id'), nullable=False, index=True)
    sender_role: Mapped[str] = mapped_column(String(12), nullable=False)
    sender_subject: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (Index('ix_thread_messages_thread_created', 'thread_id', 'created_at'),)


class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    owner_subject: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(24), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    order_id: Mapped[str | None] = mapped_column(String(48), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='open')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


def _id(prefix: str) -> str:
    return f'{prefix}-{uuid.uuid4().hex[:20]}'


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() + 'Z' if value else None


_TAG = re.compile(r'<[^>]*>')
_CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def clean_text(value: str, limit: int, multiline: bool = True) -> str:
    """Plain-text sanitiser: strips HTML tags and control characters, trims, rejects empty or over-length."""
    text = _CTRL.sub('', _TAG.sub('', value or '')).replace('\r\n', '\n').replace('\r', '\n')
    if not multiline:
        text = ' '.join(text.split())
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    if not text:
        raise HTTPException(422, 'Message cannot be empty')
    if len(text) > limit:
        raise HTTPException(422, f'Keep it under {limit} characters')
    return text


EMAIL = re.compile(r'^[^@\s]{1,64}@[^@\s]{1,120}\.[^@\s]{2,24}$')


def mask_email(email: str) -> str:
    local, _, domain = email.partition('@')
    return f'{local[:1]}***@{domain}'


class PayPalLinkInput(BaseModel):
    model_config = ConfigDict(extra='forbid')  # any card/password/token field is rejected outright
    email: str = Field(min_length=5, max_length=190)
    paypal_merchant_id: str | None = Field(default=None, max_length=32)  # optional sandbox payer id


def method_json(row: PaymentMethod, db: Session | None = None) -> dict:
    detail = db.get(ShopperPayPalDetail, row.owner_subject) if db is not None and row.provider == 'paypal' else None
    return {'id': row.id, 'provider': row.provider, 'label': row.masked_email, 'status': row.status,
            'sandbox': True, 'preferred': True, 'stored': detail is not None, 'assigned': row.status == 'sandbox_assigned',
            'paypal_merchant_id': mask_id(detail.paypal_merchant_id) if detail else None,
            'created_at': _iso(row.created_at)}


PAYMENT_NOTE = ('Sandbox only. We store your PayPal email (encrypted) as your payer label. PayFound never asks for or stores your '
                'PayPal password, tokens or card numbers. Checkout still opens PayPal\'s own approval window.')


@router.get('/me/payment-methods')
def list_payment_methods(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(PaymentMethod).where(PaymentMethod.owner_subject == p.subject)
                      .order_by(PaymentMethod.created_at)).all()
    return {'methods': [method_json(r, db) for r in rows], 'note': PAYMENT_NOTE, 'sandbox': True}


@router.post('/me/payment-methods/paypal-sandbox', status_code=201)
def link_paypal_sandbox(body: PayPalLinkInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    email = body.email.strip().lower()
    if not EMAIL.match(email):
        raise HTTPException(422, 'Enter a valid email address')
    row = db.scalar(select(PaymentMethod).where(PaymentMethod.owner_subject == p.subject, PaymentMethod.provider == 'paypal'))
    if not row:
        row = PaymentMethod(id=_id('pm'), owner_subject=p.subject, provider='paypal')
        db.add(row)
    pid = (body.paypal_merchant_id or '').strip().upper() or None
    if pid and not PAYPAL_ID.match(pid):
        raise HTTPException(422, 'PayPal ID is 10-20 letters/numbers')
    throttle(f'shopper:{p.subject}', 10)
    row.masked_email = mask_email(email)
    row.status = 'sandbox_linked'
    try:
        sealed = seal({'email': email})  # encrypted at rest; only the masked label is ever returned
    except HTTPException:
        sealed = None  # no encryption key configured: keep the masked label only, never plaintext
    detail = db.get(ShopperPayPalDetail, p.subject)
    if sealed:
        if not detail:
            detail = ShopperPayPalDetail(owner_subject=p.subject)
            db.add(detail)
        detail.email_encrypted = sealed
        detail.paypal_merchant_id, detail.updated_at = pid, utcnow()
    elif detail:
        db.delete(detail)
    db.commit()
    return method_json(row, db)


@router.delete('/me/payment-methods/{method_id}')
def unlink_payment_method(method_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    row = db.get(PaymentMethod, method_id)
    if not row or row.owner_subject != p.subject:
        raise HTTPException(404, 'Payment method not found')
    detail = db.get(ShopperPayPalDetail, p.subject)
    if detail and row.provider == 'paypal':
        db.delete(detail)
    db.delete(row)
    db.commit()
    return {'removed': method_id}


def _participant(db: Session, p: Principal, thread: MessageThread) -> str | None:
    """'buyer', 'merchant' (active staff of the thread's merchant) or None."""
    if thread.buyer_subject == p.subject:
        return 'buyer'
    merchant = db.get(Merchant, thread.merchant_id)
    if merchant and merchant_role(db, p, merchant):
        return 'merchant'
    return None


def _thread_for(db: Session, p: Principal, thread_id: str) -> tuple[MessageThread, str]:
    thread = db.get(MessageThread, thread_id)
    side = _participant(db, p, thread) if thread else None
    if not thread or not side:
        raise HTTPException(404, 'Conversation not found')
    return thread, side


def message_json(m: ThreadMessage) -> dict:
    return {'id': m.id, 'sender': m.sender_role, 'body': m.body, 'created_at': _iso(m.created_at)}


def thread_json(db: Session, t: MessageThread, last: ThreadMessage | None = None) -> dict:
    merchant = db.get(Merchant, t.merchant_id)
    if last is None:
        last = db.scalar(select(ThreadMessage).where(ThreadMessage.thread_id == t.id).order_by(desc(ThreadMessage.created_at), desc(ThreadMessage.id)))
    return {'id': t.id, 'merchant_id': t.merchant_id, 'merchant_name': merchant.name if merchant else '', 'order_id': t.order_id,
            'subject': t.subject, 'updated_at': _iso(t.updated_at), 'last_message': message_json(last) if last else None}


class MessageInput(BaseModel):
    body: str = Field(max_length=5000)  # length is enforced after sanitising so tags do not count


class StartInput(BaseModel):
    merchant_id: str = Field(min_length=1, max_length=48)
    order_id: str | None = Field(default=None, max_length=48)
    body: str | None = Field(default=None, max_length=5000)


def _throttle(db: Session, p: Principal) -> None:
    since = utcnow() - timedelta(minutes=1)
    n = db.scalar(select(func.count()).select_from(ThreadMessage).where(ThreadMessage.sender_subject == p.subject, ThreadMessage.created_at >= since)) or 0
    if n >= MESSAGES_PER_MINUTE:
        raise HTTPException(429, 'You are sending messages too quickly. Wait a moment.')


def _append(db: Session, p: Principal, thread: MessageThread, side: str, body: str) -> ThreadMessage:
    _throttle(db, p)
    msg = ThreadMessage(id=_id('msg'), thread_id=thread.id, sender_role=side, sender_subject=p.subject,
                        body=clean_text(body, MAX_MESSAGE), created_at=utcnow())
    db.add(msg)
    thread.updated_at = msg.created_at
    return msg


@router.get('/me/messages')
def list_threads(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(MessageThread).where(MessageThread.buyer_subject == p.subject)
                      .order_by(desc(MessageThread.updated_at), MessageThread.id)).all()
    return {'threads': [thread_json(db, t) for t in rows],
            'note': 'Messages are saved to your account. Stores reply from the merchant workspace once that is connected.'}


@router.post('/me/messages/start', status_code=201)
def start_thread(body: StartInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = db.get(Merchant, body.merchant_id)
    if not merchant:
        raise HTTPException(404, 'Store not found')
    order = None
    if body.order_id:
        order = db.get(Order, body.order_id)
        if not order or order.buyer_subject != p.subject or order.merchant_id != merchant.id:
            raise HTTPException(404, 'Order not found')
    q = select(MessageThread).where(MessageThread.buyer_subject == p.subject, MessageThread.merchant_id == merchant.id)
    q = q.where(MessageThread.order_id == order.id) if order else q.where(MessageThread.order_id.is_(None))
    thread = db.scalar(q)
    created = thread is None
    if created:
        subject = f'Order {order.id[-8:]}' if order else 'General question'
        thread = MessageThread(id=_id('thr'), buyer_subject=p.subject, merchant_id=merchant.id, order_id=order.id if order else None,
                               subject=subject, created_at=utcnow(), updated_at=utcnow())
        db.add(thread)
        db.flush()
    if body.body:
        _append(db, p, thread, 'buyer', body.body)
    db.commit()
    return {**thread_json(db, thread), 'created': created}


@router.get('/me/messages/{thread_id}')
def get_thread(thread_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    thread, side = _thread_for(db, p, thread_id)
    msgs = db.scalars(select(ThreadMessage).where(ThreadMessage.thread_id == thread.id)
                      .order_by(ThreadMessage.created_at, ThreadMessage.id)).all()
    return {**thread_json(db, thread), 'viewer': side, 'messages': [message_json(m) for m in msgs]}


@router.post('/me/messages/{thread_id}', status_code=201)
def post_message(thread_id: str, body: MessageInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    thread, side = _thread_for(db, p, thread_id)
    msg = _append(db, p, thread, side, body.body)
    db.commit()
    return message_json(msg)


TOPICS = ('orders', 'refunds', 'payments', 'stock', 'delivery', 'account', 'other')


class TicketInput(BaseModel):
    topic: str = Field(default='other', max_length=24)
    subject: str = Field(max_length=500)
    message: str = Field(max_length=5000)
    order_id: str | None = Field(default=None, max_length=48)


def ticket_json(t: SupportTicket) -> dict:
    return {'id': t.id, 'topic': t.topic, 'subject': t.subject, 'message': t.message, 'order_id': t.order_id,
            'status': t.status, 'created_at': _iso(t.created_at)}


@router.get('/me/support-tickets')
def list_tickets(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(SupportTicket).where(SupportTicket.owner_subject == p.subject)
                      .order_by(desc(SupportTicket.created_at), SupportTicket.id)).all()
    return {'tickets': [ticket_json(t) for t in rows],
            'note': 'Demo help desk: tickets are recorded on your account. No support agent is connected yet.'}


@router.post('/me/support-tickets', status_code=201)
def create_ticket(body: TicketInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    topic = body.topic if body.topic in TOPICS else 'other'
    open_count = db.scalar(select(func.count()).select_from(SupportTicket).where(SupportTicket.owner_subject == p.subject, SupportTicket.status == 'open')) or 0
    if open_count >= 10:
        raise HTTPException(409, 'You have 10 open requests. Wait for a reply before sending more.')
    order_id = None
    if body.order_id:
        order = db.get(Order, body.order_id)
        if not order or order.buyer_subject != p.subject:
            raise HTTPException(404, 'Order not found')
        order_id = order.id
    row = SupportTicket(id=_id('tkt'), owner_subject=p.subject, topic=topic, subject=clean_text(body.subject, 120, multiline=False),
                        message=clean_text(body.message, 2000), order_id=order_id, status='open', created_at=utcnow())
    db.add(row)
    db.commit()
    return ticket_json(row)
