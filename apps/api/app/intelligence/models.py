"""Pilot tables registered on the core SQLAlchemy Base; no import-time DDL."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from ..models import utcnow


def identifier() -> str:
    return uuid.uuid4().hex


class MerchantReport(Base):
    __tablename__ = 'merchant_reports'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=identifier)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    state: Mapped[dict] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    __table_args__ = (CheckConstraint('version > 0', name='ck_merchant_report_version'),)
    __mapper_args__ = {'version_id_col': version}


class ConsentGrant(Base):
    __tablename__ = 'ai_consent_grants'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=identifier)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(String(80), nullable=False, default='remote_merchant_inference')
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    __table_args__ = (UniqueConstraint('merchant_id', 'purpose', name='uq_ai_consent_merchant_purpose'),)


class AgentRun(Base):
    __tablename__ = 'agent_runs'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=identifier)
    merchant_id: Mapped[str | None] = mapped_column(ForeignKey('merchants.id'), nullable=True, index=True)
    principal_key: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(24), nullable=False)
    mode: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    tools: Mapped[list] = mapped_column(JSON, nullable=False)
    product_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    reserved_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    usage_estimated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, index=True)


class MerchantReportCard(Base):
    """Named, assistant-built report saved per merchant (spec JSON; numbers are recomputed from live data when opened)."""
    __tablename__ = 'merchant_report_cards'
    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=identifier)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    focus: Mapped[str | None] = mapped_column(String(120))
    created_by: Mapped[str | None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    __table_args__ = (CheckConstraint('days BETWEEN 1 AND 90', name='ck_report_card_days'),)
