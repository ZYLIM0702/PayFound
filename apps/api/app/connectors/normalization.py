from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import re

from .security import ConnectorError


def timestamp(value) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return (parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed).astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError):
        raise ConnectorError('Provider returned an invalid source timestamp')


def money_cents(value, currency: str) -> int:
    # Core uses cents; unsupported/non-two-decimal currencies fail closed rather
    # than silently multiplying JPY/KWD by an incorrect minor-unit exponent.
    if currency not in {'USD', 'MYR', 'SGD', 'EUR', 'GBP', 'AUD', 'CAD', 'NZD', 'HKD', 'CHF', 'CNY', 'INR', 'THB', 'PHP', 'IDR'}:
        raise ConnectorError('Currency is not supported by the pilot cents schema')
    if not isinstance(value, (str, Decimal, int)) or isinstance(value, bool):
        raise ConnectorError('Provider price must be an exact decimal string')
    if not re.fullmatch(r'\d+(?:\.\d+)?', str(value)):
        raise ConnectorError('Provider price is invalid')
    try:
        cents = Decimal(value) * 100
        if not cents.is_finite() or cents != cents.to_integral_value() or cents < 0 or cents > 2_000_000_000:
            raise InvalidOperation()
        return int(cents)
    except (InvalidOperation, ValueError):
        raise ConnectorError('Provider price cannot be represented exactly in cents')


def quantity(value):
    if value is None:
        return None
    if type(value) is not int:
        raise ConnectorError('Provider stock must be an integer')
    # Negative provider availability means unavailable, never negative local stock.
    return max(0, min(value, 2_000_000_000))
