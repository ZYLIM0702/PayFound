"""The documented JSON contract (see apps/api/docs/pos-plugin.md). Unknown fields are ignored;"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import re
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

MAX_ROWS = 1000
MAX_REPORTED_ERRORS = 25


class ContractError(ValueError):
    """Envelope-level problem; the message is safe to show to the merchant / POS."""


def _naive_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value
    return value


class PosProduct(BaseModel):
    model_config = ConfigDict(extra='ignore', str_strip_whitespace=True)
    external_id: str = Field(min_length=1, max_length=120)
    sku: str = Field(min_length=1, max_length=90)
    name: str = Field(min_length=1, max_length=180)
    price: Decimal = Field(gt=0, le=Decimal('10000000'), decimal_places=2)
    currency: str = Field(default='USD', pattern=r'^[A-Za-z]{3}$')
    quantity: int = Field(ge=0, le=1_000_000)
    branch_external_id: str | None = Field(default=None, max_length=120)
    updated_at: datetime | None = None
    active: bool = True

    _utc = field_validator('updated_at')(_naive_utc)

    @property
    def price_cents(self) -> int:
        return int((self.price * 100).to_integral_value())


class PosBranch(BaseModel):
    model_config = ConfigDict(extra='ignore', str_strip_whitespace=True)
    external_id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=130)
    address: str = Field(default='', max_length=250)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(default='UTC', max_length=80)

    @field_validator('timezone')
    @classmethod
    def _tz(cls, value):
        if not re.fullmatch(r'[A-Za-z0-9_+\-/]{1,80}', value):
            raise ValueError('invalid timezone')
        try:
            ZoneInfo(value)
        except Exception as exc:
            raise ValueError('unknown IANA timezone') from exc
        return value


class PosStockEvent(BaseModel):
    """Absolute stock level for one product (not a delta, so redelivery is harmless)."""
    model_config = ConfigDict(extra='ignore', str_strip_whitespace=True)
    external_id: str = Field(min_length=1, max_length=120)
    quantity: int = Field(ge=0, le=1_000_000)
    updated_at: datetime | None = None

    _utc = field_validator('updated_at')(_naive_utc)


def parse_rows(raw, model, label: str):
    """Return (valid_rows, errors). `errors` are {index, external_id, error}; secrets never included."""
    if raw is None:
        return [], []
    if not isinstance(raw, list):
        raise ContractError(f'"{label}" must be a list')
    if len(raw) > MAX_ROWS:
        raise ContractError(f'"{label}" has {len(raw)} rows; the maximum is {MAX_ROWS} per request')
    valid, errors = [], []
    for index, item in enumerate(raw):
        try:
            if not isinstance(item, dict):
                raise ValueError('row must be an object')
            valid.append(model.model_validate(item))
        except (ValidationError, ValueError) as exc:
            if isinstance(exc, ValidationError):
                first = exc.errors()[0]
                reason = f"{'.'.join(str(p) for p in first['loc']) or 'row'}: {first['msg']}"
            else:
                reason = str(exc)
            ident = item.get('external_id') if isinstance(item, dict) else None
            errors.append({'index': index, 'external_id': str(ident)[:60] if ident is not None else None,
                           'error': f'{label}: {reason}'[:200]})
    return valid, errors
