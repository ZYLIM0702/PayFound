"""Connector-owned tables. Import before running the core migration/create_all step."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def new_id() -> str:
    return uuid4().hex


class ConnectorConnection(Base):
    __tablename__ = 'connector_connections'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    provider: Mapped[str] = mapped_column(String(24))
    # Unique across tenants: a store may not silently feed a second merchant.
    source_key: Mapped[str] = mapped_column(String(500), unique=True)
    store_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    shop_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default='authorization_required')
    credentials_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    capabilities: Mapped[dict] = mapped_column(JSON, default=dict)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    sync_cursor: Mapped[dict] = mapped_column(JSON, default=dict)
    generation: Mapped[str | None] = mapped_column(String(48), nullable=True)
    cycle_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(300), nullable=True)
    lease_token: Mapped[str | None] = mapped_column(String(48), nullable=True)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    state_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    state_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    authorized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    consent_subject: Mapped[str | None] = mapped_column(String(160), nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class ConnectorLocation(Base):
    __tablename__ = 'connector_locations'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    connection_id: Mapped[str] = mapped_column(ForeignKey('connector_connections.id'), index=True)
    source_location_id: Mapped[str] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(180))
    kind: Mapped[str] = mapped_column(String(24), default='physical')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # FK intentionally resolved by the shared core's MerchantLocation model.
    location_id: Mapped[str | None] = mapped_column(ForeignKey('merchant_locations.id'), nullable=True, index=True)
    mapping_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    seen_generation: Mapped[str | None] = mapped_column(String(48), nullable=True)
    __table_args__ = (UniqueConstraint('connection_id', 'source_location_id'),)


class ConnectorOffer(Base):
    __tablename__ = 'connector_offers'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    connection_id: Mapped[str] = mapped_column(ForeignKey('connector_connections.id'), index=True)
    source_location_id: Mapped[str] = mapped_column(String(160))
    source_product_id: Mapped[str] = mapped_column(String(160))
    source_variant_id: Mapped[str] = mapped_column(String(160))
    sku: Mapped[str] = mapped_column(String(90))
    product_id: Mapped[str | None] = mapped_column(ForeignKey('products.id'), nullable=True, index=True)
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    source_catalog_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_inventory_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    seen_generation: Mapped[str | None] = mapped_column(String(48), nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(160), nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('connection_id', 'source_location_id', 'source_variant_id'),)


class ConnectorSyncRun(Base):
    __tablename__ = 'connector_sync_runs'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    connection_id: Mapped[str] = mapped_column(ForeignKey('connector_connections.id'), index=True)
    status: Mapped[str] = mapped_column(String(24), default='running')
    started_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(String(300), nullable=True)


class ConnectorEvent(Base):
    __tablename__ = 'connector_events'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    connection_id: Mapped[str] = mapped_column(ForeignKey('connector_connections.id'), index=True)
    delivery_id: Mapped[str] = mapped_column(String(160))
    topic: Mapped[str] = mapped_column(String(100))
    body_hash: Mapped[str] = mapped_column(String(64))
    payload_encrypted: Mapped[str] = mapped_column(Text)
    emitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default='pending')
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(String(300), nullable=True)
    __table_args__ = (
        UniqueConstraint('connection_id', 'delivery_id'),
        UniqueConstraint('connection_id', 'topic', 'body_hash'),
        Index('ix_connector_events_pending', 'status', 'next_attempt_at'),
    )
