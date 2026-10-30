"""Pure helpers for the richer DEMO forecast: demo calendar, weekday curve, payday window, stock-out aware rates, pickup outlook."""
from __future__ import annotations

import calendar as _cal
from datetime import date, timedelta

CALENDAR_NOTE = 'Demo calendar: approximate dates written for demonstration. Not authoritative holiday data; confirm real dates before relying on them.'

# Weekday curve prior (Mon..Sun) for a neighbourhood store: weekend peak, Friday lift, quiet early week. Normalised to mean 1.
DOW_PRIOR = [0.92, 0.94, 0.97, 1.0, 1.08, 1.16, 1.0]
DOW_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# (start, end, name, kind, effect_pct on discretionary categories). Essentials get half the effect.
_INTL = [
    ('2026-11-11', None, "Singles' Day online sales", 'promotion', -3),  # pulls some spend online
    ('2026-11-27', None, 'Black Friday', 'promotion', 12),
    ('2026-11-30', None, 'Cyber Monday', 'promotion', -3),
    ('2026-12-24', None, 'Christmas Eve', 'festive', 15),
    ('2026-12-25', None, 'Christmas Day', 'public_holiday', -25),
    ('2026-12-31', None, "New Year's Eve", 'festive', 8),
    ('2027-01-01', None, "New Year's Day", 'public_holiday', -20),
    ('2027-02-14', None, "Valentine's Day", 'festive', 10),
]
_BY_COUNTRY = {
    'MY': [
        ('2026-11-08', None, 'Deepavali', 'public_holiday', -10),
        ('2026-11-21', '2027-01-03', 'School year-end holidays', 'school_holiday', 6),
        ('2027-02-06', '2027-02-08', 'Chinese New Year', 'public_holiday', 14),
        ('2027-02-08', '2027-03-09', 'Ramadan', 'festive', 7),
        ('2027-03-10', '2027-03-11', 'Hari Raya Aidilfitri', 'public_holiday', -12),
        ('2026-12-25', None, 'Christmas Day', 'public_holiday', -10),
    ],
    'SG': [
        ('2026-11-08', None, 'Deepavali', 'public_holiday', -10),
        ('2026-11-28', '2026-12-31', 'School year-end holidays', 'school_holiday', 6),
        ('2027-02-06', '2027-02-08', 'Chinese New Year', 'public_holiday', 14),
        ('2027-03-10', None, 'Hari Raya Puasa', 'public_holiday', -12),
    ],
    'US': [
        ('2026-10-31', None, 'Halloween', 'festive', 10),
        ('2026-11-11', None, 'Veterans Day', 'public_holiday', 3),
        ('2026-11-26', None, 'Thanksgiving', 'public_holiday', -18),
        ('2026-12-21', '2027-01-04', 'Winter school holidays', 'school_holiday', 6),
        ('2027-01-18', None, 'Martin Luther King Jr. Day', 'public_holiday', 4),
    ],
}
COUNTRY_NAMES = {'MY': 'Malaysia', 'SG': 'Singapore', 'US': 'United States', 'INTL': 'International'}
COUNTRY_PAYDAYS = {'MY': 'month-end and the 25th', 'SG': 'month-end', 'US': 'the 15th and month-end', 'INTL': 'month-end'}


def country_for(timezone_name: str | None, lat: float | None = None, lng: float | None = None) -> str:
    tz = timezone_name or ''
    if tz in ('Asia/Kuala_Lumpur', 'Asia/Kuching'):
        return 'MY'
    if tz == 'Asia/Singapore':
        return 'SG'
    if tz.startswith('America/') or tz.startswith('US/'):
        if lat is None or (24 <= lat <= 50 and -125 <= (lng or 0) <= -66):
            return 'US'
    return 'INTL'


def calendar_entries(country: str, start: date, end: date) -> list[dict]:
    """Demo calendar entries overlapping start..end, expanded to one row per day."""
    rows, seen = [], set()
    for s, e, name, kind, effect in _INTL + _BY_COUNTRY.get(country, []):
        first, last = date.fromisoformat(s), date.fromisoformat(e or s)
        d = max(first, start)
        while d <= min(last, end):
            if (d, name) not in seen:
                seen.add((d, name))
                rows.append({'date': d.isoformat(), 'name': name, 'kind': kind, 'effect_pct': effect, 'demo': True,
                             'range_start': first.isoformat(), 'range_end': last.isoformat()})
            d += timedelta(days=1)
    return sorted(rows, key=lambda r: (r['date'], r['name']))


def holiday_factor(entries_on_day: list[dict], essential: bool) -> tuple[float, str | None]:
    if not entries_on_day:
        return 1.0, None
    top = max(entries_on_day, key=lambda r: (abs(r['effect_pct']), r['name']))
    effect = sum(r['effect_pct'] for r in entries_on_day)
    effect = max(-40, min(30, effect)) * (0.5 if essential else 1.0)
    return round(1 + effect / 100, 3), top['name']


def paydays_in(country: str, start: date, end: date) -> list[date]:
    out = []
    y, m = start.year, start.month
    while date(y, m, 1) <= end + timedelta(days=31):
        last = _cal.monthrange(y, m)[1]
        days = {last}
        if country == 'US':
            days.add(15)
        if country == 'MY':
            days.add(25)
        out += [date(y, m, d) for d in sorted(days)]
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return sorted(d for d in out if start - timedelta(days=31) <= d <= end + timedelta(days=31))


def payday_position(day: date, country: str) -> tuple[int | None, int | None]:
    """(days since the last payday, days until the next payday) using the demo payday rule for the country."""
    days = paydays_in(country, day - timedelta(days=31), day + timedelta(days=31))
    prev = max((d for d in days if d <= day), default=None)
    nxt = min((d for d in days if d > day), default=None)
    return ((day - prev).days if prev else None, (nxt - day).days if nxt else None)


def payday_factor(day: date, country: str, essential: bool) -> tuple[float, str | None]:
    """First days after payday lift discretionary spend; the last days before it are a little tighter."""
    since, to_next = payday_position(day, country)
    if since is not None and since <= 3:
        gain = 0.10 * (1 - since / 4) * (0.4 if essential else 1.0)
        return round(1 + gain, 3), ('Payday today' if since == 0 else f'{since} day{"s" if since != 1 else ""} after payday')
    if to_next is not None and to_next <= 3:
        return round(1 - 0.03 * (0.4 if essential else 1.0), 3), f'{to_next} day{"s" if to_next != 1 else ""} before payday'
    return 1.0, None


def weekday_curve(order_days: list[date], window_days: list[date]) -> tuple[list[float], str]:
    """Weekday multipliers Mon..Sun. Blends the prior with observed orders per weekday once there are enough orders."""
    prior_mean = sum(DOW_PRIOR) / 7
    prior = [v / prior_mean for v in DOW_PRIOR]
    if len(order_days) < 30:
        return [round(v, 3) for v in prior], 'modelled'
    occurrences = [max(1, sum(1 for d in window_days if d.weekday() == k)) for k in range(7)]
    per_day = [sum(1 for d in order_days if d.weekday() == k) / occurrences[k] for k in range(7)]
    mean = sum(per_day) / 7 or 1
    observed = [v / mean for v in per_day]
    return [round(max(0.8, min(1.25, 0.65 * a + 0.35 * b)), 3) for a, b in zip(prior, observed)], 'observed'


def product_rate(series: list[float], available: int, prior: float, window: int) -> dict:
    """Units/day for a product. series[0] is today, counted backwards."""
    naive = (sum(series) + prior * 7) / (window + 7)
    suppressed = 0
    if available <= 0:
        age = next((i for i, v in enumerate(series) if v > 0), window)
        suppressed = age if age >= 2 else 0
    usable = window - suppressed
    rate = (sum(series[suppressed:]) + prior * 7) / (usable + 7)
    return {'rate': rate, 'naive_rate': naive, 'suppressed_days': suppressed,
            'clean_series': [rate if i < suppressed else v for i, v in enumerate(series)]}


def pickup_flag(expected: int, capacity: int) -> str:
    if capacity <= 0:
        return 'none'
    if expected >= capacity:
        return 'capped'
    return 'tight' if expected >= 0.85 * capacity else 'ok'
