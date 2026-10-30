from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import JSON, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Index, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Merchant(Base):
    __tablename__='merchants'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    name: Mapped[str] = mapped_column(String(130), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default='')
    category: Mapped[str] = mapped_column(String(80), default='Retail')
    address: Mapped[str] = mapped_column(String(250), default='')
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str] = mapped_column(String(80), default='')
    hours: Mapped[str] = mapped_column(String(100), default='09:00–18:00')
    status_override: Mapped[str] = mapped_column(String(20), default='auto')
    fulfillment_minutes: Mapped[int] = mapped_column(Integer, default=30)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    logo_emoji: Mapped[str] = mapped_column(String(16), default='🏪')
    owner_subject: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    products: Mapped[list['Product']] = relationship(back_populates='merchant')

class Product(Base):
    __tablename__='products'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    location_id: Mapped[str | None] = mapped_column(ForeignKey('merchant_locations.id'), nullable=True, index=True)
    canonical_product_id: Mapped[str | None] = mapped_column(ForeignKey('canonical_products.id'), nullable=True, index=True)
    image_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default='')
    category: Mapped[str] = mapped_column(String(90), default='Miscellaneous')
    sku: Mapped[str] = mapped_column(String(90), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    hold_quantity: Mapped[int] = mapped_column(Integer, default=0)
    stock_updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    image_emoji: Mapped[str] = mapped_column(String(16), default='📦')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    inventory_source: Mapped[str] = mapped_column(String(60), default='manual')
    source_product_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_observed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_metadata: Mapped[str] = mapped_column(Text, default='{}')
    availability_state: Mapped[str] = mapped_column(String(40), default='uncertain')
    supports_reservation: Mapped[bool] = mapped_column(Boolean, default=False)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    merchant: Mapped[Merchant] = relationship(back_populates='products')
    __table_args__=(Index('uq_manual_location_sku','merchant_id','location_id','sku',unique=True,
        sqlite_where=text("inventory_source IN ('manual','merchant_manual','synthetic_local')"),
        postgresql_where=text("inventory_source IN ('manual','merchant_manual','synthetic_local')")),Index('ix_products_category_name','category','name'),
        CheckConstraint('price_cents > 0', name='ck_product_price'),
        CheckConstraint('quantity >= 0 AND hold_quantity >= 0 AND hold_quantity <= quantity', name='ck_product_stock'))

class Order(Base):
    __tablename__='orders'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    location_id: Mapped[str | None] = mapped_column(ForeignKey('merchant_locations.id'), nullable=True, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id'), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    buyer_subject: Mapped[str] = mapped_column(String(160), nullable=False)
    buyer_name: Mapped[str] = mapped_column(String(130), default='Guest')
    status: Mapped[str] = mapped_column(String(32), default='RESERVED')
    payment_status: Mapped[str] = mapped_column(String(40), default='NOT_STARTED')
    payment_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    paypal_order_id: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    paypal_capture_id: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    paypal_refund_id: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    hold_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    hold_released: Mapped[bool] = mapped_column(Boolean, default=False)
    inventory_committed: Mapped[bool] = mapped_column(Boolean, default=False)
    inventory_restocked: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmation_status: Mapped[str] = mapped_column(String(32), default='CONFIRMED')
    confirmed_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expected_payee_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=0)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    __table_args__=(UniqueConstraint('buyer_subject','idempotency_key',name='uq_buyer_order_idem'),
        CheckConstraint('quantity > 0 AND amount_cents > 0', name='ck_order_amount'),
        Index('ix_order_expiry', 'payment_status', 'hold_expires_at'))

class Review(Base):
    __tablename__='reviews'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), unique=True, nullable=False)
    buyer_subject: Mapped[str] = mapped_column(String(160), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(String(1500), default='')
    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    reply: Mapped[str] = mapped_column(String(1500), default='')
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class Audit(Base):
    __tablename__='audit_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor: Mapped[str] = mapped_column(String(160), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), default='')
    details: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class ProviderWebhook(Base):
    __tablename__='provider_webhooks'
    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    event_type: Mapped[str] = mapped_column(String(120), default='')
    payload: Mapped[str] = mapped_column(Text, default='{}')
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)


class MerchantLocation(Base):
    __tablename__ = 'merchant_locations'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    name: Mapped[str] = mapped_column(String(130), default='Main branch')
    address: Mapped[str] = mapped_column(String(250), default='')
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(80), default='UTC')
    hours: Mapped[str] = mapped_column(Text, default='{}')
    special_hours: Mapped[str] = mapped_column(Text, default='{}')
    operational_status: Mapped[str] = mapped_column(String(20), default='auto')
    phone: Mapped[str] = mapped_column(String(80), default='')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (CheckConstraint("operational_status IN ('auto','open','closed','delayed')", name='ck_location_status'),
        CheckConstraint('latitude >= -90 AND latitude <= 90 AND longitude >= -180 AND longitude <= 180', name='ck_location_coordinates'))


class MerchantMembership(Base):
    __tablename__ = 'merchant_memberships'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    subject: Mapped[str] = mapped_column(String(160), index=True)
    role: Mapped[str] = mapped_column(String(20), default='staff')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (UniqueConstraint('merchant_id', 'subject', name='uq_membership_subject'),
        CheckConstraint("role IN ('owner','manager','staff')", name='ck_membership_role'))


class StaffInvitation(Base):
    __tablename__ = 'staff_invitations'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(160), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default='staff')
    invited_by: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default='PENDING')
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (CheckConstraint("role IN ('manager','staff')", name='ck_invitation_role'),)


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id'), index=True)
    product_name: Mapped[str] = mapped_column(String(180))
    sku: Mapped[str] = mapped_column(String(90))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint('order_id', 'product_id', name='uq_order_item'),
        CheckConstraint('quantity > 0 AND unit_price_cents > 0', name='ck_order_item_money'))


class InventoryReservation(Base):
    __tablename__ = 'inventory_reservations'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id'), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(32), default='PENDING_CONFIRMATION')
    source: Mapped[str] = mapped_column(String(60), default='manual_confirmation')
    proof_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (UniqueConstraint('order_id', 'product_id', name='uq_reservation_item'),
        CheckConstraint('quantity > 0', name='ck_reservation_quantity'),
        CheckConstraint("state IN ('PENDING_CONFIRMATION','HELD','CONSUMED','RELEASED')", name='ck_reservation_state'))


class PaymentAttempt(Base):
    __tablename__ = 'payment_attempts'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), unique=True)
    provider: Mapped[str] = mapped_column(String(32), default='paypal_sandbox')
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    expected_payee_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    provider_order_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    capture_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    state: Mapped[str] = mapped_column(String(40), default='CREATING')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (CheckConstraint('amount_cents > 0', name='ck_attempt_amount'),)


class ProviderOperation(Base):
    __tablename__ = 'provider_operations'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    request_id: Mapped[str] = mapped_column(String(80), unique=True)
    state: Mapped[str] = mapped_column(String(32), default='IN_FLIGHT')
    lease_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    provider_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    __table_args__ = (UniqueConstraint('order_id', 'kind', name='uq_order_provider_operation'),)


class Refund(Base):
    __tablename__ = 'refunds'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), unique=True)
    capture_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_refund_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    state: Mapped[str] = mapped_column(String(32), default='PENDING')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (CheckConstraint('amount_cents > 0', name='ck_refund_amount'),)


class PaymentEvent(Base):
    __tablename__ = 'payment_events'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    dedupe_key: Mapped[str] = mapped_column(String(200), unique=True)
    details: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class OutboxJob(Base):
    __tablename__ = 'outbox_jobs'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    kind: Mapped[str] = mapped_column(String(80))
    dedupe_key: Mapped[str] = mapped_column(String(200), unique=True)
    payload: Mapped[str] = mapped_column(Text, default='{}')
    state: Mapped[str] = mapped_column(String(20), default='PENDING')
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    lease_token: Mapped[str | None] = mapped_column(String(48), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (Index('ix_outbox_due', 'state', 'available_at'),)


class PickupSlot(Base):
    __tablename__ = 'pickup_slots'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    location_id: Mapped[str] = mapped_column(ForeignKey('merchant_locations.id'), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    capacity: Mapped[int] = mapped_column(Integer)
    booked_count: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (CheckConstraint('capacity > 0 AND booked_count >= 0 AND booked_count <= capacity', name='ck_pickup_capacity'),
        CheckConstraint('end_at > start_at', name='ck_pickup_window'),
        UniqueConstraint('location_id', 'start_at', 'end_at', name='uq_location_pickup_window'))


class PickupBooking(Base):
    __tablename__ = 'pickup_bookings'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), unique=True)
    slot_id: Mapped[str] = mapped_column(ForeignKey('pickup_slots.id'), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class FulfilmentProof(Base):
    __tablename__ = 'fulfilment_proofs'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    state: Mapped[str] = mapped_column(String(32))
    actor: Mapped[str] = mapped_column(String(160))
    proof: Mapped[str] = mapped_column(String(500), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (UniqueConstraint('order_id', 'state', name='uq_fulfilment_proof'),)


class CanonicalProduct(Base):
    __tablename__ = 'canonical_products'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    gtin: Mapped[str] = mapped_column(String(14), unique=True)
    name: Mapped[str] = mapped_column(String(180))
    brand: Mapped[str] = mapped_column(String(100), default='')
    category: Mapped[str] = mapped_column(String(90), default='Retail')
    attributes: Mapped[str] = mapped_column(Text, default='{}')


class Notification(Base):
    __tablename__ = 'notifications'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    audience: Mapped[str] = mapped_column(String(20))
    buyer_subject: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(String(300))
    seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (UniqueConstraint('order_id', 'event_type', 'audience', name='uq_notification_effect'),)


class AssistantThread(Base):
    """Server-side assistant chat history; one row per conversation, owned by exactly one subject."""
    __tablename__='assistant_threads'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_subject: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    surface: Mapped[str] = mapped_column(String(16), nullable=False, default='shopper', server_default='shopper')
    title: Mapped[str] = mapped_column(String(120), nullable=False, default='New chat')
    messages: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    __table_args__ = (Index('ix_assistant_threads_owner_updated', 'owner_subject', 'updated_at'),
                      Index('ix_assistant_threads_owner_surface', 'owner_subject', 'surface', 'updated_at'),
                      CheckConstraint("surface IN ('shopper','merchant')", name='ck_assistant_threads_surface'))
