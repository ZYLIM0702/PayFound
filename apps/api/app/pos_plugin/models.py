"""Custom POS connector tables. Import registers them with Base.metadata."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..connectors.models import now
from ..database import Base


def new_id() -> str:
    return uuid4().hex


class PosConnection(Base):
    __tablename__ = 'pos_connections'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    name: Mapped[str] = mapped_column(String(80))
    mode: Mapped[str] = mapped_column(String(8))  # api | push
    # connected | syncing | error | paused | disconnected
    status: Mapped[str] = mapped_column(String(16), default='connected')
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    products_path: Mapped[str] = mapped_column(String(200), default='/products')
    branches_path: Mapped[str | None] = mapped_column(String(200), nullable=True, default='/branches')
    health_path: Mapped[str] = mapped_column(String(200), default='/health')
    auth_scheme: Mapped[str] = mapped_column(String(16), default='bearer')  # bearer | api_key
    credentials_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    credential_hint: Mapped[str | None] = mapped_column(String(16), nullable=True)  # masked, last 4 only
    schedule: Mapped[str] = mapped_column(String(8), default='manual')  # 15m | 1h | manual
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    cursor_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(300), nullable=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    __table_args__ = (Index('ix_pos_connections_due', 'status', 'next_sync_at'),)


class PosSyncRun(Base):
    __tablename__ = 'pos_sync_runs'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=new_id)
    connection_id: Mapped[str] = mapped_column(ForeignKey('pos_connections.id'), index=True)
    trigger: Mapped[str] = mapped_column(String(12))  # manual | schedule | push
    status: Mapped[str] = mapped_column(String(12), default='running')  # running | ok | partial | failed
    started_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created: Mapped[int] = mapped_column(Integer, default=0)
    updated: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(String(300), nullable=True)
    row_errors: Mapped[list] = mapped_column(JSON, default=list)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Webhook replay guard: signature digest of an accepted delivery.
    delivery_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    __table_args__ = (UniqueConstraint('connection_id', 'delivery_id', name='uq_pos_run_delivery'),)
